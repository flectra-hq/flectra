# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api


class ProjectTeam(models.Model):
    _name = "project.team"
    _inherit = ['ir.branch.company.mixin', 'mail.thread']
    _description = "Project Team"

    name = fields.Char("Team Name", required=True, track_visibility="onchange")
    strength = fields.Text("Team Strength", track_visibility="onchange")
    member_ids = fields.Many2many("res.users", string="Members")
    master_id = fields.Many2one(
        "res.users", string="Scrum Master", track_visibility="onchange")
    description = fields.Html()
    project_id = fields.Many2one(
        'project.project', string="Project", track_visibility="onchange")

    @api.onchange('project_id')
    def onchange_project(self):
        if self.project_id and self.project_id.branch_id:
            self.branch_id = self.project_id.branch_id
