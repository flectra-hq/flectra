# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'ESC/POS Hardware Driver',
    'author' : 'Odoo S.A',
    'category': 'Point of Sale',
    'sequence': 6,
    'website': 'https://flectrahq.com/page/point-of-sale',
    'summary': 'Hardware Driver for ESC/POS Printers and Cashdrawers',
    'description': """
ESC/POS Hardware Driver
=======================

This module allows Odoo to print with ESC/POS compatible printers and
to open ESC/POS controlled cashdrawers in the point of sale and other modules
that would need such functionality.

""",
    'depends': ['hw_proxy'],
    'external_dependencies': {
        'python' : ['usb.core','serial','qrcode'],
    },
}
