# Part of flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    posted_to_forum = fields.Boolean(string='Posted to Forum', copy=False)
    display_post = fields.Boolean(string='Display', compute="_compute_displaypost", 
                                  default=False, store=True, readonly=True)
  
    @api.depends("team_id")
    def _compute_displaypost(self):
        if self.team_id.forum_id:
            self.display_post = True

    def post_to_forum(self):
        for record in self:
            if record.team_id and record.team_id.forum_id:
                self.env['forum.post'].create(
                    {'forum_id': record.team_id.forum_id.id,
                     'name': record.issue_name,
                     'content': record.help_description})
                self.posted_to_forum = True
                body = "#%s Issue Posted on Forum: %s" % (
                    record.ticket_seq, record.team_id.forum_id.name)
                self.env['mail.message'].create({
                    'subject': _('Issue Posted on Forum'),
                    'body': body,
                    'record_name': record.issue_name,
                    'model': record._name,
                    'res_id': record.id,
                    'no_auto_thread': True,
                })
