# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_hr_timesheet = fields.Boolean("Timesheets")
    module_rating_project = fields.Boolean(string="Rating on Tasks")
    group_subtask_project = fields.Boolean("Sub-tasks", implied_group="project.group_subtask_project")
