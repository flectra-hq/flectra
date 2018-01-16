# -*- encoding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Decimal Precision Configuration',
    'author' : 'Odoo S.A',
    'description': """
Configure the price accuracy you need for different kinds of usage: accounting, sales, purchases.
=================================================================================================
""",
    'version': '0.1',
    'depends': ['base'],
    'category' : 'Hidden',
    'data': [
        'views/decimal_precision_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
}
