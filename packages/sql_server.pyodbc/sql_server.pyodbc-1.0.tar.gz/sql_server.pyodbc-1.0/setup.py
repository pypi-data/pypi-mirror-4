#!/usr/bin/env python

from distutils.core import setup

setup(name='sql_server.pyodbc',
      version='1.0',
      description='Django MS SQL Server backends using pyodbc\nNote, I did not write this package. If you are the package owner and want me to transfer ownership, just email us at hi@aurora.io. Thanks!',
      author='django-pyodbc team',
      url='http://code.google.com/p/django-pyodbc',
      packages=['sql_server', 'sql_server.pyodbc', 'sql_server.extra'],
 )
