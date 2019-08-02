# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.tools.misc import formatLang


class AccountDiscountConfig(models.Model):
    _name = 'account.discount.config'

    group_id = fields.Many2one('res.groups', 'Groups', required=True)
    fix_amount = fields.Float('Fix Amount', required=True)
    percentage = fields.Float('Percentage', required=True)

    @api.constrains('group_id')
    def _check_already_exist(self):
        check_name = self.search(
            [('id', '!=', self.id),
             ('group_id.name', '=', self.group_id.name)])
        if check_name:
            raise ValueError(
                _("Assigned group already exist!"))

    @api.constrains('fix_amount')
    def _check_fix_amount_value(self):
        config_data = self.env['res.config.settings'].get_values()
        fix_amount = config_data.get('global_discount_fix_invoice_amount')
        if config_data.get('global_discount_invoice_apply') \
                and fix_amount < self.fix_amount:
            raise ValueError(
                _("Fix amount (%s) is greater than configuration Amount (%s)!"
                  ) % (formatLang(self.env, self.fix_amount, digits=2),
                       formatLang(self.env,
                                  config_data.get('global_discount_fix_invoice_amount'),
                                  digits=2)))

    @api.constrains('percentage')
    def _check_percentage(self):
        if self.percentage < 0 or self.percentage > 100:
            raise ValueError(_("Percentage should be between 0% to 100%!"))
        config_data = self.env['res.config.settings'].get_values()
        percentage = config_data.get('global_discount_percentage_invoice')
        if config_data.get('global_discount_invoice_apply') \
                and percentage < self.percentage:
            raise ValueError(
                _("Percentage (%s) is greater than configuration Percentage "
                  "(%s)!") % (
                    formatLang(self.env, self.percentage, digits=2),
                    formatLang(self.env,
                               config_data.get('global_discount_percentage_invoice'),
                               digits=2)))
