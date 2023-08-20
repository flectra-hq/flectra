# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api, _
from flectra.exceptions import ValidationError
from datetime import datetime, timedelta, date


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _inherit = 'mail.thread'
    _description = "Sprint of the Project"
    _rec_name = 'sprint_seq'

    sprint_seq = fields.Char(
        string="Reference", readonly=True)
    name = fields.Char("Sprint Name", required=True,
                       tracking=True)
    goal_of_sprint = fields.Char("Goal of Sprint", tracking=True)

    meeting_date = fields.Datetime("Planning Meeting Date", required=True,
                                   tracking=True)
    hour = fields.Float(string="Hour", tracking=True)
    time_zone = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM'),
    ], tracking=True)
    estimated_velocity = fields.Integer(
        compute="_compute_calculate_estimated_velocity", string="Estimated Velocity",
        store=True, tracking=True)
    actual_velocity = fields.Integer(
        compute="_compute_calculate_actual_velocity", string="Actual Velocity",
        store=True, tracking=True)
    sprint_planning_line = fields.One2many(
        'sprint.planning.line', 'sprint_id', string="Sprint Planning Lines")
    project_id = fields.Many2one('project.project', string="Project",
                                 tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    working_days = fields.Integer(
        compute="_compute_calculate_business_days", string="Business Days",
        store=True, tracking=True)
    productivity_hours = fields.Float(string="Productivity Hours",
                                      tracking=True)
    productivity_per = fields.Float(
        compute="_compute_calculate_productivity_per", string="Productivity (%)",
        store=True, tracking=True)
    holiday_type = fields.Selection(
        [('hours', 'Hours'), ('days', 'Days')],
        string="Holiday (Hours / Days)", default='hours',
        tracking=True)
    holiday_count = fields.Float(string="Holiday Count",
                                 tracking=True)
    holiday_days = fields.Float(
        compute="_compute_calculate_holiday_days", string="Holiday Days", store=True,
        tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], string="State", default='draft',
        tracking=True)
    team_id = fields.Many2one('project.team', string="Team",
                              tracking=True, required=True)
    task_line = fields.One2many('project.task', 'sprint_id', string='Tasks')
    color = fields.Integer('Color Index')
    task_count = fields.Integer(compute='_compute_task_count', store=True)

    @api.depends("task_line")
    def _compute_task_count(self):
        for record in self:
            record.task_count = len(record.task_line)

    duration = fields.Integer(
        "Duration (In Days)", compute='_compute_days_calculate', store=True,
        tracking=True)

    @api.depends("start_date")
    def _compute_days_calculate(self):
        for days in self:
            if days.start_date and days.end_date:
                diff = datetime.strptime(
                    str(days.end_date), '%Y-%m-%d').date() - datetime.strptime(
                    str(days.start_date), '%Y-%m-%d').date()
                days.duration = diff.days

    def _compute_get_task_count(self):
        for record in self:
            record.number_of_tasks = record.env['project.task'].search_count([
                ('sprint_id', '=', record.id)])

    number_of_tasks = fields.Integer(
        string="# of tasks", compute="_compute_get_task_count")

    def _compute_get_story_count(self):
        for record in self:
            count = record.env['project.story'].search_count([
                ('sprint_id', '=', record.id)])
            record.number_of_stories = count

    number_of_stories = fields.Integer(
        string="# of stories", compute="_compute_get_story_count")

    def _compute_get_retrospective_count(self):
        for record in self:
            count = record.env['retrospective'].search_count([
                ('sprint_id', '=', record.id)])
            record.number_of_retrospectives = count

    number_of_retrospectives = fields.Integer(
        string="# of Retrospectives", compute="_compute_get_retrospective_count")

    @api.depends('task_line', 'task_line.stage_id', 'task_line.sprint_id',
                 'estimated_velocity', 'start_date', 'end_date', 'project_id',
                 'team_id')
    def _compute_calculate_tasks_json(self):
        data = []
        for record in self:
            task_ids = self.env['project.task'].search([
                ('sprint_id', '=', record.id)])
            velocity = record.estimated_velocity or 1.0
            for task in task_ids:
                data.append({
                    'task': task.task_seq or '/',
                    'velocity': task.velocity or 0,
                    'per': round(((float(task.velocity) * 100) / float(
                        velocity)), 2)
                })
            record.tasks_json = data

    tasks_json = fields.Char(
        string="Tasks", compute="_compute_calculate_tasks_json", store=True)

    def get_data(self):
        task_dict_list = []
        for record in self:
            task_pool = self.env['project.task'].search([
                ('sprint_id', '=', record.id)])
            for task in task_pool:
                task_dict = {
                    'reference': task.task_seq,
                    'name': task.name,
                    'velocity': task.velocity,
                    'start_date': task.start_date,
                    'end_date': task.end_date,
                    'actual_end_date': task.actual_end_date,
                    'assigned_to': task.user_id.name,
                    'state': task.stage_id.name,
                }
                task_dict_list.append(task_dict)
        return task_dict_list

    def set_state_open(self):
        self.state = 'in_progress'

    def set_state_cancel(self):
        self.state = 'cancel'

    def set_state_pending(self):
        self.state = 'pending'

    def redirect_to_view(self, model, caption):
        return {
            'name': (_(caption)),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': model,
            'domain': [('sprint_id', '=', self.id)],
            'context': {
                'default_sprint_id': self.id,
                'default_project_id': self.project_id.id
            }
        }

    def action_view_tasks(self):
        return self.redirect_to_view("project.task", "Tasks")

    def action_view_stories(self):
        return self.redirect_to_view("project.story", "Stories")

    def action_view_release_planning(self):
        return self.redirect_to_view("release.planning", "Release Planning")

    def action_view_retrospective(self):
        return self.redirect_to_view("retrospective", "Retrospective")

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        if self.start_date and self.end_date and (
                self.start_date > self.end_date):
            raise ValidationError(
                "Start Date can not be greater than End date, Dude!")

    @api.onchange('holiday_type')
    def onchange_holiday_type(self):
        self.holiday_count = 0.0
        self.holiday_days = 0.0

    @api.depends('project_id', 'project_id.no_of_days', 'start_date',
                 'end_date')
    def _compute_calculate_business_days(self):
        for record in self:
            if record.start_date and record.end_date:
                days_dict = {
                    0: (1, 2, 3, 4, 5, 6, 7),
                    1: (2, 3, 4, 5, 6, 7),
                    2: (3, 4, 5, 6, 7),
                    3: (4, 5, 6, 7),
                    4: (5, 6, 7),
                    5: (6, 7),
                    6: (7,),
                    7: (),
                }
                start = datetime.strptime(str(record.start_date), "%Y-%m-%d").date()
                end = datetime.strptime(str(record.end_date), "%Y-%m-%d").date()
                delta = timedelta(days=1)
                days = 0

                if record.project_id and end > start:
                    working_days = record.project_id.no_of_days
                    non_working_days = days_dict[working_days]

                    while end != start:
                        end -= delta
                        if end.isoweekday() not in non_working_days:
                            days += 1

                    record.working_days = days

    @api.depends('project_id', 'project_id.no_of_hours', 'productivity_hours')
    def _compute_calculate_productivity_per(self):
        for record in self:
            project_id = record.project_id
            no_of_hours = project_id.no_of_hours if project_id else 0
            prod_hours = record.productivity_hours
            if project_id and no_of_hours > 0 and prod_hours:
                record.productivity_per = (prod_hours / no_of_hours) * 100

    @api.depends('project_id', 'project_id.no_of_hours', 'holiday_count')
    def _compute_calculate_holiday_days(self):
        for record in self:
            if record.holiday_type == 'days' and record.project_id:
                hours = record.holiday_count * record.project_id.no_of_hours
                record.holiday_days = hours

    @api.depends('project_id', 'task_line', 'task_line.velocity')
    def _compute_calculate_estimated_velocity(self):
        for record in self:
            task_ids = record.env['project.task'].search([
                ('sprint_id', '=', record.id)
            ])
            total_velocity = sum([
                task.velocity for task in task_ids if task.velocity])
            record.estimated_velocity = total_velocity

    @api.depends('project_id', 'end_date', 'task_line', 'task_line.velocity',
                 'task_line.stage_id')
    def _compute_calculate_actual_velocity(self):
        for record in self:
            task_ids = record.env['project.task'].search([
                ('sprint_id', '=', record.id),
                ('actual_end_date', '<=', record.end_date),
            ])
            total_velocity = sum([
                task.velocity for task in task_ids if task.velocity])
            record.actual_velocity = total_velocity

    @api.onchange('duration')
    def onchange_start_date(self):
        if self.start_date:
            end_date = datetime.strptime(
                str(self.start_date), '%Y-%m-%d') + timedelta(days=self.duration)
            self.end_date = end_date

    def check_sprint_state(self):
        for record in self.search([('state', '!=', 'done')]):
            if record.end_date and record.end_date < fields.Date.today():
                record.state = 'done'

    @api.constrains('sprint_planning_line')
    def check_users_in_planning_line(self):
        user_list = []
        for user in self.sprint_planning_line:
            if user.user_id.id not in user_list:
                user_list.append(user.user_id.id)
            else:
                raise ValidationError(
                    "You can't add the same user twice in Sprint Planning!")

    @api.model
    def create(self, vals):
        vals['sprint_seq'] = self.env[
            'ir.sequence'].next_by_code('project.sprint')

        res = super(ProjectSprint, self).create(vals)
        partner_list = []

        mail_channel_id = self.env['mail.channel'].sudo().search([
            ('name', '=', 'Project Sprint')
        ])
        if mail_channel_id:
            mail_channel_ids = self.env['mail.followers'].sudo().search([
                ('channel_id', '=', mail_channel_id.id),
                ('res_model', '=', res._name),
                ('res_id', '=', res.id),
            ])
            if not mail_channel_ids:
                self.env['mail.followers'].sudo().create({
                    'channel_id': mail_channel_id.id,
                    'res_model': res._name,
                    'res_id': res.id,
                })

        if 'team_id' in vals:
            team_id = self.env['project.team'].browse(vals['team_id'])
            partner_list += [member.partner_id.id
                             for member in team_id.member_ids]

        for follower in partner_list:
            if follower:
                mail_follower_ids = self.env['mail.followers'].sudo().search([
                    ('res_id', '=', res.id),
                    ('partner_id', '=', follower),
                    ('res_model', '=', res._name),
                ])
                if not mail_follower_ids:
                    self.env['mail.followers'].sudo().create({
                        'res_id': res.id,
                        'res_model': res._name,
                        'partner_id': follower,
                        'team_id': team_id.id,
                    })
        return res

    def write(self, vals):
        res = super(ProjectSprint, self).write(vals)

        if 'team_id' in vals:
            team_id = self.env['project.team'].browse(vals['team_id'])
        else:
            team_id = self.team_id

        delete_team_id = self.env['mail.followers'].sudo().search([
            ('team_id', '!=', team_id.id),
            ('res_id', '=', self.id),
        ])
        delete_team_id.unlink()

        partner_list = [member.partner_id.id for member in team_id.member_ids]
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
                        'team_id': team_id.id,
                    })
        return res

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('project_scrum.state_sprint_draft')
        elif 'state' in init_values and self.state == 'in_progress':
            return self.env.ref('project_scrum.state_sprint_in_progress')
        elif 'state' in init_values and self.state == 'pending':
            return self.env.ref('project_scrum.state_sprint_pending')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('project_scrum.state_sprint_done')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('project_scrum.state_sprint_cancel')
        return super(ProjectSprint, self)._track_subtype(init_values)


