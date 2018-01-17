# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    use_replacement = fields.Boolean(string='Replacement')
    replacements_count = fields.Integer(
        compute='_compute_replacements',
        string='Number of replacements')

    def _compute_replacements(self):
        for replace in self:
            if replace.use_replacement:
                rma_ids = self.env['rma.request'].search([
                    ('team_id.id', '=', replace.id)])
                replace.replacements_count = len(rma_ids)
