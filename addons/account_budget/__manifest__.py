# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright & licensing details.
 
##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': 'Budget Management',
    'author': 'FlectraHQ Inc, Odoo Mates, Odoo SA',
    'category': 'Accounting',
    'version': '3.0.1.0',
    'description': """Use budgets to compare actual with expected revenues and costs""",
    'summary': 'Budget Management',
    'sequence': 10,
    'website': 'https://www.flectrahq.com',
    'depends': ['account_accountant'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': ['data/account_budget_demo.xml'],
}
