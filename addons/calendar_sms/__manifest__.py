# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': "Calendar SMS",
    'author' : 'Odoo S.A',
    'summary': 'Send text messages as event reminders',
    'description': "Send text messages as event reminders",
    'category': 'Hidden',
    'version': '1.0',
    'depends': ['calendar', 'sms'],
    'data': [
        'views/calendar_views.xml',
    ],
    'application': False,
    'auto_install': True,
}
