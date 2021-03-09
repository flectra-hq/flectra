# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing
# details.

{
    'name': 'Recurring Documents',
    'category': 'Extra Tools',
    'author': 'FlectraHQ',
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
    'depends': ['account', 'purchase', 'sales_team', 'base', 'contacts', 'sale',
                'l10n_generic_coa'],
    'data': [
        'security/ir.model.access.csv',
        'views/recurring_view.xml',
    ],
    'demo': ['demo/recurring_demo.xml'],
    'license': 'LGPL-3',
}
