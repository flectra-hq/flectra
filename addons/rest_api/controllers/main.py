# Part of Flectra. See LICENSE file for full copyright and licensing details.

import functools
import hashlib
import os
import werkzeug.wrappers
import ast
try:
    import simplejson as json
except ImportError:
    import json
import flectra
from flectra import http
from flectra.http import request
from flectra import fields
from ..rest_exception import *

_logger = logging.getLogger(__name__)


def eval_json_to_data(modelname, json_data, create=True):
    Model = request.env[modelname]
    model_fiels = Model._fields
    field_name = [name for name, field in Model._fields.items()]
    values = {}
    for field in json_data:
        if field not in field_name:
            continue
        if field not in field_name:
            continue
        val = json_data[field]
        if not isinstance(val, list):
            values[field] = val
        else:
            values[field] = []
            if not create and isinstance(model_fiels[field], fields.Many2many):
                values[field].append((5,))
            for res in val:
                recored = {}
                for f in res:
                    recored[f] = res[f]
                if isinstance(model_fiels[field], fields.Many2many):
                    values[field].append((4, recored['id']))

                elif isinstance(model_fiels[field], flectra.fields.One2many):
                    if create:
                        values[field].append((0, 0, recored))
                    else:
                        if 'id' in recored:
                            id = recored['id']
                            del recored['id']
                            values[field].append((1, id, recored)) if len(recored) else values[field].append((2, id))
                        else:
                            values[field].append((0, 0, recored))
    return values


def object_read(model_name, params, status_code):
    domain = []
    fields = []
    offset = 0
    limit = None
    order = None
    if 'filters' in params:
        domain += ast.literal_eval(params['filters'])
    if 'field' in params:
        fields += ast.literal_eval(params['field'])
    if 'offset' in params:
        offset = int(params['offset'])
    if 'limit' in params:
        limit = int(params['limit'])
    if 'order' in params:
        order = params['order']

    data = request.env[model_name].search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
    if data:
        return valid_response(status=status_code, data={
            'count': len(data),
            'results': data
        })
    else:
        return object_not_found_all(model_name)


def object_read_one(model_name, rec_id, params, status_code):
    fields = []
    if 'field' in params:
        fields += ast.literal_eval(params['field'])
    try:
        rec_id = int(rec_id)
    except Exception as e:
        rec_id = False

    if not rec_id:
        return invalid_object_id()
    data = request.env[model_name].search_read(domain=[('id', '=', rec_id)], fields=fields)
    if data:
        return valid_response(status=status_code, data=data)
    else:
        return object_not_found(rec_id, model_name)


def object_create_one(model_name, data, status_code):
    try:
        res = request.env[model_name].create(data)
    except Exception as e:
        return no_object_created(e)
    if res:
        return valid_response(status_code, {'id': res.id})


def object_update_one(model_name, rec_id, data, status_code):
    try:
        rec_id = int(rec_id)
    except Exception as e:
        rec_id = None

    if not rec_id:
        return invalid_object_id()

    try:
        res = request.env[model_name].search([('id', '=', rec_id)])
        if res:
            res.write(data)
        else:
            return object_not_found(rec_id, model_name)
    except Exception as e:
        return no_object_updated(e)
    if res:
        return valid_response(status_code, {'desc': 'Record Updated successfully!', 'update': True})


def object_delete_one(model_name, rec_id, status_code):
    try:
        rec_id = int(rec_id)
    except Exception as e:
        rec_id = None

    if not rec_id:
        return invalid_object_id()

    try:
        res = request.env[model_name].search([('id', '=', rec_id)])
        if res:
            res.unlink()
        else:
            return object_not_found(rec_id, model_name)
    except Exception as e:
        return no_object_deleted(e)
    if res:
        return valid_response(status_code, {'desc': 'Record Successfully Deleted!', 'delete': True})


def check_valid_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get('access_token')
        if not access_token:
            info = "Missing access token in request header!"
            error = 'access_token_not_found'
            _logger.error(info)
            return invalid_response(400, error, info)

        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data._get_access_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_token()

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


