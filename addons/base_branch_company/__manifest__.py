# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Branch & Company Mixin',
    'version': '1.1',
    'category': 'Discuss',
    'author': 'FlectraHQ',
    'sequence': 25,
    'summary': 'Include Branch & Company support',
    'description': """
Branch & Company
================

Main Features
-------------
* Include Branch & Company in all objects
* Just need to inherit ir.branch.company.mixin in your object
* And in your xml file add below 2 lines in your Views
    <field name="branch_id" />
    <field name="company_id" />
""",
    'website': '',
    'depends': ['base', 'base_setup'],
    'data': [
            'demo/branch_data.xml',
            'wizard/branch_config_view.xml',
            'security/branch_security.xml',
            'security/ir.model.access.csv',
            'views/res_branch_view.xml',
            'views/res_branch_config_view.xml',
    ],
    'demo': [
        'demo/branch_demo.xml',
    ],
    'installable': True,
    'auto_install': True
}
