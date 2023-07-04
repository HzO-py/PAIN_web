from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认的Django配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PAIN.settings')

app = Celery('PAIN', broker='redis://localhost:6379/0')

# 从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks()