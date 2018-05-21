# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Sale Advance Pricelist',
    'version': '1.0.0',
    'category': 'Sale',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'sequence': 25,
    'summary': 'Add Price Rules, Cart Rules and Coupon Rules',
    'depends': ['sale_advance_pricelist', 'website_sale'],
    'data': [
            'views/sale_order_view.xml',
            'views/asset.xml',
            'data/pricelist_view.xml',
    ],
    'demo': [
        'demo/sale_order_demo.xml',
    ],
    'qweb': [
    ],
    'auto_install': False
}
