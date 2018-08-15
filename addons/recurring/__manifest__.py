# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing
# details.

{
    'name': 'Recurring Documents',
    'category': 'Extra Tools',
    'description': """
Create recurring documents.
===========================

This module allows to create new documents and add recurring on that
document.

e.g. To have an invoice generated automatically periodically:
-------------------------------------------------------------
    * Define a document type based on Invoice object
    * Define a recurring whose source document is the document defined as
      above. Specify the interval information and partner to be invoiced.
      Module taken from odoov10 subscription.
    """,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/recurring_view.xml',
    ],
    'demo': ['demo/recurring_demo.xml'],
}
