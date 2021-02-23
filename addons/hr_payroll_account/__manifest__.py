# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll Accounting',
    'version': '2.0',
    'category': 'Human Resources/Contracts',
    'summary': """
          Generic Payroll system Integrated with Accounting,Expense Encoding,Payment Encoding,Company Contribution Management
    """,
    'description': "",
    'website': 'https://flectrahq.com/expenses',
    'depends': ['hr_payroll', 'account'],
    'data': ['views/hr_payroll_account_views.xml'],
    'test': ['../account/test/account_minimal_test.xml'],

    'installable': True,
    'application': True,
    'auto_install': False,
}
