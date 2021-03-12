# Part of flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Helpdesk',
    'version': '1.0',
    'summary': '''Website Helpdesk''',
    'category': 'Human Resources',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['helpdesk_basic', 'website', 'portal', 'rating'],
    'data': [
        'security/ir.model.access.csv',
        'views/pages/helpdesk_register_website_view.xml',
        'views/pages/helpdesk_website_view.xml',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
