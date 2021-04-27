# Part of flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    need_project = fields.Boolean(string='Need Project',
                                  compute="_compute_need_project_field")
    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')

    def action_create_task(self):
        self.ensure_one()
        user = self.env['res.users'].search(
            [('partner_id', '=', self.partner_id.id)], limit=1)
        vals = {'name': self.issue_name,
                'helpdesk_id': self.id,
                'partner_id': self.user_id.id,
                'description':
                    self.issue_name or '' + '<br/>' + self.help_description or '',
                'user_id': user and user.id,
                'priority': '1',
                }
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('use_project'):
            vals.update({
                'project_id':
                    self.team_id and self.team_id.project_id and
                    self.team_id.project_id.id})
        self.env['project.task'].create(vals)

    def action_get_tasks(self):
        self.ensure_one()
        context = {'default_helpdesk_id': self.id}
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('use_project') and \
                self.team_id and self.team_id.project_id and \
                self.team_id.project_id:
            context.update({'default_project_id': self.team_id.project_id.id})
        return {
            'name': _('Tasks'),
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('helpdesk_id', '=', self.id)],
            'context': context,
        }

    def _compute_task_count(self):
        for ticket in self:
            ticket.task_count = self.env['project.task'].search_count([(
                'helpdesk_id', '=', self.id)])

    def _compute_need_project_field(self):
        config_data = self.env['res.config.settings'].get_values()
        for team in self:
            if config_data.get('use_project'):
                team.need_project = True
            else:
                team.need_project != True

