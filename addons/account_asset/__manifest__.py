# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Assets Management',
    'author': 'Odoo S.A',
    'depends': ['account_invoicing'],
    'description': """
Assets management
=================
Manage assets owned by a company or a person.
Keeps track of depreciations, and creates corresponding journal entries.

    """,
    'website': 'https://flectrahq.com/accounting',
    'category': 'Accounting',
    'sequence': 32,
    'demo': [
        'data/account_asset_demo.yml',
    ],
    'data': [
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'data/account_asset_data.xml',
        'wizard/asset_modify_views.xml',
        'wizard/sale_asset_wizard_view.xml',
        'wizard/asset_depreciation_summary_wizard_view.xml',
        'views/account_asset_views.xml',
        'views/account_invoice_views.xml',
        'views/account_asset_templates.xml',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
        'report/report_paperformat.xml',
        'report/asset_reports.xml',
        'report/asset_depreciation_report_template.xml',
        'report/account_asset_report_views.xml'
    ],
    'qweb': [
        "static/src/xml/account_asset_template.xml",
    ],
}
