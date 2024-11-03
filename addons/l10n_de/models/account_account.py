from flectra import models, _
from flectra.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = ['account.account']

    def write(self, vals):
        if (
            'code' in vals
            and 'DE' in self.company_id.account_fiscal_country_id.mapped('code')
            and any(a.code != vals['code'] for a in self)
        ):
            if self.env['account.move.line'].search_count([('account_id', 'in', self.ids)], limit=1):
                raise UserError(_("You can not change the code of an account."))
        return super().write(vals)
