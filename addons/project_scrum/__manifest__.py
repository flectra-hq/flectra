# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Scrum',
    'version': '1.0',
    'category': 'Project',
    'author': 'Flectra',
    'website': 'https://flectrahq.com',
    'sequence': 40,
    'summary': 'A module for Scrum implementation',
    'depends': [
        'project', 'resource'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/scrum_security.xml',
        'views/other_views.xml',
        'views/project_sprint_views.xml',
        'views/project_story_views.xml',
        'views/project_team_views.xml',
        'views/release_planning_views.xml',
        'views/cron_view.xml',
        'views/assets.xml',
        'views/retrospective_method_views.xml',
        'views/retrospective_views.xml',
        'reports/project_scrum_report.xml',
        'reports/release_planning_template.xml',
        'reports/project_sprint_template.xml',
        'data/sprint_sequence.xml',
        'data/project_sprint_data.xml',
    ],
    'demo': [
        'demo/project_team_demo.xml',
        'demo/project_sprint_demo.xml',
        'demo/project_story_demo.xml',
        'demo/project_release_planning_demo.xml',
        'demo/retrospective_demo.xml',
        'demo/project_task_demo.xml',
    ],
    'qweb': [
        'static/src/xml/scrum_dashboard.xml',
    ],
    'installable': True,
    'application': True,
}