class Project(models.Model):
    _inherit = "project.project"

    def _compute_sprint_count(self):
        for project in self:
            count = project.env['project.sprint'].search_count([
                ('project_id', '=', project.id)
            ])
            project.sprint_count = count

    sprint_count = fields.Integer(
        compute="_compute_sprint_count", string="No. of sprints related to")

    def show_sprints(self):
        self.ensure_one()
        return {
            'name': ("Sprints"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.sprint',
            'domain': [('project_id', '=', self.id)]
        }

    no_of_hours = fields.Integer(
        related="resource_calendar_id.no_of_hours",
        string="Working Hour(s) per Day", store=True)
    no_of_days = fields.Integer(
        related="resource_calendar_id.no_of_days",
        string="Working Day(s) per Week", store=True)
    task_type_ids = fields.Many2many(
        'project.task.type', 'project_task_type_rel', 'project_id', 'type_id',
        string='Project(s)')


class SprintPlanningLine(models.Model):
    _name = "sprint.planning.line"
    _description = "Sprint Planning Line"

    @api.depends('available_per', 'sprint_id.project_id',
                 'sprint_id.project_id.no_of_hours',
                 'sprint_id', 'sprint_id.working_days')
    def _compute_calculate_hours(self):
        for record in self:
            project_id = record.sprint_id.project_id
            no_of_hours = project_id and project_id.no_of_hours or 0.0
            calc = (record.available_per *
                    record.sprint_id.working_days * no_of_hours) / 100
            record.productivity_hours = float(calc)

    @api.depends('sprint_id', 'available_per', 'sprint_id.working_days',
                 'sprint_id.productivity_hours')
    def _compute_calculate_sprint_hours(self):
        for record in self:
            hours = (record.available_per * record.sprint_id.working_days *
                     record.sprint_id.productivity_hours) / 100
            record.sprint_hours = hours

    @api.depends('sprint_id', 'sprint_id.holiday_count',
                 'sprint_id.holiday_days', 'sprint_hours', 'off_hours')
    def _compute_calculate_total_hours(self):
        for record in self:
            if record.sprint_id.holiday_type == 'hours':
                hours = (record.sprint_hours - record.sprint_id.holiday_count -
                         record.off_hours)
            else:
                hours = (record.sprint_hours - record.sprint_id.holiday_days -
                         record.off_hours)
            record.total_hours = hours

    sprint_id = fields.Many2one('project.sprint', string="Sprint")
    user_id = fields.Many2one('res.users', string="User")
    role_id = fields.Many2one(
        related="user_id.role_id", string="Role", store=True)
    available_per = fields.Integer(string="Available (%)")
    productivity_hours = fields.Float(
        compute="_compute_calculate_hours", string="Productivity Hour(s)", store=True)
    sprint_hours = fields.Float(
        compute="_compute_calculate_sprint_hours", string="Sprint Hour(s)", store=True)
    off_hours = fields.Float(string="Off Hour(s)")
    total_hours = fields.Float(
        compute="_compute_calculate_total_hours", string="Total Hour(s)", store=True)


class UserRole(models.Model):
    _name = "user.role"
    _description = "User Role"

    name = fields.Char(string="Role")
    code = fields.Char(string="Code")


class ResUsers(models.Model):
    _inherit = "res.users"

    role_id = fields.Many2one("user.role", string="User Role")


class ProjectTask(models.Model):
    _inherit = "project.task"

    sprint_id = fields.Many2one(
        'project.sprint', string="Sprint", tracking=True)
    velocity = fields.Integer(string="Velocity", tracking=True)
    story_id = fields.Many2one(
        'project.story', string="Story", tracking=True)
    release_planning_id = fields.Many2one(
        "release.planning", string="Release Planning",
        tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    actual_end_date = fields.Date(
        compute='_compute_calculate_actual_end_date', string="Actual End Date",
        store=True, tracking=True
    )
    task_seq = fields.Char(
        string="Reference", tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'project.task') or '/')

    @api.depends('stage_id')
    def _compute_calculate_actual_end_date(self):
        for stage in self:
            if stage.stage_id.name == 'Done':
                stage.actual_end_date = date.today()

    @api.onchange('story_id')
    def onchange_story(self):
        if self.story_id:
            self.description = self.story_id.description

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        if self.sprint_id:
            start_date = self.sprint_id.start_date
            end_date = self.sprint_id.end_date

            if self.start_date and start_date and (
                    self.start_date < start_date):
                raise ValidationError(
                    "Start date is not valid according to the Sprint.")

            if self.end_date and end_date and (self.end_date > end_date):
                raise ValidationError(
                    "End date is not valid according to the Sprint.")

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)

        partner_list = [
            member.partner_id.id
            for member in res.sprint_id.team_id.member_ids
        ]

        for follower in partner_list:
            if follower:
                mail_follower_ids = self.env['mail.followers'].sudo().search([
                    ('res_id', '=', res.id),
                    ('partner_id', '=', follower),
                    ('res_model', '=', self._name),
                ])
                if not mail_follower_ids:
                    self.env['mail.followers'].sudo().create({
                        'res_id': res.id,
                        'res_model': self._name,
                        'partner_id': follower,
                        'team_id': res.sprint_id.team_id.id,
                    })
        return res

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if len(self._ids) == 0:
            if self.task_seq == '/':
                vals['task_seq'] = self.env['ir.sequence'].next_by_code(
                    'project.task')
            data = []
            for record in self:
                task_ids = self.search([
                    ('sprint_id', '=', record.sprint_id.id)])
                for task in task_ids:
                    data.append({
                        'task': task.task_seq or '/',
                        'velocity': task.velocity or 0,
                        'per': round(((float(task.velocity) * 100) / float(
                            record.sprint_id.estimated_velocity)), 2)
                        if record.sprint_id.estimated_velocity > 0 else 0
                    })

                record.sprint_id.write({'tasks_json': data})

            if 'sprint_id' in vals:
                sprint_id = self.env['project.sprint'].browse(vals['sprint_id'])
                team_id = sprint_id.team_id
            else:
                team_id = self.sprint_id.team_id

            delete_team_id = self.env['mail.followers'].sudo().search([
                ('team_id', '!=', team_id.id),
                ('res_id', '=', self.id),
            ])
            delete_team_id.unlink()

            partner_list = [member.partner_id.id for member in team_id.member_ids]
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
                            'team_id': team_id.id,
                        })
        return res


