# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Recurring',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Create recurring of sale order',
    'description': """
    Sale Order Recurring allows to automatically create recurring of
    any particular sale order
    """,
    'author': 'FlectraHQ',
    'website': 'https://www.flectrahq.com/',
    'depends': ['sale_management', 'recurring'],
    'data': [
        'views/sale_views.xml',
    ],
    'demo': ['demo/sale_recurring_demo.xml'],
    'installable': True,
    'auto_install': False,
}
