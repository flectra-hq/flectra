# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup

from flectra import models, fields, _

class Users(models.Model):
    _inherit = 'res.users'

    flectrabot_state = fields.Selection(
        [
            ('not_initialized', 'Not initialized'),
            ('onboarding_emoji', 'Onboarding emoji'),
            ('onboarding_attachement', 'Onboarding attachment'),
            ('onboarding_command', 'Onboarding command'),
            ('onboarding_ping', 'Onboarding ping'),
            ('idle', 'Idle'),
            ('disabled', 'Disabled'),
        ], string="FlectraBot Status", readonly=True, required=False)  # keep track of the state: correspond to the code of the last message sent
    flectrabot_failed = fields.Boolean(readonly=True)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['flectrabot_state']

    def _init_messaging(self):
        flectrabot_onboarding = False
        if self.flectrabot_state in [False, 'not_initialized'] and self._is_internal():
            flectrabot_onboarding = True
            self._init_flectrabot()
        res = super()._init_messaging()
        res['flectrabotOnboarding'] = flectrabot_onboarding
        return res

    def _init_flectrabot(self):
        self.ensure_one()
        flectrabot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        channel = self.env['discuss.channel'].channel_get([flectrabot_id, self.partner_id.id])
        message = Markup("%s<br/>%s<br/><b>%s</b> <span class=\"o_flectrabot_command\">:)</span>") % (
            _("Hello,"),
            _("Flectra's chat helps employees collaborate efficiently. I'm here to help you discover its features."),
            _("Try to send me an emoji")
        )
        channel.sudo().message_post(body=message, author_id=flectrabot_id, message_type="comment", subtype_xmlid="mail.mt_comment")
        self.sudo().flectrabot_state = 'onboarding_emoji'
        return channel
