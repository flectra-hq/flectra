# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.phone_validation.tools import phone_validation
from flectra.exceptions import UserError
from flectra.tests import tagged
from flectra.tests.common import BaseCase


@tagged('phone_validation')
class TestPhonenumbers(BaseCase):

    def test_country_code_falsy(self):
        self.assertEqual(
            phone_validation.phone_format('0456998877', 'BE', '32', force_format='E164'),
            '+32456998877'
        )
        # no country code -> UserError, no internal traceback
        with self.assertRaises(UserError):
            self.assertEqual(
                phone_validation.phone_format('0456998877', None, '32', force_format='E164'),
                '+32456998877'
            )
