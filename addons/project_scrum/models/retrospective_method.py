# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class RetrospectiveMethod(models.Model):
    _name = "retrospective.method"
    _inherit = ['ir.branch.company.mixin', 'mail.thread']
    _description = "Retrospective Implementation for Project Scrum"

    name = fields.Char(
        string="Method Name", required=True, track_visibility='onchange')

    description = fields.Text(
        string="Description", track_visibility='onchange')
