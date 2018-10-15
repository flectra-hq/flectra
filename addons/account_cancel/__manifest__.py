# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cancel Journal Entries',
    'author': 'Odoo S.A',
    'version': '1.1',
    'category': 'Accounting',
    'description': """
Allows canceling accounting entries.
====================================

This module adds a checkbox on the accounting journals to allow the cancellation of journal entries.

This checkbox is only visible on the accounting journals when the debug mode is active.

If this checkbox is set to TRUE, it allows users to cancel journal entries.

The accounting entry that is cancelled can then be modified and reposted or deleted.

It also operates on invoices, bank statements, payments ...

Be careful with this module as it has audit implications. Cancelling accounting entries is not authorized in all countries.
""",
    'website': 'https://flectrahq.com/accounting',
    'depends': ['account'],
    'data': ['views/account_views.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
