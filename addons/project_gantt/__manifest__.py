{
    'name': 'Project Gantt Chart Demo',
    'category': 'Project',
    'version': '2.0',
    'summary': 'Project Gantt Chart Demo',
    'depends': [
        'web_gantt',
        'project'
    ],
    'data': [
        'views/project_task_inherit.xml',
    ],
    'demo': ['data/project_task_demo.xml'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
