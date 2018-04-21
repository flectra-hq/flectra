# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("insert into website_pricelist_rule_rel (website_id,pricelist_id) select website_id,pricelist_id from website_product_pricelist")
    cr.execute("drop table if exists website_product_pricelist")
