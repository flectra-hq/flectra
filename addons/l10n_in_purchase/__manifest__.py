# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Indian - Purchase Report(GST)',
    'author' : 'Odoo S.A',
    'version': '1.0',
    'description': """GST Purchase Report""",
    'category': 'Localization',
    'depends': [
        'l10n_in',
        'purchase',
    ],
    'data': [
        'views/report_purchase_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
