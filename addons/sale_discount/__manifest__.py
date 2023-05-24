# -*- coding: utf-8 -*-
{
    'name': "Sale Document Discount",
    'summary': """
        Use Document Discounts in Sale  
        """,
    'description': """
        Use Document Discounts in Sale
    """,
    'author': "Jamotion GmbH",
    'website': "https://jamotion.ch",
    'category': 'Sales',
    'version': '0.1',
    'depends': [
        'sale_management', 'sale'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/res_config_settings_views.xml',
        # 'views/product_views.xml',
        'views/sale_views.xml',
        'reports/sale_report_templates.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
