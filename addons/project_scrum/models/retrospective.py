# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api


class Retrospective(models.Model):
    _name = "retrospective"
    _description = "Retrospective"
    _inherit = 'mail.thread'

    name = fields.Char(string="Retrospective Name", required=True,
                       tracking=True)
    retrospective_method_id = fields.Many2one(
        "retrospective.method", string="Retrospective Method",
        tracking=True)
    scrum_master = fields.Many2one("res.users", string="Scrum Master",
                                   tracking=True)
    sprint_id = fields.Many2one(
        "project.sprint", string="Sprint", tracking=True)
    retrospective_line_ids = fields.One2many(
        "retrospective.lines", "retrospective_id",
        string="Retrospective Lines", tracking=True)
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")

    @api.onchange('sprint_id')
    def on_sprint_id_change(self):
        self.scrum_master = self.sprint_id.team_id.master_id.id


class RetrospectiveLines(models.Model):
    _name = "retrospective.lines"
    _description = "Retrospective Lines"

    user_id = fields.Many2one("res.users", string="User", readonly=True,
                              required=True,
                              default=lambda self: self.env.user)
    message = fields.Text(string="Message")
    retrospective_id = fields.Many2one("retrospective", string="Retrospective")
