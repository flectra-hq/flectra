# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Belgium - Payroll with Accounting',
    'author' : 'Odoo S.A',
    'category': 'Localization',
    'depends': ['l10n_be_hr_payroll', 'hr_payroll_account', 'l10n_be'],
    'description': """
Accounting Data for Belgian Payroll Rules.
==========================================
    """,

    'auto_install': True,
    'website': 'https://flectrahq.com/page/accounting',
    'data':[
        'data/l10n_be_hr_payroll_account_data.xml',
    ],
    'post_init_hook': '_set_accounts',
}
