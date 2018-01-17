# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api, _


class ProjectStory(models.Model):
    _name = "project.story"
    _inherit = ['ir.branch.company.mixin', 'mail.thread']
    _description = "Project Story"

    name = fields.Char("Title", required=True, track_visibility="onchange")
    priority_id = fields.Many2one('story.priority', string="Priority",
                                  track_visibility="onchange")
    story_type_id = fields.Many2one('story.type', string="Type",
                                    track_visibility="onchange")
    tags = fields.Char("Tags", track_visibility="onchange")
    description = fields.Text("Description", track_visibility="onchange")
    owner_id = fields.Many2one(
        'res.users', string="Owner", default=lambda self: self.env.user.id,
        track_visibility='onchange')
    sprint_id = fields.Many2one('project.sprint', string="Sprint",
                                track_visibility="onchange")
    estimated_velocity = fields.Integer(
        compute="calculate_estimated_velocity", string="Estimated Velocity",
        store=True, track_visibility="onchange")
    actual_velocity = fields.Integer(
        compute="calculate_actual_velocity", string="Actual Velocity",
        store=True, track_visibility="onchange")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ], string="states", track_visibility="onchange", default="draft")

    @api.multi
    def set_state_active(self):
        self.state = "in_progress"

    @api.multi
    def set_state_cancel(self):
        self.state = "cancel"

    @api.multi
    def set_state_done(self):
        self.state = "done"

    @api.multi
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

    @api.multi
    @api.depends('sprint_id')
    def calculate_estimated_velocity(self):
        for story in self:
            task_ids = story.env['project.task'].search([
                ('sprint_id', '=', story.sprint_id.id)
            ])
            total_velocity = sum([
                task.velocity for task in task_ids if task.velocity])
            story.estimated_velocity = total_velocity

    @api.multi
    @api.depends('sprint_id', 'sprint_id.end_date')
    def calculate_actual_velocity(self):
        for story in self:
            task_ids = story.env['project.task'].search([
                ('sprint_id', '=', story.sprint_id.id),
                ('actual_end_date', '<=', story.sprint_id.end_date)
            ])
            total_velocity = sum([
                task.velocity for task in task_ids if task.velocity])
            story.actual_velocity = total_velocity

    @api.onchange('sprint_id')
    def onchange_project(self):
        if self.sprint_id and self.sprint_id.project_id.branch_id:
            self.branch_id = self.sprint_id.project_id.branch_id

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

    @api.multi
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
    _inherit = 'mail.thread'

    name = fields.Char("Name", track_visibility="onchange")
    code = fields.Char("Code", track_visibility="onchange")


class StoryType(models.Model):
    _name = "story.type"
    _inherit = 'mail.thread'

    name = fields.Char("Name", track_visibility="onchange")
    code = fields.Char("Code", track_visibility="onchange")
