# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import decimal
import datetime

import test
import builder


class TestQueryBuilder(test.TestCase):

  testee = None


  def setUp(self):
    self.testee = builder.QueryBuilder(**test.config)

  def testQuote(self):
    self.assertEqual("'\\' OR 1=1--'",         self.testee.quote("' OR 1=1--"))
    self.assertEqual("'\\' OR 1=1--\xd1\x91'", self.testee.quote(u"' OR 1=1--ё"))
    
    self.assertEqual('123',     self.testee.quote(123))
    self.assertEqual('123',     self.testee.quote(123L))
    self.assertEqual('-123',    self.testee.quote(-123))
    self.assertEqual("'12312'", self.testee.quote('12312'))
    self.assertEqual("'12312'", self.testee.quote(u'12312'))
    self.assertEqual("'12.34'", self.testee.quote(decimal.Decimal('12.34')))
    
    self.assertEqual(('1', '2', '3'), self.testee.quote((1, 2, 3)))
    self.assertEqual("('1', '2', '3')", '%s' % (self.testee.quote((1, 2, 3)),))

    # this is why str list won't work for IN
    self.assertEqual(("'a'", "'b'", "'c'"), self.testee.quote(('a', 'b', "c")))
    self.assertEqual("(\"'a'\", \"'b'\", \"'c'\")", '%s' % (self.testee.quote(('a', 'b', 'c')),))
    self.assertEqual(("'a'", "'b'", "'c\\''"), self.testee.quote(('a', 'b', "c'")))
    self.assertEqual("(\"'a'\", \"'b'\", \"'c\\\\''\")", '%s' % (self.testee.quote(('a', 'b', "c'")),))

  def testToUnderscore(self):
    names = (
      'name', 'nameTo', 'nameToName', 'nameToNameTo',
      'nameToNameToName', 'NameToName',
      'name_to', 'name_to', 'name_to_name'
    )
    expected = (
      'name', 'name_to', 'name_to_name', 'name_to_name_to',
      'name_to_name_to_name', 'name_to_name',
      'name_to', 'name_to', 'name_to_name'
    )

    for i, name in enumerate(names):
      self.assertEqual('`{0}`'.format(expected[i]), self.testee._to_(name))

  def testQuery(self):
    sql = '''
      SELECT address, district
      FROM country cn
      JOIN city    ct USING(country_id)
      JOIN address ad USING(city_id)
    '''

    where = {
      'ad.address2'  : None,
      'ct.cityId'    : 300,
      'ad.addressId' : (1, 2, 3) 
    }
    cursor = self.testee.query(sql, where, [('ad.lastUpdate', 'desc')], 1)
    
    self.assertEqual([{'district': u'Alberta', 'address': u'47 MySakila Drive'}], list(cursor))
    
    
    sql = '''
      SELECT address, district
      FROM (
        SELECT ad.*
        FROM country cn
        JOIN city    ct USING(country_id)
        JOIN address ad USING(city_id)
        {where}
        {order}
     ) `inner`
     {limit}
    '''

    cursor = self.testee.query(sql, where, [('ad.addressId', 'desc')], 1)
    
    self.assertEqual([{'address': u'23 Workhaven Lane', 'district': u'Alberta'}], list(cursor))

  def testSelect(self):
    expected = (u'WAYNE', u'TRACY')
    actual   = self.testee.select(
      ('lastName',), 
      'actor', 
      {'actorId' : range(20, 30), 'lastUpdate' : datetime.datetime(2006, 2, 15, 4, 34, 33)}, 
      (('lastName', 'desc'),), 
      2
    )
    self.assertEqual(expected, actual)

    expected = (
      {'lastName': u'STREEP',  'firstName': u'CAMERON'}, 
      {'lastName': u'PALTROW', 'firstName': u'KIRSTEN'}
    )
    actual = self.testee.select(
      ('lastName', 'firstName'), 
      'actor', 
      {'actorId' : range(20, 30), 'lastUpdate' : datetime.datetime(2006, 2, 15, 4, 34, 33)}, 
      [('lastName', 'desc')], 
      (2, 2)
    )
    self.assertEqual(expected, actual)

  def testOne(self):
    where = {
      'staffId' : range(1, 3),
      'storeId' : range(1, 3),
      'active'  : True
    }
    self.assertEqual(u'Hillyer', self.testee.one(['lastName'], 'staff', where))

    expected = {
      'email'     : u'Jon.Stephens@sakilastaff.com',
      'firstName' : u'Jon',
      'lastName'  : u'Stephens'
    }
    actual = self.testee.one(
      ['firstName', 'lastName', 'email'],
      'staff',
      dict(where, username = 'jon'),
      [('staffId', 'desc'), ('username', 'asc')]
    )
    self.assertEqual(expected, actual)
    
    where['storeId'] = (1,)
    self.assertEqual(u'Hillyer', self.testee.one(['lastName'], 'staff', where))
    self.assertEqual((1,), where['storeId'])

  def testCount(self):
    self.assertEqual(16049, self.testee.count('payment'))
    self.assertEqual(46, self.testee.count('payment', {'customerId' : (1, 2, 3), 'staffId' : 1}))

  def testInsert(self):
    self.testee.begin()

    now = datetime.datetime.now()

    actor = {
      'firstName' : u'Проверка',
      'lastName'  : u'Связи',
    }

    actorId = self.testee.insert('actor', actor)
    self.assertIsInstance(actorId, long)

    expected = dict(actor, actorId = actorId, lastUpdate = now.replace(microsecond = 0))
    actual   = self.testee.one(
      ('actorId', 'firstName', 'lastName', 'lastUpdate'), 
      'actor', 
      {'actorId' : actorId}
    )
    self.assertEqual(expected, actual)

    self.testee.rollback()

  def testUpdate(self):
    self.testee.begin()

    self.testee.update('rental', {'customerId' : 128}, {'rentalId' : 5})
    self.assertEqual(128, self.testee.one(['customerId'], 'rental', {'rentalId' : 5}))

    self.testee.rollback()
    
    # same key for value and creterion
    self.testee.begin()

    self.testee.update('staff', {'storeId' : 1}, {'storeId' : (1, 2)})

    self.assertEqual((1, 1), self.testee.select(['storeId'], 'staff'))

    self.testee.rollback()

  def testDelete(self):
    self.testee.begin()

    self.assertEqual(16049, self.testee.count('payment'))
    
    self.testee.delete('payment', {'paymentId' : 32})
    self.assertEqual(0, self.testee.count('payment', {'paymentId' : 32}))
    
    self.assertEqual(16049 - 1, self.testee.count('payment'))
    
    self.testee.delete('payment', {'paymentId' : range(1, 10), 'staffId' : ()})
    
    for id in range(1, 10):
      self.assertEqual(0, self.testee.count('payment', {'paymentId' : id}))
      
    self.assertEqual(16049 - 1 - 9, self.testee.count('payment'))

    self.testee.rollback()

  def testPing(self):
    self.testee.ping()
    
  def testCursor(self):
    sql = '''
      SELECT *
      FROM country
      WHERE country_id = 20  
    '''
    
    cursor = self.testee.cursor()
    self.assertTrue(cursor.__class__ is builder.NamedCursor)
    cursor.execute(sql)
    self.assertEqual(((20, u'Canada', datetime.datetime(2006, 2, 15, 4, 44)),), cursor.fetchall())
     
    cursor = self.testee.cursor(dict)
    self.assertTrue(cursor.__class__ is builder.NamedDictCursor)
    cursor.execute(sql)
    self.assertEqual(({
      'country'     : u'Canada', 
      'country_id'  : 20, 
      'last_update' : datetime.datetime(2006, 2, 15, 4, 44)
    },), cursor.fetchall())

  def testBegin(self):
    self.testee.begin()
    self.testee.commit()

  def testCommit(self):
    try:
      self.testee.begin()
      self.testee.update('customer', {'active' : False}, {'customerId' : 4})
      self.testee.commit()
  
      # check from another connection
      self.setUp()
      self.assertEqual(0, self.testee.one(['active'], 'customer', {'customerId' : 4}))
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active' : True}, {'customerId' : 4})

  def testRollback(self):
    self.testee.begin()
    self.testee.update('customer', {'active' : False}, {'customerId' : 4})
    self.testee.rollback()

    # check from another connection
    self.setUp()
    self.assertEqual(1, self.testee.one(['active'], 'customer', {'customerId' : 4}))

  def testRollbackSavepoint(self):
    try:
      self.testee.begin()
      self.testee.update('customer', {'active' : False}, {'customerId' : 4})
  
      self.testee.begin()
      self.testee.update('customer', {'active' : 3}, {'customerId' : 4})
      self.testee.rollback()
  
      self.testee.commit()
  
      self.assertEqual(0, self.testee.one(['active'], 'customer', {'customerId' : 4}))
    finally:
      # revert
      self.setUp()
      self.testee.update('customer', {'active' : True}, {'customerId' : 4})
