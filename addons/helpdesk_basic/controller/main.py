# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from flectra import http
from flectra.http import request
from flectra.tools.translate import _
from flectra.tools import plaintext2html
from werkzeug.exceptions import NotFound, Forbidden
from flectra.tools.misc import get_lang

_logger = logging.getLogger(__name__)

MAPPED_RATES = {
    1: 1,
    5: 3,
    10: 5,
}

def _check_special_access(res_model, res_id, token='', _hash='', pid=False):
    record = request.env[res_model].browse(res_id).sudo()
    if token:  # Token Case: token is the global one of the document
        token_field = request.env[res_model]._mail_post_token_field
        return (token and record and consteq(record[token_field], token))
    elif _hash and pid:  # Signed Token Case: hash implies token is signed by partner pid
        return consteq(_hash, record._sign_token(pid))
    else:
        raise Forbidden()

def _message_post_helper(res_model, res_id, message, token='', _hash=False, pid=False, nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread. We
        distinguish 2 cases:
            1/ If a token is specified, all logged in users will be able to write a message regardless
            of access rights; if the user is the public user, the message will be posted under the name
            of the partner_id of the object (or the public user if there is no partner_id on the object).

            2/ If a signed token is specified (`hash`) and also a partner_id (`pid`), all post message will
            be done under the name of the partner_id (as it is signed). This should be used to avoid leaking
            token to all users.

        Required parameters
        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        Optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param string hash: signed token by a partner if model uses some token field to bypass access right
                            post messages.
        :param string pid: identifier of the res.partner used to sign the hash
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].browse(res_id)

    # check if user can post with special token/signed token. The "else" will try to post message with the
    # current user access rights (_mail_post_access use case).
    if token or (_hash and pid):
        pid = int(pid) if pid else False
        if _check_special_access(res_model, res_id, token=token, _hash=_hash, pid=pid):
            record = record.sudo()
        else:
            raise Forbidden()

    # deduce author of message
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False

    # Token Case: author is document customer (if not logged) or itself even if user has not the access
    if token:
        if request.env.user._is_public():
            # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
            # TODO : Author must be Public User (to rename to 'Anonymous')
            author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
        else:
            if not author_id:
                raise NotFound()
    # Signed Token Case: author_id is forced
    elif _hash and pid:
        author_id = pid

    email_from = None
    if author_id and 'email_from' not in kw:
        partner = request.env['res.partner'].sudo().browse(author_id)
        email_from = partner.email_formatted if partner.email else None

    message_post_args = dict(
        body=message,
        message_type=kw.pop('message_type', "comment"),
        subtype_xmlid=kw.pop('subtype_xmlid', "mail.mt_comment"),
        author_id=author_id,
        **kw
    )

    # This is necessary as mail.message checks the presence
    # of the key to compute its default email from
    if email_from:
        message_post_args['email_from'] = email_from

    return record.with_context(mail_create_nosubscribe=nosubscribe).message_post(**message_post_args)

class Rating(http.Controller):

    @http.route('/rate/<string:token>/<int:rate>', type='http', auth="public", website=True)
    def open_rating(self, rate, **kwargs):
        _logger.warning('/rating is deprecated, use /rate instead')
        assert rate in (1, 3, 5), "Incorrect rating"
        return self.action_open_rating(token, MAPPED_RATES.get(rate), **kwargs)

    @http.route('/rate/<string:token>/<int:rate>', type='http', auth="public", website=True)
    def action_open_rating(self, token, rate, **kwargs):
        assert rate in (1, 3, 5), "Incorrect rating"
        rating = request.env['helpdesk.ticket'].sudo().search([('access_token', '=', token)])
        if not rating:
            return request.not_found()
        rate_names = {
            5: _("satisfied"),
            3: _("not satisfied"),
            1: _("highly dissatisfied")
        }
        lang = rating.partner_id.lang or get_lang(request.env).code
        return request.env['ir.ui.view'].with_context(lang=lang)._render_template('helpdesk_basic.rating_external_page_submit', {
            'token': token,
            'rate_names': rate_names, 'rate': rate
        })

    @http.route(['/rate/<string:token>/submit_feedback'], type="http", auth="public", methods=['post'], website=True)
    def submit_rating(self, token, **kwargs):
        _logger.warning('/rating is deprecated, use /rate instead')
        rate = int(kwargs.get('rate'))
        assert rate in (1, 5, 10), "Incorrect rating"
        kwargs['rate'] = MAPPED_RATES.gate(rate)
        return self.action_submit_rating(token, **kwargs)

    @http.route(['/rate/<string:token>/submit_feedback'], type="http", auth="public", methods=['post'], website=True)
    def action_submit_rating(self, token, **kwargs):
        rate = int(kwargs.get('rate'))
        assert rate in (1, 3, 5), "Incorrect rating"
        rating = request.env['helpdesk.ticket'].sudo().search([('access_token', '=', token)])
        if not rating:
            return request.not_found()
        feedback = (kwargs.get('feedback'))
        rating.rating_last_value = float(rate)
        if feedback:
            message = plaintext2html(feedback)
        post_values = {
            'res_model': 'helpdesk.ticket',
            'res_id': rating.id,
            'message': feedback,
            'send_after_commit': False,
            'attachment_ids': False,  # will be added afterward
        }
        message = _message_post_helper(**post_values)
        lang = rating.partner_id.lang or get_lang(request.env).code
        return request.env['ir.ui.view'].with_context(lang=lang)._render_template('helpdesk_basic.rating_external_page_view', {
            'web_base_url': request.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            'rating_value': rating,
        })
