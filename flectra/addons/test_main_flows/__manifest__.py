# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Test Main Flow',
    'author': 'Odoo S.A',
    'version': '1.0',
    'category': 'Tools',
    'description': """
This module will test the main workflow of Odoo, Flectra.
It will install some main apps and will try to execute the most important actions.
""",
    'depends': ['crm', 'sale_timesheet', 'purchase', 'mrp', 'account'],
    'data': [
        'views/templates.xml',
    ], 
    'installable': True,
}
