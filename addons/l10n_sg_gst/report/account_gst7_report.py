# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import time
from datetime import datetime
from flectra.addons.l10n_sg_gst.report.account_gst5_report import \
    taxes_query, gst_taxes_query, AccountGst5Report

from flectra import api, models, _
from flectra.exceptions import UserError


class AccountGst7Report(models.AbstractModel):
    _name = 'report.l10n_sg_gst.account_gst7_report_view'

    def get_boolean_data(self, data):
        return AccountGst5Report.get_boolean_data(self, data)

    def get_tax(self, data, tax_group):
        return AccountGst5Report.get_tax(self, data, tax_group)
    #
    def get_company(self, data):
        res = AccountGst5Report.get_company(self, data)
        return res

    @api.constrains('declaration_of_error')
    def _get_declaration_of_error(self, data):
        return data['form']['declaration_of_error']

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
            'time': time,
            'datetime': datetime,
            'get_tax': self.get_tax,
            'get_boolean_data': self.get_boolean_data,
            'get_company': self.get_company,
            'get_declaration_of_error': self._get_declaration_of_error
        }
