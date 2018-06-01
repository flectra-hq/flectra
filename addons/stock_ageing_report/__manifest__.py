# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Ageing Report',
    'version': '1.0',
    'category': 'Stock',
    'author': 'FlectraHQ',
    'website': "https://flectrahq.com",
    'depends': ['stock'],
    'sequence': 40,
    'summary': """Stock Ageing Report to display
    product's stock by ageing period.""",
    'description': """
Main Features
-------------
Stock Ageing Reports.
An Ageing Analysis Report in Flectra displays the age of the stock in hand.
This report lists the age-wise break-up of Inventory to point out old stock.
Flectra gives its users the flexibility to define their own ageing slabs.
""",
    'data': [
        'wizard/stock_ageing_wizard_view.xml',
        'report/stock_ageing_report_view.xml',
        'report/stock_ageing_report_template.xml',
    ],
    'demo': [],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': False,
}
