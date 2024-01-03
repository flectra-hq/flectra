# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    sms_template_id = fields.Many2one('sms.template', string="SMS Template",
        domain=[('model', '=', 'project.task')],
        help="If set, an SMS Text Message will be automatically sent to the customer when the task reaches this stage.")
