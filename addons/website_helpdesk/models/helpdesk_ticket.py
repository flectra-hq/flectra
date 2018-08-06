# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['helpdesk.ticket', 'portal.mixin']

    def _compute_portal_url(self):
        super(HelpdeskTicket, self)._compute_portal_url()
        for ticket in self:
            ticket.portal_url = '/my/ticket/%s' % ticket.id
