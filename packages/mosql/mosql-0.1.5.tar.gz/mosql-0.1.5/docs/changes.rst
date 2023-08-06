
The Changes
===========

v0.1.5
------

1. refined the :py:mod:`mosql.mysql`.
2. both PostgreSQL and MySQL with MoSQL passed all of the injection tests from `sqlmap <http://sqlmap.org/>`_.

v0.1.4
------

1. fixed the dumped value of datetime, date and time

v0.1.3
------

1. reverted the #3 changes in the previous version.
2. make the rows order by nothing by default.

v0.1.2
------

1. added the :py:mod:`mosql.mysql`.
2. make :py:meth:`mosql.result.Model.seek` respect the arguments from users.
3. make :py:attr:`~mosql.result.Model.group_by` use the value of :py:attr:`~mosql.result.Model.identify_by`, by default.
4. stop using the value of :py:attr:`~mosql.result.Model.identify_by` as :py:attr:`~mosql.result.Model.order_by`.

v0.1.1
------

1. added the :py:mod:`mosql.json`.
2. added the :py:meth:`mosql.result.Model.customize`.
3. supports using attribute to access :py:class:`~mosql.result.Model`.
4. allows customizing insert, select, update and delete by the class methods of a :py:class:`~mosql.result.Model`.
5. respects the ``column_names`` when do a select.
6. fixed the wrong sql without specifying ``identify_by``.
7. fixed the SQL dumped with None. (issue `#1 <https://github.com/moskytw/mosql/issues/1>`_)
