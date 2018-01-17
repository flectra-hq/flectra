# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    rma_id = fields.Many2one('rma.request', string='RMA Order Number')

    @api.model
    def create(self, vals):
        result = super(StockPicking, self).create(vals)
        rma_id = False
        if self._context.get('active_model') == 'stock.picking':
            rma_id = result.rma_id and result.rma_id.id or False
        elif self._context.get('active_model') == 'rma.request':
            rma_id = self._context.get('active_id')
        result.update({'rma_id': rma_id})
        return result
