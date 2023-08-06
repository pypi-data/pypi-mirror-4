from distutils.core import setup

setup(
  name             = 'MysqlSimpleQueryBuilder',
  version          = '0.2.3',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['myquerybuilder', 'myquerybuilder.test'],
  url              = 'http://code.google.com/p/mysql-simple-query-builder/',
  license          = 'LGPL',
  description      = 'Simple MySQL query builder and profiler',
  long_description = open('README.txt').read(),
  install_requires = ['MySQL-python >= 1.2'],
  platforms        = ['Any'],
  classifiers      = [
    'Topic :: Database',
    'Programming Language :: Python :: 2.7',
    'Intended Audience :: Developers'
  ]
)