# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, fields


class StockAgeingWizard(models.TransientModel):

    _name = 'stock.ageing.wizard'
    _description = 'Wizard that opens the stock ageing'

    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)
    branch_id = fields.Many2one('res.branch', string="Branch",
                                default=lambda self:
                                self.env.user.default_branch_id)
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouse")
    location_ids = fields.Many2many("stock.location", string='Location',
                                    domain="[('usage', '=', 'internal')]")
    product_category_ids = fields.Many2many("product.category",
                                            string="Product Category")
    product_ids = fields.Many2many('product.product', string='Product',
                                   domain="[('type', '=', 'product')]")
    period_length = fields.Integer(string='Period Length (days)', default=30)
    date = fields.Datetime(string="Date",
                           help="Choose a date to get the inventory ageing "
                                "report",
                           default=fields.Datetime.now())

    @api.multi
    def print_report(self):
        """
        To get the Stock Ageing report and print the report
        @return : return stock ageing report
        """
        datas = {'ids': self._context.get('active_ids', [])}
        res = self.read(
            ['company_id', 'branch_id', 'warehouse_ids', 'location_ids',
             'product_category_ids', 'product_ids',
             'period_length', 'date'])
        for ageing_dict in res:
            res = res and res[0] or {}
            res['company_id'] = ageing_dict['company_id'] and\
                ageing_dict['company_id'][0] or False
            res['branch_id'] = ageing_dict['branch_id'] and \
                ageing_dict['branch_id'][0] or False
            res['warehouse_id'] = ageing_dict['warehouse_ids']
            res['location_id'] = ageing_dict['location_ids']
            res['product_category_id'] = ageing_dict['product_category_ids']
            res['product_id'] = ageing_dict['product_ids']
            res['period_length'] = ageing_dict['period_length'] or False
            res['date'] = ageing_dict['date'] or False
            datas['form'] = res
            return self.env.ref(
                'stock_ageing_report.action_stock_ageing_report'
                '').report_action(self, data=datas)
