# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class MassMail(models.TransientModel):
    _name = 'mass.mail'
    _description = 'Mass Mail Options'

    message = fields.Char('Message')

    @api.multi
    def mass_emails(self):
        send_method = self.env.context['mail']
        active_ids = self.env.context['active_ids']        
        lines = self.env['mail.mail'].search([( 'id', 'in', active_ids)])
        if send_method == 'mark_outgoing':
            lines.mark_outgoing()  
        elif send_method == 'send':
            lines.send()
        elif send_method == 'cancel':
            lines.cancel()
