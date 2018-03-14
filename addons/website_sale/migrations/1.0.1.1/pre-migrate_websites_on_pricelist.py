# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("delete from ir_ui_view where name='website_sale.pricelist.form'")
