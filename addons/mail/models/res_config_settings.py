# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

import datetime

from werkzeug import urls

from flectra import api, fields, models, tools


class ResConfigSettings(models.TransientModel):
    """ Inherit the base settings to add a counter of failed email + configure
    the alias domain. """
    _inherit = 'res.config.settings'

    fail_counter = fields.Integer('Fail Mail', readonly=True)
    alias_domain = fields.Char('Alias Domain', help="If you have setup a catch-all email domain redirected to "
                               "the Flectra server, enter the domain name here.")
    send_limit = fields.Integer(
            string='Send Limit',
            help='Maximum number of mails sent in one step.',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        previous_date = datetime.datetime.now() - datetime.timedelta(days=30)

        alias_domain = self.env["ir.config_parameter"].get_param("mail.catchall.domain", default=None)
        if alias_domain is None:
            domain = self.env["ir.config_parameter"].get_param("web.base.url")
            try:
                alias_domain = urls.url_parse(domain).host
            except Exception:
                pass

        try:
            send_limit = int(self.env["ir.config_parameter"].get_param("mail.send.limit", default='10000'))
        except ValueError:
            send_limit = 10000

        res.update(
            fail_counter=self.env['mail.mail'].sudo().search_count([
                ('date', '>=', previous_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                ('state', '=', 'exception')]),
            alias_domain=alias_domain or False,
            send_limit=send_limit,
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param("mail.catchall.domain", self.alias_domain or '')
        self.env['ir.config_parameter'].set_param("mail.send.limit", self.send_limit or '10000')
