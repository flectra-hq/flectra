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
    'depends': ['base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pwa_config_view.xml',
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
