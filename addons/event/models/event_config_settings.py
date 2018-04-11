# -*- coding: utf-8 -*-

from flectra import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_event_sale = fields.Boolean("Tickets")
    module_website_event_track = fields.Boolean("Tracks and Agenda")
    module_website_event_questions = fields.Boolean("Registration Survey")
    module_website_event_sale = fields.Boolean("Online Ticketing")
