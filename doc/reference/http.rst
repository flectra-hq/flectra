:banner: banners/flectra_web_controllers.jpg

===============
Web Controllers
===============

.. _reference/http/routing:

Routing
=======

.. autofunction:: flectra.http.route

.. _reference/http/request:

Request
=======

The request object is automatically set on :data:`flectra.http.request` at
the start of the request

.. autoclass:: flectra.http.WebRequest
    :members:
    :member-order: bysource
.. autoclass:: flectra.http.HttpRequest
    :members:
.. autoclass:: flectra.http.JsonRequest
    :members:

Response
========

.. autoclass:: flectra.http.Response
    :members:
    :member-order: bysource

    .. maybe set this to document all the fine methods on Werkzeug's Response
       object? (it works)
       :inherited-members:

.. _reference/http/controllers:

Controllers
===========

Controllers need to provide extensibility, much like
:class:`~flectra.models.Model`, but can't use the same mechanism as the
pre-requisites (a database with loaded modules) may not be available yet (e.g.
no database created, or no database selected).

Controllers thus provide their own extension mechanism, separate from that of
models:

Controllers are created by :ref:`inheriting <python:tut-inheritance>` from

.. autoclass:: flectra.http.Controller

and defining methods decorated with :func:`~flectra.http.route`::

    class MyController(flectra.http.Controller):
        @route('/some_url', auth='public')
        def handler(self):
            return stuff()

To *override* a controller, :ref:`inherit <python:tut-inheritance>` from its
class and override relevant methods, re-exposing them if necessary::

    class Extension(MyController):
        @route()
        def handler(self):
            do_before()
            return super(Extension, self).handler()

* decorating with :func:`~flectra.http.route` is necessary to keep the method
  (and route) visible: if the method is redefined without decorating, it
  will be "unpublished"
* the decorators of all methods are combined, if the overriding method's
  decorator has no argument all previous ones will be kept, any provided
  argument will override previously defined ones e.g.::

    class Restrict(MyController):
        @route(auth='user')
        def handler(self):
            return super(Restrict, self).handler()

  will change ``/some_url`` from public authentication to user (requiring a
  log-in)
