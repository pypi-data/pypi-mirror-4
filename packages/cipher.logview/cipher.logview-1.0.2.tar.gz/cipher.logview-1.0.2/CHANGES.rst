Changes
=======

1.0.2 (2012-12-13)
------------------

- Handle views that are methods (e.g. <browser:page class="..."
  attribute="..." />): show the class and method name, the correct source
  location of the method, and the context.  Previously you'd see
  "Calling __builtin__.instancemethod - no source information available".

- Add cipher.logview.format_tb.  Use it to format exception tracebacks
  (requires Dozer 0.3).

- Add support for __traceback_supplement__ in format_stack/format_tb.
  This is used by Zope Page Templates to indicate the page template
  filename/line/column/expression.


1.0.1 (2012-12-07)
------------------

- Handle dynamic subclasses created by <browser:page> and show the real class.

- Bugfix: sometimes enumerating interfaces of the context could trigger a
  ForbiddenAttribute exception.

- Mention logging levels gotcha in README.rst.


1.0.0 (2012-12-05)
------------------

- First public release.

