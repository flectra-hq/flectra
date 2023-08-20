# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.


{
    'name': 'Flectra Core Frontend',
    'version': '2.0.1.0',
    "category": "Hidden",
    "website": "https://flectrahq.com/",
    "author": "FlectraHQ",
    "license": "LGPL-3",
    'summary': 'Frontend For Flectra',
    'depends': ['website'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': True,
}
