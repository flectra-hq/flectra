# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra.addons.account.models.chart_template import update_taxes_from_templates


def migrate(cr, version):
    update_taxes_from_templates(cr, 'l10n_tr.l10ntr_tek_duzen_hesap')
