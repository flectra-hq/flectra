# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'SMS gateway',
    'author': 'Odoo S.A.',
    'category': 'Tools',
    'summary': 'SMS Text Messaging',
    'description': """
This module gives a framework for SMS text messaging
----------------------------------------------------

The service is provided by the In App Purchase Flectra platform.
""",
    'depends': ['base', 'iap', 'mail'],
    'data': [
        'wizard/send_sms_views.xml',
        'views/res_partner_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/sms_widget.xml',
    ],
    'installable': True,
    'auto_install': True,
}
