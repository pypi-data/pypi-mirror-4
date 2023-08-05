Configuring from ZMI
====================

`ZSPARQLMethod` is intended to be used in a Zope 2 application, in a fashion
similar to `ZSQLMethod`. You create an instance, configure its `id` and
`title`, write a query template and specify arguments. Afterwards the method
can be called from a Python script, page template, or even as a REST service.


.. _zsparqlmethod-properties:

Properties of a ZSPARQLMethod
-----------------------------

SPARQL endpoint URL
    The URL of a SPARQL endpoint where queries are sent. See
    SparqlImplementations_ on the w3.org wiki for a list of server
    implementations. To avoid entering this value for each new method
    you can set a ``ZSPARQLMETHOD_DEFAULT_ENDPOINT`` property on a
    parent object and it will be used to set the endpoint.

Timeout
    Queries may take a long time to complete. In order to avoid blocking a
    Zope publisher thread for too long, you may specify a timeout value.
    The query executes in a separate thread, and if it takes too long, the
    publisher returns an error; the query thread will terminate when it
    finally gets a response.

Arguments
    Definition of the arguments this method expects to receive. It will be
    parsed using :py:func:`.parse_arg_spec`.

Query
    The SPARQL query template, processed using `string.Template`_ from the
    Python standard library.

.. _SparqlImplementations: http://www.w3.org/wiki/SparqlImplementations#Query_Engines
.. _`string.Template`: http://docs.python.org/library/string#template-strings


Caching
-------

ZSPARQLMethod implements the ZCacheable_ protocol, so caching of query results
is easy: create a cache manager, then configure the ZSPARQLMethod instance to
use the cache. This is done from the `Cache` ZMI tab.

.. _ZCacheable: http://docs.zope.org/zope2/zope2book/ZopeServices.html#caching-services

The cache is invalidated whenever the ZSPARQLMethod object is edited. Cache
keys are calculated based on the arguments received.


.. _tutorial:

Tutorial
--------

Select "Z SPARQL Method" from the ZMI's `add` menu:

.. image:: zmi-screenshots/1.png

Enter an ID and a title and click `Add`:

.. image:: zmi-screenshots/2.png

The new method will appear in the folder listing:

.. image:: zmi-screenshots/3.png

We need to enter a SPARQL endpoint URL. All queries will be sent to this
address. Also, enter the query template and arguments specification:

.. image:: zmi-screenshots/4.png

Now let's run a test query from the `test` tab. Initially no argumenet is set,
so we are shown variable's placeholder:

.. image:: zmi-screenshots/5.png

After we enter a value, we submit the query and get a result:

.. image:: zmi-screenshots/6.png
