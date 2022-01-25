# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounting',
    'version': '2.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Accounting Reports, Asset Management and Account Budget For Flectra Community Edition',
    'sequence': '1',
    'website': 'https://www.flectrahq.com',
    'author': 'FlectraHQ, Odoo Mates, Odoo SA',
    'company': 'FlectraHQ',
    'maintainer': 'FlectraHQ',
    'license': 'LGPL-3',
    'depends': ['web_flectra','accounting_pdf_reports', 'account_asset',
                'account_budget'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',
        'views/account.xml',
        'views/account_type.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'qweb': [],
}
