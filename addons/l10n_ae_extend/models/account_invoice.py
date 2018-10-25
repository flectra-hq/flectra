# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api, _
from flectra.exceptions import Warning


class ReverseAccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'
    _name = 'reverse.account.invoice.tax'


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _default_config_type(self):
        domain = []
        if self._context.get('type', False) in ['out_invoice', 'out_refund']:
            domain = [('journal_id.type', '=', 'sale')]
        elif self._context.get('type', False) in ['in_invoice', 'in_refund']:
            domain = [('journal_id.type', '=', 'purchase')]
        return self.vat_config_type.search(domain, limit=1)

    vat_config_type = fields.Many2one(
        'vat.config.type', 'Vat Type', default=_default_config_type,
        readonly=True, states={'draft': [('readonly', False)]})
    reverse_charge = fields.Boolean(
        'Reverse Charge', readonly=True,
        states={'draft': [('readonly', False)]})
    reverse_tax_line_ids = fields.One2many(
        'reverse.account.invoice.tax', 'invoice_id', string='Tax Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    @api.onchange('vat_config_type')
    def onchange_vat_config_type(self):
        if self.vat_config_type:
            self.journal_id = self.vat_config_type.journal_id.id
            if self.vat_config_type.vat_type == 'designated_zone_purchase':
                fiscal_position_id = self.fiscal_position_id.search(
                    [('name', 'ilike', 'exempt')], limit=1)
                if not fiscal_position_id:
                    fiscal_position_id = self.env.ref('l10n_ae.fp_in_exempted')
                else:
                    fiscal_position_id = fiscal_position_id.id
                self.fiscal_position_id = fiscal_position_id
        else:
            self.journal_id = self._default_journal()

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        super(AccountInvoice, self)._compute_residual()
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        if self.reverse_charge:
            residual = self.residual - self.amount_tax
            self.residual_signed = abs(residual) * sign
            self.residual = abs(residual)

    @api.multi
    def action_invoice_open(self):
        if not self.reverse_charge:
            return super(AccountInvoice, self).action_invoice_open()
        if not self.company_id.rc_vat_account_id:
            raise Warning(_('Define Reverse Charge Account in Company!'))
        list_data = []
        account_tax_obj = self.env['account.tax']
        custom_amount = 0.0
        self.reverse_tax_line_ids = [[6, 0, []]]
        for tax_line in self.tax_line_ids:
            tax_id = account_tax_obj.search([('name', 'ilike', tax_line.name)])
            custom_amount += \
                tax_line.amount_total if tax_id.tax_type == 'customs' else 0.0
            account_id = tax_id.account_id.id
            if self.partner_id.vat:
                account_id = tax_line.account_id.id
            elif tax_id.tax_type == 'vat':
                account_id = self.company_id.vat_expense_account_id.id
            list_data.append((0, 0, {
                'name': tax_line.name,
                'partner_id':
                    self.partner_id.parent_id.id or self.partner_id.id,
                'account_id': account_id,
                'debit': tax_line.amount_total,
                'move_id': False,
                'invoice_id': self.id,
                'tax_line_id': tax_id,
                'quantity': 1,
                }
            ))

        total_tax_amount = self.amount_tax
        reverse_list_data = []
        for tax_line_id in self.tax_line_ids:
            reverse_list_data.append((0, 0, tax_line_id.read()[0]))

        if reverse_list_data:
            self.update({'reverse_tax_line_ids': reverse_list_data})
        for line_id in self.invoice_line_ids:
            line_id.reverse_invoice_line_tax_ids = \
                [[6, 0, line_id.invoice_line_tax_ids.ids]]

        self.invoice_line_ids.update({'invoice_line_tax_ids': [[6, 0, []]]})
        self.update({'tax_line_ids': [[6, 0, []]], 'amount_tax': 0.0})
        res = super(AccountInvoice, self).action_invoice_open()

        for move_line_id in list_data:
            move_line_id[2].update({'move_id': self.move_id.id})
        list_data.append(
            (0, 0, self.get_move_line_vals(total_tax_amount - custom_amount)))
        if custom_amount:
            list_data.append((0, 0, self.get_move_line_vals(custom_amount)))
        self.move_id.state = 'draft'
        self.move_id.line_ids = list_data
        self.move_id.post()
        return res

    @api.multi
    def get_move_line_vals(self, credit):
        return {
            'name': '/',
            'partner_id': self.partner_id.parent_id.id or self.partner_id.id,
            'account_id': self.company_id.rc_vat_account_id.id,
            'credit': credit,
            'move_id': self.move_id.id,
            'invoice_id': self.id,
            'quantity': 1,
        }

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id:
            self.vat_config_type = self.purchase_id.vat_config_type.id
            self.reverse_charge = self.purchase_id.reverse_charge
        return super(AccountInvoice, self).purchase_order_change()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        self.journal_id = self.vat_config_type.journal_id.id
        return res

    @api.onchange('state', 'partner_id', 'invoice_line_ids',
                  'vat_config_type', 'reverse_charge')
    def _onchange_allowed_purchase_ids(self):
        result = super(AccountInvoice, self)._onchange_allowed_purchase_ids()
        result['domain']['purchase_id'] += [
            ('vat_config_type', '=', self.vat_config_type.id),
            ('reverse_charge', '=', self.reverse_charge)]
        return result

    @api.onchange('fiscal_position_id')
    def _onchange_fiscal_position_id(self):
        if self.fiscal_position_id:
            for line in self.invoice_line_ids:
                line._set_taxes()

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None,
               date=None, description=None, journal_id=None):
        result = super(AccountInvoice, self).refund(
            date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        result.write({
            'vat_config_type': result.refund_invoice_id.vat_config_type.id})
        if result.refund_invoice_id.type == 'in_invoice':
            result.write(
                {'reverse_charge': result.refund_invoice_id.reverse_charge})
        if result.type == 'in_refund' \
                and result.refund_invoice_id.reverse_charge:
            for index, line_id in enumerate(result.invoice_line_ids):
                line_id.invoice_line_tax_ids = [[
                    6, 0, result.refund_invoice_id.invoice_line_ids[
                        index].reverse_invoice_line_tax_ids.ids]]
            result._onchange_invoice_line_ids()
        return result


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    reverse_invoice_line_tax_ids = fields.Many2many(
        'account.tax', string='Taxes', copy=False)

    @api.v8
    def get_invoice_line_account(self, type, product, fpos, company):
        return self.invoice_id.vat_config_type.\
            journal_id.default_debit_account_id
