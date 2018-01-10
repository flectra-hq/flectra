{
    'name': 'Website Theme Install',
    'author': 'Odoo S.A.',
    'description': "Propose to install a theme on website installation",
    'category': 'Website',
    'version': '1.0',
    'data': [
        'views/assets.xml',
        'views/views.xml',
    ],
    'depends': ['website'],
    'auto_install': False,
    'installable': False
}
