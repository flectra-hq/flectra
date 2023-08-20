# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class ReleasePlanning(models.Model):
    _name = "release.planning"
    _description = "Release Planing"
    _inherit = 'mail.thread'

    name = fields.Char(string="Planning Name", tracking=True)
    release_date = fields.Datetime(
        string="Release Date", tracking=True)
    sprint_id = fields.Many2one(
        'project.sprint', string="Sprint", tracking=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')], string="Priority", default='low',
        tracking=True)
    velocity = fields.Integer(
        related="sprint_id.estimated_velocity", string="Sprint Velocity",
        tracking=True, store=True)
    task_id = fields.One2many(
        "project.task", "release_planning_id", string="Task")
