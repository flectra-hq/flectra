# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.


{
    'name': 'Contacts Directory',
    'author' : 'Odoo S.A',
    'category': 'Tools',
    'summary': 'Customers, Vendors, Partners,...',
    'description': """
This module gives you a quick view of your contacts directory, accessible from your home page.
You can track your vendors, customers and other contacts.
""",
    'depends': ['base'],
    'data': [
        'views/contact_views.xml',
    ],
    'application': True,
}
