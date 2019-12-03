# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'Margins in Sales Orders',
    'author': 'Odoo S.A.',
    'version':'1.0',
    'category': 'Sales',
    'description': """
This module adds the 'Margin' on sales order.
=============================================

This gives the profitability by calculating the difference between the Unit
Price and Cost Price.
    """,
    'depends':['sale_management'],
    'demo':['data/sale_margin_demo.xml'],
    'data':['security/sale_security.xml','security/ir.model.access.csv','views/sale_margin_view.xml'],
}
