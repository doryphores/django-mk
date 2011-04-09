import os, sys, site

apache_configuration= os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(apache_configuration)
sys.path.append(PROJECT_ROOT)

site.addsitedir(os.path.join(PROJECT_ROOT, 'env/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

#import mk.monitor
#mk.monitor.start(interval=1.0)