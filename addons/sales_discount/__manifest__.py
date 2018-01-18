# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': "Sale Discount",
    'category': 'Sale',
    'description': """
        Customized module for amending discounts
    """,
    'summary': 'Global Discount on Sale Order',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'version': '1.0',
    'depends': ['sale_management', 'account_discount'],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_discount_data.xml',
        'views/sale_discount_config_view.xml',
        'views/res_config_settings_views.xml',
        'views/sale_view.xml',
        'report/sale_order_report_view.xml',
    ],
    'demo': [
        'demo/sale_order.xml',
    ],
    'installable': True,
    'auto_install': True,
}
