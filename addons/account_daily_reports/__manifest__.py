# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright & licensing details.
 
##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': 'Cash Book, Day Book, Bank Book Financial Reports',
    'version': '3.0.1.1',
    'category': 'Invoicing Management',
    'summary': 'Cash Book, Day Book and Bank Book Report',
    'description': 'Cash Book, Day Book and Bank Book Report',
    'sequence': '10',
    'author': 'FlectraHQ Inc, Odoo Mates',
    'license': 'LGPL-3',
    'company': 'FlectraHQ Inc',
    'maintainer': 'FlectraHQ Inc',
    'website': 'https://www.flectrahq.com',
    'depends': ['accounting_pdf_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/om_daily_reports.xml',
        'wizard/daybook.xml',
        'wizard/cashbook.xml',
        'wizard/bankbook.xml',
        'report/reports.xml',
        'report/report_daybook.xml',
        'report/report_cashbook.xml',
        'report/report_bankbook.xml',
    ],
}
