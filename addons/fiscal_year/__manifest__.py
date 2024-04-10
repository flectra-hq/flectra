# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright & licensing details.
 
##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': 'Fiscal Year & Lock Date',
    'version': '3.0.1.3',
    'category': 'Accounting',
    'summary': 'Fiscal Year, Lock Date',
    'description': 'Fiscal Year',
    'sequence': '1',
    'website': 'https://www.flectrahq.com',
    'author': 'FlectraHQ Inc, Odoo Mates, Odoo SA',
    'maintainer': 'FlectraHQ Inc',
    'license': 'LGPL-3',
    'depends': ['account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',
        'wizard/change_lock_date.xml',
        'views/fiscal_year.xml',
        'views/settings.xml',
    ],
}
