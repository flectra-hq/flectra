# Part of Flectra. See LICENSE file for full copyright and licensing details.


from flectra import api, models

VAT_SALE_TYPE = ['local_sale', 'inside_gcc_sale',
                 'outside_gcc_sale', 'designated_zone_sale']
VAT_PURCHASE_TYPE = ['local_purchase', 'inside_gcc_purchase',
                     'outside_gcc_purchase', 'designated_zone_purchase']


class ReportVat201(models.AbstractModel):
    _name = 'report.l10n_ae_extend.vat_201'

    def get_invoice_ids(self, data, invoice_type, vat_type, reverse_charge):
        return self.env['account.invoice'].search([
            ('date_invoice', '<=', data['form']['date_to']),
            ('date_invoice', '>=', data['form']['date_from']),
            ('state', 'in', ['open', 'paid']),
            ('type', 'in', invoice_type),
            ('vat_config_type.vat_type', 'in', vat_type),
            ('reverse_charge', '=', reverse_charge)])

    def get_local_sale(self, data):
        return self.get_invoice_data_for_local(data, ['local_sale'])

    def get_inside_gcc_sale(self, data):
        return self.get_invoice_data_for_local(data, ['inside_gcc_sale'])

    def get_outside_gcc_sale(self, data):
        return self.get_invoice_data_for_local(data, ['outside_gcc_sale'])

    def get_designated_zone_sale(self, data):
        return self.get_invoice_data_for_local(data, VAT_SALE_TYPE)

    def get_total_sale(self, data):
        return self.get_invoice_data_for_local(data, VAT_SALE_TYPE)

    def get_vat_amount(self, tax_ids):
        account_tax_object = self.env['account.tax']
        vat_amount = 0.0
        for tax_line_id in tax_ids:
            tax_id = account_tax_object.search([
                ('name', '=', tax_line_id.name), ('tax_type', '=', 'vat')])
            if tax_id.tax_type != 'vat':
                continue
            vat_amount += tax_line_id.base
        return vat_amount

    def get_tax_amount(self, tax_ids):
        return sum([tax_id.amount for tax_id in tax_ids
                    if tax_id.tax_id.tax_type == 'vat'])

    def get_invoice_data_for_local(self, data, vat_type):
        invoices = self.get_invoice_ids(
            data, ['out_invoice', 'out_refund'], vat_type, False)
        data_dict = {
            'amount': 0.0, 'total_exempted_amount': 0.0,
            'total_exempted_adjustment': 0.0, 'adjustment': 0.0,
            'tax_amount': 0.0, 'return_tax_amount': 0.0,
            'total_zero_amount': 0.0, 'zero_adjustment': 0.0}
        for invoice_id in invoices:
            check_line_vat_tax = 0.0
            tax_amount = self.get_tax_amount(invoice_id.tax_line_ids)
            for line in invoice_id.invoice_line_ids:
                data_dict.update(
                    self.set_zero_exempted_amount(
                        data_dict, invoice_id, line,
                        line.invoice_line_tax_ids))
            check_line_vat_tax += self.get_vat_amount(invoice_id.tax_line_ids)
            if invoice_id.type == 'out_refund':
                data_dict['adjustment'] += check_line_vat_tax
                data_dict['return_tax_amount'] += tax_amount
            else:
                data_dict['amount'] += check_line_vat_tax
                data_dict['tax_amount'] += tax_amount
        return data_dict

    def set_zero_exempted_amount(
            self, data_dict, invoice_id, line, tax_line_ids):
        for tax_id in tax_line_ids:
            if tax_id.amount == 0.0:
                if invoice_id.type in ['out_invoice',  'in_invoice']:
                    data_dict['total_exempted_amount'] += \
                        line.price_subtotal \
                        if tax_id.tax_type == 'exempted' else 0.0
                    data_dict['total_zero_amount'] += \
                        line.price_subtotal \
                        if tax_id.tax_type != 'exempted' else 0.0
                elif invoice_id.type in ['out_refund', 'in_refund']:
                    data_dict['total_exempted_adjustment'] += \
                        line.price_subtotal \
                        if tax_id.tax_type == 'exempted' else 0.0
                    data_dict['zero_adjustment'] += \
                        line.price_subtotal \
                        if tax_id.tax_type != 'exempted' else 0.0
        return data_dict

    def get_invoice_data_for_local_purchase(self, data, vat_type):
        invoices = self.get_invoice_ids(
            data, ['in_invoice', 'in_refund'], vat_type, False)
        return self.get_data(invoices)

    def get_data(self, invoices):
        data_dict = {
            'amount': 0.0, 'total_exempted_amount': 0.0,
            'total_exempted_adjustment': 0.0, 'adjustment': 0.0,
            'tax_amount': 0.0, 'return_tax_amount': 0.0,
            'total_zero_amount': 0.0, 'zero_adjustment': 0.0}
        for invoice_id in invoices:
            check_line_vat_tax = 0.0
            invoice_tax_lines = invoice_id.tax_line_ids
            if invoice_id.reverse_charge:
                invoice_tax_lines = invoice_id.reverse_tax_line_ids
            tax_amount = self.get_tax_amount(invoice_tax_lines)

            for line in invoice_id.invoice_line_ids:
                tax_line_ids = line.invoice_line_tax_ids
                if invoice_id.reverse_charge:
                    tax_line_ids = line.reverse_invoice_line_tax_ids
                data_dict.update(self.set_zero_exempted_amount(
                    data_dict, invoice_id, line, tax_line_ids))
            tax_ids = invoice_id.tax_line_ids
            if invoice_id.reverse_charge:
                tax_ids = invoice_id.reverse_tax_line_ids
            check_line_vat_tax += self.get_vat_amount(tax_ids)
            if invoice_id.type == 'in_refund':
                data_dict['adjustment'] += check_line_vat_tax
                data_dict['return_tax_amount'] += tax_amount
            else:
                data_dict['amount'] += check_line_vat_tax
                data_dict['tax_amount'] += tax_amount
        return data_dict

    def get_local_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(
            data, ['local_purchase'])

    def get_inside_outside_gcc_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(
            data, ['inside_gcc_purchase', 'outside_gcc_purchase'])

    def get_zero_vat_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(
            data, VAT_PURCHASE_TYPE)

    def get_total_purchase(self, data):
        reverse_dict = self.get_reverse_charge_data(data)
        all_type_dict = self.get_invoice_data_for_local_purchase(
            data, VAT_PURCHASE_TYPE)
        all_type_dict['amount'] += \
            reverse_dict['amount'] + all_type_dict['total_zero_amount'] + \
            all_type_dict['total_exempted_amount']
        all_type_dict['tax_amount'] += reverse_dict['tax_amount']
        all_type_dict['return_tax_amount'] += reverse_dict['return_tax_amount']
        all_type_dict['adjustment'] += \
            reverse_dict['adjustment'] + all_type_dict['zero_adjustment'] + \
            all_type_dict['total_exempted_adjustment']
        return all_type_dict

    def get_reverse_charge_data(self, data):
        invoices = self.get_invoice_ids(
            data, ['in_invoice', 'in_refund'], VAT_PURCHASE_TYPE, True)
        return self.get_data(invoices)

    def get_total_vat_due(self, data):
        sale_data = self.get_total_sale(data)
        purchase_data = self.get_total_purchase(data)
        vals = {
            'total_tax_amount':
                (sale_data['tax_amount'] - sale_data['return_tax_amount']
                 ) - (purchase_data['tax_amount'] - purchase_data[
                    'return_tax_amount'])}
        return vals

    @api.model
    def get_report_values(self, docids, data=None):
        currency_id = \
            self.env['res.currency'].browse(data['form']['currency_id'][0])
        return {
            'data': data,
            'currency_name': currency_id.name,
            'get_local_sale': self.get_local_sale(data),
            'get_inside_gcc_sale': self.get_inside_gcc_sale(data),
            'get_outside_gcc_sale': self.get_outside_gcc_sale(data),
            'get_designated_zone_sale': self.get_designated_zone_sale(data),
            'get_total_sale': self.get_total_sale(data),
            'get_local_purchase': self.get_local_purchase(data),
            'get_inside_outside_gcc_purchase':
                self.get_inside_outside_gcc_purchase(data),
            'get_zero_vat_purchase': self.get_zero_vat_purchase(data),
            'get_total_purchase': self.get_total_purchase(data),
            'get_total_vat_due': self.get_total_vat_due(data),
            'get_reverse_charge_data': self.get_reverse_charge_data(data),
            'currency_id': currency_id,
        }
