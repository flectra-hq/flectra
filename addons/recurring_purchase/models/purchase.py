# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    recurring_id = fields.Many2one('recurring', string='Recurring Reference')
    rec_source_id = fields.Many2one('purchase.order',
                                    string='Recurring Source')

    def get_recurring(self):
        result = self.env['recurring'].get_recurring('purchase.order', self.id)
        return result

    def get_recurring_documents(self):
        result = self.env['recurring'].get_recurring_documents(
            'purchase.order', 'purchase.purchase_rfq', self.recurring_id)
        return result

    def button_cancel(self):
        if self.recurring_id:
            self.recurring_id.set_done()
        return super(PurchaseOrder, self).button_cancel()
