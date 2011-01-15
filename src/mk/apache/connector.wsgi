import os, sys

apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mk.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

import mk.monitor
mk.monitor.start(interval=1.0)