.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library which assists programmer to use SQL.

It has two major parts:

The first part is SQL builders which help you to build SQL with common Python data types:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the Python data types to SQL statements. You can find more exmaples in :py:mod:`mosql.common`.

The second part is a easy-to-use interface of the result set. We assume there is a table like this:

::

    db=> select * from detail where person_id='mosky';
     detail_id | person_id |   key   |   val            
    -----------+-----------+---------+---------
             4 | mosky     | address | address
             3 | mosky     | address | ...
            10 | mosky     | email   | email
             6 | mosky     | email   | ...
             1 | mosky     | email   | ...
    (5 rows)

After setuped the :py:class:`mosql.result.Model`, it is more easy to access this table:

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [1, 6, 10], 'val': ['email', '...', '...'], 'key': 'email'}

For simplicity, the :py:class:`~mosql.result.Model` is rendered as a dict, and the lists in the :py:class:`~mosql.result.Model` are not simple lists, too. They are :py:class:`mosql.result.Column` which act as a proxy. It will redirect your operations on it to the :py:class:`~mosql.result.Model` which it belongs to.

:ref:`tutorial-of-model` describes more details about how to use :py:class:`mosql.result.Model`.

Installation
------------

It is easy to install MoSQL with `pip`:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

The documentions
================

.. toctree::
    :maxdepth: 2

    result.rst
    builders.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

