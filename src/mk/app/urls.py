from django.conf.urls.defaults import *

urlpatterns = patterns('mk.app.views',
	url(r'^$', 'home', name="home-page"),
	url(r'^new/$', 'new', name="new-event"),
	(r'^race/(?P<race_id>\d+)/$', 'race'),
	(r'^race/$', 'race'),
	url(r'^confirm/$', 'confirm', name="confirm-results"),
	url(r'^finish/$', 'finish', name="finish-event"),
	url(r'^players/$', 'players', name='player-list'),
	(r'^player/(?P<player_id>\d+)/$', 'player'),
	url(r'^tracks/$', 'tracks', name="track-list"),
	(r'^track/(?P<track_id>\d+)/$', 'track'),
)