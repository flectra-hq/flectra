# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dashboards',
    'author' : 'Odoo S.A',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Create your custom dashboard',
    'description': """
Lets the user create a custom dashboard.
========================================

Allows users to create custom dashboard.
    """,
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/board_views.xml',
        'views/board_templates.xml',
    ],
    'qweb': ['static/src/xml/board.xml'],
    'application': True,
}
