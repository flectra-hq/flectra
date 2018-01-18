# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': "Account Discount",
    'description': """
        Customized module for amending discounts
    """,
    'summary': 'Global Discount on Account Invoice',
    'author': 'FlectraHQ',
    'category': 'Accounting',
    'website': 'https://flectrahq.com',
    'version': '1.0',
    'depends': ['account_invoicing'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_discount_data.xml',
        'views/account_invoice_views.xml',
        'views/discount_config_view.xml',
        'views/res_config_settings_views.xml',
        'report/report_menu.xml',
        'report/custom_invoice_report.xml',
    ],
    'demo': [
        'demo/discount_config_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
}
