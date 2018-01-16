# -*- coding: utf-8 -*-
from flectra.tests import common


class TestCrmBranch(common.TransactionCase):

    def setUp(self):
        super(TestCrmBranch, self).setUp()

        self.branch_1 = self.env.ref('base_branch_company.data_branch_1')
        self.branch_2 = self.env.ref('base_branch_company.data_branch_2')
        self.model_crm = self.env['crm.lead']
        self.sale_user_group = self.env.ref('sales_team.group_sale_manager')
        self.main_company = self.env.ref('base.main_company')
        self.crm_user_group = self.env.ref('base.group_user')

        self.user_1 = self.create_crm_user(self.main_company, self.branch_1, [self.branch_1],'user_1', [self.sale_user_group,
                                                  self.crm_user_group])
        self.user_2 = self.create_crm_user(self.main_company, self.branch_2, [self.branch_2], 'user_2', [self.sale_user_group,
                                                  self.crm_user_group])
        self.team1=self.env.ref('sales_team.team_sales_department')
        self.team1.write({'branch_id': self.branch_1.id, 'user_id': self.user_1.id})
        self.team2 = self.env.ref('sales_team.crm_team_1')
        self.team2.write({'branch_id': self.branch_2.id, 'user_id': self.user_2.id})

        self.lead_1 = self.lead_create(self.branch_1, self.team1, self.user_1.id)
        self.lead_2 = self.lead_create(self.branch_2, self.team2, self.user_2.id)

    def create_crm_user(self, main_company, branch, branch_ids, login_user, groups):
        groups = [group.id for group in groups]
        user_obj = self.env['res.users'].create({
            'company_id': main_company.id,
            'branch_ids': [(4, branch_id.id) for branch_id in branch_ids],
            'default_branch_id': branch.id,
            'company_ids': [(4, main_company.id)],
            'groups_id': [(6, 0, groups)],
            'login': login_user,
            'name': 'CRM Test ' + login_user,
            'email': 'demo@yourcompany.com',
            'password': '123',
        })
        return user_obj


    def lead_create(self, branch_id, team_id, user_id, ):
        lead_name = 'CRM LEAD '
        lead = self.model_crm.create({
            'user_id': user_id,
            'team_id': team_id.id,
            'name': lead_name + branch_id.name,
            'branch_id': branch_id.id,
        })
        return lead

    def test_lead_authentication(self):
        lead_ids = self.model_crm.sudo(self.user_2.id).search(
            [('branch_id', '=', self.branch_1.id), ('id', '=', self.lead_1.id)])
        self.assertEqual(lead_ids.ids, [], ('%s should not have'
                                            ' access to %s')
                         % (self.user_2.name, self.branch_1.name))

    def test_team_branch(self):
        lead = self.lead_create(self.branch_2, self.team2, self.user_2.id )
        self.assertEqual(
            lead.branch_id, self.branch_2, ('%s lead '
                                            'should have %s as branch')
                                           % (self.user_2.name,
                                              self.branch_2.name))
