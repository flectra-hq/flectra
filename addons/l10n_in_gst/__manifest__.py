# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'GST Reporting For Indian Localization',
    'version': '1.0',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'category': 'Accounting',
    'summary': 'Goods and Services Tax (India)',
    'description': '''
    GST module for Flectra enables Indian Organization to use Flectra
     Accounting in accordance to GST taxation structure. Providing
     necessary reporting data for GSTR-1 & GSTR-2 filling, Tax Credit etc.
    ''',
    'depends': ['account_invoicing', 'l10n_in'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_uom_data.xml',
        'data/note_issue_reason_data.xml',
        'data/res_company_data.xml',
        'wizard/account_invoice_refund_view.xml',
        'views/product_uom_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
        'views/res_config_settings_views.xml',
        'views/gst_report_view.xml',
        'views/assets.xml',
        'views/note_issue_reason_view.xml',
        'views/menuitems_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'demo': [
        'demo/res_company_demo.xml',
        'demo/res_partner_demo.xml',
        'demo/product_demo.xml',
        'demo/account_account_demo.xml',
        'demo/account_invoice_demo.xml',
    ],
    'installable': True,
    'auto_install': False
}
