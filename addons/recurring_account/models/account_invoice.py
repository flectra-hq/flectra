# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    recurring_id = fields.Many2one('recurring', string='Recurring Reference')
    rec_source_id = fields.Many2one('account.invoice',
                                    string='Recurring Source')

    @api.multi
    def get_recurring(self):
        result = self.env['recurring'].get_recurring(
            'account.invoice', self.id)
        return result

    @api.multi
    def get_recurring_documents(self):
        result = self.env['recurring'].get_recurring_documents(
            'account.invoice', 'account.action_invoice_tree1',
            self.recurring_id)
        return result

    @api.multi
    def action_invoice_cancel(self):
        res = super(AccountInvoice, self).action_invoice_cancel()
        if self.recurring_id:
            self.recurring_id.set_done()
        return res
