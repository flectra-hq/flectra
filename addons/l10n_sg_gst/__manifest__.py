# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

{
    'name': 'Singapore - GST Report',
    'version': '1.0',
    'category': 'Localization',
    'summary': 'Goods and Service Tax (Singapore)',
    'description': '''
GST Reports for Singapore Localization
========================================

There are Different type of GST Reports available for Singapore Localization.
    * GST5 Report
    * GST7 Report
    * GST Analysis Report
    ''',
    "author": "FlectraHQ",
    'website': 'https://flectrahq.com',
    'depends': ['account_invoicing', 'l10n_sg'],
    'data': [
        'views/res_company_view.xml',
        'report/report_paperformat.xml',
        'wizard/gst5_select_period_view.xml',
        'wizard/gst7_select_period_view.xml',
        'wizard/gst_analysis_view.xml',
        'report/report_gst_menu.xml',
        'views/layouts_gst.xml',
        'views/account_gst_analysis_view.xml',
        'views/account_gst5_report_view.xml',
        'views/account_gst7_report_view.xml',
    ],
    'demo': [
        'demo/demo_account.xml',
        'demo/demo_product.xml'
    ],
    'installable': True,
    'auto_install': False
}
