# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM Livechat',
    'author' : 'Odoo S.A',
    'category': 'crm',
    'summary': 'Create lead from livechat conversation',
    'depends': [
        'crm',
        'im_livechat'
    ],
    'description': 'Create new lead with using /lead command in the channel',
    'auto_install': True
}
