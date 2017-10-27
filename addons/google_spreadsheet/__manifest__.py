# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Google Spreadsheet',
    'author' : 'Odoo S.A',
    'version': '1.0',
    'category': 'Extra Tools',
    'description': """
The module adds the possibility to display data from Flectra in Google Spreadsheets in real time.
=================================================================================================
""",
    'depends': ['google_drive'],
    'data': [
        'data/google_spreadsheet_data.xml',
        'views/google_spreadsheet_views.xml',
        'views/google_spreadsheet_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
