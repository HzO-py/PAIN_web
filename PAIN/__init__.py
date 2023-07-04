# 引入celery实例对象
from .celery import app

__all__ = ('app',)

import pymysql

pymysql.install_as_MySQLdb()
