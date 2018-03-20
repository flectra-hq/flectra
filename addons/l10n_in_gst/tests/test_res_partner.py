# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.osv.orm import except_orm
from .test_gst_common import TestGSTCommon


class TestResPartner(TestGSTCommon):

    def test_partner_gstin(self):
        # test cases for check constrains on create of partners
        with self.assertRaises(except_orm):
            self.env['res.partner'].create({
                'name': 'Demo IGST Unregistered Customer',
                'category_id': self.env.ref('base.res_partner_category_16'),
                'is_company': 1,
                'city': 'Darrang',
                'zip': '784527',
                'state_id': self.env.ref("base.state_in_as").id,
                'country_id': self.env.ref("base.in").id,
                'street': '16 Natrani Avenue',
                'gst_type': 'regular',
                'vat': '18weqqeqe',
                'email': 'igstur@yourcompany.example.com',
                'phone': '+91 95951 95951'
            })

        with self.assertRaises(except_orm):
            self.env['res.partner'].create({
                'name': 'Demo IGST Unregistered Customer',
                'category_id': self.env.ref('base.res_partner_category_16'),
                'is_company': 1, 'city': 'Darrang', 'zip': '784527',
                'state_id': self.env.ref("base.state_in_as").id,
                'country_id': self.env.ref("base.in").id,
                'street': '16 Natrani Avenue', 'gst_type': 'regular',
                'vat': '24weqqeqe45trfg',
                'email': 'igstur@yourcompany.example.com',
                'phone': '+91 95951 95951'
            })

        # Test case for regisetered partner
        if self.res_partner_registered.gst_type == 'regular':
            assert self.res_partner_registered.vat,\
                'Registered partner must have GSTIN'

        self.assertEquals(self.res_partner_registered.state_id.l10n_in_tin,
                          self.res_partner_registered.vat[:2],
                          'GST Number is not valid')

        self.assertEquals(len(self.res_partner_registered.vat), 15,
                          'GSTIN length must be of 15 characters!')

        if self.res_partner_registered.state_id.id == \
                self.res_partner_registered.company_id.state_id.id:
            assert not self.res_partner_registered.\
                property_account_position_id, 'Fiscal position must not be set'

        # Test case for unregisetered partner
        if self.res_partner_unregistered.gst_type == 'unregistered':
            assert not self.res_partner_unregistered.vat, \
                'Unregistered partner does not have GSTIN'
