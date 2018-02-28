# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web',
    'author': 'Odoo S.A.',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
Odoo Web core module.
========================

This module provides the core of the Odoo Web Client.
        """,
    'depends': ['base'],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/webclient_templates.xml',
        'views/report_templates.xml',
    ],
    'qweb': [
        "static/src/xml/base.xml",
        "static/src/xml/kanban.xml",
        "static/src/xml/rainbow_man.xml",
        "static/src/xml/report.xml",
        "static/src/xml/web_calendar.xml",
        "static/src/xml/backend_theme.xml",
        "static/src/xml/backend_theme_customizer.xml",
    ],
    'bootstrap': True,  # load translations for login screen
}
