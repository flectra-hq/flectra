# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Channels',
    'author': 'Odoo S.A.',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Sales Channels',
    'description': """
Using this application you can manage Sales Channels  with CRM and/or Sales
===========================================================================
 """,
    'website': 'https://flectrahq.com/page/crm',
    'depends': ['base', 'mail', 'base_branch_company'],
    'data': ['security/sales_team_security.xml',
             'security/ir.model.access.csv',
             'data/sales_team_data.xml',
             'views/crm_team_views.xml',
             'views/sales_team_dashboard.xml',
             ],
    'demo': ['data/sales_team_demo.xml'],
    'installable': True,
    'auto_install': False,
}
