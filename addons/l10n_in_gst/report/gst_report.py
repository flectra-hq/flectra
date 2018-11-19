# Part of Flectra See LICENSE file for full copyright and licensing details.

from io import BytesIO
from datetime import datetime
from operator import itemgetter
from itertools import groupby
import xlsxwriter
from functools import reduce
from flectra import api, models, _


class GSTR1Report(models.AbstractModel):
    _name = "gst.report"

    def open_document(self, options, **post):
        action_model = options.get('object')
        invoice = self.env['account.invoice'].browse(int(options.get('id')))
        view_name = 'view_move_form'
        if action_model == 'account.invoice' and invoice:
            if invoice.type in ('in_refund', 'in_invoice'):
                view_name = 'invoice_supplier_form'
            elif invoice.type in ('out_refund', 'out_invoice'):
                view_name = 'invoice_form'
            view_id = self.env['ir.model.data'].get_object_reference(
                'account', view_name)[1]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'tree',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': action_model,
                'view_id': view_id,
                'res_id': invoice.id,
            }

    def _prepare_taxable_line_data(self, line, inv, igst_amount, cgst_amount,
                                   sgst_amount, cess_amount, rate, tax):
        return {
            'id': inv.id,
            'taxable_value': line.price_subtotal,
            'cess_amount': cess_amount,
            'rate': rate,
            'place_supply': ('%s-%s') % (
                inv.partner_id.state_id.l10n_in_tin,
                inv.partner_id.state_id.name),
            'tax_id': tax.id,
            'igst': igst_amount,
            'cgst': cgst_amount,
            'sgst': sgst_amount,
            'lines': [{
                'igst_amount': igst_amount,
                'sgst_amount': sgst_amount,
                'cgst_amount': cgst_amount,
                'product_name': line.product_id.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'amount': line.price_subtotal,
                'cess': cess_amount
            }]
        }

    def _update_tax_values(self, data, line, cess_amount, igst_amount,
                           cgst_amount, sgst_amount):
        if data and line:
            data['taxable_value'] += line.price_subtotal
            data['cess_amount'] += cess_amount
            data['igst'] += igst_amount
            data['cgst'] += cgst_amount
            data['sgst'] += sgst_amount
            data['lines'].append({
                'igst_amount': igst_amount,
                'sgst_amount': sgst_amount,
                'cgst_amount': cgst_amount,
                'product_name': line.product_id.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'amount': line.price_subtotal,
                'cess': cess_amount
            })

    def _update_inv_line_details(self, line, inv, document_type):
        line.update({
            'inv_no': inv.number,
            'refund_invoice_id': inv.refund_invoice_id.id or '',
            'refund_inv_no': inv.refund_invoice_id.number or '',
            'refund_date_invoice': inv.refund_invoice_id and datetime.strptime(
                    inv.refund_invoice_id.date_invoice, '%Y-%m-%d').strftime(
                '%d %b %y') or '',
             'document_type': document_type,
            'reason': inv.name or '',
            'pre_gst': inv.date <= inv.company_id.gst_introduce_date and
            'Y' or 'N',
            'inv_date': datetime.strptime(
                inv.date_invoice, '%Y-%m-%d').strftime('%d %b %y'),
        })

    def get_data_common(self, data, start=None, end=None, **post):
        """
        Common Method for get_data_*(...)
        1. get_data_b2b(...), 2. get_data_b2cl(...), 3. get_data_b2cs(...),
        4. get_data_cdnr(...), 5. get_data_cdnur(...)
        """
        result = []
        acc_invoice = self.env['account.invoice']
        acc_tax = self.env['account.tax']
        common_domain = [('date', '>=', data['from_date']),
                         ('date', '<=', data['to_date']),
                         ('state', 'not in', ['draft', 'cancel']),
                         ('company_id', '=', data['company_id'])]
        final_invoice_ids = type_domain = refund_domain = final_inv_domain = []
        if data['summary_type'] == 'gstr1':
            type_domain = [('type', '=', 'out_invoice')]
            refund_domain = [('type', '=', 'out_refund')]
            cdnur_domain = [('gst_invoice', 'in', ['b2cl', 'b2cs']),
                            ('vat', '=', False)]
        elif data['summary_type'] == 'gstr2':
            type_domain = [('type', '=', 'in_invoice')]
            refund_domain = [('type', '=', 'in_refund')]
            cdnur_domain = [('gst_invoice', '=', 'b2bur'),
                            ('vat', '=', False)]
        if post.get('gst_invoice') == 'b2b':
            final_inv_domain = common_domain + type_domain + [(
                'gst_invoice', '=', 'b2b')]
        if post.get('gst_invoice') == 'b2bur':
            final_inv_domain = common_domain + type_domain + [
                ('gst_invoice', '=', 'b2bur')]
        if post.get('gst_invoice') == 'b2cl':
            final_inv_domain = common_domain + type_domain + [(
                'gst_invoice', '=', 'b2cl')]
        if post.get('gst_invoice') == 'b2cs':
            final_inv_domain = common_domain + type_domain + [
                ('gst_invoice', '=', 'b2cs')]
        if post.get('gst_invoice') == 'cdnr':
            final_inv_domain = common_domain + refund_domain + [
                ('gst_invoice', '=', 'b2b'), ('vat', '!=', False)]
        if post.get('gst_invoice') == 'cdnur':
            final_inv_domain = common_domain + refund_domain + cdnur_domain
        final_invoice_ids = acc_invoice.search(final_inv_domain)
        for inv in final_invoice_ids:
            inv_data_list = []
            tax_list = []
            document_type = None
            gst_invoice_type = None

            if post.get('gst_invoice') in ['cdnr', 'cdnur']:
                if inv.type == 'out_refund' and inv.amount_total < \
                        inv.refund_invoice_id.amount_total:
                    document_type = 'C'
                elif inv.type == 'in_refund' and inv.amount_total < \
                        inv.refund_invoice_id.amount_total:
                    document_type = 'D'
                else:
                    document_type = 'R'
            if post.get('gst_invoice') == 'cdnur':
                gst_invoice_type = dict(inv.fields_get(
                    ['gst_invoice'])['gst_invoice']['selection']).get(
                    inv.gst_invoice)

            for line in inv.invoice_line_ids:
                cess_amount = igst_amount = cgst_amount = sgst_amount = 0.0
                if inv.reverse_charge:
                    tax_lines = line.reverse_invoice_line_tax_ids
                else:
                    tax_lines = line.invoice_line_tax_ids
                if tax_lines:
                    price_unit = line.price_unit * (
                        1 - (line.discount or 0.0) / 100.0)
                    taxes = tax_lines.compute_all(
                        price_unit, line.invoice_id.currency_id,
                        line.quantity, line.product_id,
                        line.invoice_id.partner_id)['taxes']
                    for tax_data in taxes:
                        tax = acc_tax.browse(tax_data['id'])
                        if tax.tax_group_id.name == 'Cess':
                            cess_amount += tax_data['amount']
                        if tax.tax_group_id.name == 'IGST' and (post.get(
                                'gst_invoice') != 'b2b' or
                                tax_data['amount'] > 0):
                            igst_amount += tax_data['amount']
                        if tax.tax_group_id.name == 'CGST' and (post.get(
                                'gst_invoice') != 'b2b' or tax_data[
                                'amount'] > 0):
                            cgst_amount += tax_data['amount']
                        if tax.tax_group_id.name == 'SGST' and (post.get(
                                'gst_invoice') != 'b2b' or tax_data[
                                'amount'] > 0):
                            sgst_amount += tax_data['amount']

                    for tax in tax_lines:
                        rate = 0
                        if tax.id not in tax_list:
                            if tax.tax_group_id.name == 'IGST' \
                                    and tax.amount > 0:
                                rate = tax.amount
                            else:
                                for child in tax.children_tax_ids:
                                    if child.tax_group_id.name == 'IGST' \
                                            and child.amount > 0:
                                        rate = child.amount
                                    elif child.tax_group_id.name in ['SGST',
                                                                     'CGST'] \
                                            and child.amount > 0:
                                        rate += child.amount
                            if post.get('gst_invoice') == 'cdnur':
                                if tax.tax_group_id.name == 'IGST':
                                    rate = tax.amount
                                else:
                                    for child in tax.children_tax_ids:
                                        if child.tax_group_id.name == 'CGST':
                                            rate += child.amount
                                        if child.tax_group_id.name == 'SGST':
                                            rate += child.amount
                            if tax.tax_group_id.name != 'Cess':
                                line_data = self._prepare_taxable_line_data(
                                    line, inv, igst_amount, cgst_amount,
                                    sgst_amount, cess_amount, rate, tax)
                                if post.get('gst_invoice') in \
                                        ['b2b', 'b2cl', 'b2cs', 'b2bur']:
                                    line_data.update({
                                        'partner': inv.company_id.name,
                                        'ecommerce_gstin':
                                            inv.e_commerce_partner_id and
                                            inv.e_commerce_partner_id.vat or
                                            '',
                                    })

                                line_data.update({
                                    'gstin_partner': inv.vat,
                                    'value': inv.amount_total,
                                })

                                if post.get('gst_invoice') in \
                                        ['b2b', 'b2cl', 'b2bur']:
                                    line_data.update({
                                        'inv_no': inv.number,
                                        'date': datetime.strptime(
                                            inv.date_invoice,
                                            '%Y-%m-%d').strftime('%d %b %y'),
                                    })

                                if post.get('gst_invoice') == 'b2b':
                                    line_data.update({
                                        'inv_type': 'Regular',
                                        'reverse_charge': 'Y' if inv.reverse_charge else 'N',
                                    })
                                if post.get('gst_invoice') == 'b2bur':
                                    supply_type = dict(inv.fields_get(
                                        ['partner_location'])[
                                        'partner_location']['selection']).get(
                                        inv.partner_location)
                                    line_data.update({
                                        'supplier': inv.partner_id.name,
                                        'supply_type': supply_type if
                                        inv.partner_location !=
                                        'inter_country' else 0.0,
                                    })
                                if post.get('gst_invoice') == 'b2cs':
                                    line_data.update({
                                        'inv_no': inv.number,
                                        'type':
                                            inv.e_commerce_partner_id and
                                            'E' or 'OE',
                                    })

                                if post.get('gst_invoice') in ['cdnr',
                                                               'cdnur']:
                                    self._update_inv_line_details(
                                        line_data, inv, document_type)

                                if post.get('gst_invoice') == 'cdnur':
                                    line_data.update({
                                        'gst_invoice_type': gst_invoice_type,
                                    })

                                tax_list.append(tax.id)
                                inv_data_list.append(line_data)
                                result.append(line_data)
                        elif tax.id in tax_list:
                            for data in inv_data_list:
                                if data['tax_id'] == tax.id:
                                    self._update_tax_values(
                                        data, line, cess_amount,
                                        igst_amount, cgst_amount,
                                        sgst_amount)
        # pagination records display
        if start and end:
            return {
                'data': result[start - 1: end],
                'length': len(result)
            }
        else:
            return result

    @api.multi
    def get_data_b2b(self, data, start=None, end=None, **post):
        """ B2B data as per month, year and company selection:
        - Registered customer invoices details (without reverse charge
        applicability)
        - Registered supplier invoices details (with reverse charge
        applicability)
        """
        post['gst_invoice'] = 'b2b'
        post['summary_type'] = data['summary_type']
        return self.get_data_common(data=data, start=start, end=end, **post)

    @api.multi
    def get_data_b2bur(self, data, start=None, end=None, **post):
        """ B2BUR data as per month, year and company selection:
        - Unegistered supplier invoices details (with reverse charge
        applicability)
        """
        post['gst_invoice'] = 'b2bur'
        post['summary_type'] = data['summary_type']
        return self.get_data_common(data=data, start=start, end=end, **post)

    @api.multi
    def get_data_b2cl(self, data, start=None, end=None, **post):
        """ B2CL data as per month, year and company selection:
        - Unregistered customers' invoices details where:
            (1) The place of supply is outside the state where company is
            registered
            (2) Total invoice value is more than company's B2CL limit
        """
        post['gst_invoice'] = 'b2cl'
        post['summary_type'] = data['summary_type']
        return self.get_data_common(data=data, start=start, end=end, **post)

    @api.multi
    def get_data_b2cs(self, data, start=None, end=None, **post):
        """ B2CS data as per month, year and company selection:
        - Unregistered customers' invoices details where:
            (1) Intra-State: any value
            (2) Inter-State: Total invoice value is less than company's B2CS
            limit
        """
        post['gst_invoice'] = 'b2cs'
        post['summary_type'] = data['summary_type']
        return self.get_data_common(data=data, start=start, end=end, **post)

    @api.multi
    def get_data_cdnr(self, data, start=None, end=None, **post):
        """ CDNR data as per month, year and company selection:
        - Refunds of B2B type invoices
         """
        post['gst_invoice'] = 'cdnr'
        post['summary_type'] = data['summary_type']
        return self.get_data_common(data=data, start=start, end=end, **post)

    @api.multi
    def get_data_cdnur(self, data, start=None, end=None, **post):
        """ CDNUR data as per month, year and company selection:
        - Refunds of Export and B2CL type invoices
         """
        post['gst_invoice'] = 'cdnur'
        post['summary_type'] = data['summary_type']
        return self.get_data_common(data=data, start=start, end=end, **post)

    @api.multi
    def get_data_hsn(self, data, start=None, end=None, **post):
        """ HSN data as per month, year and company selection.
        """
        result = []
        list_product = []
        acc_tax = self.env['account.tax']
        invoice_domain = [('invoice_id.date', '>=', data['from_date']),
            ('invoice_id.date', '<=', data['to_date']),
            ('invoice_id.state', 'not in', ['draft', 'cancel']),
            ('invoice_id.company_id', '=', data['company_id'])]
        if data['summary_type'] == 'gstr1':
            invoice_domain += [('invoice_id.type', '=', 'out_invoice'),
            ('invoice_id.gst_invoice', 'in', ('b2b', 'b2cl', 'b2cs'))]
        if data['summary_type'] == 'gstr2':
            invoice_domain += [('invoice_id.type', '=', 'in_invoice'), (
            'invoice_id.gst_invoice', 'in', ('b2b', 'b2bur'))]
        hsn_invoice_line_ids = self.env['account.invoice.line'].search(
                invoice_domain)
        for line in hsn_invoice_line_ids:
            igst_amount = cgst_amount = sgst_amount = cess_amount = 0.0
            if line.invoice_id.reverse_charge:
                tax_lines = line.reverse_invoice_line_tax_ids
            else:
                tax_lines = line.invoice_line_tax_ids
            if tax_lines:
                price_unit = line.price_unit * (
                    1 - (line.discount or 0.0) / 100.0)
                taxes = tax_lines.compute_all(
                    price_unit, line.invoice_id.currency_id,
                    line.quantity, line.product_id,
                    line.invoice_id.partner_id)['taxes']
                for tax in taxes:
                    tax_id = acc_tax.browse(tax['id'])
                    if tax_id.tax_group_id.name == 'Cess':
                        cess_amount += tax['amount']
                    elif tax_id.tax_group_id.name == 'IGST':
                        igst_amount += tax['amount']
                    elif tax_id.tax_group_id.name == 'CGST':
                        cgst_amount += tax['amount']
                    elif tax_id.tax_group_id.name == 'SGST':
                        sgst_amount += tax['amount']
            if line.product_id.id not in list_product:
                hsn_data = {
                    'product_name': line.product_id.product_tmpl_id.name,
                    'hsn': line.product_id.l10n_in_hsn_code,
                    'value': (line.price_subtotal + igst_amount +
                              cgst_amount + sgst_amount + cess_amount),
                    'taxable_value': line.price_subtotal,
                    'cess_amount': cess_amount,
                    'igst_amt': igst_amount,
                    'cgst_amt': cgst_amount,
                    'sgst_amt': sgst_amount,
                    'uqc': ("%s-%s") % (line.product_id.uom_id.code,
                                        line.product_id.uom_id.name),
                    'product_main_id': line.product_id.id,
                    'total_qty': line.quantity}
                list_product.append(line.product_id.id)
                result.append(hsn_data)
            elif line.product_id.id in list_product:
                for l in result:
                    if l['product_main_id'] == line.product_id.id:
                        l['value'] += line.price_subtotal + igst_amount + \
                            cgst_amount + sgst_amount + cess_amount
                        l['taxable_value'] += line.price_subtotal
                        l['cess_amount'] += cess_amount
                        l['igst_amt'] += igst_amount
                        l['cgst_amt'] += cgst_amount
                        l['sgst_amt'] += sgst_amount
                        l['total_qty'] += line.quantity
        # pagination records display
        if start and end:
            return {
                'data': result[start - 1: end],
                'length': len(result)
            }
        else:
            return result

    def get_data_common_summary(self, result, **post):
        """
        Common Method for get_data_*_summary(...)
        1. get_data_b2b_summary(...), 2. get_data_b2cl_summary(...),
        3. get_data_b2cs_summary(...), 4. get_data_cdnr_summary(...),
        5. get_data_cdnur_summary(...),
        """
        summary = {}
        if result:
            invoices_list = []
            recepient_list = []
            taxable_value_total = cess_amt_total = igst_amount = cgst_amount =\
                sgst_amount = 0.0
            no_of_recepient = 0

            for inv in result:
                if inv.get('reverse_charge') != 'Y':
                    taxable_value_total += float(inv['taxable_value'])
                    igst_amount += float(inv['igst'])
                    sgst_amount += float(inv['sgst'])
                    cgst_amount += float(inv['cgst'])

                if post.get('gst_invoice') == 'b2b':
                    if inv['reverse_charge'] == 'N':
                        cess_amt_total += inv['cess_amount']
                    recepient_list.append(inv['gstin_partner'])
                if post.get('gst_invoice') in ['b2cl', 'b2cs']:
                    cess_amt_total += inv['cess_amount']
                if post.get('gst_invoice') in ['cdnr', 'cdnur']:
                    if inv['document_type'] == 'C':
                        cess_amt_total -= inv['cess_amount']
                    else:
                        cess_amt_total += inv['cess_amount']
                    recepient_list.append(inv['gstin_partner'])
                invoices_list.append(inv['inv_no'])

            if post.get('gst_invoice') in ['b2b', 'cdnr', 'cdnur']:
                no_of_recepient = len(set(recepient_list))

            no_of_invoices = len(set(invoices_list))
            invoices_list = set(invoices_list)
            invoice_value = 0.0
            for invoice_id in invoices_list:
                ids = self.env['account.invoice'].search(
                    [('number', '=', invoice_id), ('reverse_charge', '=', False)])
                invoice_value += ids.amount_total
            summary.update({
                "no_of_invoices": no_of_invoices,
                "taxable_value_total": taxable_value_total,
                "cess_amt_total": cess_amt_total,
                "invoice_value": invoice_value,
                "igst_amount": igst_amount,
                "sgst_amount": sgst_amount,
                "cgst_amount": cgst_amount,
            })
            if post.get('gst_invoice') == 'b2b':
                if post.get('summary_type') == 'gstr1':
                    name = _("B2B Invoices - 4A, 4B, 4C, 6B, 6C")
                elif post.get('summary_type') == 'gstr2':
                    name = _("Supplies From Registered Suppliers B2B - 3,4A")
                summary.update({
                    "name": name,
                    "action": "get_data_b2b",
                    "no_of_recepient": no_of_recepient,
                })
            if post.get('gst_invoice') == 'b2bur':
                summary.update({
                    "name": _("Supplies From Unregistered Suppliers B2BUR - "
                              "4C"),
                    "action": "get_data_b2bur",
                })
            if post.get('gst_invoice') == 'b2cl':
                summary.update({
                    "name": _("B2C(Large) Invoices - 5A, 5B"),
                    "action": "get_data_b2cl",
                })
            if post.get('gst_invoice') == 'b2cs':
                summary.update({
                    "name": _("B2C(Small) Details - 7"),
                    "action": "get_data_b2cs",
                })
            if post.get('gst_invoice') == 'cdnr':
                if post.get('summary_type') == 'gstr1':
                    name = _("Credit/Debit Notes(Registered) - 9B")
                elif post.get('summary_type') == 'gstr2':
                    name = _("Debit/Credit Notes(Registered) - 6C")
                summary.update({
                    "name": name,
                    "action": "get_data_cdnr",
                    "no_of_recepient": no_of_recepient,
                })
            if post.get('gst_invoice') == 'cdnur':
                if post.get('summary_type') == 'gstr1':
                    name = _("Credit/Debit Notes(Unregistered) - 9B")
                elif post.get('summary_type') == 'gstr2':
                    name = _("Debit/Credit Notes(Unregistered) - 6C")
                summary.update({
                    "name": name,
                    "action": "get_data_cdnur",
                    "no_of_recepient": no_of_recepient,
                })
        return summary

    def get_data_b2b_summary(self, data, **post):
        """ B2B summary details and fetch required data """
        post['gst_invoice'] = 'b2b'
        post['summary_type'] = data['summary_type']
        result = self.get_data_b2b(data=data, **post)
        return self.get_data_common_summary(result=result, **post)

    def get_data_b2bur_summary(self, data, **post):
        post['gst_invoice'] = 'b2bur'
        post['summary_type'] = data['summary_type']
        result = self.get_data_b2bur(data=data, **post)
        return self.get_data_common_summary(result=result, **post)

    def get_data_b2cl_summary(self, data, **post):
        """ B2CL summary details and fetch required data """
        post['gst_invoice'] = 'b2cl'
        post['summary_type'] = data['summary_type']
        result = self.get_data_b2cl(data=data, **post)
        return self.get_data_common_summary(result=result, **post)

    def get_data_b2cs_summary(self, data, **post):
        """ B2CS summary details and fetch required data """
        post['gst_invoice'] = 'b2cs'
        post['summary_type'] = data['summary_type']
        result = self.get_data_b2cs(data=data, **post)
        return self.get_data_common_summary(result=result, **post)

    def get_data_cdnr_summary(self, data, **post):
        """ CDNR summary details and fetch required data """
        post['gst_invoice'] = 'cdnr'
        post['summary_type'] = data['summary_type']
        result = self.get_data_cdnr(data=data, **post)
        return self.get_data_common_summary(result=result, **post)

    def get_data_cdnur_summary(self, data, **post):
        """ CDNUR summary details and fetch required data """
        post['gst_invoice'] = 'cdnur'
        post['summary_type'] = data['summary_type']
        result = self.get_data_cdnur(data=data, **post)
        return self.get_data_common_summary(result=result, **post)

    def get_data_hsn_summary(self, data, **post):
        """ HSN summary details and fetch required data """
        result = self.get_data_hsn(data, **post)
        summary = {}
        value_total = 0.0
        no_of_hsn = 0
        taxable_value_total = value_total = 0.0
        cess_amt_total = cgst_total = igst_total = sgst_total = 0.0
        for inv in result:
            value_total += inv['value']
            sgst_total += inv['sgst_amt']
            cgst_total += inv['cgst_amt']
            igst_total += inv['igst_amt']
            if inv['hsn']:
                no_of_hsn += 1
            taxable_value_total += inv['taxable_value']
            cess_amt_total += inv['cess_amount']
        name = ''
        if data['summary_type'] == 'gstr1':
            name = _("HSN-Wise Summary of outward Supplies - 12")
        elif data['summary_type'] == 'gstr2':
            name = _("HSN-Wise Summary of inward Supplies - 13")
        summary = {
            "name": name,
            "no_of_invoices": "",
            "no_of_hsn": no_of_hsn,
            "taxable_value_total": taxable_value_total,
            "cess_amt_total": cess_amt_total,
            "action": "get_data_hsn",
            "value_total": value_total,
            "sgst_amount": sgst_total,
            "cgst_amount": cgst_total,
            "igst_amount": igst_total
        }
        return summary

    def get_gstr_summary(self, data, flag=None, **post):
        """ GSTR1 Summary """
        summary = {
            'summary': [],
            'companies': {},
            'summary_type': data.get("summary_type") and data[
                'summary_type'] or '',
        }
        b2b_summary = self.get_data_b2b_summary(data=data, **post)
        b2bur_summary = self.get_data_b2bur_summary(data=data, **post)
        b2cl_summary = self.get_data_b2cl_summary(data=data, **post)
        b2cs_summary = self.get_data_b2cs_summary(data=data, **post)
        cdnr_summary = self.get_data_cdnr_summary(data=data, **post)
        cdnur_summary = self.get_data_cdnur_summary(data=data, **post)
        hsn_summary = self.get_data_hsn_summary(data=data, **post)
        if b2b_summary:
            summary['summary'].append(b2b_summary)
        if b2bur_summary and data.get("summary_type") == "gstr2":
            summary['summary'].append(b2bur_summary)
        if b2cl_summary:
            summary['summary'].append(b2cl_summary)
        if b2cs_summary:
            summary['summary'].append(b2cs_summary)
        if cdnr_summary:
            summary['summary'].append(cdnr_summary)
        if cdnur_summary:
            summary['summary'].append(cdnur_summary)
        if hsn_summary:
            summary['summary'].append(hsn_summary)
        res_company = self.env['res.company'].search(
            [('gst_type', 'in', ['regular', 'volunteer'])])
        if res_company:
            for company in res_company:
                summary['companies'].update({
                    company.id: company.name,
                })
        if flag:
            return summary
        else:
            return summary['summary']

    def cell_format(self, workbook, **post):
        """ Define cell formats """
        return {
            'header_cell_format': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'locked': True, 'align': 'center', 'text_wrap': True,
                 'bg_color': '#e5b7a2', 'bottom': 1}),
            'header_cell_format_help': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'locked': True, 'align': 'center', 'text_wrap': True,
                 'font_color': '#ff0000', 'bottom': 1, 'underline': True}),
            'borederd_header_cell_format': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'align': 'center', 'text_wrap': True, 'top': 1,
                 'bottom': 1, 'left': 1, 'right': 1, 'bold': True,
                 'bg_color': '#2a6cb7', 'font_color': '#ffffff'}),
            'regular_cell_format': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'text_wrap': True}),
            'regular_cell_format_center': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'text_wrap': True}),
            'regular_cell_format_right': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'text_wrap': True, 'align': 'right'}),
            'borederd_header_cell_format_count': workbook.add_format({
                'font_name': 'Times New Roman', 'font_size': 11,
                'text_wrap': True, 'align': 'right'
            }),
            'borederd_header_cell_format_right': workbook.add_format({
                'font_name': 'Times New Roman', 'font_size': 11,
                'align': 'right', 'text_wrap': True, 'top': 1, 'bottom': 1,
                'left': 1, 'right': 1, 'bold': True
            }).set_num_format('0.00'),
            'regular_cell_format_date': workbook.add_format(
                {'font_name': 'Times New Roman', 'font_size': 11,
                 'text_wrap': True, 'num_format': 'dd-mmm-yy',
                 'align': 'center'})}

    def set_summary_header(self, worksheet, summary_label, total_cols, row,
                           col, cell_format):
        for col_no in range(0, total_cols):
            if col_no == 0:
                worksheet.write(row, col, summary_label,
                                cell_format['borederd_header_cell_format'])
            elif col_no == (total_cols - 1):
                worksheet.write(row, col + col_no, 'HELP',
                                cell_format['header_cell_format_help'])
            else:
                worksheet.write(row, col + col_no, '',
                                cell_format['regular_cell_format'])

    def write_data_worksheet_header(self, worksheet, header_list, cell_format,
                                    row, col):
        """
        Common method to write data into all the worksheets.
        :param worksheet: selected worksheet object
        :param header_list: list of all the values or headers to be added
        :param cell_format: cell format of the perticular cell
        :param row: row number
        :param col: column number
        :param summary: dictionary in case summary value and invoice value
        :return:
        """
        count = 0
        for header in header_list:
            worksheet.write(row, col + count, header, cell_format)
            count += 1

    def write_data_worksheet_values(self, worksheet, values, row, col):

        count = 0
        for values_dict in values:
            worksheet.write(row, col + count, values_dict['value'],
                            values_dict['format'])
            count += 1

    def sheet_b2b(self, data, workbook, **post):
        """ Generate excel sheet for 'b2b' data """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('b2b')
        workbook.add_format({'locked': 1})
        worksheet.protect()
        worksheet.set_column(0, 20, 20)
        inv_ids_b2b = self.get_data_b2b(data=data, **post)

        # Calculation of header
        summary = self.get_data_b2b_summary(data=data, **post)

        # formatting
        row = 0
        # summary header
        self.set_summary_header(worksheet, 'Summary For B2B(4)', 11,
                                0, 0, cell_format)
        row += 1
        col = 0
        # set summary sub header
        header_list = ["No. of Recipients",  "No. of Invoices", " ",
                       "Total Invoice Value", " ", " ", " ", " ", " ",
                       "Total Taxable Value", "Total Cess"]
        self.write_data_worksheet_header(worksheet, header_list,
                                         cell_format[
                                             'borederd_header_cell_format'],
                                         row, col)
        row += 1

        col = 0
        if summary:
            summary_value = [{
                'value': summary['no_of_recepient'],
                'format': cell_format['borederd_header_cell_format_count']}, {
                'value': summary['no_of_invoices'],
                'format': cell_format['borederd_header_cell_format_count']}, {
                'value': " ",
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': summary['invoice_value'],
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': " ",
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': " ",
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': " ",
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': " ",
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': " ",
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': summary['taxable_value_total'],
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': summary['cess_amt_total'],
                'format': cell_format['borederd_header_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, summary_value, row,
                                             col)
        row += 1

        worksheet.set_row(3, 15)
        row = 3
        col = 0
        # set main invoice header
        invoice_header = ["GSTIN/UIN of Recipient", "Invoice Number",
                          "Invoice date", "Invoice Value", "Place Of Supply",
                          "Reverse Charge", "Invoice Type", "E-Commerce GSTIN",
                          "Rate", "Taxable Value", "Cess Amount"]
        self.write_data_worksheet_header(
            worksheet, invoice_header, cell_format[
                'header_cell_format'], row, col)
        row += 1
        col = 0
        for inv in inv_ids_b2b:
            inv_value = [{
                'value': inv['gstin_partner'],
                'format': cell_format['regular_cell_format']},
                {'value': inv['inv_no'],
                 'format': cell_format['regular_cell_format']},
                {'value': datetime.strptime(inv['date'], '%d %b %y'),
                 'format': cell_format['regular_cell_format_date']},
                {'value': inv['value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['place_supply'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['reverse_charge'],
                 'format': cell_format['regular_cell_format_center']},
                {'value': inv['inv_type'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['ecommerce_gstin'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['rate'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['taxable_value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cess_amount'] if inv['cess_amount'] > 0.0 else
                 '',
                 'format': cell_format['regular_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def sheet_b2cl(self, data, workbook, **post):
        """ Generate excel sheet for 'b2cl' data """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('b2cl')
        workbook.add_format({'locked': 1})
        worksheet.set_column(0, 20, 20)
        worksheet.protect()
        inv_ids_b2cl = self.get_data_b2cl(data=data, **post)
        # Calculation of header
        summary = self.get_data_b2cl_summary(data=data, **post)
        row = 0
        # summary header
        self.set_summary_header(worksheet, 'Summary For B2CL(5)', 8, 0, 0,
                                cell_format)
        row += 1
        col = 0
        # set summary sub header
        header_list = ["No. of Invoices", " ", "Total Invoice Value", " ",
                       " ", "Total Taxable Value", "Total Cess", " "]
        self.write_data_worksheet_header(
            worksheet, header_list, cell_format[
                'borederd_header_cell_format'], row, col)
        row += 1
        col = 0
        if summary:
            summary_value = [{
                'value': summary['no_of_invoices'],
                'format': cell_format['borederd_header_cell_format_count']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['invoice_value'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['taxable_value_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['cess_amt_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, summary_value, row,
                                             col)
        row += 1
        worksheet.set_row(3, 15)
        row = 3
        col = 0
        # set main invoice header
        invoice_header = ["Invoice Number", "Invoice date", "Invoice Value",
                          "Place Of Supply", "Rate", "Taxable Value",
                          "Cess Amount", "E-Commerce GSTIN"]
        self.write_data_worksheet_header(
            worksheet, invoice_header, cell_format[
                'header_cell_format'], row, col)
        row += 1
        for inv in inv_ids_b2cl:
            inv_value = [{
                'value': inv['inv_no'],
                'format': cell_format['regular_cell_format']},
                {'value': datetime.strptime(inv['date'], '%d %b %y'),
                 'format': cell_format['regular_cell_format_date']},
                {'value': inv['value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['place_supply'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['rate'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['taxable_value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cess_amount'] if inv['cess_amount'] > 0.0
                 else 0.0,
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['ecommerce_gstin'],
                 'format': cell_format['regular_cell_format']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def _groupby_b2cs_inv(self, invoices):
        keys = ['place_supply', 'rate']

        return [reduce(lambda a,b: {
            "place_supply":a["place_supply"],
            "rate": a['rate'], "type": a['type'],
            "taxable_value":a["taxable_value"]+b["taxable_value"],
            "cess_amount":a["cess_amount"]+b["cess_amount"],
            "ecommerce_gstin":a["ecommerce_gstin"]},list(g))
            for k, g in groupby(sorted(invoices, key=itemgetter(
                *keys)), key=itemgetter(*keys))
        ]


    def sheet_b2cs(self, data, workbook, **post):
        """ Generate excel sheet for 'b2cs' data """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('b2cs')
        workbook.add_format({'locked': 1})
        worksheet.set_column(0, 20, 20)
        worksheet.protect()
        inv_ids_b2cs = self.get_data_b2cs(data=data, **post)
        b2cs_data = self._groupby_b2cs_inv(inv_ids_b2cs)
        # Calculation of header
        summary = self.get_data_b2cs_summary(data=data, **post)
        row = 0
        # summary header
        self.set_summary_header(worksheet, 'Summary For B2CS(7)', 6, 0, 0,
                                cell_format)
        row += 1
        col = 0
        # set summary sub header
        header_list = [" ", " ", " ", "Total Taxable Value", "Total Cess", " "]
        self.write_data_worksheet_header(
            worksheet, header_list, cell_format[
                'borederd_header_cell_format'], row, col)
        row += 1
        col = 0
        if summary:
            summary_value = ['', '', '', summary['taxable_value_total'],
                             summary['cess_amt_total'], '']
            self.write_data_worksheet_header(
                worksheet, summary_value,
                cell_format['borederd_header_cell_format_right'],
                row, col)

        row += 1
        worksheet.set_row(3, 15)
        row = 3
        col = 0
        # set main invoice header
        invoice_header = ["Type", "Place Of Supply", "Rate", "Taxable Value",
                          "Cess Amount", "E-Commerce GSTIN"]
        self.write_data_worksheet_header(
            worksheet, invoice_header, cell_format[
                'header_cell_format'], row, col)
        row += 1
        for inv in b2cs_data:
            inv_value = [{
                'value': inv['type'],
                'format': cell_format['regular_cell_format']},
                {'value': inv['place_supply'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['rate'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['taxable_value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cess_amount'] if inv['cess_amount'] > 0.0
                 else 0.0,
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['ecommerce_gstin'],
                 'format': cell_format['regular_cell_format']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def sheet_b2bur(self, data, workbook, **post):
        """ Generate excel sheet for 'b2cl' data """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('b2bur')
        workbook.add_format({'locked': 1})
        worksheet.set_row(0, 30)
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 20, 20)
        worksheet.protect()
        inv_ids_b2bur = self.get_data_b2bur(data=data, **post)

        # Calculation of header
        summary = self.get_data_b2bur_summary(data=data, **post)

        # formatting
        row = 0
        # summary header
        self.set_summary_header(worksheet,
                                'Summary of Supplies From Unregistered '
                                'Suppliers B2BUR(4B)', 12, 0, 0, cell_format)
        row += 1
        col = 0
        # set summary sub header
        header_list = [" ", "No. of Invoices", " ", "Total Invoice Value",
                       " ", " ", " ", "Total Taxable Value",
                       "Total Integrated Tax", "Total Central Tax",
                       "Total State/UT Tax", "Total Cess"]
        self.write_data_worksheet_header(worksheet, header_list, cell_format[
            'borederd_header_cell_format'], row, col)
        row += 1
        col = 0
        if summary:
            summary_value = [{
                'value': '',
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': summary['no_of_invoices'],
                'format': cell_format['borederd_header_cell_format_count']
                }, {
                'value': '',
                'format': cell_format['borederd_header_cell_format_right']
                }, {
                'value': summary['invoice_value'],
                'format': cell_format['borederd_header_cell_format_right']
                }, {
                'value': '',
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': '',
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': '',
                'format': cell_format['borederd_header_cell_format_right']}, {
                'value': summary['taxable_value_total'],
                'format': cell_format['borederd_header_cell_format_right']
                }, {
                'value': summary['igst_amount'],
                'format': cell_format['borederd_header_cell_format_right']
                }, {
                'value': summary['cgst_amount'],
                'format': cell_format['borederd_header_cell_format_right']
                }, {
                'value': summary['sgst_amount'],
                'format': cell_format['borederd_header_cell_format_right']
                }, {
                'value': summary['cess_amt_total'],
                'format': cell_format['borederd_header_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, summary_value, row,
                                             col)
        row += 1

        worksheet.set_row(3, 15)
        row = 3
        col = 0
        # set main invoice header
        invoice_header = ['Supplier Name', 'Invoice Number', 'Invoice Date',
                          'Invoice Value', 'Place Of Supply', 'Supply Type',
                          'Rate', 'Taxable Value', 'Integrated Tax Amount',
                          'Central Tax Amount', 'State/UT Tax Amount',
                          'Cess Amount']
        self.write_data_worksheet_header(worksheet, invoice_header,
                                         cell_format['header_cell_format'],
                                         row, col)
        row += 1

        for inv in inv_ids_b2bur:
            inv_value = [{
                'value': inv['supplier'],
                'format': cell_format['regular_cell_format']
                }, {
                'value': inv['inv_no'],
                'format': cell_format['regular_cell_format']
                }, {
                'value': datetime.strptime(inv['date'], '%d %b %y'),
                'format': cell_format['regular_cell_format_date']
                }, {
                'value': inv['value'],
                'format': cell_format['regular_cell_format_right']
                }, {
                'value': inv['place_supply'],
                'format': cell_format['regular_cell_format']
                }, {
                'value': inv['supply_type'],
                'format': cell_format['regular_cell_format']
                }, {
                'value': inv['rate'],
                'format': cell_format['regular_cell_format_right']
                }, {
                'value': inv['taxable_value'],
                'format': cell_format['regular_cell_format_right']
                }, {
                'value': inv['igst'] if inv['igst'] > 0.0 else 0.0,
                'format': cell_format['regular_cell_format_right']}, {
                'value': inv['cgst'] if inv['cgst'] > 0.0 else 0.0,
                'format': cell_format['regular_cell_format_right']}, {
                'value': inv['sgst'] if inv['sgst'] > 0.0 else 0.0,
                'format': cell_format['regular_cell_format_right']}, {
                'value': inv['cess_amount'] if inv['cess_amount'] > 0.0 else
                '',
                'format': cell_format['regular_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def sheet_cdnr(self, data, workbook, **post):
        """ Generate excel sheet for 'cdnr' data """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('cdnr')
        workbook.add_format({'locked': 1})
        worksheet.set_column(0, 20, 25)
        worksheet.protect()
        inv_ids_cdnr = self.get_data_cdnr(data=data, **post)
        row = 0
        # Calculation of header
        summary = self.get_data_cdnr_summary(data=data, **post)
        # summary header
        self.set_summary_header(worksheet, 'Summary For CDNR(9B)', 13, 0, 0,
                                cell_format)
        row += 1
        col = 0
        # set summary sub header
        header_list = ["No. of Recipients", "No. of Invoices", " ",
                       'No. of Notes/Vouchers', " ", " ", " ", " ", " ", "",
                       "Total Taxable Value", "Total Cess", " "]
        self.write_data_worksheet_header(
            worksheet, header_list, cell_format[
                'borederd_header_cell_format'], row, col)
        row += 1
        col = 0
        if summary:
            summary_value = [{
                'value': summary['no_of_recepient'],
                'format': cell_format['borederd_header_cell_format_count']},
                {'value':  summary['no_of_invoices'],
                 'format':cell_format['borederd_header_cell_format_count']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['no_of_invoices'],
                 'format': cell_format['borederd_header_cell_format_count']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['invoice_value'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['taxable_value_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['cess_amt_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, summary_value, row,
                                             col)
        row += 1
        col = 0
        # set main invoice header
        invoice_header = ["GSTIN/UIN of Recipient",
                          'Invoice/Advance Receipt Number',
                          'Invoice/Advance Receipt date',
                          'Note/Refund Voucher Number',
                          'Note/Refund Voucher date',
                          'Document Type',
                          'Reason For Issuing document', "Place Of Supply",
                          'Note/Refund Voucher Value',
                          "Rate", "Taxable Value", "Cess Amount", 'Pre GST']
        self.write_data_worksheet_header(
            worksheet, invoice_header, cell_format[
                'header_cell_format'], row, col)
        row += 1
        col = 0
        for inv in inv_ids_cdnr:
            inv_value = [{
                'value': inv['gstin_partner'],
                'format': cell_format['regular_cell_format']},
                {'value': inv['refund_inv_no'],
                 'format': cell_format['regular_cell_format']},
                {'value':  inv['refund_date_invoice'] and datetime.strptime(inv['refund_date_invoice'],
                                            '%d %b %y') or '',
                 'format': cell_format['regular_cell_format_date']},
                {'value': inv['inv_no'],
                 'format': cell_format['regular_cell_format']},
                {'value': datetime.strptime(inv['inv_date'], '%d %b %y'),
                 'format': cell_format['regular_cell_format_date']},
                {'value': inv['document_type'],
                 'format': cell_format['regular_cell_format_center']},
                {'value': inv['reason'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['place_supply'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['rate'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['taxable_value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cess_amount'] if inv['cess_amount'] > 0.0 else
                 '',
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['pre_gst'],
                 'format': cell_format['regular_cell_format_center']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def sheet_cdnur(self, data, workbook, **post):
        """ Generate excel sheet for 'cdnur' data """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('cdnur')
        workbook.add_format({'locked': 1})
        worksheet.set_column(0, 20, 25)
        worksheet.protect()
        inv_ids_cdnur = self.get_data_cdnur(data=data, **post)

        # Calculation of header
        summary = self.get_data_cdnr_summary(data=data, **post)

        # formatting
        row = 0
        # summary header
        self.set_summary_header(worksheet, 'Summary For CDNUR(9B)', 13, 0, 0,
                                cell_format)
        row += 1
        col = 0
        # set summary sub header
        header_list = ['', 'No. of Notes/Vouchers', '', '', 'No. of Invoices',
                       '', '', '', 'Total Note Value', '',
                       "Total Taxable Value", "Total Cess", '']
        self.write_data_worksheet_header(
            worksheet, header_list, cell_format[
                'borederd_header_cell_format'], row, col)
        row += 1
        col = 0
        if summary:
            summary_value = [{
                'value': '',
                'format': cell_format['borederd_header_cell_format_right']},
                {'value':  summary['no_of_invoices'],
                 'format':cell_format['borederd_header_cell_format_count']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['no_of_invoices'],
                 'format': cell_format['borederd_header_cell_format_count']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['invoice_value'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['taxable_value_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['cess_amt_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, summary_value, row,
                                             col)
        row = 3
        col = 0
        # set main invoice header
        invoice_header = ['UR Type', 'Note/Refund Voucher Number',
                          'Note/Refund Voucher date', 'Document Type',
                          'Invoice/Advance Receipt Number',
                          'Invoice/Advance Receipt date',
                          'Reason For Issuing document', "Place Of Supply",
                          'Note/Refund Voucher Value', "Rate", "Taxable Value",
                          "Cess Amount", 'Pre GST', ]
        self.write_data_worksheet_header(worksheet, invoice_header,
                                         cell_format['header_cell_format'],
                                         row, col)
        row += 1
        col = 0
        for inv in inv_ids_cdnur:
            inv_value = [{
                'value': inv['gst_invoice_type'],
                'format': cell_format['regular_cell_format_center']},
                {'value': inv['inv_no'],
                 'format': cell_format['regular_cell_format']},
                {'value': datetime.strptime(inv['inv_date'], '%d %b %y'),
                 'format': cell_format['regular_cell_format_date']},
                {'value': inv['document_type'],
                 'format': cell_format['regular_cell_format_center']},
                {'value': inv['refund_inv_no'],
                 'format': cell_format['regular_cell_format']},
                {'value': datetime.strptime(inv['refund_date_invoice'],
                                            '%d %b %y'),
                 'format': cell_format['regular_cell_format_date']},
                {'value': inv['reason'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['place_supply'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['rate'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['taxable_value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cess_amount'] if
                 inv['cess_amount'] > 0.0 else 0.0,
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['pre_gst'],
                 'format': cell_format['regular_cell_format_center']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def sheet_hsn(self, data, workbook, **post):
        """
         Generate excel sheet for 'hsn' Data
        :param data:
        :param workbook:
        :param post:
        :return:
        """
        cell_format = self.cell_format(workbook=workbook, **post)
        worksheet = workbook.add_worksheet('hsn')
        workbook.add_format({'locked': 1})
        worksheet.set_column(0, 20, 20)
        worksheet.protect()
        inv_ids_hsn = self.get_data_hsn(data=data, **post)

        # Calculation of header
        summary = self.get_data_hsn_summary(data=data, **post)

        # formatting
        row = 0
        # summary header
        self.set_summary_header(worksheet, 'Summary For HSN(12)', 10, 0, 0,
                                cell_format)
        row += 1
        # total summary header
        col = 0
        summary_header = ['No. of HSN', '', '', '', 'Total Value',
                          'Total Taxable Value', 'Total Integrated Tax',
                          'Total Central Tax', 'Total State/UT Tax',
                          'Total Cess']
        self.write_data_worksheet_header(
            worksheet, summary_header, cell_format[
                'borederd_header_cell_format'], row, col)
        row += 1

        col = 0
        if summary:
            summary_value = [{
                'value': summary['no_of_hsn'],
                'format': cell_format['borederd_header_cell_format_count']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': '',
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['value_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['taxable_value_total'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['igst_amount'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['cgst_amount'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['sgst_amount'],
                 'format': cell_format['borederd_header_cell_format_right']},
                {'value': summary['cess_amt_total'],
                 'format': cell_format['borederd_header_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, summary_value, row,
                                             col)
        worksheet.set_row(3, 15)
        row = 3
        col = 0
        # insert hsn main header
        hsn_header = ['HSN', 'Description', 'UQC', 'Total Quantity',
                      'Total Value', 'Taxable Value', 'Integrated Tax Amount',
                      'Central Tax Amount', 'State/UT Tax Amount',
                      'Cess Amount']
        self.write_data_worksheet_header(worksheet, hsn_header, cell_format[
            'header_cell_format'], row, col)
        row += 1
        col = 0
        # product wise hsn lines
        for inv in inv_ids_hsn:
            inv_value = [{
                'value': inv['hsn'],
                'format': cell_format['regular_cell_format_center']},
                {'value': inv['product_name'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['uqc'],
                 'format': cell_format['regular_cell_format']},
                {'value': inv['total_qty'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['taxable_value'],
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['igst_amt'] if inv['igst_amt'] > 0.0 else '',
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cgst_amt'] if inv['cgst_amt'] > 0.0 else '',
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['sgst_amt'] if inv['sgst_amt'] > 0.0 else '',
                 'format': cell_format['regular_cell_format_right']},
                {'value': inv['cess_amount'] if inv['cess_amount'] > 0.0 else
                 '',
                 'format': cell_format['regular_cell_format_right']}]
            self.write_data_worksheet_values(worksheet, inv_value, row, col)
            row += 1

    def write_data_into_sheets(self, data, response=False, **post):
        output_stream = BytesIO()
        workbook = xlsxwriter.Workbook(output_stream, {'in_memory': True})
        # b2b
        self.sheet_b2b(data=data['form'], workbook=workbook, **post)
        if data['form'].get('summary_type') == 'gstr1':
            # b2cl
            self.sheet_b2cl(data=data['form'], workbook=workbook, **post)

            # b2cs
            self.sheet_b2cs(data=data['form'], workbook=workbook, **post)
        elif data['form'].get('summary_type') == 'gstr2':
            self.sheet_b2bur(data=data['form'], workbook=workbook, **post)
        # cdnr
        self.sheet_cdnr(data=data['form'], workbook=workbook, **post)

        # cdnur
        self.sheet_cdnur(data=data['form'], workbook=workbook, **post)

        # hsn
        self.sheet_hsn(data=data['form'], workbook=workbook, **post)
        workbook.close()
        output_stream.seek(0)
        if response:
            response.stream.write(output_stream.read())
        output_stream.close()

    @api.multi
    def print_report(self, values, flag=None, response=None, **post):
        """ Export GSTR1 excel report """
        if flag:
            data = {'form': values}
        else:
            data = {
                'form': {
                    'from_date': self.from_date, 'to_date': self.to_date,
                    'company_id':
                        self.company_id and self.company_id.id or False,
                }
            }
        self.write_data_into_sheets(data, response, **post)
