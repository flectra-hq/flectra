# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api


class ReleasePlanning(models.Model):
    _name = "release.planning"
    _inherit = ['ir.branch.company.mixin', 'mail.thread']

    name = fields.Char(string="Planning Name", track_visibility="onchange")
    release_date = fields.Datetime(
        string="Release Date", track_visibility="onchange")
    sprint_id = fields.Many2one(
        'project.sprint', string="Sprint", track_visibility="onchange")
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')], string="Priority", default='low',
        track_visibility="onchange")
    velocity = fields.Integer(
        related="sprint_id.estimated_velocity", string="Sprint Velocity",
        track_visibility="onchange", store=True)
    task_id = fields.One2many(
        "project.task", "release_planning_id", string="Task", readonly=True)

    @api.onchange('sprint_id')
    def onchange_project(self):
        if self.sprint_id and self.sprint_id.project_id.branch_id:
            self.branch_id = self.sprint_id.project_id.branch_id
