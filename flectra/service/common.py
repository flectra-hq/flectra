# -*- coding: utf-8 -*-

import logging

import flectra.release
import flectra.tools
from flectra.tools.translate import _

from . import security

_logger = logging.getLogger(__name__)

RPC_VERSION_1 = {
        'server_version': flectra.release.version,
        'server_version_info': flectra.release.version_info,
        'server_serie': flectra.release.serie,
        'protocol_version': 1,
}

def exp_login(db, login, password):
    # TODO: legacy indirection through 'security', should use directly
    # the res.users model
    res = security.login(db, login, password)
    msg = res and 'successful login' or 'bad login or password'
    _logger.info("%s from '%s' using database '%s'", msg, login, db.lower())
    return res or False

def exp_authenticate(db, login, password, user_agent_env):
    res_users = flectra.registry(db)['res.users']
    return res_users.authenticate(db, login, password, user_agent_env)

def exp_version():
    return RPC_VERSION_1

def exp_about(extended=False):
    """Return information about the OpenERP Server.

    @param extended: if True then return version info
    @return string if extended is False else tuple
    """

    info = _('See http://flectrahq.com')

    if extended:
        return info, flectra.release.version
    return info

def exp_set_loglevel(loglevel, logger=None):
    # TODO Previously, the level was set on the now deprecated
    # `flectra.netsvc.Logger` class.
    return True

def dispatch(method, params):
    g = globals()
    exp_method_name = 'exp_' + method
    if exp_method_name in g:
        return g[exp_method_name](*params)
    else:
        raise Exception("Method not found: %s" % method)
