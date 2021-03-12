# Part of flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Project Extension',
    'version': '1.0',
    'summary': '''Helpdesk with project and task feature for generating
issues.''',
    'category': 'Human Resources',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['helpdesk_basic', 'project'],
    'data': [
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_team_view.xml',
        'views/project_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
