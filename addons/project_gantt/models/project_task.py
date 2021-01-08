from flectra import fields, models


class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    progress = fields.Integer(string='Progress')
