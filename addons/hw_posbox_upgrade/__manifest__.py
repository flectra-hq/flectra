# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'PosBox Software Upgrader',
    'author' : 'Odoo S.A',
    'category': 'Point of Sale',
    'website': 'https://flectrahq.com/page/point-of-sale',
    'sequence': 6,
    'summary': 'Allows to remotely upgrade the PosBox software',
    'description': """
PosBox Software Upgrader
========================

This module allows to remotely upgrade the PosBox software to a
new version. This module is specific to the PosBox setup and environment
and should not be installed on regular Odoo servers.

""",
    'depends': ['hw_proxy'],
    'installable':  False,
}
