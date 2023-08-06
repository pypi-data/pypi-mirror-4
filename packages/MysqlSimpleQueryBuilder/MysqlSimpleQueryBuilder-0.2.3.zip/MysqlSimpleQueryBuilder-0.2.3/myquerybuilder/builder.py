'''
@author: saaj
'''


import MySQLdb         as mysql
import MySQLdb.cursors as cursors
import re
import collections
import copy


class NamedCursor(cursors.Cursor):

  _placeholderRe = re.compile(':([a-zA-Z]\w+)')


  def execute(self, query, args = None):
    return super(NamedCursor, self).execute(self._placeholderRe.sub('%(\\1)s', query), args)


class NamedDictCursor(cursors.DictCursor, NamedCursor):
  pass


class QueryBuilder(object):

  # placeholders
  where = '{where}'
  order = '{order}'
  limit = '{limit}'

  _connection       = None
  _transactionLevel = 0
  _lowerToUpperRe   = re.compile('([a-z0-9])([A-Z])')


  def __init__(self, config):
    self._connection = mysql.connect(**config)

    self._connection.autocommit(True)

  def _to_(self, name):
    # a.nameToName -> a.name_To_Name
    result = self._lowerToUpperRe.sub(r'\1_\2', name)
    # a.name_To_Name -> a.`name_to_name`
    result     = result.lower().split('.')
    result[-1] = '`{0}`'.format(result[-1])
    result     = '.'.join(result)

    return result

  def _eq(self, fields, postfix = '', op = '='):
    return map(lambda f: '{0} {1} :{2}'.format(self._to_(f), op, f.replace('.', '_') + postfix), fields)

  def _selectSql(self, fields):
    return 'SELECT ' + ', '.join(map(lambda f: '{0} `{1}`'.format(self._to_(f), f), fields))

  def _fromSql(self, table):
    return 'FROM {0}'.format(self._to_(table))

  def _whereSql(self, where):
    isscalar = lambda v: not isinstance(v, (collections.Iterable)) or isinstance(v, basestring)
    
    scalar = set(filter(lambda k: isscalar(where[k]), where))
    none   = set(filter(lambda k: where[k] is None,   scalar))
    one    = set(filter(lambda k: len(tuple(where[k])) == 1, set(where.keys()) - scalar))
    vector = filter(lambda k: len(tuple(where[k])) > 1, set(where.keys()) - scalar - one)
    
    for k in one:
      where[k] = tuple(where[k])[0]
      
    condition  = self._eq(scalar - none | one)
    condition += self._eq(none,   op = 'IS')
    condition += self._eq(vector, op = 'IN')
    
    return 'WHERE ({0})'.format(' AND '.join(condition)) if condition else ''

  def _orderSql(self, order):
    return 'ORDER BY ' + ', '.join(map(lambda by: '{0} {1}'.format(self._to_(by[0]), by[1]), order))

  def _limitSql(self, limit):
    return 'LIMIT {0}, {1} '.format(*([0, limit] if isinstance(limit, int) else limit))

  def _processQueryClause(self, sql, name, content, builder):
    placeholder = getattr(self, name)
    if content:
      part = builder(content)
      sql  = sql.replace(placeholder, part) if sql.find(placeholder) != -1 else sql + '\n' + part
    elif sql.find(placeholder) != -1:
      sql = sql.replace(placeholder, '')

    return sql

  def quote(self, value):
    return self._connection.literal(value)

  def query(self, sql, where = None, order = None, limit = None):
    where = copy.copy(where)
        
    sql = self._processQueryClause(sql, 'where', where, self._whereSql)
    sql = self._processQueryClause(sql, 'order', order, self._orderSql)
    sql = self._processQueryClause(sql, 'limit', limit, self._limitSql)

    cursor = self.cursor(dict)
    cursor.execute(sql, {key.replace('.', '_') : value for key, value in where.items()} if where else None)

    return cursor

  def select(self, fields, table, where = None, order = None, limit = None):
    where  = copy.copy(where)
    cursor = self.cursor(dict)

    cursor.execute('{SELECT}\n{FROM}\n{WHERE}\n{ORDER}\n{LIMIT}'.format(
      SELECT = self._selectSql(fields),
      FROM   = self._fromSql(table),
      WHERE  = self._whereSql(where) if where else '',
      ORDER  = self._orderSql(order) if order else '',
      LIMIT  = self._limitSql(limit) if limit else ''
    ), where)

    if len(fields) == 1:
      return tuple(row[fields[0]] for row in cursor)
    else:
      return cursor.fetchall()

  def one(self, fields, table, where = None, order = None):
    where  = copy.copy(where)
    cursor = self.cursor(dict)
    cursor.execute('{SELECT}\n{FROM}\n{WHERE}\n{ORDER}\n{LIMIT}'.format(
      SELECT = self._selectSql(fields),
      FROM   = self._fromSql(table),
      WHERE  = self._whereSql(where) if where else '',
      ORDER  = self._orderSql(order) if order else '',
      LIMIT  = self._limitSql(1)
    ), where)

    result = cursor.fetchone()
    if result:
      return result[fields[0]] if len(fields) == 1 else result
    else:
      return None

  def count(self, table, where = None):
    where  = copy.copy(where)
    cursor = self.cursor()
    cursor.execute('SELECT COUNT(*)\n{FROM}\n{WHERE}'.format(
      FROM  = self._fromSql(table),
      WHERE = self._whereSql(where) if where else ''
    ), where)

    return cursor.fetchone()[0]

  def insert(self, table, values):
    fields       = ','.join(map(lambda field: '{0}'.format(self._to_(field)), values.keys()))
    placeholders = ','.join(map(lambda field: ':{0}'.format(field), values.keys()))

    cursor = self.cursor()
    cursor.execute('INSERT INTO {table}({fields})\nVALUES({placeholders})'.format(
      table        = self._to_(table),
      fields       = fields,
      placeholders = placeholders
    ), values)

    return cursor.lastrowid

  def update(self, table, values, where):
    where = copy.copy(where)
    # '__' postfix is used to separate value and condition parameters
    set    = ',\n'.join(self._eq(values.keys(), '__'))
    params = {key + '__' : value for (key, value) in values.items()}
    if where:
      params.update(where)

    self.cursor().execute('UPDATE {table}\nSET {set}\n{WHERE}'.format(
      table = self._to_(table),
      set   = set,
      WHERE = self._whereSql(where) if where else ''
    ), params)

  def delete(self, table, where):
    where = copy.copy(where)
    self.cursor().execute('DELETE {FROM}\n{WHERE}'.format(
      FROM  = self._fromSql(table),
      WHERE = self._whereSql(where) if where else ''
    ), where)

  def cursor(self, type = None):
    if type is dict:
      type = NamedDictCursor
    elif type is None:
      type = NamedCursor

    return self._connection.cursor(type)

  def ping(self):
    try:
      # reconnection in MySQLdb is damn conspiracy
      self._connection.ping(True)
    except mysql.OperationalError:
      pass

  def begin(self):
    if self._transactionLevel == 0:
      self.cursor().execute('START TRANSACTION')
    else:
      self.cursor().execute('SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

    self._transactionLevel += 1

  def commit(self):
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self._connection.commit()
    else:
      self.cursor().execute('RELEASE SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

  def rollback(self):
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self._connection.rollback()
    else:
      self.cursor().execute('ROLLBACK TO SAVEPOINT LEVEL{0}'.format(self._transactionLevel))
