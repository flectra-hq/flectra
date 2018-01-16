# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Gauge Widget for Kanban',
    'author': 'Odoo S.A.',
    'category': 'Hidden',
    'description': """
This widget allows to display gauges using d3 library.
""",
    'version': '1.0',
    'depends': ['web'],
    'data' : [
        'views/web_kanban_gauge_templates.xml',
    ],
    'qweb': [
    ],
    'auto_install': True,
}
