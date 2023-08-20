# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class ProjectTeam(models.Model):
    _name = "project.team"
    _inherit = 'mail.thread'
    _description = "Project Team"

    name = fields.Char("Team Name", required=True, tracking=True)
    strength = fields.Text("Team Strength", tracking=True)
    member_ids = fields.Many2many("res.users", string="Members")
    master_id = fields.Many2one(
        "res.users", string="Scrum Master", tracking=True)
    description = fields.Html()
    project_id = fields.Many2one(
        'project.project', string="Project", tracking=True)
