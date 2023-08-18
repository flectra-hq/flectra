# coding: utf-8
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Billing Options',
    'summary': 'Manage Timesheets and Calculate Profitability '
               'based on Invoicing Factor',
    'author': 'FlectraHQ',
    'depends': ['project', 'hr_timesheet', 'sale_timesheet', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_inherit.xml',
        'views/hr_timesheet_invoice_factor_view.xml',
        'menu/menu.xml'
    ],
    'demo': [
        'demo/demodata_invoicable_factor.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
