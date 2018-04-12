# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_group = fields.Selection([('standard_rates', 'Standard Rates'),
                                  ('zeroed', 'Zeroed'),
                                  ('exempted', 'Exempted'), ('MES', 'MES'),
                                  ('out_of_scope', 'Out Of Scope')],
                                 string='Tax Group')


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    tax_group = fields.Selection([('standard_rates', 'Standard Rates'),
                                  ('zeroed', 'Zeroed'),
                                  ('exempted', 'Exempted'), ('MES', 'MES'),
                                  ('out_of_scope', 'Out Of Scope')],
                                 string='Tax Group')

    @api.multi
    def _get_tax_vals(self, company, tax_template_to_tax):
        res = super(AccountTaxTemplate, self)._get_tax_vals(
            company, tax_template_to_tax)
        if self.tax_group:
            res.update({'tax_group': self.tax_group})
        return res
