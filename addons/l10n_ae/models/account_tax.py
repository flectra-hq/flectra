# Part of Flectra. See LICENSE file for full copyright and licensing details.


from flectra import fields, models


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    tax_type = fields.Selection([
        ('vat', 'VAT'), ('customs', 'Customs'), ('excise', 'Excise'),
        ('exempted', 'Exempted'), ('other', 'Other')], 'VAT Type')

    def _get_tax_vals(self, company, tax_template_to_tax):
        self.ensure_one()
        res = super(AccountTaxTemplate, self)._get_tax_vals(
            company, tax_template_to_tax)
        res['tax_type'] = self.tax_type
        return res


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_type = fields.Selection([
        ('vat', 'VAT'), ('customs', 'Customs'), ('excise', 'Excise'),
        ('exempted', 'Exempted'), ('other', 'Other')], 'VAT Type')
