# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class HelpdeskTeam(models.Model):

    _inherit = 'helpdesk.team'

    project_id = fields.Many2one('project.project', string='Project')
    need_project = fields.Boolean(string='Need Project',
                                  compute="_compute_need_project")

    @api.multi
    def _compute_need_project(self):
        config_data = self.env['res.config.settings'].sudo().get_values()
        for team in self:
            team.need_project = False
            if config_data.get('use_project'):
                team.need_project = True
