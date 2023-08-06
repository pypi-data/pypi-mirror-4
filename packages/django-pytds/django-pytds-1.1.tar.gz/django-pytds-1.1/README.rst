Django PYTDS Database Backend
=============================

`Django-pytds`_ is a port of `Django-mssql`_ that provies a Django database backend for Microsoft SQL Server using pure python TDS implementation.

TODO Documentation

Requirements
------------

    * Python 2.7
    * pytds_

SQL Server Versions
-------------------

Supported Versions:
    * 2005
    * 2008
    * 2008r2

The SQL Server version will be detected upon initial connection.

Django Version
--------------

The current version of django-mssql supports Django 1.2 thru 1.4. Django versions
1.0 and 1.1 are no longer actively supported, but working versions may be
found with the tags ``legacy-1.0`` and ``legacy-1.1``.

References
----------

    * DB-API 2.0 specification: http://www.python.org/dev/peps/pep-0249/

.. _`Django-mssql`: https://bitbucket.org/Manfre/django-mssql
.. _`Django-pytds`: https://bitbucket.org/denisenkom/django-pytds
.. _django-mssql.readthedocs.org: http://django-mssql.readthedocs.org/
.. _pytds: https://github.com/denisenkom/pytds
