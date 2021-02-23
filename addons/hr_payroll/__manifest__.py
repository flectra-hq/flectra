# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payroll',
    'version': '2.0',
    'category': 'Human Resources/Contracts',
    'description': "",
    'website': 'https://flectrahq.com/expenses',
    'summary': 'Manage your employee payroll records',

    'depends': [
        'hr_contract',
        'hr_holidays',
        'hr_contract_types',
    ],
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payroll_report.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
    ],
    'demo': ['data/hr_payroll_category.xml',
             'data/hr_payroll_demo.xml',
             'data/hr_payroll_sequence.xml',
             # 'data/hr_payroll_data.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
