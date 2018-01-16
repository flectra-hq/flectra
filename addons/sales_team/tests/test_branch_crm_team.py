# -*- coding: utf-8 -*-

from flectra.tests import common


class TestBranchSaleTeam(common.TransactionCase):

    def setUp(self):
        super(TestBranchSaleTeam, self).setUp()

        self.main_company = self.env.ref('base.main_company')
        self.sale_user_group = self.env.ref('sales_team.group_sale_manager')
        self.manager_user_group = self.env.ref('sales_team.group_sale_manager')
        self.branch_1 = self.env.ref('base_branch_company.data_branch_1')
        self.branch_3 = self.env.ref('base_branch_company.data_branch_3')
        self.user_id_1 = self.create_sale_team_user(self.main_company, 'user_1', self.branch_1,
                                            [self.branch_1, self.branch_3],
                                            [self.sale_user_group, self.manager_user_group])
        self.user_id_2 = self.create_sale_team_user(self.main_company, 'user_2', self.branch_3,
                                            [self.branch_3],
                                            [self.sale_user_group, self.manager_user_group])
        self.sales_team_1 = self.crm_team_create('CRM Team User 1', self.user_id_1, self.branch_1)
        self.sales_team_2 = self.crm_team_create('CRM Team User 2', self.user_id_2, self.branch_3)

    def create_sale_team_user(self, main_company, user_name, branch_id, branch_ids, groups):
        group_ids = [grp.id for grp in groups]
        data = {
            'company_ids': [(4, main_company.id)],
            'branch_ids': [(4, ou.id) for ou in branch_ids],
            'company_id': main_company.id,
            'groups_id': [(6, 0, group_ids)],
            'default_branch_id': branch_id.id,
            'login': user_name,
            'name': 'Ron Sales User',
            'password': '123',
            'email': 'ron@yourcompany.com',
        }
        user_obj = self.env['res.users'].create(data)
        return user_obj

    def crm_team_create(self, team_name, user_id, branch_id):
        crm_id = self.env['crm.team'].sudo(user_id.id).create({'name': team_name,
                                                    'branch_id': branch_id.id})
        return crm_id

    def get_crm_team(self, user_id, sales_team_1, branch_id):
        crm_team = self.env['crm.team'].sudo(user_id.id).search(
            [('id', '=', sales_team_1.id),
             ('branch_id', '=', branch_id.id)])
        return crm_team

    def test_user_authentication_2(self):
        crm_team = self.get_crm_team(self.user_id_1, self.sales_team_1, self.branch_3)
        self.assertEqual(crm_team.ids, [], ('%s should not have '
                                            'access to Branch %s') % (
            self.user_id_1.name, self.branch_1.name))
