# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import fields, models, _, api
from datetime import datetime
from flectra.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class SaleAssetWizard(models.TransientModel):
    _name = "sale.asset.wizard"

    asset_id = fields.Many2one("account.asset.asset", string="Asset")
    asset_category_id = fields.Many2one("account.asset.category",
                                        string="Asset Category", required=True)
    depreciated_amount = fields.Float(string="Depreciated Amount")
    product_id = fields.Many2one("product.product", string="Product",
                                 required=True)
    partner_id = fields.Many2one("res.partner", string="Customer",
                                 required=True)
    sale_value = fields.Float(string="Sale Value")
    sale_date = fields.Date(
        string="Date", default=lambda self: datetime.today(),
        required=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        date = False
        for line in self.asset_id.depreciation_line_ids:
            if line.move_check:
                date = line.depreciation_date
        if not date:
            date = self.asset_id.depreciation_line_ids and self.asset_id.depreciation_line_ids[0].depreciation_date or self.asset_id.date
        self.sale_date = date

    @api.onchange('sale_date')
    def onchange_sale_date(self):
        if self.sale_date:
            amount = 0.0
            last_date = False
            for line in self.asset_id.depreciation_line_ids:
                if self.sale_date >= line.depreciation_date:
                    amount += line.amount
                    last_date = line.depreciation_date
                else:
                    if not last_date:
                        last_date = line.depreciation_date
                    if line.sequence == 1:
                        last_date = self.asset_id.date
                    days, total_days = \
                        self.get_days(last_date, self.sale_date)
                    amount += (line.amount * days) / total_days
                    break
            self.depreciated_amount = amount
            self.sale_value = self.asset_id.value - amount

    @api.constrains('sale_date')
    def _check_sale_date(self):
        if self.sale_date:
            posted_line_ids = \
                self.env['account.asset.depreciation.line'].search([
                    ('asset_id', '=', self.asset_id.id),
                    ('move_check', '=', True)])
            if posted_line_ids:
                last_depreciation_date = \
                    datetime.strptime(
                        posted_line_ids[-1].depreciation_date, DF).date()
                if self.sale_date < str(last_depreciation_date):
                    raise ValueError(_("Sale date must be greater than last "
                                       "Depreciated date!"))
            if self.sale_date < self.asset_id.date:
                raise ValueError(_("Sale date must be greater than "
                                   "Date of Asset!"))

    @api.multi
    def get_days(self, last_date, sale_date):
        last_depreciation_date = datetime.strptime(last_date, DF).date()
        sale_date = datetime.strptime(sale_date, DF).date()
        delta = sale_date - last_depreciation_date
        year = last_depreciation_date.year
        total_days = (year % 4) and 365 or 366
        if self.asset_id.depreciation_line_ids and self.asset_id.depreciation_line_ids[0].depreciation_date > str(sale_date):
            depreciation_date = datetime.strptime(self.asset_id.depreciation_line_ids[0].depreciation_date, DF).date()
            asset_date = datetime.strptime(self.asset_id.date, DF).date()
            delta_day = depreciation_date - asset_date
            total_days = delta_day.days
            delta = sale_date - asset_date
        return delta.days, total_days

    @api.multi
    def last_line_info(self):
        last_date = False
        last_line = False
        sale_date = self.sale_date
        for line in self.asset_id.depreciation_line_ids:
            if sale_date >= line.depreciation_date:
                line.create_move(post_move=True)
                last_date = line.depreciation_date
                last_line = line
            else:
                last_line = line
                if not last_date:
                    last_date = line.depreciation_date
                if line.sequence == 1:
                    last_date = self.asset_id.date
                break
        days, total_days = self.get_days(last_date, sale_date)
        amount = (last_line.amount * days) / total_days
        return last_line, amount

    def sale_asset(self):
        if self.asset_id:
            self.asset_id.write({
                'state': 'close',
                'sale_date': self.sale_date,
            })
            last_line, amount = self.last_line_info()
            if last_line and amount:
                depreciated_value = \
                    (last_line.depreciated_value - last_line.amount) + amount
                last_line.update({
                    'depreciation_date': self.sale_date,
                    'amount': amount,
                    'depreciated_value': depreciated_value,
                    'remaining_value':
                        last_line.begin_value - depreciated_value,
                    })
                last_line.create_move(post_move=True)
                if last_line.move_id.state == 'draft':
                    last_line.move_id.post()
            for line in self.asset_id.depreciation_line_ids:
                if not line.move_check:
                    line.unlink()
            self.create_sale_invoice()

    def create_sale_invoice(self):
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        journal_id = self.env['account.journal'].search(
            [('code', '=', 'INV')])
        account_id = self.env['account.account'].search(
            [('internal_type', '=', 'receivable')])
        tax_ids = self.product_id.supplier_taxes_id.ids

        invoice_id = invoice_obj.create({
            'partner_id': self.partner_id.id,
            'journal_id':
                journal_id and
                journal_id[0].id or
                self.asset_id.category_id.journal_id.id,
            'account_id':
                account_id and
                account_id[0].id or
                self.asset_id.category_id.account_asset_id.id,
            'company_id': self.partner_id.company_id.id,
            'type': 'out_invoice',
            'date_invoice': self.sale_date,
            'payment_term_id':
                self.partner_id.property_supplier_payment_term_id.id,
            'currency_id': self.partner_id.company_id.currency_id.id,
            'asset_id': self.asset_id.id,
            'asset_bool': True
        })
        invoice_line_obj.create({
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'asset_id': self.asset_id.id,
            'asset_category_id': self.asset_id.category_id.id,
            'account_id': self.asset_id.category_id.account_asset_id.id,
            'quantity': 1.0,
            'price_unit': self.sale_value,
            'partner_id': self.partner_id.id,
            'company_id': self.partner_id.company_id.id,
            'invoice_line_tax_ids': tax_ids and [[6, 0, tax_ids]] or False,
            'asset_bool': True,
            'invoice_id': invoice_id.id
        })
        return {
            'name': (_('Invoices')),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'domain': [('asset_id', '=', self.asset_id.id)]
        }
