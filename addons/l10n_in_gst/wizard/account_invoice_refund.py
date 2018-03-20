# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    note_issue_reason_id = fields.Many2one('note.issue.reason',
                                           string='Reason for Issuing Note')

    @api.onchange('note_issue_reason_id')
    def onchange_note_issue_reason(self):
        """ Add value of Issuing Note into Reason """
        if self.note_issue_reason_id:
            self.description = ('%s-%s') % (self.note_issue_reason_id.code,
                                            self.note_issue_reason_id.name)
