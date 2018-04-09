# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Return Merchandise Authorizationing',
    'version': '1.0',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'description': """
        Return Merchandise Authorizationing is part of the process of a
        consumer returning a product to receive a refund or replacement
        during the product's warranty period.
    """,
    'category': 'Sales',
    'depends': ['rma', 'website_sale', 'portal'],
    'data': [
        'wizard/stock_return_web_view.xml',
        'views/rma_request_view.xml',
        'views/return_portal_template.xml',
        'views/templates.xml',

    ],
    'demo': [
        'demo/sale_order_demo.xml'
    ],
    'images': [
        'static/description/website-rma-app-banner.jpg',
    ],
}
