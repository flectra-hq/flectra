# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    activity_type = fields.Selection(related='user_type_id.activity_type')
