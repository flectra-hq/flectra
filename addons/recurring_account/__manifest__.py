# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Invoice Recurrings',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Create recurring of invoices',
    'description': """
    Account Invoice Recurring allows to automatically create
    recurring of any particular invoice
    """,
    'author': 'FlectraHQ',
    'website': 'https://www.flectrahq.com/',
    'depends': ['account', 'recurring'],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
