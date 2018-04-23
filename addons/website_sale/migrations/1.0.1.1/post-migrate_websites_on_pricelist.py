# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DO $do$ BEGIN IF EXISTS (SELECT relname FROM pg_class WHERE relname = 'website_product_pricelist') THEN INSERT INTO website_pricelist_rule_rel (website_id,pricelist_id) SELECT website_id,pricelist_id FROM website_product_pricelist; END IF; END $do$")
    cr.execute("drop table if exists website_product_pricelist")
