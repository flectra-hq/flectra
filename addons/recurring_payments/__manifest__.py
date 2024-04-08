# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright & licensing details.
 
##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': 'Recurring Payment',
    'author': 'FlectraHQ Inc, Odoo Mates',
    'category': 'Accounting',
    'version': '3.0.1.3',
    'description': """Recurring Payment,Accounting""",
    'summary': 'Use recurring payments to handle periodically repeated payments',
    'sequence': 11,
    'website': 'https://www.flectrahq.com',
    'depends': ['account_accountant'],
    'license': 'LGPL-3',
    'data': [
        'data/sequence.xml',
        'data/recurring_cron.xml',
        'security/ir.model.access.csv',
        'views/recurring_template_view.xml',
        'views/recurring_payment_view.xml'
    ],
}
