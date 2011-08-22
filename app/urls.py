from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
	url(r'^$', 'home', name="home-page"),
	
	# Race recorder
	url(r'^new/$', 'new', name="new-event"),
	url(r'^race/(?P<race_id>\d+)/$', 'race', name="race"),
	url(r'^race/$', 'race', name="race-start"),
	url(r'^confirm/$', 'confirm', name="confirm-results"),
	url(r'^finish/$', 'finish', name="finish-event"),
	
	# Players section
	url(r'^players/$', 'players', name="player-list"),
	url(r'^players/(?P<player_id>\d+)/$', 'player', name="player-details"),
	url(r'^players/(?P<player_id>\d+)/events/$', 'player_events', name="player-events"),
	url(r'^players/(?P<player_id>\d+)/tracks/$', 'player_tracks', name="player-tracks"),
	
	# Tracks section
	url(r'^tracks/$', 'tracks', name="track-list"),
	url(r'^tracks/(?P<track_id>\d+)/$', 'track', name="track-details"),
)