# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, api


class Location(models.Model):
    _inherit = "stock.location"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []

        if self.env.context.get('warehouse', False):
            warehouse_ids = self.env['stock.warehouse'].browse(
                self.env.context['warehouse'][0][2])
            lot_stock_ids = [wh.lot_stock_id.id for wh in warehouse_ids
                             if wh.lot_stock_id]
            location_ids = self.env['stock.location'].search(
                [('location_id', 'child_of', lot_stock_ids),
                 ('usage', '=', 'internal')]).ids
            location_ids += lot_stock_ids
            domain = [('id', 'in', location_ids)]

        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
