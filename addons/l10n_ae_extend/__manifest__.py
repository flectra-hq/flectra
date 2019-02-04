# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'U.A.E. - Accounting Extend',
    'author': 'FlectraHQ',
    'website': 'https://www.flectrahq.com/',
    'category': 'Localization',
    'description': """
United Arab Emirates accounting chart and localization.
=======================================================

    """,
    'depends': ['l10n_ae', 'account_invoicing',
                'sale_management', 'purchase', 'base_vat'],
    'data': [
             'security/ir.model.access.csv',
             'data/res_company_data.xml',
             'data/res_country_data.xml',
             'data/journal_data.xml',
             'data/vat_config_type_data.xml',
             'data/fiscal_position_data.xml',
             'views/report_vat_201_view.xml',
             'views/report_menu_view.xml',
             'views/vat_config_type.xml',
             'views/res_config_view.xml',
             'views/purchase_order_view.xml',
             'views/sale_order_view.xml',
             'views/account_invoice_view.xml',
             'wizard/vat_201_view.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
        'demo/account_invoice_demo.xml',
    ],
}
