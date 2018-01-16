# -*- coding: utf-8 -*-

import flectra

def migrate(cr, version):
    registry = flectra.registry(cr.dbname)
    from flectra.addons.account.models.chart_template import migrate_set_tags_and_taxes_updatable
    migrate_set_tags_and_taxes_updatable(cr, registry, 'l10n_at')
