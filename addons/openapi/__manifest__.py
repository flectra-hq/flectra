# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    "name": """REST API/OpenAPI/Swagger""",
    "summary": """RESTful API to integrate flectra with whatever system you need""",
    "category": "",
    "images": ["images/openapi-swagger.png"],
    "version": "3.0.1.2.4",
    "application": False,
    "author": "FlectraHQ Inc, IT-Projects LLC, Ivan Yelizariev",
    "support": "help@itpp.dev",
    "license": "LGPL-3",
    "depends": ["base_api", "mail"],
    "external_dependencies": {
        "python": ["bravado_core", "swagger_spec_validator", "jsonschema<4"],
        "bin": [],
    },
    "data": [
        "security/openapi_security.xml",
        "security/ir.model.access.csv",
        "security/res_users_token.xml",
        "views/openapi_view.xml",
        "views/res_users_view.xml",
        "views/ir_model_view.xml",
    ],
    "demo": ["demo/openapi_demo.xml", "demo/openapi_security_demo.xml"],
    "post_load": "post_load",
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
