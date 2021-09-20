# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models, api
from flectra.tools.translate import _
from flectra.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def unlink(self):
        for statement in self:
            if not statement.company_id._is_accounting_unalterable() or not statement.journal_id.pos_payment_method_ids:
                continue
            if statement.state != 'open':
                raise UserError(_('You cannot modify anything on a bank statement (name: %s) that was created by point of sale operations.') % (statement.name))
        return super(AccountBankStatement, self).unlink()


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def unlink(self):
        for line in self.filtered(lambda s: s.company_id._is_accounting_unalterable() and s.journal_id.pos_payment_method_ids):
            raise UserError(_('You cannot modify anything on a bank statement line (name: %s) that was created by point of sale operations.') % (line.name,))
        return super(AccountBankStatementLine, self).unlink()
