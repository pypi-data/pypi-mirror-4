'''
@author: saaj
'''


from builder import QueryBuilder
import datetime
import types


class QueryProfiler(QueryBuilder):

  _stats  = None
  _groups = ('select', 'sort', 'handler', 'created', 'innodb_buffer')


  def _status(self):
    result = {}
    for group in self._groups:
      cursor        = self.silentQuery("SHOW STATUS LIKE '{0}_%'".format(group))
      result[group] = tuple(row for row in cursor)

    return result

  def _profile(self):
    result = {
      'total'   : 0,
      'queries' : []
    }
    for query in self.silentQuery('SHOW PROFILES'):
      cursor            = self.silentQuery('SHOW PROFILE FOR QUERY {0}'.format(query['Query_ID']))
      query['statuses'] = tuple(status for status in cursor)

      result['total'] += query['Duration']
      result['queries'].append(query)

    return result

  def profile(self, profilee):
    self.silentQuery('SET profiling = 1')
    profilee()
    self.silentQuery('SET profiling = 0')
    profile = self._profile()

    self.silentQuery('FLUSH STATUS');
    profilee()
    status = self._status()

    return profile, status

  def start(self):
    self._stats = {
      'count'   : 0,
      'time'    : datetime.timedelta(),
      'queries' : []
    }

  def stop(self):
    return self._stats

  def silentQuery(self, sql, args = None):
    cursor = super(QueryProfiler, self).cursor(dict)
    cursor.execute(sql, args)

    return cursor

  def cursor(self, type = None):
    cursor = super(QueryProfiler, self).cursor(type)
    # wrap cursor's execute()
    oldExecute = cursor.execute
    def newExecute(instance, query, args = None):
      start = datetime.datetime.now()

      oldExecute(query, args)

      diff = datetime.datetime.now() - start
      self._stats['count'] += 1
      self._stats['time']  += diff
      self._stats['queries'].append((query, args, diff))
    cursor.execute = types.MethodType(newExecute, cursor, cursor.__class__)

    return cursor
