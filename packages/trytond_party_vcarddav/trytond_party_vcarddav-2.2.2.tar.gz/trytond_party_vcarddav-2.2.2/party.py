#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import copy
import uuid
from trytond.model import ModelSQL, ModelView, fields
from trytond.report import Report
from trytond.backend import TableHandler, FIELDS
from trytond.transaction import Transaction
from trytond.pool import Pool


class Party(ModelSQL, ModelView):
    _name = 'party.party'
    uuid = fields.Char('UUID', required=True,
            help='Universally Unique Identifier')
    vcard = fields.Binary('VCard')

    def __init__(self):
        super(Party, self).__init__()
        self._sql_constraints += [
                ('uuid_uniq', 'UNIQUE(uuid)',
                    'The UUID of the party must be unique!'),
        ]

    def init(self, module_name):
        cursor = Transaction().cursor
        table = TableHandler(cursor, self, module_name)

        if not table.column_exist('uuid'):
            table.add_raw_column('uuid',
                    FIELDS[self.uuid._type].sql_type(self.uuid),
                    FIELDS[self.uuid._type].sql_format, None, None)
            cursor.execute('SELECT id FROM "' + self._table + '"')
            for id, in cursor.fetchall():
                cursor.execute('UPDATE "' + self._table + '" ' \
                        'SET "uuid" = %s WHERE id = %s',
                        (self.default_uuid(), id))
        super(Party, self).init(module_name)

    def default_uuid(self):
        return str(uuid.uuid4())

    def create(self, vals):
        collection_obj = Pool().get('webdav.collection')

        res = super(Party, self).create(vals)
        # Restart the cache for vcard
        collection_obj.vcard.reset()
        return res

    def copy(self, ids, default=None):
        int_id = isinstance(ids, (int, long))
        if int_id:
            ids = [ids]

        if default is None:
            default = {}

        new_ids = []
        for party_id in ids:
            current_default = default.copy()
            current_default['uuid'] = self.default_uuid()
            new_id = super(Party, self).copy(party_id, default=current_default)
            new_ids.append(new_id)

        if int_id:
            return new_ids[0]
        return new_ids

    def write(self, ids, vals):
        collection_obj = Pool().get('webdav.collection')

        res = super(Party, self).write(ids, vals)
        # Restart the cache for vcard
        collection_obj.vcard.reset()
        return res

    def delete(self, ids):
        collection_obj = Pool().get('webdav.collection')

        res = super(Party, self).delete(ids)
        # Restart the cache for vcard
        collection_obj.vcard.reset()
        return res

    def vcard2values(self, party_id, vcard):
        '''
        Convert vcard to values for create or write

        :param party_id: the party id for write or None for create
        :param vcard: a vcard instance of vobject
        :return: a dictionary with values
        '''
        import vobject
        address_obj = Pool().get('party.address')

        res = {}
        res['name'] = vcard.fn.value
        if not hasattr(vcard, 'n'):
            vcard.add('n')
            vcard.n.value = vobject.vcard.Name(vcard.fn.value)
        res['vcard'] = vcard.serialize()
        if not party_id:
            if hasattr(vcard, 'uid'):
                res['uuid'] = vcard.uid.value
            res['addresses'] = []
            for adr in vcard.contents.get('adr', []):
                vals = address_obj.vcard2values(adr)
                res['addresses'].append(('create', vals))
            res['contact_mechanisms'] = []
            for email in vcard.contents.get('email', []):
                vals = {}
                vals['type'] = 'email'
                vals['value'] = email.value
                res['contact_mechanisms'].append(('create', vals))
            for tel in vcard.contents.get('tel', []):
                vals = {}
                vals['type'] = 'phone'
                if hasattr(tel, 'type_param') \
                        and 'cell' in tel.type_param.lower():
                    vals['type'] = 'mobile'
                vals['value'] = tel.value
                res['contact_mechanisms'].append(('create', vals))
        else:
            party = self.browse(party_id)
            i = 0
            res['addresses'] = []
            addresses_todelete = []
            for address in party.addresses:
                try:
                    adr = vcard.contents.get('adr', [])[i]
                except IndexError:
                    addresses_todelete.append(address.id)
                    i += 1
                    continue
                if not hasattr(adr, 'value'):
                    addresses_todelete.append(address.id)
                    i += 1
                    continue
                vals = address_obj.vcard2values(adr)
                res['addresses'].append(('write', address.id, vals))
                i += 1
            if addresses_todelete:
                res['addresses'].append(('delete', addresses_todelete))
            try:
                new_addresses = vcard.contents.get('adr', [])[i:]
            except IndexError:
                new_addresses = []
            for adr in new_addresses:
                if not hasattr(adr, 'value'):
                    continue
                vals = address_obj.vcard2values(adr)
                res['addresses'].append(('create', vals))

            i = 0
            res['contact_mechanisms'] = []
            contact_mechanisms_todelete = []
            for cm in party.contact_mechanisms:
                if cm.type != 'email':
                    continue
                try:
                    email = vcard.contents.get('email', [])[i]
                except IndexError:
                    contact_mechanisms_todelete.append(cm.id)
                    i += 1
                    continue
                vals = {}
                vals['value'] = email.value
                res['contact_mechanisms'].append(('write', cm.id, vals))
                i += 1
            try:
                new_emails = vcard.contents.get('email', [])[i:]
            except IndexError:
                new_emails = []
            for email in new_emails:
                if not hasattr(email, 'value'):
                    continue
                vals = {}
                vals['type'] = 'email'
                vals['value'] = email.value
                res['contact_mechanisms'].append(('create', vals))

            i = 0
            for cm in party.contact_mechanisms:
                if cm.type not in ('phone', 'mobile'):
                    continue
                try:
                    tel = vcard.contents.get('tel', [])[i]
                except IndexError:
                    contact_mechanisms_todelete.append(cm.id)
                    i += 1
                    continue
                vals = {}
                vals['value'] = tel.value
                res['contact_mechanisms'].append(('write', cm.id, vals))
                i += 1
            try:
                new_tels = vcard.contents.get('tel', [])[i:]
            except IndexError:
                new_tels = []
            for tel in new_tels:
                if not hasattr(tel, 'value'):
                    continue
                vals = {}
                vals['type'] = 'phone'
                if hasattr(tel, 'type_param') \
                        and 'cell' in tel.type_param.lower():
                    vals['type'] = 'mobile'
                vals['value'] = tel.value
                res['contact_mechanisms'].append(('create', vals))

            if contact_mechanisms_todelete:
                res['contact_mechanisms'].append(('delete',
                    contact_mechanisms_todelete))
        return res

