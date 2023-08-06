Using :mod:`zope.exceptions`
============================

This module extends the standard library's :mod:`traceback` module, allowing
application code to add additional information to the formatted tracebacks
using specially-named variables in the scope of a given frame.


Annotating Application Code
---------------------------

:py:data:`__traceback_supplement__`
+++++++++++++++++++++++++++++++++++

This variable can be defined either at either local or global scope.
The formatting functions treat objects with this name as though they support
the :py:class:`~zope.exceptions.interfaces.ITracebackSupplement` interface.
The various attributes (all optional) of that interface will be used to
add structured information to the formatted traceback.

For example, assuming your code renders a template:

.. doctest::

   >>> import os
   >>> class Supplement(object):
   ...     def __init__(self, template_file, source):
   ...         self.source_url = 'file://%s' % os.path.abspath(template_file)
   ...         self.source = source
   ...     def getInfo(self):
   ...         return self.source
   >>> def render_w_supplement(template_file, options):
   ...     source = open(template_file).read()
   ...     __traceback_supplement__ = Supplement(template_file, source)

Here, the filename and source of the template will be rendered as part of
the traceback.


:py:data:`__traceback_info__`
+++++++++++++++++++++++++++++

This variable can only be defined at local scope.  It will be converted to a
string when added to the formatted traceback.

.. doctest::

   >>> def render_w_info(template_file, options):
   ...     source = open(template_file).read()
   ...     __traceback_info__ = '%s\n\n%s' % (template_file, source)


API Functions
-------------
Three API functions support these features when formatting Python
exceptions and their associated tracebacks:

:py:func:`~zope.exceptions.exceptionformatter.format_exception`
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Use this API to format an exception and traceback as a string, using
the special annotations.  E.g.:

.. doctest::

   >>> import sys
   >>> from zope.exceptions import format_exception
   >>> try:
   ...     raise ValueError('demo')
   ... except:
   ...     t, v, tb = sys.exc_info()
   ...     report = format_exception(t, v, tb)
   ...     del tb # avoid a leak
   ...     # Now do something with report, e.g., send e-mail.


:py:func:`~zope.exceptions.exceptionformatter.print_exception`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Use this API to write the formated exception and traceback to a file-like
object, using the special annotations.  E.g.:

.. doctest::

   >>> from zope.exceptions import print_exception
   >>> try:
   ...     raise ValueError('demo')
   ... except:
   ...     t, v, tb = sys.exc_info()
   ...     print_exception(t, v, tb, file=sys.stderr)
   ...     del tb # avoid a leak


:py:func:`~zope.exceptions.exceptionformatter.extract_stack`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Use this API to format just the traceback as a list of string,s using the
special annotations.  E.g.:

.. doctest::

   >>> import sys
   >>> from zope.exceptions import extract_stack
   >>> try:
   ...     raise ValueError('demo')
   ... except:
   ...     for line in extract_stack(sys.exc_info()[2].tb_frame):
   ...         pass # do something with each line
