#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import urlparse
from DAV.errors import DAV_NotFound, DAV_Forbidden
from trytond.model import ModelView, ModelSQL
from trytond.tools import reduce_ids
from trytond.transaction import Transaction
from trytond.cache import Cache
from trytond.pool import Pool


CARDDAV_NS = 'urn:ietf:params:xml:ns:carddav'


class Collection(ModelSQL, ModelView):

    _name = "webdav.collection"

    @Cache('webdav_collection.vcard')
    def vcard(self, uri):
        '''
        Return party ids of the vcard in uri or False

        :param uri: the uri
        :return: party id
            or None if there is no party
            or False if not in Contacts
        '''
        party_obj = Pool().get('party.party')

        if uri and uri.startswith('Contacts/'):
            uuid = uri[9:-4]
            party_ids = party_obj.search([
                ('uuid', '=', uuid),
                ], limit=1)
            if party_ids:
                return party_ids[0]
            return None
        if uri == 'Contacts':
            return None
        return False

    def _carddav_filter_domain(self, filter):
        '''
        Return a domain for the carddav filter

        :param filter: the DOM Element of filter
        :return: a list for domain
        '''
        address_obj = Pool().get('party.address')
        contact_mechanism_obj = Pool().get('party.contact_mechanism')

        res = []
        if not filter:
            return []
        if filter.localName == 'addressbook-query':
            addressbook_filter = filter.getElementsByTagNameNS(
                    'urn:ietf:params:xml:ns:carddav', 'filter')[0]
            if addressbook_filter.hasAttribute('test') \
                    and addressbook_filter.getAttribute('test') == 'allof':
                res.append('AND')
            else:
                res.append('OR')

            for prop in addressbook_filter.childNodes:
                name = prop.getAttribute('name').lower()
                field = None
                if name == 'fn':
                    field = 'rec_name'
                if name == 'n':
                    field = 'name'
                if name == 'uid':
                    field = 'uid'
                if name == 'adr':
                    field = 'rec_name'
                if name in ('mail', 'tel'):
                    field = 'value'
                if field:
                    res2 = []
                    if prop.hasAttribute('test') \
                            and prop.addressbook_filter.getAttribute('test') == 'allof':
                        res2.append('AND')
                    else:
                        res2.append('OR')
                    if prop.getElementsByTagNameNS(CARDDAV_NS, 'is-not-defined'):
                        res2.append((field, '=', False))
                    for text_match in prop.getElementsByTagNameNS(CARDDAV_NS,
                            'text-match'):
                        value = text_match.firstChild.data
                        negate = False
                        if text_match.hasAttribute('negate-condition') \
                                and text_match.getAttribute(
                                        'negate-condition') == 'yes':
                            negate = True
                        type = 'contains'
                        if text_match.hasAttribute('match-type'):
                            type = text_match.getAttribute('match-type')
                        if type == 'equals':
                            pass
                        elif type in ('contains', 'substring'):
                            value = '%' + value + '%'
                        elif type == 'starts-with':
                            value = value + '%'
                        elif type == 'ends-with':
                            value = '%' + value
                        if not negate:
                            res2.append((field, 'ilike', value))
                        else:
                            res2.append((field, 'not ilike', value))
                    if name == 'adr':
                        domain = res2
                        address_ids = address_obj.search(domain)
                        res = [('addresses', 'in', address_ids)]
                    elif name in ('mail', 'tel'):
                        if name == 'mail':
                            type = ['email']
                        else:
                            type = ['phone', 'mobile']
                        domain = [('type', 'in', type), res2]
                        contact_mechanism_ids = contact_mechanism_obj.search(
                                domain)
                        res2 = [
                            ('contact_mechanisms', 'in', contact_mechanism_ids)
                            ]
                    res.append(res2)
        return res

    def get_childs(self, uri, filter=None, cache=None):
        party_obj = Pool().get('party.party')

        if uri in ('Contacts', 'Contacts/'):
            domain = self._carddav_filter_domain(filter)
            party_ids = party_obj.search(domain)
            parties = party_obj.browse(party_ids)
            if cache is not None:
                cache.setdefault('_contact', {})
                for party_id in party_ids:
                    cache['_contact'][party_id] = {}
            return [x.uuid + '.vcf' for x in parties]
        party_id = self.vcard(uri)
        if party_id or party_id is None:
            return []
        res = super(Collection, self).get_childs(uri, filter=filter,
                cache=cache)
        if not uri and not filter:
            res.append('Contacts')
        return res

    def get_resourcetype(self, uri, cache=None):
        from DAV.constants import COLLECTION, OBJECT
        party_id = self.vcard(uri)
        if party_id:
            return OBJECT
        elif party_id is None:
            return COLLECTION
        return super(Collection, self).get_resourcetype(uri, cache=cache)

    def get_contenttype(self, uri, cache=None):
        if self.vcard(uri):
            return 'text/x-vcard'
        return super(Collection, self).get_contenttype(uri, cache=cache)

    def get_creationdate(self, uri, cache=None):
        party_obj = Pool().get('party.party')
        party_id = self.vcard(uri)

        cursor = Transaction().cursor

        if party_id is None:
            raise DAV_NotFound
        if party_id:
            if cache is not None:
                cache.setdefault('_contact', {})
                ids = cache['_contact'].keys()
                if party_id not in ids:
                    ids.append(party_id)
                elif 'creationdate' in cache['_contact'][party_id]:
                    return cache['_contact'][party_id]['creationdate']
            else:
                ids = [party_id]
            res = None
            for i in range(0, len(ids), cursor.IN_MAX):
                sub_ids = ids[i:i + cursor.IN_MAX]
                red_sql, red_ids = reduce_ids('id', sub_ids)
                cursor.execute('SELECT id, ' \
                            'EXTRACT(epoch FROM create_date) ' \
                        'FROM "' + party_obj._table + '" ' \
                        'WHERE ' + red_sql, red_ids)
                for party_id2, date in cursor.fetchall():
                    if party_id2 == party_id:
                        res = date
                    if cache is not None:
                        cache['_contact'].setdefault(party_id2, {})
                        cache['_contact'][party_id2]['creationdate'] = date
            if res is not None:
                return res
        return super(Collection, self).get_creationdate(uri, cache=cache)

    def get_lastmodified(self, uri, cache=None):
        pool = Pool()
        party_obj = pool.get('party.party')
        address_obj = pool.get('party.address')
        contact_mechanism_obj = pool.get('party.contact_mechanism')

        cursor = Transaction().cursor

        party_id = self.vcard(uri)
        if party_id:
            if cache is not None:
                cache.setdefault('_contact', {})
                ids = cache['_contact'].keys()
                if party_id not in ids:
                    ids.append(party_id)
                elif 'lastmodified' in cache['_contact'][party_id]:
                    return cache['_contact'][party_id]['lastmodified']
            else:
                ids = [party_id]
            res = None
            for i in range(0, len(ids), cursor.IN_MAX):
                sub_ids = ids[i:i + cursor.IN_MAX]
                red_sql, red_ids = reduce_ids('p.id', sub_ids)
                cursor.execute('SELECT p.id, ' \
                            'MAX(EXTRACT(epoch FROM ' \
                                'COALESCE(p.write_date, p.create_date))), ' \
                            'MAX(EXTRACT(epoch FROM ' \
                                'COALESCE(a.write_date, a.create_date))), ' \
                            'MAX(EXTRACT(epoch FROM ' \
                                'COALESCE(c.write_date, c.create_date))) ' \
                        'FROM "' + party_obj._table + '" p ' \
                            'LEFT JOIN "' + address_obj._table + '" a ' \
                            'ON p.id = a.party ' \
                            'LEFT JOIN "' + contact_mechanism_obj._table + '" c ' \
                            'ON p.id = c.party ' \
                        'WHERE ' + red_sql + ' ' \
                        'GROUP BY p.id', red_ids)
                for party_id2, date_p, date_a, date_c in cursor.fetchall():
                    date = max(date_p, date_a, date_c)
                    if party_id2 == party_id:
                        res = date
                    if cache is not None:
                        cache['_contact'].setdefault(party_id2, {})
                        cache['_contact'][party_id2]['lastmodified'] = date
            if res is not None:
                return res
        return super(Collection, self).get_lastmodified(uri, cache=cache)

    def get_data(self, uri, cache=None):
        vcard_obj = Pool().get('party_vcarddav.party.vcard', type='report')
        party_id = self.vcard(uri)
        if party_id is None:
            raise DAV_NotFound
        if party_id:
            val = vcard_obj.execute([party_id],
                    {'id': party_id, 'ids': [party_id]},
                    )
            return str(val[1])
        return super(Collection, self).get_data(uri, cache=cache)

    def get_address_data(self, uri, cache=None):
        vcard_obj = Pool().get('party_vcarddav.party.vcard', type='report')
        party_id = self.vcard(uri)
        if not party_id:
            raise DAV_NotFound
        return vcard_obj.execute([party_id],
            {'id': party_id, 'ids': [party_id]},
            ).decode('utf-8')

    def put(self, uri, data, content_type, cache=None):
        import vobject
        party_obj = Pool().get('party.party')

        party_id = self.vcard(uri)
        if party_id is None:
            vcard = vobject.readOne(data)
            values = party_obj.vcard2values(None, vcard)
            try:
                party_id = party_obj.create(values)
            except Exception:
                raise DAV_Forbidden
            party = party_obj.browse(party_id)
            return (Transaction().cursor.database_name + '/Contacts/' +
                    party.uuid + '.vcf')
        if party_id:
            vcard = vobject.readOne(data)
            values = party_obj.vcard2values(party_id, vcard)
            try:
                party_obj.write(party_id, values)
            except Exception:
                raise DAV_Forbidden
            return
        return super(Collection, self).put(uri, data, content_type, cache=cache)

    def mkcol(self, uri, cache=None):
        party_id = self.vcard(uri)
        if party_id is None:
            raise DAV_Forbidden
        if party_id:
            raise DAV_Forbidden
        return super(Collection, self).mkcol(uri, cache=cache)

    def rmcol(self, uri, cache=None):
        party_id = self.vcard(uri)
        if party_id is None:
            raise DAV_Forbidden
        if party_id:
            raise DAV_Forbidden
        return super(Collection, self).rmcol(uri, cache=cache)

    def rm(self, uri, cache=None):
        party_obj = Pool().get('party.party')

        party_id = self.vcard(uri)
        if party_id is None:
            raise DAV_Forbidden
        if party_id:
            try:
                party_obj.delete(party_id)
            except Exception:
                raise DAV_Forbidden
            return 200
        return super(Collection, self).rm(uri, cache=cache)

    def exists(self, uri, cache=None):
        party_id = self.vcard(uri)
        if party_id is None or party_id:
            if party_id:
                return 1
            if uri in ('Contacts', 'Contacts/'):
                return 1
            return 0
        return super(Collection, self).exists(uri, cache=cache)

Collection()
