# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Directory',
    'author' : 'Odoo S.A',
    'version': '1.1',
    'category': 'Human Resources',
    'sequence': 75,
    'summary': 'Jobs, Departments, Employees Details',
    'description': "",
    'website': 'https://flectrahq.com/page/employees',
    'images': [
        'images/hr_department.jpeg',
        'images/hr_employee.jpeg',
        'images/hr_job_position.jpeg',
        'static/src/img/default_image.png',
    ],
    'depends': [
        'base_setup',
        'mail',
        'resource',
        'web',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/hr_templates.xml',
        'views/res_config_settings_views.xml',
        'data/hr_data.xml',
    ],
    'demo': [
        'data/hr_demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
