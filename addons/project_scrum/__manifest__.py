# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Scrum',
    'version': '2.0',
    'category': 'Project',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'sequence': 40,
    'summary': 'A module for Scrum implementation',
    'depends': [
        'project', 'resource'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/other_views.xml',
        'views/project_sprint_views.xml',
        'views/project_story_views.xml',
        'views/project_team_views.xml',
        'views/release_planning_views.xml',
        'views/cron_view.xml',
        'views/retrospective_method_views.xml',
        'views/retrospective_views.xml',
        'report/project_scrum_report.xml',
        'report/release_planning_template.xml',
        'report/project_sprint_template.xml',
        'data/sprint_sequence.xml',
        'data/project_sprint_data.xml',
        'data/project_task_sequence.xml',
    ],
    'demo': [
        'demo/project_scrum_demo.xml',
        'demo/project_story_demo.xml',
        'demo/project_release_planning_demo.xml',
        'demo/retrospective_demo.xml',
        'demo/project_task_demo.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False
}