class MailFollowers(models.Model):
    _inherit = "mail.followers"

    team_id = fields.Many2one("project.team", string="Project Team")


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    no_of_hours = fields.Integer(string="No. of Hour(s) a Day", default=8)
    no_of_days = fields.Integer(string="No. of Day(s) a Week", default=5)

    @api.constrains('no_of_hours', 'no_of_days', 'attendance_ids')
    def _check_days_hours(self):
        week_days = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }

        for resource in self:
            res = {}
            current_hours = resource.no_of_hours
            current_days = resource.no_of_days

            if current_days > 7 or current_days < 1:
                raise ValidationError(_(
                    "No. of Days should be in between 1 - 7."))

            for attendance in resource.attendance_ids:
                day = attendance.dayofweek
                diff = abs(attendance.hour_from - attendance.hour_to)
                if day not in res:
                    res[day] = diff
                else:
                    res[day] += diff

            if current_days and len(res) > current_days:
                raise ValidationError(_(
                    "You can not Add Working Hour(s) for more than %s\
                    different days.") % current_days)

            for day, hours in sorted(list(res.items())):
                if current_hours and hours > current_hours:
                    raise ValidationError(_(
                        "Invalid hours for %s!\n\nWorking hours per day should\
                        not be greater than %s.") % (week_days[int(day)],
                                                     current_hours))
