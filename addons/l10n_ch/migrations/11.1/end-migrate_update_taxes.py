# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import api, SUPERUSER_ID
from flectra.addons.account.models.chart_template import update_taxes_from_templates


def migrate(cr, version):
    new_template_to_tax = update_taxes_from_templates(cr, 'l10n_ch.l10nch_chart_template')
    if new_template_to_tax:
        _, new_tax_ids = zip(*new_template_to_tax)
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['account.tax'].browse(new_tax_ids).active = True
