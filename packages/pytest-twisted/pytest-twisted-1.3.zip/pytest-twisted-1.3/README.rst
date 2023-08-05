.. -*- mode: rst; coding: utf-8 -*-

==============================================================================
pytest-twisted - test twisted code with pytest
==============================================================================


:Authors: Ralf Schmitt <ralf@systemexit.de>
:Version: 1.3
:Date:    2012-11-22
:Download: http://pypi.python.org/pypi/pytest-twisted#downloads
:Code: https://github.com/schmir/pytest-twisted


pytest-twisted is a plugin for pytest, which allows to test code,
which uses the twisted framework. test functions can return Deferred
objects and pytest will wait for their completion with this plugin.

Installation
==================
Install the plugin with::

    pip install pytest-twisted


Using the plugin
==================

The plugin must be enabled. This can be done in the following ways:

1. Run py.test with the --twisted command line option

2. Put the following into conftest.py::

    pytest_plugins = "pytest_twisted"

3. Put the following into pytest.ini::

    [pytest]
    twisted = 1


inlineCallbacks
=================
Using `twisted.internet.defer.inlineCallbacks` as a decorator for test
functions, which take funcargs, does not work. Please use
`pytest.inlineCallbacks` instead::

  @pytest.inlineCallbacks
  def test_some_stuff(tmpdir):
      res = yield threads.deferToThread(os.listdir, tmpdir.strpath)
      assert res == []


That's all.
