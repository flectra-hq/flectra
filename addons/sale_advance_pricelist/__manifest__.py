# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Advance Pricelist',
    'version': '1.0.0',
    'category': 'Sale',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'sequence': 25,
    'summary': 'Add Price Rules, Cart Rules and Coupon Rules',
    'description': """
Pricelist
=========
Main Features
-------------
* Price Rules
* Cart Rules
* Coupon Rules
* View Calculation of all discount
""",
    'depends': ['sales_discount'],
    'data': [
            'security/ir.model.access.csv',
            'data/pricelist_view.xml',
            'views/pricelist_view.xml',
            'views/price_rule_view.xml',
            'views/sale_views.xml',
            'views/sale_pricelist.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
        'demo/price_rule_demo.xml',
        'demo/cart_rule_view_data.xml',
        'demo/coupon_code_demo.xml',
        'demo/sale_order_demo.xml',
    ],
    'qweb': [
        "static/src/xml/discount_details_view.xml",
    ],
    'auto_install': False
}
