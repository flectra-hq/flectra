# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ReplacementReason(models.Model):
    _name = "replacement.reason"
    _description = "Replacement Reason"

    name = fields.Char(string='Reason')
