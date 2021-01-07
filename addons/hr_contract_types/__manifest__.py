# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Contracts Types',
    'version': '2.0',
    'category': 'Human Resources/Contracts',
    'sequence': 336,
    'summary': """
        Contract type in contracts
    """,
    'description': "",
    'website': 'https://flectrahq.com/expenses',
    'depends': ['hr', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'data/hr_contract_type_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}