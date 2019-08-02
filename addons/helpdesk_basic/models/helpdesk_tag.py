# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class HelpdeskTag(models.Model):
    _name = 'helpdesk.tag'
    _description = 'Helpdesk Tags'

    name = fields.Char('Name', translate=True, required=True)
    code = fields.Char('Code', required=True)
