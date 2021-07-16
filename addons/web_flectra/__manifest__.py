# -*- coding: utf-8 -*-
# Copyright 2016, 2020 Openworx - Mario Gielissen
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Flectra Core Backend',
    'version': '2.0.1.0',
    "category": "Hidden",
    "website": "https://flectrahq.com/",
    "author": "FlectraHQ,Openworx",
    "license": "LGPL-3",
    'summary': 'Backend Theme For Flectra',
    'depends': ['base_setup', 'iap'],
    'data': [
        'security/ir.model.access.csv',
        'data/theme_config.xml',
        'data/ir_config_param_data.xml',
        'data/pwa_config_data.xml',
        'views/assets.xml',
        'views/res_partner_view.xml',
        'views/pwa_config_view.xml',
        'views/ir_module_view_inherit.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_view.xml',
        'views/sidebar.xml',
        'views/web.xml',
        'views/home.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'auto_install': True,
    "uninstall_hook": "_uninstall_reset_changes",
}
