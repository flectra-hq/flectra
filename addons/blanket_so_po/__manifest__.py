# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Blanket Sale Order/Purchase Order',
    'version': "1.0",
    'category': 'Sales and Purchase Management',
    'summary': 'A Blanket Sales/Purchase Order clearly lays out the terms '
               'and conditions of a Sales/Purchase including quantities '
               'required and when they are to be delivered.',
    "author": "Flectra",
    'website': 'https://flectrahq.com',
    'depends': ['purchase', 'sale_stock'],
    'data': [
        'wizard/transfer_so_products_view.xml',
        'wizard/transfer_po_products_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    'demo': [
        'demo/blanket_sale_demo.xml',
        'demo/blanket_purchase_demo.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
