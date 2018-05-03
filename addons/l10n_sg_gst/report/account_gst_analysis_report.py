# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import time

from flectra import api, models, _
from flectra.exceptions import UserError
from flectra.addons.l10n_sg_gst.report.account_gst5_report import taxes_query, \
    gst_taxes_query

class AccountGstAnalysisView(models.AbstractModel):
    _name = 'report.l10n_sg_gst.account_gst_analysis_view'

    def compute_total(self, tax_browse, taxes_result, group_name):
        amount = 0.00
        for i in range(len(taxes_result)):
            if tax_browse.id == taxes_result[i][0] and tax_browse.tax_group_id in group_name:
                    amount += taxes_result[i][1]
        return abs(amount) or 0.00

    def get_common_data(self, tax_ids, data):
        result = []
        gst_perc = standard_total = zeroed_total = exempted_total = mes_total \
            = out_scope_total = gross_amount_total = gst_amount_total = 0.0
        group_name = tax_ids.mapped('tax_group_id')
        for tax_browse in tax_ids:
            date_start = data['form']['date_from']
            date_stop = data['form']['date_to']
            self._cr.execute(taxes_query % (
            date_stop, date_start, self.env.user.company_id.id))
            texes_result = self._cr.fetchall()
            self._cr.execute(gst_taxes_query % (date_stop, date_start))
            gst_taxes_result = self._cr.fetchall()
            if tax_browse.amount_type == 'fixed':
                gst_perc = tax_browse.amount * 100
            elif tax_browse.amount_type == 'percent':
                gst_perc = tax_browse.amount
            elif tax_browse.amount_type == 'group':
                tax = [(6, 0, tax_browse.children_tax_ids)]
                gst_perc += tax.amount
            else:
                gst_perc = tax_browse.amount

            standard = self.compute_total(tax_browse,
                    gst_taxes_result, [self.env.ref("l10n_sg.tax_group_7")])
            standard_total += standard
            zeroed = self.compute_total(tax_browse,
                    gst_taxes_result, [self.env.ref("l10n_sg.tax_group_0")])
            zeroed_total += zeroed
            exempted = self.compute_total(tax_browse,
                    gst_taxes_result, [self.env.ref("l10n_sg.tax_group_exempted")])
            exempted_total += exempted
            mes = self.compute_total(tax_browse,
                    gst_taxes_result, [self.env.ref("l10n_sg.tax_group_mes")])
            mes_total += mes
            out_scope = self.compute_total(tax_browse,
                    gst_taxes_result, [self.env.ref("l10n_sg.tax_group_oos")])
            out_scope_total += out_scope

            gross_amount = self.compute_total(tax_browse,
                    gst_taxes_result, group_name)
            gross_amount_total += gross_amount
            gst_amount = self.compute_total(tax_browse,
                    texes_result, group_name)
            gst_amount_total += gst_amount
            result.append({
                'tax_name': tax_browse.name,
                'standard': standard,
                'zeroed': zeroed,
                'exempted': exempted,
                'mes': mes,
                'out_scope': out_scope,
                'gross_amount': gross_amount,
                'gst_amount': gst_amount,
                'gst_perc': gst_perc,
            })
        total = {
            'standard_total': standard_total,
            'zeroed_total': zeroed_total,
            'exempted_total': exempted_total,
            'mes_total': mes_total,
            'out_scope_total': out_scope_total,
            'gross_amount_total': gross_amount_total,
            'gst_amount_total': gst_amount_total
        }
        return result, total

    def get_purchase_data(self, data):
        tax_ids = self.env['account.tax'].search([('type_tax_use', '=', 'purchase')])
        return self.get_common_data(tax_ids, data)


    def get_sale_data(self, data):
        tax_ids = self.env['account.tax'].search([('type_tax_use', '=', 'sale')])
        return self.get_common_data(tax_ids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get(
                'active_model'):
            raise UserError(_(
                "Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        purchase_data, purchase_total = self.get_purchase_data(data)
        sale_data, sale_total = self.get_sale_data(data)
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'time': time,
            'get_sale_data': sale_data,
            'get_purchase_data': purchase_data,
            'get_sale_standard_total': sale_total['standard_total'],
            'get_sale_zeroed_total': sale_total['zeroed_total'],
            'get_sale_exempted_total': sale_total['exempted_total'],
            'get_sale_mes_total': sale_total['mes_total'],
            'get_sale_out_scope_total': sale_total['out_scope_total'],
            'get_sale_gross_amount_total': sale_total['gross_amount_total'],
            'get_sale_gst_amount_total': sale_total['gst_amount_total'],
            'get_purchase_standard_total': purchase_total['standard_total'],
            'get_purchase_zeroed_total': purchase_total['zeroed_total'],
            'get_purchase_exempted_total': purchase_total['exempted_total'],
            'get_purchase_mes_total': purchase_total['mes_total'],
            'get_purchase_out_scope_total': purchase_total['out_scope_total'],
            'get_purchase_gross_amount_total': purchase_total[
                'gross_amount_total'],
            'get_purchase_gst_amount_total': purchase_total[
                'gst_amount_total'],
        }
