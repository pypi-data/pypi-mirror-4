.. py:currentmodule:: Products.ZSPARQLMethod.Method

Python API
==========

When writing a Python Script, through-the-web and stored in the ZODB,
you would normally send queries to a `ZSPARQLMethod` instance. Use the
method as a function (:py:meth:`.ZSPARQLMethod.__call__`), it will box
its arguments according to the method's argument spec (see
:ref:`zsparqlmethod-properties`).

The underlying module-level API is also documented below. It can only be
used from normal on-disk Python code.


The ZSPARQLMethod class
-----------------------

.. autoclass:: Products.ZSPARQLMethod.Method.ZSPARQLMethod
    :members: __call__, index_html, test_html, map_arguments, execute

.. autoclass:: Products.ZSPARQLMethod.Method.MethodResult


:py:mod:`Products.ZSPARQLMethod.Method` module
----------------------------------------------

.. automodule:: Products.ZSPARQLMethod.Method
    :members: query_and_get_result, run_with_timeout, parse_arg_spec,
     map_arg_values, interpolate_query, interpolate_query_html
