# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.


{
    'name': 'Purchase and MRP Management',
    'author': 'Odoo S.A.',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module provides facility to the user to install mrp and purchase modules at a time.
========================================================================================

It is basically used when we want to keep track of production orders generated
from purchase order.
    """,
    'website': 'https://flectrahq.com/manufacturing',
    'depends': ['mrp', 'purchase'],
    'data': [],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
