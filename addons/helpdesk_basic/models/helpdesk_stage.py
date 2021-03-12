# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, _


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _order = 'sequence, id'
    _description = 'Helpdesk Stage'

    def _default_team_ids(self):
        team_id = self.env.context.get('default_team_id')
        if team_id:
            return [(4, team_id, 0)]

    name = fields.Char('Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer('Sequence', default=10)
    stage_type = fields.Selection([('draft', 'Draft'), ('new', 'New'),
                                   ('in_progress', 'In Progress'),
                                   ('done', 'Done')], string='Stage Type',
                                   required=True)
    is_close = fields.Boolean(
        'Closing Stage', 
        help='Tickets in this stage are considered as done. This is used notably when '
             'computing SLAs and KPIs on tickets.')
    fold = fields.Boolean(
        'Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    team_ids = fields.Many2many(
        'helpdesk.team', relation='team_stage_rel', string='Team',
        default=_default_team_ids,
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    template_id = fields.Many2one(
        'mail.template', 'Email Template',
        domain="[('model', '=', 'helpdesk.ticket')]",
        help="Automated email sent to the ticket's customer when the ticket reaches this stage.")
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')

    def unlink(self):
        stages = self
        default_team_id = self.env.context.get('default_team_id')
        if default_team_id:
            shared_stages = self.filtered(lambda x: len(x.team_ids) > 1 and default_team_id in x.team_ids.ids)
            tickets = self.env['helpdesk.ticket'].with_context(active_test=False).search([('team_id', '=', default_team_id), ('stage_id', 'in', self.ids)])
            if shared_stages and not tickets:
                shared_stages.write({'team_ids': [(3, default_team_id)]})
                stages = self.filtered(lambda x: x not in shared_stages)
        return super(HelpdeskStage, stages).unlink()
        