# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    is_helpdesk = fields.Boolean(string='Use in Helpdesk')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    helpdesk_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')
