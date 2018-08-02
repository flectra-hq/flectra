# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, models, _
from datetime import datetime
from flectra.exceptions import UserError


class AssetDepreciation(models.AbstractModel):
    _name = "report.account_asset.asset_depreciation_template"

    def get_date(self, data):
        date_lst = [{
            'start_date': data['start_date'],
            'end_date': data['end_date']
        }]
        return date_lst

    def get_data(self, data):
        asset_dep_line_id_list = list()
        asset_dep_line_id_list = \
            self.env['account.asset.depreciation.line'].search([
                ('depreciation_date', '>=', data['start_date']),
                ('depreciation_date', '<=', data['end_date']),
                ('move_check', '=', True),
                ('move_id', '!=', False),
                ('move_id.state', '=', 'posted')
            ])
        if not asset_dep_line_id_list:
            raise UserError(_("No Depreciation Lines in this fiscal year.."))
        data_dict = {}
        for line_id in asset_dep_line_id_list:
            product_id = line_id.asset_id.product_id.id
            depre_date = datetime.strptime(
                line_id.depreciation_date, "%Y-%m-%d")
            purchase_date = datetime.strptime(
                line_id.asset_id.date, "%Y-%m-%d")
            if product_id not in data_dict:
                if depre_date.year == purchase_date.year \
                        or line_id.sequence == 1:
                    open_asset = 0.0
                    open_dep = 0.0
                    add_asset = line_id.begin_value
                else:
                    open_asset = line_id.begin_value
                    add_asset = 0.00
                    open_dep = line_id.depreciated_value - line_id.amount
                add_dep = line_id.amount
                total_dep = open_dep + add_dep
                total_asset = open_asset + add_asset
                data_dict[product_id] = {
                    'name': line_id.asset_id.name,
                    'product_name': line_id.asset_id.product_id.name,
                    'category': line_id.asset_id.category_id.name,
                    'open_asset': open_asset,
                    'add_asset': add_asset,
                    'total_asset': total_asset,
                    'open_dep': open_dep,
                    'add_dep': add_dep,
                    'total_dep': total_dep,
                    'open_net': open_asset - open_dep,
                    'add_net': add_asset - add_dep,
                    'total_net': total_asset - total_dep
                }
            else:
                add_dep = line_id.amount
                if depre_date.year == purchase_date.year \
                        or line_id.sequence == 1:
                    open_asset = 0.0
                    add_asset = line_id.begin_value
                    open_dep = 0.0
                else:
                    open_asset = line_id.begin_value
                    add_asset = 0.00
                    open_dep = line_id.depreciated_value - line_id.amount
                if line_id.asset_id.sale_date \
                        and line_id.asset_id.sale_date >= data['start_date'] \
                        and line_id.asset_id.sale_date <= data['end_date']:
                    add_asset -= line_id.begin_value
                    add_dep -= line_id.depreciated_value
                total_dep = open_dep + add_dep
                total_asset = open_asset + add_asset
                data_dict[product_id]['open_asset'] += open_asset
                data_dict[product_id]['add_asset'] += add_asset
                data_dict[product_id]['total_asset'] += total_asset
                data_dict[product_id]['open_dep'] += open_dep
                data_dict[product_id]['add_dep'] += add_dep
                data_dict[product_id]['total_dep'] += total_dep
                data_dict[product_id]['open_net'] += open_asset - open_dep
                data_dict[product_id]['add_net'] += add_asset - add_dep
                data_dict[product_id]['total_net'] += total_asset - total_dep

        final_data = []
        for key in data_dict:
            final_data.append(data_dict[key])
        return final_data

    @api.model
    def get_report_values(self, docids, data=None):
        report_lines = self.get_data(data.get('form'))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {'doc_ids': docids, 'doc_model': model, 'data': data,
                'docs': docs, 'get_data': report_lines}
