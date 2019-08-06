# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    need_project = fields.Boolean(string='Need Project',
                                  compute="_compute_need_project")
    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')

    @api.multi
    def action_create_task(self):
        self.ensure_one()
        user = self.env['res.users'].search(
            [('partner_id', '=', self.partner_id.id)], limit=1)
        vals = {'name': self.name,
                'helpdesk_id': self.id,
                'partner_id': self.assigned_to_id.id,
                'description':
                    self.name or '' + '<br/>' + self.description or '',
                'user_id': user and user.id or False,
                'priority': 'l',
                }
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('use_project'):
            vals.update({
                'project_id':
                    self.team_id and self.team_id.project_id and
                    self.team_id.project_id.id or False})
        self.env['project.task'].create(vals)

    @api.multi
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

    @api.multi
    def _compute_task_count(self):
        for ticket in self:
            ticket.task_count = self.env['project.task'].search_count([(
                'helpdesk_id', '=', self.id)])

    @api.multi
    def _compute_need_project(self):
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('use_project'):
            for team in self:
                team.need_project = True
