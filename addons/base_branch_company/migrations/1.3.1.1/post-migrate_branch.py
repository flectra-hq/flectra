# -*- coding: utf-8 -*-
import flectra

def migrate(cr, version):
    registry = flectra.registry(cr.dbname)
    from flectra.addons.base_branch_company.models.res_branch import \
        migrate_company_branch
    migrate_company_branch(cr, registry)