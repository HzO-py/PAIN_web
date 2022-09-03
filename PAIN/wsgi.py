"""
WSGI config for PAIN project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os,sys

sys.path.append('/home/ubuntu/PAIN')
sys.path.append('/home/ubuntu/anaconda3/envs/py36/Lib/site-packages')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PAIN.settings')

application = get_wsgi_application()
