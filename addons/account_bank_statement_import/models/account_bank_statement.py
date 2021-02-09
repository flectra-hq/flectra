# -*- coding: utf-8 -*-

from flectra import api, fields, models, _
import base64
from flectra.exceptions import UserError, ValidationError
import time


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    accounting_date = fields.Date(string="Accounting Date",
                                  help="If set, the accounting entries created"
                                       " during the bank statement reconciliation"
                                       " process will be created at this date.\n"
                                       "This is useful if the accounting period"
                                       " in which the entries should normally"
                                       " be booked is already closed.",
                                  states={'open': [('readonly', False)]}, readonly=True)

    def action_bank_reconcile_bank_statements(self):
        self.ensure_one()
        bank_stmt_lines = self.mapped('line_ids')
        return {
            'type': 'ir.actions.client',
            'tag': 'bank_statement_reconciliation_view',
            'context': {'statement_line_ids': bank_stmt_lines.ids, 'company_ids': self.mapped('company_id').ids},
        }

    def button_confirm_bank(self):
        self._balance_check()
        statements = self.filtered(lambda r: r.state == 'open')
        for statement in statements:
            moves = self.env['account.move']
            # `line.journal_entry_ids` gets invalidated from the cache during the loop
            # because new move lines are being created at each iteration.
            # The below dict is to prevent the ORM to permanently refetch `line.journal_entry_ids`
            line_journal_entries = {line: line.journal_entry_ids for line in statement.line_ids}
            for st_line in statement.line_ids:
                #upon bank statement confirmation, look if some lines have the account_id set. It would trigger a journal entry
                #creation towards that account, with the wanted side-effect to skip that line in the bank reconciliation widget.
                journal_entries = line_journal_entries[st_line]
                st_line.fast_counterpart_creation()
                if not st_line.account_id and not journal_entries.ids and not st_line.statement_id.currency_id.is_zero(st_line.amount):
                    raise UserError(_('All the account entries lines must be processed in order to close the statement.'))
            moves = statement.mapped('line_ids.journal_entry_ids.move_id')
            if moves:
                moves.filtered(lambda m: m.state != 'posted').post()
            statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
            if statement.journal_id.type == 'bank':
                # Attach report to the Bank statement
                content, content_type = self.env.ref('account.action_report_account_statement').render_qweb_pdf(statement.id)
                self.env['ir.attachment'].create({
                    'name': statement.name and _("Bank Statement %s.pdf") % statement.name or _("Bank Statement.pdf"),
                    'type': 'binary',
                    'datas': base64.encodestring(content),
                    'res_model': statement._name,
                    'res_id': statement.id
                })
        statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})
