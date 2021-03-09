# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    recurring_id = fields.Many2one('recurring', string='Recurring Reference')
    rec_source_id = fields.Many2one('account.move',
                                    string='Recurring Source')

    def get_recurring(self):
        result = self.env['recurring'].get_recurring(
            'account.move', self.id)
        return result

    def get_recurring_documents(self):
        result = self.env['recurring'].get_recurring_documents(
            'account.move', 'account.action_move_out_invoice_type',
            self.recurring_id)
        return result

    def action_invoice_cancel(self):
        res = super(AccountMove, self).action_invoice_cancel()
        if self.recurring_id:
            self.recurring_id.set_done()
        return res
