# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import test
import profiler


_profiler = profiler.QueryProfiler(**test.config)

class TestQueryProfiler(test.ModelBenchmark):

  def setUp(self):
    test.ModelBenchmark.profiler = _profiler
    
    super(TestQueryProfiler, self).setUp()

  @test.ModelBenchmark.profile
  def testProfile(self):
    # naturally model method is tested this way
    
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
    _profiler.query(sql, {
      'ad.address2'  : None,
      'ct.cityId'    : 300,
      'ad.addressId' : (1, 2, 3) 
    }, [('ad.addressId', 'desc')])
    
    sql = '''
      SELECT ad.*
      FROM country cn
      JOIN city    ct USING(country_id)
      JOIN address ad USING(city_id)
      {where} AND city_id > 50
    '''
    _profiler.query(sql, {
      'ad.address2'  : None,
      'ct.cityId'    : 300,
      'ad.addressId' : (1, 2, 3) 
    }, [('ad.addressId', 'asc')])
