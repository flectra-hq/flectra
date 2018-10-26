# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'VAT Number Autocomplete',
    'author': 'Odoo S.A',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
Auto-Complete Addresses based on VAT numbers
============================================

    This module requires the python library stdnum to work.
    """,
    'depends': ['base_vat'],
    'website': 'https://flectrahq.com/accounting',
    'data': [
        'views/res_partner_views.xml',
        'views/res_company_view.xml',
    ],
    'auto_install': True
}
