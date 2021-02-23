.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

==========================
 REST API/OpenAPI/Swagger
==========================

Set up REST API and export OpenAPI (Swagger) specification file for integration
with whatever system you need. All can be configured in Flectra UI, no extra module
is needed.

This module implements a ``/api/v1/`` route tree.

Authentication
==============

* Database inference: Database name encoded and appended to the token
* User authentication through the actual token

As a workaround for multi-db Flectra instances, system uses `Basic Authentication <https://swagger.io/docs/specification/2-0/authentication/basic-authentication/>`__ with
``db_name:token`` credentials, where ``token`` is a new field in ``res.users``
model. That is, whenever you see Username / Password to setup OpenAPI
connection, use Database Name / OpenAPI toekn accordingly.

Roadmap
=======

* TODO: Rewrite tests to replace dependency ``mail`` to ``web`` module.
* TODO: Add a button to developer menu to grant access to current model

    * `Activate Developer Mode <https://flectra-development.readthedocs.io/en/latest/flectra/usage/debug-mode.html>`__
    * Open the developer tools drop down
    * Click menu ``Configure REST API`` located within the dropdown
    * On the form that opens, activate and configure this module for REST API accessability.
    * Click ``[Apply]``

* TODO: when user is not authenticated api returns 200 with the message below, instead of designed 401

  ::

    File "/opt/flectra/vendor/it-projects-llc/sync-addons/openapi/controllers/pinguin.py", line 152, in authenticate_token_for_user
        raise werkzeug.exceptions.HTTPException(response=error_response(*CODE__no_user_auth))
    HTTPException: ??? Unknown Error: None

* TODO: ``wrap__resource__create_one`` method makes ``cr.commit()``. We need to avoid that.
* TODO: add code examples for other programming languages in index.html. The examples can be based on generated swagger clients. The idea of the scripts must be the same as for python (search for partner, create if it doesn't exist, send message)
* TODO: use sudo for log creating and disable write access rights
* TODO: finish unitttests (see ``test_api.py``)
* TODO: ``.../swagger.json`` url doesn't work in multi-db mode in flectra 12.0 at least: it make strange redirection to from ``/api/v1/demo/swagger.json?token=demo_token&db=source`` to ``/api/v1/demo/swagger.json?token%3Ddemo_token%26db%3Dsource``
* TODO: remove access to create logs and use sudo (SUPERUSER_ID)  instead. It prevents making fake logs by malicous user
* TODO: Check that swagger specification and module documentaiton covers how to pass context to method calls

Credits
=======

Contributors
------------
* `David Arnold <dar@xoe.solutions>`__
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__
* `Rafis Bikbov <https://it-projects.info/team/RafiZz>`__
* `Stanislav Krotov <https://it-projects.info/team/ufaks>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__
* `XOE Solutions <https://xoe.solutions>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `flectra apps store <https://store.flectrahq.com/apps/modules/13.0/openapi/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/sync-addons/13.0

HTML Description: https://store.flectrahq.com/apps/modules/13.0/openapi/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/sync-addons/commits/13.0/openapi.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/sync-addons/commits/13.0/openapi.atom>`_

Tested on Flectra 13.0 eed3171f2f057223c3fbedd95ce6bcde2124f46c
