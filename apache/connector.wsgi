import os, sys, site

apache_configuration= os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(apache_configuration)
sys.path.append(PROJECT_ROOT)

if os.name == 'nt':
	site.addsitedir(os.path.join(PROJECT_ROOT, '.env\\Lib\\site-packages'))
else:
	site.addsitedir('/home/martin/.virtualenvs/mk/lib/python2.7/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

if os.name == 'nt':
	import monitor
	monitor.start(interval=1.0)