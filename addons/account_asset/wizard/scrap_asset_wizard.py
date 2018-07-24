# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import fields, models, api
from datetime import datetime


class ScrapAssetWizard(models.TransientModel):
    _name = "scrap.asset.wizard"

    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    asset_id = fields.Many2one("account.asset.asset", string="Asset")
    asset_category_id = fields.Many2one("account.asset.category",
                                        string="Asset Category", required=True)
    product_id = fields.Many2one("product.product", string="Product",
                                 required=True)
    depreciated_amount = fields.Float(string="Depreciated Amount",
                                      required=True)
    sale_date = fields.Date(
        string="Date", default=lambda self: datetime.today(),
        required=True)

    financial_move = fields.Boolean(string="Create Financial Move")
    journal_id = fields.Many2one("account.journal", string="Payment Journal",
                                 domain=[('type', 'in', ('bank', 'cash'))])
    amount = fields.Float(string="Payment Amount")

    @api.multi
    def do_scrap(self):
        asset_id = self.env['account.asset.asset'].browse(
            self._context['active_id'])

        if asset_id:
            asset_id.write({
                'active': False,
                'state': 'close'
            })
            depreciation_line_ids = self.env[
                'account.asset.depreciation.line'].search(
                [('asset_id', '=', asset_id.id), ('move_check', '=', False)])

            if depreciation_line_ids:
                depreciation_line_ids.unlink()
        return True
