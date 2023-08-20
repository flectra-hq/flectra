# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models
from flectra.addons.base_import.models.base_import import FIELDS_RECURSION_LIMIT


class BaseImportCSV(models.TransientModel):
    _inherit = 'base_import.import'

    def _prepare_list(self):
        return [{
            'id': 'balance',
            'name': 'balance',
            'string': 'Cumulative Balance',
            'required': False,
            'fields': [],
            'type': 'monetary',
        }]

    @api.model
    def get_fields(self, model, depth=FIELDS_RECURSION_LIMIT):
        default_added_fields = super(
            BaseImportCSV, self).get_fields(model, depth=depth)
        f_list = self._prepare_list()
        for field in f_list:
            default_added_fields.append(field)
        return default_added_fields

    def _set_debit_credit_data(self, fields_info, parse_info, options):
        bank_bl = {}
        fields_info.append('statement_id/.id')
        fields_info.append('sequence')
        idx_bl = False

        if 'balance' in fields_info:
            idx_bl = fields_info.index('balance')
            self._parse_float_from_data(
                parse_info, idx_bl, 'balance', options)
            bank_bl['balance_start'] = parse_info and float(
                parse_info[0][idx_bl]) or 0.00
            bank_bl['balance_start'] -= float(
                parse_info[0][fields_info.index('amount')]) or 0.00
            bank_bl['balance_end_real'] = parse_info[len(
                parse_info) - 1][idx_bl]
            fields_info.remove('balance')
        return {
            'idx_bl': idx_bl,
            'bank_bl': bank_bl
        }

    def _remove_index_set_data(self, import_fields, parse_data, res, st):
        currency_index = (('foreign_currency_id' in import_fields
                           ) and (import_fields.index('foreign_currency_id')
                                  )) or False

        idx_bl = res['idx_bl']
        list_data = []
        for i, lst in enumerate(parse_data):
            lst.append(st)
            lst.append(i)
            rm_index = []
            if idx_bl:
                rm_index.append(idx_bl)
            for i in sorted(rm_index, reverse=True):
                lst.remove(lst[i])
            if lst[import_fields.index('amount')]:
                list_data.append(lst)
            if (currency_index is not False) and (
                    lst[currency_index] == st.company_id.currency_id.name):
                lst[currency_index] = False
        return list_data

    def _parse_import_data(self, data, fields_info, options):
        parse_info = super(
            BaseImportCSV, self)._parse_import_data(
            data, fields_info, options)
        st_id = self._context.get('bank_statement_id', False)
        account_stmt_obj = self.env['account.bank.statement']

        if not st_id:
            return parse_info
        st = account_stmt_obj.browse(st_id)
        res = self._set_debit_credit_data(fields_info, parse_info, options)
        bank_bl = res['bank_bl']
        list_data = self._remove_index_set_data(fields_info, parse_info, res, st)
        if 'date' in fields_info:
            bank_bl['date'] = parse_info[len(parse_info) - 1][fields_info.index('date')]
        if bank_bl:
            st.write(bank_bl)
        return list_data

    def do(self, fields, columns, options, dryrun=False):
        st = self._context.get('active_id') if self.res_model == 'account.bank.statement' else None
        res = super(
            BaseImportCSV, self.with_context(
                bank_statement_id=st)).do(
            fields, columns, options, dryrun=dryrun)
        return res
