# Part of flectra See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk',
    'version': '1.0',
    'summary': '''A help desk is a department inside an organization that is
    responsible for answering the technical questions of its users.
''',
    'category': 'Human Resources',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'depends': ['base_setup', 'mail', 'utm', 'rating', 'web_tour', 'resource',
                'portal', 'digest', 'portal_rating'],
    'data': [
        'security/helpdesk_security_view.xml',
        'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'data/ticket_mail_template.xml',
        'data/ticket_rating_cron.xml',
        'views/view.xml',
        'views/assets.xml',
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_team_view.xml',
        'views/issue_type_view.xml',
        'views/helpdesk_tag_view.xml',
        'views/helpdesk_stage_view.xml',
        'views/res_config_setting_view.xml',
        'views/raring_template_view.xml',
        'report/helpdesk_report_view.xml',
    ],
    'demo': [
        'demo/helpdesk_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
