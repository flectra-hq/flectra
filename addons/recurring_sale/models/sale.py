# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    recurring_id = fields.Many2one('recurring', string='Recurring Reference')
    rec_source_id = fields.Many2one('sale.order', string='Recurring Source')

    def get_recurring(self):
        result = self.env['recurring'].get_recurring('sale.order', self.id)
        return result

    def get_recurring_documents(self):
        result = self.env['recurring'].get_recurring_documents(
            'sale.order', 'sale.action_quotations', self.recurring_id)
        return result

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if self.recurring_id:
            self.recurring_id.set_done()
        return res
