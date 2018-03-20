# Part of Flectra See LICENSE file for full copyright and licensing details.

from .test_gst_common import TestGSTCommon


class TestResCompany(TestGSTCommon):
    def test_res_company(self):
        # Test case for regisetered company
        if self.demo_company.gst_type == 'regular':
            assert self.demo_company.vat,\
                'Registered company must have GSTIN'

        self.assertEquals(self.demo_company.state_id.l10n_in_tin,
                          self.demo_company.vat[:2],
                          'GST Number is not valid')

        self.assertEquals(len(self.demo_company.vat), 15,
                          'GSTIN length must be of 15 characters!')

        # Test case for unregisetered company
        if self.demo_company.gst_type == 'unregistered':
            assert not self.res_partner_unregistered.vat, \
                'Unregistered partner does not have GSTIN'

        # Test case for B2C Limit lines
        self.assertTrue(len(self.demo_company.company_b2c_limit_line.ids) != 0,
                        'Company must have B2C Limit')
