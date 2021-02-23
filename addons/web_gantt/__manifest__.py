{
    'name': 'Web Gantt Chart',
    'category': 'Project',
    'version': '2.0',
    'summary': 'Gantt Chart',
    'depends': [
        'web'
    ],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
