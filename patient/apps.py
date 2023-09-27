from django.apps import AppConfig
from mmfc import MMFC
import threading
from django.core.cache import cache
ai = None
lock=None

class PatientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient'
    verbose_name = '病人样本'

    def ready(self):
        global ai,lock
        ai = MMFC()
        ai.model_setup(0,0,1)
        lock=threading.Lock()
        cache.clear()