def generate_token(length=40):
    random_data = os.urandom(100)
    hash_gen = hashlib.new('sha512')
    hash_gen.update(random_data)
    return hash_gen.hexdigest()[:length]


# Read OAuth2 constants and setup token store:
db_name = flectra.tools.config.get('db_name')


# List of REST resources in current file:
#   (url prefix)            (method)     (action)
# /api/auth/get_tokens        POST    - Login in flectra and get access tokens
# /api/auth/delete_tokens     POST    - Delete access tokens from token store


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Login in flectra database and get access tokens:
    @http.route('/api/auth/get_tokens', methods=['POST'], type='http',
                auth='none', csrf=False)
    def api_auth_gettokens(self, **post):
        # Convert http data into json:
        db = post['db'] if post.get('db') else db_name
        username = post['username'] if post.get('username') else None
        password = post['password'] if post.get('password') else None

        # Empty 'db' or 'username' or 'password:
        if not db or not username or not password:
            info = "Empty value of 'db' or 'username' or 'password'!"
            error = 'empty_db_or_username_or_password'
            _logger.error(info)
            return invalid_response(400, error, info)
        # Login in flectra database:
        try:
            request.session.authenticate(db, username, password)
        except:
            # Invalid database:
            info = "Invalid database!"
            error = 'invalid_database'
            _logger.error(info)
            return invalid_response(400, error, info)
        uid = request.session.uid
        # flectra login failed:
        if not uid:
            info = "flectra User authentication failed!"
            error = 'flectra_user_authentication_failed'
            _logger.error(info)
            return invalid_response(401, error, info)
        # Generate tokens
        access_token = request.env['oauth.access_token']._get_access_token(user_id = uid, create = True)

        # Save all tokens in store
        _logger.info("Save OAuth2 tokens of user in store...")

        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                'uid': uid,
                'user_context': request.session.get_context() if uid else {},
                'company_id': request.env.user.company_id.id if uid else 'null',
                'access_token': access_token,
                'expires_in': request.env.ref('rest_api.oauth2_access_token_expires_in').sudo().value,
                }),
        )

    # Delete access tokens from token store:
    @http.route('/api/auth/delete_tokens', methods=['POST'], type='http',
                auth='none', csrf=False)
    def api_auth_deletetokens(self, **post):
        # Try convert http data into json:
        access_token = request.httprequest.headers.get('access_token')
        access_token_data = request.env['oauth.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if not access_token_data:
            info = "No access token was provided in request!"
            error = 'no_access_token'
            _logger.error(info)
            return invalid_response(400, error, info)
        access_token_data.sudo().unlink()
        # Successful response:
        return valid_response(
            200,
            {"desc": 'Token Successfully Deleted', "delete": True}
        )

    @http.route([
        '/api/<model_name>',
        '/api/<model_name>/<id>'
    ], type='http', auth="none", methods=['POST', 'GET', 'PUT', 'DELETE'],
        csrf=False)
    @check_valid_token
    def restapi_access_token(self, model_name=False, id=False, **post):
        Model = request.env['ir.model']
        Model_id = Model.sudo().search([('model', '=', model_name)], limit=1)

        for key, value in post.items():
            ir_model_obj = request.env['ir.model.fields']
            ir_model_field = ir_model_obj.search(
                [('model', '=', model_name), ('name', '=', key)])
            field_type = ir_model_field.ttype
            if field_type == "many2one" or field_type == "one2many" or field_type == "many2many":
                post[key] = int(value)

        if Model_id:
            if Model_id.rest_api:
                return getattr(self, '%s_data' % (
                    request.httprequest.method).lower())(
                    model_name=model_name, id=id, **post)
            else:
                return rest_api_unavailable(model_name)
        return modal_not_found(model_name)

    def get_data(self, model_name=False, id=False, **get):
        if id:
            return object_read_one(model_name, id, get, status_code=200)
        return object_read(model_name, get, status_code=200)

    def put_data(self, model_name=False, id=False, **put):
        return object_update_one(model_name, id, put, status_code=200)

    def post_data(self, model_name=False, **post):
        return object_create_one(model_name, post, status_code=200)

    def delete_data(self, model_name=False, id=False):
        return object_delete_one(model_name, id, status_code=200)
