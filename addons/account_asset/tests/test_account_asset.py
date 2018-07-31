# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import tools
from flectra.tests import common
from flectra.modules.module import get_resource_path
from datetime import date, datetime
from flectra.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import logging


class TestAccountAsset(common.TransactionCase):

    def _load(self, module, *args):
        tools.convert_file(self.cr, 'account_asset',
                           get_resource_path(module, *args),
                           {}, 'init', False, 'test', self.registry._assertion_report)

    def test_00_account_asset_asset(self):
        self._load('account', 'test', 'account_minimal_test.xml')
        self._load('account_asset', 'test', 'account_asset_demo_test.xml')

        self.asset_id_1 = self.env.ref("account_asset.account_asset_1")
        self.asset_id_2 = self.env.ref("account_asset.account_asset_2")
        self.partner_id = self.env.ref("base.res_partner_2")

        # In order to test the process of Account Asset, I perform a action to confirm Account Asset.
        self.browse_ref("account_asset.account_asset_asset_vehicles_test0").validate()

        # I check Asset is now in Open state.
        self.assertEqual(self.browse_ref("account_asset.account_asset_asset_vehicles_test0").state, 'open',
            'Asset should be in Open state')

        # I compute depreciation lines for asset of CEOs Car.
        self.browse_ref("account_asset.account_asset_asset_vehicles_test0").compute_depreciation_board()
        value = self.browse_ref("account_asset.account_asset_asset_vehicles_test0")
        self.assertEqual(value.method_number, len(value.depreciation_line_ids),
            'Depreciation lines not created correctly')

        # I create account move for all depreciation lines.
        ids = self.env['account.asset.depreciation.line'].search([('asset_id', '=', self.ref('account_asset.account_asset_asset_vehicles_test0'))])
        for line in ids:
            line.create_move()

        # I check the move line is created.
        asset = self.env['account.asset.asset'].browse([self.ref("account_asset.account_asset_asset_vehicles_test0")])[0]
        self.assertEqual(len(asset.depreciation_line_ids), asset.entry_count,
            'Move lines not created correctly')

        # I Check that After creating all the moves of depreciation lines the state "Close".
        self.assertEqual(self.browse_ref("account_asset.account_asset_asset_vehicles_test0").state, 'close',
            'State of asset should be close')

        # WIZARD
        # I create a record to change the duration of asset for calculating depreciation.
        account_asset_asset_office0 = self.browse_ref('account_asset.account_asset_asset_office_test0')
        asset_modify_number_0 = self.env['asset.modify'].create({
            'name': 'Test reason',
            'method_number': 10.0,
        }).with_context({'active_id': account_asset_asset_office0.id})
        # I change the duration.
        asset_modify_number_0.with_context({'active_id': account_asset_asset_office0.id}).modify()

        # I check the proper depreciation lines created.
        self.assertEqual(account_asset_asset_office0.method_number, len(account_asset_asset_office0.depreciation_line_ids))
        # I compute a asset on period.
        context = {
            "active_ids": [self.ref("account_asset.menu_asset_depreciation_confirmation_wizard")],
            "active_id": self.ref('account_asset.menu_asset_depreciation_confirmation_wizard'),
            'type': 'sale'
        }
        asset_compute_period_0 = self.env['asset.depreciation.confirmation.wizard'].create({})
        asset_compute_period_0.with_context(context).asset_compute()

        assert self.asset_id_1.product_id, "Product is not there in %s" % \
                                           self.asset_id_1

        assert self.asset_id_1.category_id, "Asset Category is not there " \
                                            "in %s" % self.asset_id_1

        assert self.asset_id_1.partner_id, "Vendor is not defined in %s" % \
                                           self.asset_id_1

        assert self.asset_id_1.date, "Asset Purchase date is not defined."

        assert self.asset_id_1.value, "Definig an asset value is necessary"

        if self.asset_id_1.method is 'degressive':
            assert self.asset_id_1.method_progress_factor, \
                "Degressive Factor is required for further calculation"

        if self.asset_id_1.method_time is 'number':
            assert self.asset_id_1.method_number, "Method number is required"

        if self.asset_id_1.method_time is 'end':
            assert self.asset_id_1.method_end, "Ending Date is required"

        assert self.asset_id_1.method_period, "Field 'Number of months in " \
                                              "a period is blank'"

        self.asset_id_1.validate()
        if self.asset_id_1.state != 'open':
            raise AssertionError("Asset state must be in open state!")

        sale_asset_id = self.env['sale.asset.wizard'].create({
            'asset_id': self.asset_id_1.id,
            'product_id': self.asset_id_1.product_id.id,
            'asset_category_id': self.asset_id_1.category_id.id,
            'sale_date': date.today(),
            'partner_id': self.partner_id.id,
        })
        sale_asset_id.onchange_sale_date()
        sale_asset_id.with_context(
            {'active_id': self.asset_id_1.id}).sale_asset()

        if self.asset_id_1.state != 'close':
            raise AssertionError("Asset is not sold")
        else:
            logging.info("Asset Sale Function successfully executed")

        # Check Fiscal Year
        account_config = self.env['res.config.settings'].create({
                'fiscalyear_last_month': 3,
            })
        account_config.execute()
        self.assertEqual(self.asset_id_2.prorata, 'fiscal_year')
        self.assertEqual(self.asset_id_2.method_period, 12)
        self.asset_id_2.compute_depreciation_board()
        self.asset_id_2.validate()
        fl_depreciation_date = self.asset_id_2.depreciation_line_ids[0].depreciation_date
        first_line_date = datetime.strptime(fl_depreciation_date, DF).date()
        self.assertEqual(first_line_date.month, 3)
        sl_depreciation_date = self.asset_id_2.depreciation_line_ids[1].depreciation_date
        second_line_date = datetime.strptime(sl_depreciation_date, DF).date()
        self.assertEqual(second_line_date.month, 3)
