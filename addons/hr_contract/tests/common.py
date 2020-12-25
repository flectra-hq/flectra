# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests.common import SavepointCase


class TestContractCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestContractCommon, cls).setUpClass()

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Richard',
            'gender': 'male',
            'country_id': cls.env.ref('base.be').id,
        })
