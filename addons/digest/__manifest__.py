# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'KPI Digests',
    'category': 'Marketing',
    'description': """
Send KPI Digests periodically
=============================
""",
    'version': '1.0',
    'author': 'Odoo SA, FlectraHQ',
    'summary': 'Get KPIs sent by email periodically according to your preferences',
    'depends': [
        'mail',
        'portal',
        'resource',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/digest_template_data.xml',
        'data/digest_data.xml',
        'data/ir_cron_data.xml',
        'data/res_config_settings_data.xml',
        'views/digest_templates.xml',
        'views/digest_views.xml',
        'wizard/digest_custom_fields_view.xml',
        'wizard/digest_custom_remove_view.xml',
        'views/digest_views_inherit.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
