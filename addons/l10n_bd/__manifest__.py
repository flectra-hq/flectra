# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bangladesh - Accounting',
    'website': 'https://flectrahq.com/documentation/17.0/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['bd'],
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': ' This is the base module to manage chart of accounts and localization for the Bangladesh ',
    'depends': [
        'account',
    ],
    'data': [
        'data/account_tax_report_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}
