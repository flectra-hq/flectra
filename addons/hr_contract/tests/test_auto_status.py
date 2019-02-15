# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from flectra.tests.common import TransactionCase
from dateutil.relativedelta import relativedelta


class TestHrContracts(TransactionCase):

    def setUp(self):
        super(TestHrContracts, self).setUp()
        self.contracts = self.env['hr.contract'].with_context(tracking_disable=True)
        self.employee = self.env.ref('hr.employee_root')
        self.test_contract = dict(name='Test', wage=1, employee_id=self.employee.id, state='open')

    def apply_cron(self):
        self.env.ref('hr_contract.ir_cron_data_contract_update_state').method_direct_trigger()

    def test_contract_enddate(self):
        self.test_contract.update(dict(date_end=datetime.now() + relativedelta(days=100)))
        self.contract = self.contracts.create(self.test_contract)
        self.apply_cron()
        self.assertEquals(self.contract.state, 'open')

        self.test_contract.update(dict(date_end=datetime.now() + relativedelta(days=5)))
        self.contract.write(self.test_contract)
        self.apply_cron()
        self.assertEquals(self.contract.state, 'pending')

        self.test_contract.update({
            'date_start': datetime.now() + relativedelta(days=-50),
            'date_end': datetime.now() + relativedelta(days=-1),
            'state': 'pending',
        })
        self.contract.write(self.test_contract)
        self.apply_cron()
        self.assertEquals(self.contract.state, 'close')

    def test_contract_pending_visa_expire(self):
        self.employee.visa_expire = datetime.now() + relativedelta(days=30)
        self.test_contract.update(dict(date_end=False))
        self.contract = self.contracts.create(self.test_contract)
        self.apply_cron()
        self.assertEquals(self.contract.state, 'pending')

        self.employee.visa_expire = datetime.now() + relativedelta(days=-5)
        self.test_contract.update({
            'date_start': datetime.now() + relativedelta(days=-50),
            'state': 'pending',
        })
        self.contract.write(self.test_contract)
        self.apply_cron()
        self.assertEquals(self.contract.state, 'close')

    def test_return_contract_in_force_for_date(self):
        self.test_contract.update({
            'date_start': datetime.now() + relativedelta(days=-50),
            'date_end': datetime.now() + relativedelta(days=-20),
        })
        contract_past = self.contracts.create(self.test_contract)
        self.test_contract.update({
            'date_start': datetime.now() + relativedelta(days=-19),
            'date_end': datetime.now() + relativedelta(days=5),
        })
        contract_in_force = self.contracts.create(self.test_contract)

        self.test_contract.update({
            'date_start': datetime.now() + relativedelta(days=6),
            'date_end': datetime.now() + relativedelta(days=50),
        })
        contract_future = self.contracts.create(self.test_contract)

        self.assertEqual(self.employee.contract_id, contract_in_force)
        self.assertEqual(self.employee.with_context(
            force_contract_date=datetime.now() + relativedelta(days=14)).contract_id, contract_future)
        self.assertEqual(self.employee.with_context(
            force_contract_date=datetime.now() + relativedelta(days=-25)).contract_id, contract_past)
