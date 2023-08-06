# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name' : 'Party - vCardDAV',
    'name_bg_BG': 'Фирма - vCardDAV',
    'name_de_DE': 'Parteien vCardDAV',
    'name_es_CO' : 'vCardDAV de Compañía',
    'name_es_ES' : 'Tercero - vCardDAV',
    'name_fr_FR': 'Tiers - vCardDAV',
    'version' : '2.2.2',
    'author' : 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': 'Add CardDAV on parties',
    'description_bg_BG': 'Добавя към партньор поддръжка на CardDAV',
    'description_de_DE': 'Ermöglicht CardDAV für Parteien',
    'description_es_CO': 'Soporte de CardDAV para terceros',
    'description_es_ES': 'Añade soporte de CardDAV para terceros',
    'description_fr_FR': 'Ajoute le support CardDAV pour les tiers',
    'depends' : [
        'ir',
        'res',
        'party',
        'webdav',
    ],
    'xml' : [
        'party.xml',
    ],
    'translation': [
        'locale/bg_BG.po',
        'locale/cs_CZ.po',
        'locale/de_DE.po',
        'locale/es_CO.po',
        'locale/es_ES.po',
        'locale/fr_FR.po',
        'locale/nl_NL.po',
        'locale/ru_RU.po',
    ],
}
