# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api


class Retrospective(models.Model):
    _name = "retrospective"
    _inherit = ['ir.branch.company.mixin', 'mail.thread']

    name = fields.Char(string="Retrospective Name", required=True,
                       track_visibility='onchange')
    retrospective_method_id = fields.Many2one(
        "retrospective.method", string="Retrospective Method",
        track_visibility='onchange')
    scrum_master = fields.Many2one("res.users", string="Scrum Master",
                                   track_visibility='onchange')
    sprint_id = fields.Many2one(
        "project.sprint", string="Sprint", track_visibility='onchange')
    retrospective_line_ids = fields.One2many(
        "retrospective.lines", "retrospective_id",
        string="Retrospective Lines", track_visibility='onchange')
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")

    @api.onchange('sprint_id')
    def on_sprint_id_change(self):
        self.scrum_master = self.sprint_id.team_id.master_id.id

    @api.onchange('sprint_id')
    def onchange_project(self):
        if self.sprint_id and self.sprint_id.project_id.branch_id:
            self.branch_id = self.sprint_id.project_id.branch_id


class RetrospectiveLines(models.Model):
    _name = "retrospective.lines"

    user_id = fields.Many2one("res.users", string="User", readonly=True,
                              required=True,
                              default=lambda self: self.env.user)
    message = fields.Text(string="Message")
    retrospective_id = fields.Many2one("retrospective", string="Retrospective")
