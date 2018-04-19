# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class AccountCashFlow(models.TransientModel):
    """Credit Notes"""
    # TODO: Add date filters

    _inherit = "account.common.report"
    _name = "account.cash.flow"
    _description = "Cash Flow"

    no_of_year = fields.Integer(string='Previous Period', default=0)

    def _print_report(self, data):
        data['form'].update(self.read(['no_of_year', 'company_id',
                                       'branch_id'])[0])
        landscape = False
        if self.no_of_year > 2:
            landscape = True
        return self.env.ref(
            'account_cash_flow.action_cash_flow_report').with_context(landscape=landscape).report_action(self, data=data)
