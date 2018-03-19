# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase
from datetime import date, timedelta


class TestStockAgeingReport(TransactionCase):
    def setUp(self):
        super(TestStockAgeingReport, self).setUp()
        self.location = self.env['stock.location']
        self.location_barcode = self.env.ref('stock.stock_location_3')
        self.barcode = self.location_barcode.barcode
        self.warehouse = self.env["stock.warehouse"]

    def test_20_stock_ageing_report(self):
        # Print the Stock Ageing Report through the wizard
        data_dict = {
            'company_id': [],
            'warehouse_ids': [],
            'location_ids': [],
            'product_category_ids': [(6, 0, [self.env.ref(
                'product.product_category_5').id])],
            'product_ids': [(6, 0, [self.env.ref(
                'product.product_product_5b').id])],
            'period_length': 30,
            'date': date.today() - timedelta(days=30),
        }
        wizard = self.env['stock.ageing.wizard'].create(data_dict)
        wizard.with_context(data_dict).print_report()
