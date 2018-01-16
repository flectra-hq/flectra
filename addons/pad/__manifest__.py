# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Collaborative Pads',
    'author' : 'Odoo S.A',
    'version': '2.0',
    'category': 'Extra Tools',
    'description': """
Adds enhanced support for (Ether)Pad attachments in the web client.
===================================================================

Lets the company customize which Pad installation should be used to link to new
pads (by default, http://etherpad.com/).
    """,
    'website': 'https://flectrahq.com/page/notes',
    'depends': ['web', 'base_setup'],
    'data': [
        'views/pad.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': ['data/pad_demo.xml'],
    'web': True,
    'qweb': ['static/src/xml/pad.xml']
}
