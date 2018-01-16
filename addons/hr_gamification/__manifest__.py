# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Gamification',
    'author' : 'Odoo S.A',
    'version': '1.0',
    'category': 'Human Resources',
    'website': 'https://flectrahq.com/page/employees',
    'depends': ['gamification', 'hr'],
    'description': """Use the HR resources for the gamification process.

The HR officer can now manage challenges and badges.
This allow the user to send badges to employees instead of simple users.
Badge received are displayed on the user profile.
""",
    'data': [
        'security/gamification_security.xml',
        'security/ir.model.access.csv',
        'wizard/gamification_badge_user_wizard_views.xml',
        'views/gamification_views.xml',
        'views/hr_employee_views.xml',
        'views/gamification_templates.xml',
    ],
    'auto_install': True,
}
