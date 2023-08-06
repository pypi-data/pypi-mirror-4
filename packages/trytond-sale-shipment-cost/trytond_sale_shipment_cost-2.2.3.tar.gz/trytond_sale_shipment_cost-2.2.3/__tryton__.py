# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name' : 'Sale Shipment Cost',
    'name_de_DE': 'Verkauf Lieferposten Kosten',
    'name_es_ES': 'Costo del método de envio',
    'name_fr_FR': "Coût d'expédition de vente",
    'version': '2.2.3',
    'author' : 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': 'Add sale shipment cost',
    'description_de_DE': '''
    - Fügt den Verkäufen die Verwaltung von Kosten für Lieferposten hinzu.
    ''',
    'description_fr_FR': "Ajoute le coût d'expédition sur les ventes",
    'description_es_ES': "Agrega un costo al método de envio.",
     'depends' : [
        'ir',
        'res',
        'carrier',
        'sale',
        'currency',
        'account_invoice',
        'stock',
    ],
    'xml' : [
        'sale.xml',
        'stock.xml',
    ],
    'translation': [
        'locale/bg_BG.po',
        'locale/cs_CZ.po',
        'locale/de_DE.po',
        'locale/es_ES.po',
        'locale/es_CO.po',
        'locale/fr_FR.po',
        'locale/nl_NL.po',
        'locale/ru_RU.po',
    ],
}
