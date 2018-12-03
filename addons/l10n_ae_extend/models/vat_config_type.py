# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class JournalConfigType(models.Model):
    _name = 'vat.config.type'
    _description = 'Config Type'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    vat_type = fields.Selection([
        ('local_sale', 'Local Sale'),
        ('inside_gcc_sale', 'Inside GCC Sale'),
        ('outside_gcc_sale', 'Outside GCC Sale'),
        ('designated_zone_sale', 'Designated Zone Sale'),
        ('local_purchase', 'Local Purchase'),
        ('inside_gcc_purchase', 'Inside GCC Purchase'),
        ('outside_gcc_purchase', 'Outside GCC Purchase'),
        ('designated_zone_purchase', 'Designated Zone Purchase')],
        'VAT Type', required=True)
    type = fields.Selection([
        ('sale', 'Sale'), ('purchase', 'Purchase')], 'Type', required=True)
