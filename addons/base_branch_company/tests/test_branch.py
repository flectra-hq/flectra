# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase
import logging
_logger = logging.getLogger(__name__)


class TestMultiBranch(TransactionCase):
    def setUp(self):
        super(TestMultiBranch, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.main_company = self.env.ref('base.main_company')

        self.branch0 = self.env.ref('base_branch_company.data_branch_1')
        self.branch1 = self.env.ref('base_branch_company.data_branch_2')

        self.user_1 = self.create_user(
            self.main_company, 'user_1', self.branch0,
            [self.branch0, self.branch1])
        self.user_2 = self.create_user(
            self.main_company, 'user_2', self.branch1, [self.branch1])

        self.model_id = \
            self.env['ir.model'].search([('model', '=', 'res.partner')])
        self.record_rules = self.env['ir.rule'].create({
            'name': 'Partner',
            'model_id': self.model_id.id,
            'domain_force':
                "['|',('branch_id','=', False),'|', "
                "('branch_id','=',user.default_branch_id.id), "
                "('branch_id','in', [b.id for b in user.branch_ids] )]"
        })
        self.branch_partner0 = self.partner_obj.create({
            'name': 'Test Partner0',
            'email': 'test@123.example.com',
            'branch_id': self.branch0.id
        })

        self.env = self.env(user=self.user_1)
        self.branch_partner1 = self.partner_obj.create({
            'name': 'Test Partner1',
            'email': 'test@123.example.com',
            'branch_id': self.branch0.id
        })

    def create_user(self, main_company, user_name, branch_id, branch_ids):
        data = {
            'company_ids': [(4, main_company.id)],
            'branch_ids': [(4, branch.id) for branch in branch_ids],
            'company_id': main_company.id,
            'default_branch_id': branch_id.id,
            'login': user_name,
            'name': 'Test User',
            'password': '123',
            'email': 'testuser@yourcompany.com',

        }
        user_obj = self.env['res.users'].create(data)
        return user_obj

    def test_user_authentication(self):
        partner = self.partner_obj.sudo(self.user_1.id).search(
            [('id', '=', self.branch_partner1.id),
             ('branch_id', '=', self.branch0.id)])
        self.assertNotEqual(partner.ids, [],
                            'Test User have access to Branch %s' %
                            self.branch0.name)

        partner = self.partner_obj.sudo(self.user_2.id).search(
            [('id', '=', self.branch_partner0.id),
             ('branch_id', '=', self.branch0.id)])
        self.assertEqual(partner.ids, [],
                         'Test User should not have access to Branch %s' %
                         self.branch0.name)
