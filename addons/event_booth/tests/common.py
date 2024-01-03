# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.event.tests.common import EventCase


class TestEventBoothCommon(EventCase):

    @classmethod
    def setUpClass(cls):
        super(TestEventBoothCommon, cls).setUpClass()

        cls.event_booth_category_1 = cls.env['event.booth.category'].create({
            'name': 'Standard',
            'description': '<p>Standard</p>',
        })
        cls.event_booth_category_2 = cls.env['event.booth.category'].create({
            'name': 'Premium',
            'description': '<p>Premium</p>',
        })
