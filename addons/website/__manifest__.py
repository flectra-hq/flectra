# -*- encoding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Builder',
    'author': 'Odoo S.A.',
    'category': 'Website',
    'sequence': 50,
    'summary': 'Build Your Enterprise Website',
    'website': 'https://flectrahq.com/page/website-builder',
    'version': '1.0',
    'description': "",
    'depends': ['web', 'web_editor', 'web_planner',
                'http_routing', 'portal', 'base_automation'],
    'installable': True,
    'data': [
        'data/website_data.xml',
        'security/website_security.xml',
        'security/ir.model.access.csv',
        'views/website_templates.xml',
        'views/website_navbar_templates.xml',
        'views/snippets.xml',
        'views/website_views.xml',
        'views/res_config_settings_views.xml',
        'views/ir_actions_views.xml',
        'views/res_company_views.xml',
        'views/module_view.xml',
        'wizard/base_language_install_views.xml',
        'data/web_planner_data.xml',
    ],
    'demo': [
        'data/website_demo.xml',
    ],
    'qweb': ['static/src/xml/website.backend.xml'],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
}
