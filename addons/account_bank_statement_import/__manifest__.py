# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bank Reconciliation',
    'version': '1.1',
    'summary': 'Bank Reconciliation',
    'sequence': 15,
    'description': """Bank Reconciliation""",
    'category': '',
    'website': '',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'account_bank_statement_import_view.xml',
        'account_import_tip_data.xml',
        'wizard/journal_creation.xml',
        'views/account_bank_statement_import_templates.xml',
        'views/account_journal_dashboard_inherit.xml',
        'views/account_journal_inherit.xml',
        'views/account_payment_inherit.xml',
        'views/account_bank_statement_view_inherit.xml',
        'views/assets.xml'
    ],
    'demo': [
        'demo/partner_bank.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
