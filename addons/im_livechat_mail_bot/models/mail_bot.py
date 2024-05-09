# Part of Flectra. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup
from flectra import models, _


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    def _get_answer(self, record, body, values, command):
        flectrabot_state = self.env.user.flectrabot_state
        if self._is_bot_in_private_channel(record):
            if flectrabot_state == "onboarding_attachement" and values.get("attachment_ids"):
                self.env.user.flectrabot_failed = False
                self.env.user.flectrabot_state = "onboarding_canned"
                return Markup(_("Wonderful! 😇<br/>Try typing %s to use canned responses.", "<span class=\"o_flectrabot_command\">:</span>"))
            elif flectrabot_state == "onboarding_canned" and self.env.context.get("canned_response_ids"):
                self.env.user.flectrabot_failed = False
                self.env.user.flectrabot_state = "idle"
                return Markup(_("Good, you can customize canned responses in the live chat application.<br/><br/><b>It's the end of this overview</b>, you can now <b>close this conversation</b> or start the tour again with typing <span class=\"o_flectrabot_command\">start the tour</span>. Enjoy discovering Flectra!"))
            # repeat question if needed
            elif flectrabot_state == 'onboarding_canned' and not self._is_help_requested(body):
                self.env.user.flectrabot_failed = True
                return _("Not sure what you are doing. Please, type %s and wait for the propositions. Select one of them and press enter.",
                    Markup("<span class=\"o_flectrabot_command\">:</span>"))
        return super(MailBot, self)._get_answer(record, body, values, command)