Party()


class Address(ModelSQL, ModelView):
    _name = 'party.address'

    def vcard2values(self, adr):
        '''
        Convert adr from vcard to values for create or write

        :param adr: a adr from vcard instance of vobject
        :return: a dictionary with values
        '''
        country_obj = Pool().get('country.country')
        subdivision_obj = Pool().get('country.subdivision')

        vals = {}
        vals['street'] = adr.value.street or ''
        vals['city'] = adr.value.city or ''
        vals['zip'] = adr.value.code or ''
        if adr.value.country:
            country_ids = country_obj.search([
                ('rec_name', '=', adr.value.country),
                ], limit=1)
            if country_ids:
                vals['country'] = country_ids[0]
                if adr.value.region:
                    subdivision_ids = subdivision_obj.search([
                            ('rec_name', '=', adr.value.region),
                            ('country', '=', country_ids[0]),
                            ], limit=1)
                    if subdivision_ids:
                        vals['subdivision'] = subdivision_ids[0]
        return vals

Address()


class ActionReport(ModelSQL, ModelView):
    _name = 'ir.action.report'

    def __init__(self):
        super(ActionReport, self).__init__()
        new_ext = ('vcf', 'VCard file')
        if new_ext not in self.extension.selection:
            self.extension = copy.copy(self.extension)
            self.extension.selection = copy.copy(self.extension.selection)
            self.extension.selection.append(new_ext)
            self._reset_columns()

