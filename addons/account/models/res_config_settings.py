# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    def _default_fiscalyear_last_day(self):
        return self.env.user.company_id.fiscalyear_last_day or 31

    def _default_fiscalyear_last_month(self):
        return self.env.user.company_id.fiscalyear_last_month or 12


    has_accounting_entries = fields.Boolean(compute='_compute_has_chart_of_accounts')
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", required=True,
        string='Currency', help="Main currency of the company.")
    currency_exchange_journal_id = fields.Many2one(
        'account.journal',
        related='company_id.currency_exchange_journal_id',
        string="Exchange Gain or Loss Journal",
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]",
        help='The accounting journal where automatic exchange differences will be registered')
    has_chart_of_accounts = fields.Boolean(compute='_compute_has_chart_of_accounts', string='Company has a chart of accounts')
    chart_template_id = fields.Many2one('account.chart.template', string='Template',
        domain="[('visible','=', True)]")
    code_digits = fields.Integer(string='# of Digits *', related='company_id.accounts_code_digits', help="No. of digits to use for account code")
    tax_calculation_rounding_method = fields.Selection([
        ('round_per_line', 'Round calculation of taxes per line'),
        ('round_globally', 'Round globally calculation of taxes '),
        ], related='company_id.tax_calculation_rounding_method', string='Tax calculation rounding method')
    group_analytic_accounting = fields.Boolean(string='Analytic Accounting',
        implied_group='analytic.group_analytic_accounting')
    group_warning_account = fields.Boolean(string="Warnings", implied_group='account.group_warning_account')
    group_cash_rounding = fields.Boolean(string="Cash Rounding", implied_group='account.group_cash_rounding')
    module_account_asset = fields.Boolean(string='Assets Management')
    module_account_budget = fields.Boolean(string='Budget Management')
    module_account_payment = fields.Boolean(string='Online Payment')
    default_sale_tax_id = fields.Many2one('account.tax', string="Default Sale Tax",
        company_dependent=True, oldname="default_sale_tax")
    default_purchase_tax_id = fields.Many2one('account.tax', string="Default Purchase Tax",
        company_dependent=True, oldname="default_purchase_tax")
    module_account_plaid = fields.Boolean(string="Plaid Connector")
    module_product_margin = fields.Boolean(string="Allow Product Margin")
    module_l10n_eu_service = fields.Boolean(string="EU Digital Goods VAT")
    module_account_taxcloud = fields.Boolean(string="Account TaxCloud")
    tax_exigibility = fields.Boolean(string='Cash Basis', related='company_id.tax_exigibility')
    tax_cash_basis_journal_id = fields.Many2one('account.journal', related='company_id.tax_cash_basis_journal_id', string="Tax Cash Basis Journal")
    account_hide_setup_bar = fields.Boolean(string='Hide Setup Bar', related='company_id.account_setup_bar_closed',help="Tick if you wish to hide the setup bar on the dashboard")


    fiscalyear_last_day = fields.Integer(related='company_id.fiscalyear_last_day',
        default=lambda self: self._default_fiscalyear_last_day())
    fiscalyear_last_month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')],
        related='company_id.fiscalyear_last_month', default=lambda self: self._default_fiscalyear_last_month())
    period_lock_date = fields.Date(string="Lock Date for Non-Advisers", related='company_id.period_lock_date', help="Only users with the 'Adviser' role can edit accounts prior to and inclusive of this date. Use it for period locking inside an open fiscal year, for example.")
    fiscalyear_lock_date = fields.Date(string="Lock Date", related='company_id.fiscalyear_lock_date', help="No users, including Advisers, can edit accounts prior to and inclusive of this date. Use it for fiscal year locking for example.")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # ONLY FOR v11. DO NOT FORWARD-PORT
        IrDefault = self.env['ir.default'].sudo()
        default_sale_tax_id = IrDefault.get('product.template', "taxes_id", company_id=self.company_id.id or self.env.user.company_id.id)
        default_purchase_tax_id = IrDefault.get('product.template', "supplier_taxes_id", company_id=self.company_id.id or self.env.user.company_id.id)
        res.update(
            default_purchase_tax_id=default_purchase_tax_id[0] if default_purchase_tax_id else False,
            default_sale_tax_id=default_sale_tax_id[0] if default_sale_tax_id else False,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.group_multi_currency:
            self.env.ref('base.group_user').write({'implied_ids': [(4, self.env.ref('product.group_sale_pricelist').id)]})
        """ Set the product taxes if they have changed """
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('product.template', "taxes_id", self.default_sale_tax_id.ids, company_id=self.company_id.id)
        IrDefault.set('product.template', "supplier_taxes_id", self.default_purchase_tax_id.ids, company_id=self.company_id.id)
        """ install a chart of accounts for the given company (if required) """
        if self.chart_template_id and self.chart_template_id != self.company_id.chart_template_id:
            wizard = self.env['wizard.multi.charts.accounts'].create({
                'company_id': self.company_id.id,
                'chart_template_id': self.chart_template_id.id,
                'transfer_account_id': self.chart_template_id.transfer_account_id.id,
                'code_digits': self.code_digits or 6,
                'sale_tax_rate': 15.0,
                'purchase_tax_rate': 15.0,
                'complete_tax_set': self.chart_template_id.complete_tax_set,
                'currency_id': self.currency_id.id,
                'bank_account_code_prefix': self.chart_template_id.bank_account_code_prefix,
                'cash_account_code_prefix': self.chart_template_id.cash_account_code_prefix,
            })
            wizard.onchange_chart_template_id()
            wizard.execute()

    @api.depends('company_id')
    def _compute_has_chart_of_accounts(self):
        self.has_chart_of_accounts = bool(self.company_id.chart_template_id)
        self.chart_template_id = self.company_id.chart_template_id or False
        self.has_accounting_entries = self.env['wizard.multi.charts.accounts'].existing_accounting(self.company_id)

    @api.onchange('module_account_budget')
    def onchange_module_account_budget(self):
        if self.module_account_budget:
            self.group_analytic_accounting = True

    @api.onchange('tax_exigibility')
    def _onchange_tax_exigibility(self):
        res = {}
        tax = self.env['account.tax'].search([
            ('company_id', '=', self.env.user.company_id.id), ('tax_exigibility', '=', 'on_payment')
        ], limit=1)
        if not self.tax_exigibility and tax:
            self.tax_exigibility = True
            res['warning'] = {
                'title': _('Error!'),
                'message': _('You cannot disable this setting because some of your taxes are cash basis. '
                             'Modify your taxes first before disabling this setting.')
            }
        return res

    @api.model
    def create(self, values):
        # Optimisation purpose, saving a res_config even without changing any values will trigger the write of all
        # related values, including the currency_id field on res_company. This in turn will trigger the recomputation
        # of account_move_line related field company_currency_id which can be slow depending on the number of entries
        # in the database. Thus, if we do not explicitely change the currency_id, we should not write it on the company
        # Same for the field `code_digits` which will trigger a write on all the account.account to complete the
        # code the missing characters to complete the desired number of digit, leading to a sql_constraint.
        if ('company_id' in values and 'currency_id' in values):
            company = self.env['res.company'].browse(values.get('company_id'))
            if company.currency_id.id == values.get('currency_id'):
                values.pop('currency_id')
            if company.accounts_code_digits == values.get('code_digits'):
                values.pop('code_digits')
        return super(ResConfigSettings, self).create(values)
