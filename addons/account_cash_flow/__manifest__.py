# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Cash Flow',
    'version': '1.1',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'summary': "cash flow statement",
    'description': """

The cash flow statement is intended to:

1 : provide information on a firm's liquidity and solvency and its ability to change cash flows in future circumstances

2 : provide additional information for evaluating changes in assets, liabilities and equity

3 : improve the comparability of different firms' operating performance by eliminating the effects of different accounting methods

4 : indicate the amount, timing and probability of future cash flows


 """,
    'category': 'Sales',
    'depends': ['account', 'account_invoicing'],
    'data': [
        'data/data_account_type.xml',
        'wizard/account_cash_flow.xml',
        'views/account_view.xml',
        'views/account_move_line.xml',
        'wizard/account_cash_flow.xml',
        'report/report_menu.xml',
        'report/report_account_cash_flow.xml',

    ],

    'demo': [

    ]

}
