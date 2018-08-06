# Part of Flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Forum',
    'version': '1.0',
    'description': '''Helpdesk Forum will provide you forum per
helpdesk team''',
    'summary': '''Helpdesk Forum will provide you forum per
helpdesk team''',
    'category': 'Human Resources',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['helpdesk_basic', 'website_forum'],
    'data': [
        'views/helpdesk_team_view.xml',
        'views/helpdesk_ticket_view.xml',
    ],
    'demo': [
        'demo/helpdesk_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
