# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'United States - Accounting',
    'author' : 'Odoo S.A',
    'version': '1.1',
    'category': 'Localization',
    'description': """
United States - Chart of accounts.
==================================
    """,
    'depends': ['l10n_generic_coa'],
    'data': [
        'data/res_company_data.xml',
        'views/res_partner_bank_views.xml'
    ],
}
