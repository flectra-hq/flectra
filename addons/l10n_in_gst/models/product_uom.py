# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ProductUomCode(models.Model):
    _inherit = 'product.uom'

    code = fields.Char(string='Code')
