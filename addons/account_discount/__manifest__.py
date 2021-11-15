# -*- coding: utf-8 -*-
{
    'name': "Invoice Document Discount",
    'summary': """
        Use Document Discounts on Invoices  
        """,
    'description': """
        Use Document Discounts on Invoices
    """,
    'author': "Jamotion GmbH, Flectra HQ",
    'website': "https://flectra-hq.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'account',
    ],
    'data': [
        # 'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'reports/invoice_report_views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
