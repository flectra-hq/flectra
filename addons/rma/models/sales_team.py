# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    use_return = fields.Boolean(string='Return')
    returns_count = fields.Integer(
        compute='_compute_returns',
        string='Number of returns')

    def _compute_returns(self):
        for return_req in self:
            if return_req.use_return:
                rma_ids = self.env['rma.request'].search([
                    ('team_id.id', '=', return_req.id)])
                return_req.returns_count = len(rma_ids)
