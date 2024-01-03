# -*- coding: utf-8 -*-
from flectra import models
from flectra.tools.translate import _
from flectra.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self, is_modify=False):
        self.ensure_one()
        for move in self.move_ids:
            if move.journal_id.country_code == 'SA' and not self.reason:
                raise UserError(_("For Credit/Debit notes issued in Saudi Arabia, you need to specify a Reason"))
        return super().reverse_moves(is_modify=is_modify)