ActionReport()


class VCard(Report):
    _name = 'party_vcarddav.party.vcard'

    def execute(self, ids, datas):
        party_obj = Pool().get('party.party')
        action_report_obj = Pool().get('ir.action.report')

        action_report_ids = action_report_obj.search([
            ('report_name', '=', self._name)
            ])
        if not action_report_ids:
            raise Exception('Error', 'Report (%s) not find!' % self._name)
        action_report = action_report_obj.browse(action_report_ids[0])

        parties = party_obj.browse(ids)

        data = ''.join(self.create_vcard(party).serialize() for party in parties)

        return ('vcf', buffer(data), False, action_report.name)

    def create_vcard(self, party):
        '''
        Return a vcard instance of vobject for the party

        :param party: a BrowseRecord of party.party
        :return: a vcard instance of vobject
        '''
        import vobject

        if party.vcard:
            vcard = vobject.readOne(str(party.vcard))
        else:
            vcard = vobject.vCard()
        if not hasattr(vcard, 'n'):
            vcard.add('n')
        if not vcard.n.value:
            vcard.n.value = vobject.vcard.Name(party.name)
        if not hasattr(vcard, 'fn'):
            vcard.add('fn')
        vcard.fn.value = party.full_name
        if not hasattr(vcard, 'uid'):
            vcard.add('uid')
        vcard.uid.value = party.uuid

        i = 0
        for address in party.addresses:
            try:
                adr = vcard.contents.get('adr', [])[i]
            except IndexError:
                adr = None
            if not adr:
                adr = vcard.add('adr')
            if not hasattr(adr, 'value'):
                adr.value = vobject.vcard.Address()
            adr.value.street = address.street and address.street + (
                address.streetbis and  (" " + address.streetbis) or '') or ''
            adr.value.city = address.city or ''
            if address.subdivision:
                adr.value.region = address.subdivision.name or ''
            adr.value.code = address.zip or ''
            if address.country:
                adr.value.country = address.country.name or ''
            i += 1
        try:
            older_addresses = vcard.contents.get('adr', [])[i:]
        except IndexError:
            older_addresses = []
        for adr in older_addresses:
            vcard.contents['adr'].remove(adr)

        email_count = 0
        tel_count = 0
        for cm in party.contact_mechanisms:
            if cm.type == 'email':
                try:
                    email = vcard.contents.get('email', [])[email_count]
                except IndexError:
                    email = None
                if not email:
                    email = vcard.add('email')
                email.value = cm.value
                if not hasattr(email, 'type_param'):
                    email.type_param = 'internet'
                elif 'internet' not in email.type_param.lower():
                    email.type_param += ',internet'
                email_count += 1
            elif cm.type in ('phone', 'mobile'):
                try:
                    tel = vcard.contents.get('tel', [])[tel_count]
                except IndexError:
                    tel = None
                if not tel:
                    tel = vcard.add('tel')
                tel.value = cm.value
                if cm.type == 'mobile':
                    if not hasattr(tel, 'type_param'):
                        tel.type_param = 'cell'
                    elif 'cell' not in tel.type_param.lower():
                        tel.type_param += ',cell'
                else:
                    if not hasattr(tel, 'type_param'):
                        tel.type_param = 'voice'
                tel_count += 1

        try:
            older_emails = vcard.contents.get('email', [])[email_count:]
        except IndexError:
            older_emails = []
        for email in older_emails:
            vcard.contents['email'].remove(email)

        try:
            older_tels = vcard.contents.get('tel', [])[tel_count:]
        except IndexError:
            older_tels = []
        for tel in older_tels:
            vcard.contents['tel'].remove(tel)

        return vcard

VCard()
