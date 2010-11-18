from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from mk.app import views

urlpatterns = patterns('',
	(r'^$', 'mk.app.views.home'),
	(r'^new/$', 'mk.app.views.new'),
	(r'^race/(?P<race_id>\d+)/$', 'mk.app.views.race'),
    (r'^race/$', 'mk.app.views.race'),
    (r'^confirm/$', 'mk.app.views.confirm'),
	(r'^finish/$', 'mk.app.views.finish'),
    # Example:
    # (r'^django_mk/', include('django_mk.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
