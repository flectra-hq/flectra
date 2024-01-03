# -*- coding: utf-8 -*-
from flectra.tests import common


class TestAttributes(common.TransactionCase):

    def test_we_cannot_add_attributes(self):
        Model = self.env['test_new_api.category']
        instance = Model.create({'name': 'Foo'})

        with self.assertRaises(AttributeError):
            instance.unknown = 42
