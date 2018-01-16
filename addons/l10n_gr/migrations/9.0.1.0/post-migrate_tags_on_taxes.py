# -*- coding: utf-8 -*-

import flectra

def migrate(cr, version):
    registry = flectra.registry(cr.dbname)
    from flectra.addons.account.models.chart_template import migrate_tags_on_taxes
    migrate_tags_on_taxes(cr, registry)
