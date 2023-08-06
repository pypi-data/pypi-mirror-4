# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import unittest
import datetime
import decimal

import test
import builder


class BenchmarkQueryBuilder(unittest.TestCase):

  testee = None
  repeat = 256


  def setUp(self):
    self.testee = builder.QueryBuilder(**test.config)

  def _report(self, native, qb):
    # At least twice as slow
    self.assertGreaterEqual(1 - qb.total_seconds() / native.total_seconds(), -1)
    # At least 100qps
    self.assertGreaterEqual(1 / qb.total_seconds() * self.repeat, 100)
    
    print '{0:.0f}qps, {1:+.2f}%'.format(
      1 / qb.total_seconds() * self.repeat,
      (1 - qb.total_seconds() / native.total_seconds()) * 100
    )

  def testSelectOneFieldNoFilter(self):
    sql = '''
      SELECT country
      FROM country 
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.select(('country',), 'country')
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testSelectManyFieldsNoFilter(self):
    sql = '''
      SELECT country_id, country, last_update
      FROM country 
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.DictCursor) 
      cursor.execute(sql)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.select(('countryId', 'country', 'lastUpdate'), 'country')
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testSelectOneField(self):
    where = {
      'rentalId' : (1725, 5326, 13176, 14762, 9470, 9688, 10289), 
      'amount'   : decimal.Decimal('4.99')
    }
    
    sql       = '''
      SELECT amount
      FROM payment
      WHERE rental_id IN %(rentalId)s AND amount = %(amount)s
      ORDER BY staff_id
      LIMIT 0, 3
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, where)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.select(('amount',), 'payment', where, (('staffId', 'asc'),), (0, 3))
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testSelectManyFields(self):
    where = {
      'rentalId' : (1725, 5326, 13176, 14762, 9470, 9688, 10289), 
      'amount'   : decimal.Decimal('4.99')
    }
        
    sql = '''
      SELECT payment_id, customer_id, staff_id, rental_id, amount, payment_date
      FROM payment
      WHERE rental_id IN %(rentalId)s AND amount = %(amount)s
      ORDER BY staff_id
      LIMIT 0, 3
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.DictCursor) 
      cursor.execute(sql, where)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.select(
        ('paymentId', 'customerId', 'staffId', 'rentalId', 'amount', 'paymentDate'), 
        'payment', 
        where,
        (('staffId', 'asc'),),
        (0, 3)
      )
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testOneOneField(self):
    where = {
      'rentalId' : (1725, 5326, 13176, 14762, 9470, 9688, 10289), 
      'amount'   : decimal.Decimal('4.99')
    }
    
    sql = '''
      SELECT payment_date
      FROM payment
      WHERE rental_id IN %(rentalId)s AND amount = %(amount)s
      ORDER BY staff_id
      LIMIT 0, 1
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, where)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.one(('paymentDate',), 'payment', where, (('staffId', 'asc'),))
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testOneManyFields(self):
    where = {
      'rentalId' : (1725, 5326, 13176, 14762, 9470, 9688, 10289), 
      'amount'   : decimal.Decimal('4.99')
    }
    
    sql = '''
      SELECT payment_id, customer_id, staff_id, rental_id, amount, payment_date
      FROM payment
      WHERE rental_id IN %(rentalId)s AND amount = %(amount)s
      ORDER BY staff_id
      LIMIT 0, 1
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, where)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.one(
        ('paymentId', 'customerId', 'staffId', 'rentalId', 'amount', 'paymentDate'), 
        'payment', 
        where,
        (('staffId', 'asc'),)
      )
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)    
    
  def testCount(self):
    where = {
      'rentalId' : (1725, 5326, 13176, 14762, 9470, 9688, 10289), 
      'amount'   : decimal.Decimal('4.99')
    }
    
    sql = '''
      SELECT COUNT(*)
      FROM payment
      WHERE rental_id IN %(rentalId)s AND amount = %(amount)s
      ORDER BY staff_id
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, where)
      cursor.fetchall()
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.count('payment', where)
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testQuery(self):
    where = {
      'ad.address2'  : None,
      'ct.cityId'    : 300,
      'ad.addressId' : (1, 2, 3) 
    }
    
    sql = '''
      SELECT address, district
      FROM (
        SELECT ad.*
        FROM country cn
        JOIN city    ct USING(country_id)
        JOIN address ad USING(city_id)
        WHERE ad.address2 IS %(ad.address2)s AND ct.city_id = %(ct.cityId)s AND 
          ad.address_id IN %(ad.addressId)s AND city_id > 50
        ORDER BY ad.address_id DESC
     ) `inner`
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, where)
      cursor.fetchall()
    native = datetime.datetime.now() - native

    sql = '''
      SELECT address, district
      FROM (
        SELECT ad.*
        FROM country cn
        JOIN city    ct USING(country_id)
        JOIN address ad USING(city_id)
        {where} AND city_id > 50
        {order}
     ) `inner`
    '''
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.query(sql, where, [('ad.addressId', 'desc')])
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
  def testInsert(self):
    self.testee.begin()
    
    values = {
      'address'    : '1566 Inegl Manor',
      'address2'   : None,
      'district'   : 'Mandalay',
      'cityId'     : 361,
      'postalCode' : '53561',
      'phone'      : '705814003527',
      'lastUpdate' : datetime.datetime(2011, 11, 13, 12, 10, 07)
    }
    
    sql = '''
      INSERT INTO address(address, address2, district, city_id, postal_code, phone) 
        VALUES(%(address)s, %(address2)s, %(district)s, %(cityId)s, %(postalCode)s, %(phone)s)
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, values)
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.insert('address', values)
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
    self.testee.rollback()
   
  def testUpdate(self):
    self.testee.begin()
    
    set    = {'filmId' : 1, 'storeId' : 2, 'lastUpdate' : datetime.datetime(2011, 11, 13, 12, 10, 07)}
    params = dict(set, inventoryId = (-1, -2, -3, -4, -5))
    sql = '''
      UPDATE inventory
      SET 
        film_id     = %(filmId)s,
        store_id    = %(storeId)s,
        last_update = %(lastUpdate)s
      WHERE inventory_id IN %(inventoryId)s
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, params)
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.update('inventory', set, {'inventoryId' : (-1, -2, -3, -4, -5)})
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
    self.testee.rollback()
   
  def testDelete(self):
    self.testee.begin()
    
    where = {'inventoryId' : (-1, -2, -3, -4, -5), 'filmId' : 0, 'storeId' : 0}
    sql = '''
      DELETE
      FROM inventory
      WHERE inventory_id IN %(inventoryId)s AND film_id = %(filmId)s AND store_id = %(storeId)s
    '''
    native = datetime.datetime.now()
    for _ in xrange(self.repeat):
      cursor = self.testee.cursor(builder.cursors.Cursor) 
      cursor.execute(sql, where)
    native = datetime.datetime.now() - native
    
    qb = datetime.datetime.now()
    for _ in xrange(self.repeat):
      self.testee.delete('inventory', where)
    qb = datetime.datetime.now() - qb
    
    self._report(native, qb)
    
    self.testee.rollback()
