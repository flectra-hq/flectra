# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'eCommerce Optional Products',
    'author': 'Odoo S.A.',
    'category': 'Website',
    'version': '1.0',
    'website': 'https://flectrahq.com/page/e-commerce',
    'description': """
Odoo E-Commerce
==================

        """,
    'depends': ['website_sale'],
    'data': [
        'views/product_views.xml',
        'views/website_sale_options_templates.xml',
    ],
    'demo': [
        'data/product_demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
