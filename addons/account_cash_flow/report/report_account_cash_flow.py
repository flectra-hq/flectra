# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, api
import datetime
from datetime import timedelta
import calendar
from collections import Counter



class ReportAccountCashFlow(models.AbstractModel):
    _name = 'report.account_cash_flow.report_account_cash_flow'

    def get_years(self, data, is_getdata):
        company_id = self.env['res.company'].browse(
            data['form']['company_id'][0])
        date_dict = {}
        year_list = [datetime.datetime.now().year - year for year in
                     range(0, data['form']['no_of_year'] + 1)]
        for year in year_list:
            no_days = calendar.isleap(year) and 365 or 364
            date_dict.update({year: [
                str(datetime.date(year, company_id.fiscalyear_last_month,
                                  company_id.fiscalyear_last_day) -
                    timedelta(days=no_days)),
                str(datetime.date(year, company_id.fiscalyear_last_month,
                                  company_id.fiscalyear_last_day))]})
        year_list.sort(reverse=True)
        if is_getdata:
            return date_dict
        return year_list

    def get_move_lines(self, date_from, date_to, key, dummy_list,
                       company_id, branch_id):
        self._cr.execute("select CASE WHEN acc_type.activity_type is null THEN acc.name ELSE acc_type.activity_type END AS activity_type, "
                         "aml.account_id, "
                         "(sum(aml.debit) - sum(aml.credit)) * -1 as "
                         "balance "
                         "from account_move_line aml, "
                         "account_account acc, "
                         "account_account_type acc_type "
                         "where acc.id = aml.account_id and "
                         "aml.date >= '%s'" % date_from + "and "
                         "aml.date <= '%s'" % date_to + "and "
                         "acc.user_type_id = acc_type.id and "
                         "aml.company_id = %s " % company_id + "and "
                         "aml.branch_id = %s " % branch_id +
                         "group by aml.account_id, "
                         "acc_type.activity_type, acc.name")
        balance_data = self._cr.dictfetchall()
        [d.update({'year': {key: d['balance']}}) for d in balance_data]
        for dummy in dummy_list:
            [d['year'].update({dummy: 0.0}) for d in balance_data]
        return balance_data

    def get_data(self, data):
        final_dict = {}
        balance_data = []
        date_dict = self.get_years(data, is_getdata=True)
        for key in sorted(date_dict, reverse=True):
            dummy_list = list(date_dict.keys())
            dummy_list.remove(key)
            balance_data += self.get_move_lines(date_dict[key][0],
                                               date_dict[key][1], key,
                                                dummy_list, data['form'][
                                                    'company_id'][0],
                                                data['form']['branch_id'][0])
        for data in balance_data:
            if data['activity_type'] not in final_dict:
                final_dict[data['activity_type']] = {'account': {}}
                final_dict[data['activity_type']]['account'] = {data['account_id']: data['year']}
                final_dict[data['activity_type']]['total'] = data['year']
            else:
                if data['account_id'] not in \
                        final_dict[data['activity_type']]['account']:
                    final_dict[data['activity_type']]['account'][data['account_id']] = data['year']
                else:
                    f_year = final_dict[data['activity_type']]['account'][data['account_id']]
                    d_year = data['year']
                    total = {k : f_year.get(k, 0) + d_year.get(k,0) for k in set(f_year.keys()) | set(d_year.keys())}
                    final_dict[data['activity_type']]['account'][data['account_id']] = total
                y_total = final_dict[data['activity_type']]['total']
                total = {k : y_total.get(k, 0) + data['year'].get(k,0) for k in set(y_total.keys()) | set(data['year'].keys())}
                final_dict[data['activity_type']]['total'] = total
        return final_dict

    def get_acc_details(self, account_id):
        acc_details = {'ac_nm': self.env['account.account'].browse(
            account_id).name,
            'ac_no': self.env['account.account'].browse(
            account_id).code}
        return acc_details

    def get_total(self, data_dict, year, type_list):
        total_bal = 0.00
        for value in type_list:
            if value in data_dict:
                total_bal += data_dict[value]['total'][year]
        return total_bal

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['account.move.line'].browse(docids)
        docargs = {
            'doc_model': 'account.move.line',
            'docs': docs,
            'branch_name': data['form']['branch_id'][1],
            'get_data': self.get_data(data),
            'get_years': self.get_years(data, is_getdata=False),
            'get_acc_details': self.get_acc_details,
            'get_total': self.get_total,
        }
        return docargs
