:banner: banners/flectra_testing_modules.jpg

.. _reference/testing:


===============
Testing Modules
===============

Flectra provides support for testing modules using unittest.

To write tests, simply define a ``tests`` sub-package in your module, it will
be automatically inspected for test modules. Test modules should have a name
starting with ``test_`` and should be imported from ``tests/__init__.py``,
e.g.

.. code-block:: text

    your_module
    |-- ...
    `-- tests
        |-- __init__.py
        |-- test_bar.py
        `-- test_foo.py

and ``__init__.py`` contains::

    from . import test_foo, test_bar

.. warning::

    test modules which are not imported from ``tests/__init__.py`` will not be
    run

the test runner would only run modules added to two lists
``fast_suite`` and ``checks`` in ``tests/__init__.py``.

The test runner will simply run any test case, as described in the official
`unittest documentation`_, but Flectra provides a number of utilities and helpers
related to testing Flectra content (modules, mainly):

.. autoclass:: flectra.tests.common.TransactionCase
    :members: browse_ref, ref

.. autoclass:: flectra.tests.common.SingleTransactionCase
    :members: browse_ref, ref

.. autoclass:: flectra.tests.common.SavepointCase

.. autoclass:: flectra.tests.common.HttpCase
    :members: browse_ref, ref, url_open, phantom_js

By default, tests are run once right after the corresponding module has been
installed. Test cases can also be configured to run after all modules have
been installed, and not run right after the module installation:

.. autofunction:: flectra.tests.common.at_install

.. autofunction:: flectra.tests.common.post_install

The most common situation is to use
:class:`~flectra.tests.common.TransactionCase` and test a property of a model
in each method::

    class TestModelA(common.TransactionCase):
        def test_some_action(self):
            record = self.env['model.a'].create({'field': 'value'})
            record.some_action()
            self.assertEqual(
                record.field,
                expected_field_value)

        # other tests...

.. note::

    Test methods must start with ``test_``

Running tests
-------------

Tests are automatically run when installing or updating modules if
:option:`--test-enable <flectra-bin --test-enable>` was enabled when starting the
Flectra server.

As of Flectra, running tests outside of the install/update cycle is not
supported.

.. _unittest documentation: https://docs.python.org/3/library/unittest.html
