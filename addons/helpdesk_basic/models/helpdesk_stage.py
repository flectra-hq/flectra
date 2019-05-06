# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _order = 'sequence, id'
    _description = 'Helpdesk Stage'

    name = fields.Char('Name', translate=True, required=True)
    description = fields.Text(translate=True)
    fold = fields.Boolean(string='Fold in Kanban')
    stage_type = fields.Selection([('draft', 'Draft'), ('new', 'New'),
                                   ('in_progress', 'In Progress'),
                                   ('done', 'Done')], string='Stage Type', translate=True,
                                  required=True)
    sequence = fields.Integer(default=1)
