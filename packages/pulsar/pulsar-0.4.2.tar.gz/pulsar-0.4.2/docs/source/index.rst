================
Pulsar
================

An asynchronous concurrent framework for Python. Tested in Windows and Linux,
it requires python 2.6 up to python 3.3 in a single code base.


.. toctree::
   :maxdepth: 1
   
   overview
   changelog
   design
   api
   http
   settings
   

.. _apps-framework:

.. module:: pulsar.apps

Application Framework
=========================

Pulsar application framework is built on top of :mod:`pulsar` concurrent
framework. It is designed to facilitate the development of server-side applications
such as web servers, task queues or any asynchronous and/or parallel 
idea you may have in mind.
To write a new application, you subclass :class:`pulsar.Application` or
any of the battery included applications listed below, and implement some of
the callbacks available.

Currently, the package is shipped with the following battery included
applications which can be found in the :mod:`pulsar.apps` module:

.. toctree::
   :maxdepth: 1
   
   apps/socket
   apps/wsgi
   apps/rpc
   apps/tasks
   apps/websockets
   apps/test
   apps/shell
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`