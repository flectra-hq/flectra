# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import time
from datetime import datetime

from flectra import api, models, _
from flectra.exceptions import UserError

taxes_query = """SELECT l.tax_line_id, \
            COALESCE(SUM(l.debit-l.credit), 0)
            FROM account_move as m, account_move_line as l
            WHERE (l.move_id=m.id) AND \
            ((((l.date <= '%s')  AND  \
            ((l.date >= '%s')))  AND  \
            (m.state = 'posted'))  AND  \
            (l.company_id = '%s')) \
            GROUP BY l.tax_line_id \
            """
gst_taxes_query = """SELECT r.account_tax_id,\
                COALESCE(SUM(l.debit-l.credit), 0)
                 FROM account_move as m, account_move_line as l\
                 INNER JOIN account_move_line_account_tax_rel r ON \
                 (l.id = r.account_move_line_id)\
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)\
                 WHERE (l.move_id=m.id) AND \
                 ((l.date <= '%s')  AND  \
                 ((l.date >= '%s') AND  \
                (m.state = 'posted'))\
                 ) group by r.account_tax_id"""

class AccountGst5Report(models.AbstractModel):
    _name = 'report.l10n_sg_gst.account_gst5_report_view'

    def get_boolean_data(self, data):
        res = {}
        if data['form']:
            res = {
                'answer1_yes': data['form']['answer1_yes'] and '◉' or '○',
                'answer1_no': data['form']['answer1_no'] and '◉' or '○',
                'answer2_yes': data['form']['answer2_yes'] and '◉' or '○',
                'answer2_no': data['form']['answer2_no'] and '◉' or '○',
                'answer3_yes': data['form']['answer3_yes'] and '◉' or '○',
                'answer3_no': data['form']['answer3_no'] and '◉' or '○',

            }
        return res

    def get_tax(self, data, tax_group):
        total = 0.0
        flag = 0
        final_domain = []
        date_start = data['date_from']
        date_stop = data['date_to']
        self._cr.execute(taxes_query % (date_stop, date_start, self.env.user.company_id.id))
        taxes_result = self._cr.fetchall()
        self._cr.execute(gst_taxes_query % (date_stop, date_start))
        final_sale_domain = [('type_tax_use', '=', 'sale')]
        final_purchase_domain = [('type_tax_use', '=', 'purchase')]
        gst_taxes_results = self._cr.fetchall()
        if tax_group == 'MES':
            final_domain = final_purchase_domain + [('tax_group_id', '=', self.env.ref("l10n_sg.tax_group_mes").name)]
        elif tax_group == 'purchase':
            final_domain = final_purchase_domain + [('tax_group_id', '!=', self.env.ref("l10n_sg.tax_group_mes").name)]
        elif tax_group == 'purchase-tax':
            flag = 1
            final_domain = final_purchase_domain
        if tax_group == 'standard_rates':
            final_domain = final_sale_domain + [('tax_group_id', '=', self.env.ref("l10n_sg.tax_group_7").name)]
        elif tax_group == 'zeroed':
            final_domain = final_sale_domain + [('tax_group_id', '=', self.env.ref("l10n_sg.tax_group_0").name)]
        elif tax_group == 'exempted':
            final_domain = final_sale_domain + [('tax_group_id', '=', self.env.ref("l10n_sg.tax_group_exempted").name)]
        elif tax_group == 'sales-tax':
            flag = 1
            final_domain = final_sale_domain
        elif tax_group == 'sales':
            final_domain = final_sale_domain
        tax_ids = self.env['account.tax'].search(final_domain)
        print("tax_ids......",tax_ids)

        if flag:
            for i in range(len(taxes_result)):
                for tax in tax_ids:
                    if tax.id == taxes_result[i][0]:
                        total += taxes_result[i][1]
            return abs(total)

        for i in range(len(gst_taxes_results)):
            for tax in tax_ids:
                if tax.id == gst_taxes_results[i][0]:
                    total += gst_taxes_results[i][1]
        return abs(total)

    def get_company(self, data):
        res = {}
        company_id = self.env['res.company'].browse(
            data['form']['company_id'][0])
        if company_id:
            res.update({
                'contact_address':
                    company_id.partner_id.contact_address or '',
                'name': company_id.name,
                'gst_number': company_id.gst_number})
        return res

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get(
                'active_model'):
            raise UserError(_(
                "Form content is missing, this report cannot be printed."))
        tax_ids = self.env['account.tax'].browse(self.env.context.get('active_ids', []))
        return {
            'doc_ids': docids,
            'doc_model': 'account.tax',
            'docs': tax_ids,
            'data': data,
            'datetime': datetime,
            'get_tax': self.get_tax,
            'get_boolean_data': self.get_boolean_data,
            'get_company': self.get_company,
        }
