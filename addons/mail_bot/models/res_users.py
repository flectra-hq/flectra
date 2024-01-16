# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields

class Users(models.Model):
    _inherit = 'res.users'

    flectrabot_state = fields.Selection(
        [
            ('not_initialized', 'Not initialized'),
            ('onboarding_emoji', 'Onboarding emoji'),
            ('onboarding_attachement', 'Onboarding attachement'),
            ('onboarding_command', 'Onboarding command'),
            ('onboarding_ping', 'Onboarding ping'),
            ('idle', 'Idle'),
            ('disabled', 'Disabled'),
        ], string="FlectraBot Status", readonly=True, required=False)  # keep track of the state: correspond to the code of the last message sent
    flectrabot_failed = fields.Boolean(readonly=True)

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(Users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        pool[self._name].SELF_READABLE_FIELDS = pool[self._name].SELF_READABLE_FIELDS + ['flectrabot_state']
        return init_res
