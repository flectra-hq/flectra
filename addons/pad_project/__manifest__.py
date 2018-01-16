# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pad on tasks',
    'author' : 'Odoo S.A',
    'category': 'Project',
    'description': """
This module adds a PAD in all project form views.
=================================================
    """,
    'website': 'https://flectrahq.com/page/project-management',
    'depends': [
        'project',
        'pad'
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/project_views.xml'
    ],
    'auto_install': True,
}
