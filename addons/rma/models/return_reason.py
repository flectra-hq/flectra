# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ReturnReason(models.Model):
    _name = "return.reason"
    _description = "Return Reason"

    name = fields.Char(string='Reason')
