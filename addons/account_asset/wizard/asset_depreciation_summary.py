# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, fields, models
from datetime import datetime
from flectra.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AssetDepreciationWizard(models.TransientModel):
    _name = "asset.depreciation.wizard"

    @api.depends('start_date')
    def _compute_get_end_date(self):
        if self.start_date:
            last_day = self.env.user.company_id.fiscalyear_last_day
            last_month = self.env.user.company_id.fiscalyear_last_month
            date = datetime.strptime(self.start_date, DF).date()
            if date.month <= 3 and date.day < 31:
                year = date.year
            else:
                year = date.year + 1
            date = date.replace(month=last_month, day=last_day, year=year)
            self.end_date = datetime.strftime(date, '%Y-%m-%d')

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(compute='_compute_get_end_date', store=True)

    @api.multi
    def print_depreciation_lines(self):
        data = {'form': self.read(['start_date', 'end_date'])[0]}
        return self.env.ref(
            'account_asset.asset_depreciation_report').report_action(
            self,
            data=data,
            config=False)
