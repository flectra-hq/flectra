# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Contact Form Number Validation',
    'author': 'Odoo S.A.',
    'summary': 'Validate and format contact form numbers',
    'sequence': '9999',
    'category': 'Hidden',
    'description': """
Contact Number Validation on Website
====================================

Validate contact (phone,mobile) numbers and normalize them on leads and contacts:
- use the national format for your company country
- use the international format for all others
        """,
    'data': [],
    'depends': [
        'crm_phone_validation',
        'website_crm',
        'website_form',
    ],
    'auto_install': True,
}
