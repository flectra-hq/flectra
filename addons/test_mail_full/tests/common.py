# -*- coding: utf-8 -*-

from flectra.addons.phone_validation.tools import phone_validation
from flectra.addons.mass_mailing_sms.tests.common import MassSMSCommon
from flectra.addons.test_mail.tests.common import TestRecipients
from flectra.addons.test_mass_mailing.tests.common import TestMassMailCommon


class TestMailFullCommon(TestMassMailCommon, MassSMSCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMailFullCommon, cls).setUpClass()


class TestRecipients(TestRecipients):

    @classmethod
    def setUpClass(cls):
        super(TestRecipients, cls).setUpClass()
        cls.partner_numbers = [
            phone_validation.phone_format(partner.mobile, partner.country_id.code, partner.country_id.phone_code, force_format='E164')
            for partner in (cls.partner_1 | cls.partner_2)
        ]
