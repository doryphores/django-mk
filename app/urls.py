from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
	url(r'^$', 'home', name="home-page"),
	url(r'^new/$', 'new', name="new-event"),
	(r'^race/(?P<race_id>\d+)/$', 'race'),
	(r'^race/$', 'race'),
	url(r'^confirm/$', 'confirm', name="confirm-results"),
	url(r'^finish/$', 'finish', name="finish-event"),
	url(r'^players/$', 'players', name='player-list'),
	(r'^player/(?P<player_id>\d+)/$', 'player'),
	url(r'^player/(?P<player_id>\d+)/events/$', 'player_events', name="player-events"),
	url(r'^player/(?P<player_id>\d+)/tracks/$', 'player_tracks', name="player-tracks"),
	url(r'^tracks/$', 'tracks', name="track-list"),
	(r'^track/(?P<track_id>\d+)/$', 'track'),
)