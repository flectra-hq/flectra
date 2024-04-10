# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright & licensing details.
 
##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': 'Accounting Financial Reports',
    'version': '3.0.1.3',
    'category': 'Invoicing Management',
    'description': 'Accounting Reports, Accounting Financial Reports, '
                   'Financial Reports',
    'summary': 'Accounting Reports',
    'sequence': '1',
    'author': 'FlectraHQ Inc, Odoo Mates, Odoo SA',
    'license': 'LGPL-3',
    'company': 'FlectraHQ Inc',
    'maintainer': 'FlectraHQ Inc',
    'website': 'https://www.flectrahq.com',
    'depends': ['account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_account_type.xml',
        'views/menu.xml',
        'views/ledger_menu.xml',
        'views/financial_report.xml',
        'views/settings.xml',
        'wizard/account_report_common_view.xml',
        'wizard/partner_ledger.xml',
        'wizard/general_ledger.xml',
        'wizard/trial_balance.xml',
        'wizard/balance_sheet.xml',
        'wizard/profit_and_loss.xml',
        'wizard/tax_report.xml',
        'wizard/aged_partner.xml',
        'wizard/journal_audit.xml',
        'report/report.xml',
        'report/report_partner_ledger.xml',
        'report/report_general_ledger.xml',
        'report/report_trial_balance.xml',
        'report/report_financial.xml',
        'report/report_tax.xml',
        'report/report_aged_partner.xml',
        'report/report_journal_audit.xml',
        'report/report_journal_entries.xml',
    ],
    'pre_init_hook': '_pre_init_clean_m2m_models',
}
