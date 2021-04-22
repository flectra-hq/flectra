# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models

from flectra.addons.google_calendar.models.google_sync import google_calendar_token
from flectra.addons.google_calendar.utils.google_calendar import GoogleCalendarService

class Attendee(models.Model):
    _name = 'calendar.attendee'
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(self, template_xmlid, force_send=False, ignore_recurrence=False):
        """ Override
        If not synced with Google, let Flectra in charge of sending emails
        Otherwise, nothing to do: Google will send them
        """
        with google_calendar_token(self.env.user.sudo()) as token:
            if not token:
                super()._send_mail_to_attendees(template_xmlid, force_send, ignore_recurrence)

    def write(self, vals):
        res = super().write(vals)
        if vals.get('state'):
            # When the state is changed, the corresponding event must be sync with google
            google_service = GoogleCalendarService(self.env['google.service'])
            self.event_id.filtered('google_id')._sync_flectra2google(google_service)
        return res
