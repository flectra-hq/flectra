# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.


{
    'name': 'Flectra Enhancement for CRM',
    'version': '2.0.1.0',
    "category": "Hidden",
    "website": "https://flectrahq.com/",
    "author": "FlectraHQ",
    "license": "LGPL-3",
    'summary': 'Flectra Enhancement for CRM',
    'depends': ['crm'],
    'data': [
        'views/res_config_settings_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': True,
}
