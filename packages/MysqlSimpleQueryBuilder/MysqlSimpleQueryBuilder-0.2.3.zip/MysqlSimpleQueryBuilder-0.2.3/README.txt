
**************************
MySql Simple Query Builder
**************************
Following the rule **simple easy, complex possibe**, *MySql Simple Query Builder* provides API for 
basic queries, nested transactions, and aid in complex query building and profiling.

DML
===

SELECT
------
The following modes are supported:

 * counting: 
 
   .. code-block:: python

      db.count('customer', {'storeId' : 1}) 
      # 326L
        
 * single row's field value: 
 
   .. code-block:: python

      db.one(('firstName',), 'customer', {'customerId' : 1}) 
      # u'MARY'
      
 * single row's fields value dictionary: 
 
   .. code-block:: python

      db.one(('firstName', 'lastName'), 'customer', {'customerId' : 1})
      # {'firstName': u'MARY', 'lastName': u'SMITH'}
      
 * multiple rows' single field value projection:
 
   .. code-block:: python

      db.select(('firstName',), 'customer', {'customerId' : (1, 2)})
      # (u'MARY', u'PATRICIA')
        
 * multiple rows' fields value tuple:
   
   .. code-block:: python

      db.select(('firstName', 'lastName'), 'customer', {'customerId' : (1, 2)})
      # ({'firstName': u'MARY', 'lastName': u'SMITH'}, {'firstName': u'PATRICIA', 'lastName': u'JOHNSON'})
  
*WHERE* condition is a conjunction. Supported arguments are ones support by underlying library, 
*MySQLdb*, and its escaping functionality:
    
  * None,
  * int (long, float, Decimal),
  * datetime (date),
  * unicode (str),
  * tuple of int (list of int),

Besides supported are *ORDER BY* and *LIMIT*.

Complex query
-------------
.. code-block:: python

   sql = '''
     SELECT c.first_name `firstName`, c.last_name `lastName`
     FROM customer c
     JOIN store    s USING(store_id)
     JOIN staff    t ON s.manager_staff_id = t.staff_id
     {0} AND t.email LIKE {1}
   '''
   db.query(
     # escape % as % operator is used by MySQLdb
     sql.format('{where}', db.quote('%%@sakilastaff.com')),
     {'c.active' : True},
     limit = 1
   ).fetchall()
   # ({'firstName': u'MARY', 'lastName': u'SMITH'},)
   
Or the same with cursor:

.. code-block:: python

   sql = '''
     SELECT c.first_name `firstName`, c.last_name `lastName`
     FROM customer c
     JOIN store    s USING(store_id)
     JOIN staff    t ON s.manager_staff_id = t.staff_id
     WHERE c.active = :active AND t.email LIKE :email
     LIMIT 0, 1
   '''
   cursor = db.cursor(dict)
   cursor.execute(sql, {'active' : True, 'email' : '%@sakilastaff.com'})
   cursor.fetchall()
   # ({'firstName': u'MARY', 'lastName': u'SMITH'},)

INSERT
------
Supports single row insert.

UPDATE
------
Supports one table at a time. Has the same *WHERE* features as *SELECT*.

DELETE
------
Supports one table at a time. Has the same *WHERE* features as *SELECT*.


Test
====
Test suite is built against `Sakila test database <http://dev.mysql.com/doc/sakila/en/index.html>`_ 
available at *MySQL* site. Besides allowing further refacotring, it provides examples of usage.
