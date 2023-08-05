cipher.logview
==============

WSGI middleware that shows you log messages produced during request handling.

Wraps Dozer_ and adds a few features:

- Pretty request timeline for functions decorated with
  ``@cipher.logview.timed``.

- Stack formatter shows the value of ``__traceback_info__`` in each stack
  frame, if a local with that name exists (which is a convention used by
  `zope.exceptions`_\.exceptionformatter).

- A monkey-patch for `zope.browserpage`_\'s ViewPageTemplateFile that logs the
  names of page templates being rendered (enable with ``monkeypatch=True``).

- A monkey-patch for `zope.app.publication`_\'s ZopePublication that logs the
  name of the view class that is being called, and also the representation of
  and interfaces provided by the content object (enable with
  ``monkeypatch=True``).

You'll need this branch of Dozer that contains bugfixes and features not yet
included upstream: https://bitbucket.org/mgedmin/dozer


Usage
-----

Add ``cipher.logview.LogviewMiddleware`` in your WSGI pipeline.

For example, here's an excerpt for a PasteDeploy_-style paster.ini::

    [filter-app:logview]
    use = egg:cipher.logview
    next = main
    loglevel = DEBUG
    keep_tracebacks = yes
    monkeypatch = yes

    # highlighting rules: logview.substring = css-color
    logview.sql = #fee
    logview.txn = #efe

    # traceback highlighting rules: traceback.substring=css-color
    traceback.dozer/ = #ddd
    traceback.python2.7/ = #ccc
    traceback.paste/ = #bbb
    traceback.webob/ = #aaa
    traceback.weberror/ = #999
    traceback.zope/ = #888
    traceback.z3c/ = #888
    traceback.storm/ = #777
    traceback.transaction/ = #666
    traceback.ZODB/ = #555
    traceback.keas/ = #444
    traceback.cipher/ = #840

which lets you optionally enable the middleware from the command line ::

    bin/paster serve paster.ini -n logview


.. Links

.. _Dozer: http://pypi.python.org/pypi/Dozer
.. _PasteDeploy: http://pypi.python.org/pypi/PasteDeploy
.. _zope.exceptions: http://pypi.python.org/pypi/zope.exceptions
.. _zope.browserpage: http://pypi.python.org/pypi/zope.browserpage
.. _zope.app.publication: http://pypi.python.org/pypi/zope.app.publication
