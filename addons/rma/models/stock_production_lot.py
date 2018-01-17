# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    warranty_date = fields.Date(string='Warranty Expiry Date')
