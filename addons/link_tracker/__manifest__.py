{
    'name': 'Link Tracker',
    'author' : 'Odoo S.A',
    'category': 'Marketing',
    'description': """
Create short and trackable URLs.
=====================================================

        """,
    'version': '1.0',
    'depends': ['utm'],
    'data': [
        'views/link_tracker.xml',
        'security/ir.model.access.csv',
    ],
}
