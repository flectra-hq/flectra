# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    posted_to_forum = fields.Boolean(string='Posted to Forum', copy=False)
    display_post = fields.Boolean(string='Display',
                                  compute='_compute_display_post')

    @api.multi
    def _compute_display_post(self):
        for record in self:
            if record.team_id and record.team_id.forum_id:
                record.display_post = True

    @api.multi
    def post_to_forum(self):
        for record in self:
            if record.team_id and record.team_id.forum_id:
                self.env['forum.post'].create(
                    {'forum_id': record.team_id.forum_id.id,
                     'name': record.name,
                     'content': record.description})
                self.posted_to_forum = True
                body = "#%s Issue Posted on Forum: %s" % (
                    record.sequence, record.team_id.forum_id.name)
                self.env['mail.message'].create({
                    'subject': _('Issue Posted on Forum'),
                    'body': body,
                    'record_name': record.name,
                    'model': record._name,
                    'res_id': record.id,
                    'no_auto_thread': True,
                })
