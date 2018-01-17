# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class WarrantyExpireLine(models.Model):
    _name = "warranty.expire.line"
    _description = "Warranty Expire Lines"

    rma_id = fields.Many2one('rma.request', string='RMA Request Number')
    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.production.lot',
                             string='Stock production lot')
    qty_expired = fields.Float(string="Expired Quantity")
    warranty_date = fields.Date('Lot Warranty Date')
