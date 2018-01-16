# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Attachments List and Document Indexation',
    'author' : 'Odoo S.A',
    'version': '2.1',
    'category': 'Document Management',
    'description': """
Attachments list and document indexation
========================================
* Show attachment on the top of the forms
* Document Indexation: odt
""",
    'depends': ['web'],
    'data': [
        'views/document_templates.xml',
    ],
    'installable': True,
}
