'''
@author: saaj
'''


import unittest
import types
import math


config = {
  'host'    : '127.0.0.1',
  'user'    : 'guest',
  'passwd'  : '',
  'db'      : 'sakila',
  'charset' : 'utf8'            
}


class TestCase(unittest.TestCase):

  testee = None


  def testMethodCoverage(self):
    if self.__class__ is TestCase:
      return

    def methods(object):
      return {
        name for (name, value) in object.__class__.__dict__.items()
        if isinstance(value, types.FunctionType) and name[0] != '_'
      }

    self.assertFalse(self.testee is None, 'Testee must be created in setUp()')

    diff = set('test' + name[0].upper() + name[1:] for name in methods(self.testee)) - methods(self)
    self.assertEqual(0, len(diff), 'Test case misses: {0}'.format(', '.join(diff)))
    
    
class ModelBenchmark(unittest.TestCase):

  profiler = None
  testee   = None

  def printReport(self):
    stats = self.profiler.stop()

    print '{0}.{1}({2}): {3}'.format(
      self.__class__.__name__,
      self._testMethodName,
      stats['count'],
      stats['time']
    )

  @staticmethod
  def profile(profilee):
    def numberFormat(count):
      e = int(math.log(count, 1000) if count else 0)
      return '{0:.1f} {1}'.format((count + 0.0) / 1000 ** e, ('', 'K', 'M', 'G', 'T')[e])
    def dumpExplain(query, args):
      print '\n    ' + ' plan '.center(28, '*')
        
      planCursor  = ModelBenchmark.profiler.silentQuery('EXPLAIN ' + query, args)
      planFields  = ('select_type', 'table', 'type', 'possible_keys') 
      planFields += ('key', 'key_len', 'ref', 'rows', 'Extra') 
      for row in planCursor:
        print '      ' + ' id:{0} '.format(row['id']).center(40, '*')
        for k in planFields:
          print '      {0} {1}'.format(k.lower().ljust(15), row[k] if row[k] else '')
    def dumpQuery(query, args):
      print '\n' + query
      print '\n    ' + str(args) + '\n'
    def dumpProfile(profile):
      print ' profile '.center(28, '*')
      for i, query in enumerate(profile['queries']):
        percent = query['Duration'] / profile['total']
        print '  #{0} {1} - {2:.1%}'.format(query['Query_ID'], query['Duration'], percent)
        for status in query['statuses']:
          if float(status['Duration']) / query['Duration'] > 0.1:
            print '    {0} {1}'.format(status['Status'].lower().ljust(15), status['Duration'])
        # query['Query'] is 300-char limited
        profiledQuery = ModelBenchmark.profiler.stop()['queries'][i + 1]

        dumpExplain(profiledQuery[0], profiledQuery[1])
        dumpQuery(profiledQuery[0], profiledQuery[1])
    def dumpStatues(statuses):
      for group, values in statuses.items():
        values = filter(lambda value: int(value['Value']), values)
        if values:
          print ' status {0} '.format(group).center(28, '*')
          for value in values:
            print '  {0} {1}'.format(value['Variable_name'].lower().ljust(37), value['Value'])
    def wrapper(*args, **kw):
      profile, statuses = ModelBenchmark.profiler.profile(lambda: profilee(*args, **kw))
      dumpProfile(profile)
      dumpStatues(statuses)
      print '\n'

    return wrapper

  def setUp(self):
    self.profiler.silentQuery('SET SESSION query_cache_type = OFF')
    self.profiler.start()
    self.profiler.begin()

  def tearDown(self):
    self.profiler.rollback()
    self.printReport()
