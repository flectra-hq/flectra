# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    forum_id = fields.Many2one('forum.forum', string="Forum")

    @api.model
    def create(self, values):
        res = super(HelpdeskTeam, self).create(values)
        res.forum_id = self.env['forum.forum'].sudo().create(
            {'name': 'Forum %s' % (res.name or '')})
        return res
