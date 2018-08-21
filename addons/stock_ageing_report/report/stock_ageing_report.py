# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, _
from flectra.exceptions import UserError
from datetime import datetime, timedelta
from flectra.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class StockAgeingReport(models.AbstractModel):
    _name = 'report.stock_ageing_report.stock_ageing_report_template'

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get(
                'active_model') or not self.env.context.get('active_id'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        report = self.env['ir.actions.report']._get_report_from_name(
            'stock_ageing_report.action_stock_ageing_report')
        get_data = self._get_data(data)
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
            'data': {
                'company': [get_data['company_id']],
                'branch': [get_data['branch_id']],
                'warehouse': [get_data['warehouse_id']],
                'location': [get_data['location_id']],
                'product_category': [get_data['product_category_id']],
                'product': [get_data['product_id']],
                'period_length': [get_data['period_length']],
                'date': [get_data['date']],
                'period_list': get_data['period_list'],
                'product_list': get_data['product_list']
            }
        }

    def _get_product_wise_detail(self, product_ids, location_id, date,
                                 period_length, branch_id, company_id):
        product_list = []
        date_1 = datetime.strftime(date, DATETIME_FORMAT)
        date_2 = datetime.strftime(
            date - timedelta(days=period_length), DATETIME_FORMAT)
        date_3 = datetime.strftime(
            date - timedelta(days=(period_length * 2)), DATETIME_FORMAT)
        date_4 = datetime.strftime(
            date - timedelta(days=(period_length * 3)), DATETIME_FORMAT)
        date_5 = datetime.strftime(
            date - timedelta(days=(period_length * 4)), DATETIME_FORMAT)
        date_period = [date_1, date_2, date_3, date_4, date_5]
        final_dates = [
            (date, date_period[date_period.index(date) + 1] if
            date_period.index(date) < 4 else date)
            for date in date_period]
        for product in product_ids:
            qty_period_list = self.calculate_virtual_qty(
                product, location_id, branch_id, company_id, final_dates)
            product_dict = {'product_id': product.name_get()[0][1],
                            'qty_period_list': qty_period_list,
                            'qty_available': sum(qty_period_list),
                            'total_amount': sum(qty_period_list) *
                                            product.list_price}
            product_list.append(product_dict)
        return product_list

    def calculate_virtual_qty(self, product, location_id, branch_id,
                              company_id, date_range):
        product_list = []
        quant_obj = self.env['stock.quant']
        move_obj = self.env['stock.move']
        for date in date_range:
            domain = []
            to_date = False
            from_date = date[0]
            if date[0] != date[1]:
                to_date = date[1]
            domain += [('product_id', '=', product.id)]
            if product.tracking != 'none':
                domain += [('location_id', 'in', location_id.ids),
                           ('in_date', '<=', from_date),
                           ('branch_id', '=', branch_id.id),
                           ('company_id', '=', company_id.id)]
                if to_date:
                    domain += [('in_date', '>', to_date)]
                virtual_available = sum(
                    [quant.quantity for quant in quant_obj.search(domain)])
                print ("\n domain", domain)
            else:
                domain += ['|', ('location_id', 'in', location_id.ids),
                           ('location_dest_id', 'in', location_id.ids),
                           ('state', '=', 'done'), ('bal_qty', '>', 0),
                           ('date', '<=', from_date),
                           ('branch_dest_id', '=', branch_id.id),
                           ('company_id', '=', company_id.id)]
                if to_date:
                    domain += [('date', '>', to_date)]
                virtual_available = sum(
                    [move.bal_qty for move in move_obj.search(domain)])
            product_list.append(virtual_available)
        return product_list

    def _get_data(self, data):
        domain = []
        company_id = self.env['res.company'].browse(data['form']['company_id'])
        branch_id = self.env['res.branch'].browse(data['form']['branch_id'])
        warehouse_id = self.env['stock.warehouse'].browse(
            data['form']['warehouse_id'])
        location_id = self.env['stock.location'].browse(
            data['form']['location_id'])
        product_category_id = self.env['product.category'].browse(
            data['form']['product_category_id'])
        product_id = self.env['product.product'].browse(
            data['form']['product_id'])
        if not location_id:
            location_id = self.env['stock.location'].search([
                ('company_id', '=', company_id.id),
                ('usage', '=', 'internal')])
        period_length = data['form']['period_length']
        date = datetime.strptime(data['form']['date'], DATETIME_FORMAT)

        if product_id:
            domain += [('id', 'in', product_id.ids)]
        elif product_category_id:
            domain += [('categ_id', 'in', product_category_id.ids),
                       ('type', '=', 'product')]
        else:
            domain += [('qty_available', '>', 0)]
        product_ids = self.env['product.product'].search(domain)
        product_list = self._get_product_wise_detail(
            product_ids, location_id, date, period_length, branch_id,
            company_id)
        warehouse = location = product_category = ''
        if warehouse_id:
            warehouse = ','.join(
                wh.name_get()[0][1] for wh in
                warehouse_id) if len(warehouse_id) > 1 else\
                warehouse_id.name_get()[0][1]
        if data['form']['location_id']:
            location = ','.join(loc.name_get()[0][1] for loc in location_id) \
                if len(location_id) > 1 else location_id.name_get()[0][1] or ''
        if product_category_id:
            product_category = ','.join(
                categ.name_get()[0][1] for categ in product_category_id
            ) if len(product_category_id) > 1 else\
                product_category_id.name_get()[0][1] or ''
        period_list = ['0 - ' + str(period_length),
                       str(period_length) + ' - ' + str(period_length * 2),
                       str(period_length * 2) + ' - ' + str(period_length * 3),
                       str(period_length * 3) + ' - ' + str(period_length * 4),
                       ' + ' + str(period_length * 4)]
        data['form'].update({
            'company_id': company_id,
            'branch_id': branch_id,
            'warehouse_id': warehouse or '',
            'location_id': location or '',
            'product_category_id': product_category or '',
            'product_id': product_id or '',
            'period_length': period_length,
            'date': datetime.strftime(date, DATETIME_FORMAT),
            'period_list': period_list,
            'product_list': product_list})
        return data['form']
