# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api, _


class ProjectStory(models.Model):
    _name = "project.story"
    _inherit = 'mail.thread'
    _description = "Project Story"
    _order = "sprint_seq,sequence"

    name = fields.Char("Title", required=True, tracking=True)
    priority_id = fields.Many2one('story.priority', string="Priority",
                                  tracking=True)
    story_type_id = fields.Many2one('story.type', string="Type",
                                    tracking=True)
    tags = fields.Char("Tags", tracking=True)
    description = fields.Text("Description", tracking=True)
    owner_id = fields.Many2one(
        'res.users', string="Owner", default=lambda self: self.env.user.id,
        tracking=True)
    sprint_id = fields.Many2one('project.sprint', string="Sprint",
                                tracking=True)
    estimated_velocity = fields.Integer(
        compute="_compute_calculate_estimated_velocity", string="Estimated Velocity",
        store=True, tracking=True)
    actual_velocity = fields.Integer(
        compute="_compute_calculate_actual_velocity", string="Actual Velocity",
        store=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ], string="states", tracking=True, default="draft")
    sequence = fields.Integer(string='Sequence', default=1)
    sprint_seq = fields.Char(
        related="sprint_id.sprint_seq", string="Reference", readonly=True)

    def set_state_active(self):
        self.state = "in_progress"

    def set_state_cancel(self):
        self.state = "cancel"

    def set_state_done(self):
        self.state = "done"

    def action_view_tasks(self):
        return {
            'name': (_('Tasks')),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('sprint_id', '=', self.sprint_id.id)],
            'context': {
                'default_sprint_id': self.sprint_id.id,
                'default_project_id': self.sprint_id.project_id.id,
            }
        }

    @api.depends('sprint_id')
    def _compute_calculate_estimated_velocity(self):
        for story in self:
            task_ids = story.env['project.task'].search([
                ('sprint_id', '=', story.sprint_id.id)
            ])
            total_velocity = sum([
                task.velocity for task in task_ids if task.velocity])
            story.estimated_velocity = total_velocity

    @api.depends('sprint_id', 'sprint_id.end_date')
    def _compute_calculate_actual_velocity(self):
        for story in self:
            task_ids = story.env['project.task'].search([
                ('sprint_id', '=', story.sprint_id.id),
                ('actual_end_date', '<=', story.sprint_id.end_date)
            ])
            total_velocity = sum([
                task.velocity for task in task_ids if task.velocity])
            story.actual_velocity = total_velocity

    @api.model
    def create(self, vals):
        res = super(ProjectStory, self).create(vals)

        partner_list = [
            member.partner_id.id for member in res.sprint_id.team_id.member_ids
        ]

        for follower in partner_list:
            if follower:
                mail_followers_ids = self.env['mail.followers'].sudo().search([
                    ('res_id', '=', res.id),
                    ('partner_id', '=', follower),
                    ('res_model', '=', self._name),
                ])

                if not mail_followers_ids:
                    self.env['mail.followers'].sudo().create({
                        'res_id': res.id,
                        'res_model': self._name,
                        'partner_id': follower,
                        'team_id': res.sprint_id.team_id.id,
                    })
        return res

    def write(self, vals):
        res = super(ProjectStory, self).write(vals)
        delete_team_id = self.env['mail.followers'].sudo().search([
            ('team_id', '!=', self.sprint_id.team_id.id),
            ('res_id', '=', self.id),
        ])

        delete_team_id.unlink()

        partner_list = [
            member.partner_id.id for member in
            self.sprint_id.team_id.member_ids
        ]

        for follower in partner_list:
            if follower:
                mail_follower_ids = self.env['mail.followers'].sudo().search([
                    ('res_id', '=', self.id),
                    ('partner_id', '=', follower),
                    ('res_model', '=', self._name),
                ])
                if not mail_follower_ids:
                    self.env['mail.followers'].sudo().create({
                        'res_id': self.id,
                        'res_model': self._name,
                        'partner_id': follower,
                        'team_id': self.sprint_id.team_id.id,
                    })
        return res


class StoryPriority(models.Model):
    _name = "story.priority"
    _description = "Story Priority"
    _inherit = 'mail.thread'

    name = fields.Char("Name", tracking=True)
    code = fields.Char("Code", tracking=True)


class StoryType(models.Model):
    _name = "story.type"
    _description = "Story Type"
    _inherit = 'mail.thread'

    name = fields.Char("Name", tracking=True)
    code = fields.Char("Code", tracking=True)
