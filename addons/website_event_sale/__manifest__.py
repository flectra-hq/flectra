# -*- coding: utf-8 -*-

{
    'name': "Online Event's Tickets",
    'author': 'Odoo S.A.',
    'category': 'Marketing',
    'summary': "Manage Events and Sell Tickets Online",
    'website': 'https://flectrahq.com/page/events',
    'description': """
Online Event's Tickets
======================

        """,
    'depends': ['website_event', 'event_sale', 'website_sale'],
    'data': [
        'data/event_data.xml',
        'views/event_templates.xml',
        'security/ir.model.access.csv',
        'security/website_event_sale_security.xml',
    ],
    'auto_install': True
}
