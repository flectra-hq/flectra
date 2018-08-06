# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Helpdesk',
    'version': '1.0',
    'description': '''Website Helpdesk''',
    'summary': '''Website Helpdesk''',
    'category': 'Human Resources',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['helpdesk_basic', 'website', 'portal', 'website_rating'],
    'data': [
        'views/pages/helpdesk_register_website_view.xml',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
