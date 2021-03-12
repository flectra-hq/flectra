# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    elearning_id = fields.Many2one('slide.channel', string="E Learning")
