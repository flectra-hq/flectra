from flectra import models, _
from flectra.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('bj_syscebnl')
    def _get_bj_syscebnl_template_data(self):
        return {
            'name': _('SYSCEBNL for Associations'),
            'parent': 'syscebnl',
            'code_digits': '6',
        }

    @template('bj_syscebnl', 'res.company')
    def _get_bj_syscebnl_res_company(self):
        company_values = super()._get_syscebnl_res_company()
        company_values[self.env.company.id].update(
            {
                'account_fiscal_country_id': 'base.bj',
                'account_sale_tax_id': 'syscebnl_tva_sale_18',
                'account_purchase_tax_id': 'syscebnl_tva_purchase_18',
            }
        )
        return company_values

    @template('bj_syscebnl', 'account.account')
    def _get_bj_syscebnl_account_account(self):
        return self._parse_csv('bj_syscebnl', 'account.account', module='l10n_syscohada')
