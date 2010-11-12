from django.contrib import admin
from mk.app.models import Player, Track, Event, Race, EventResult, RaceResult

admin.site.register(Player)

admin.site.register(Track)

class EventAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'player_list', 'complete')
	date_hierarchy = 'event_date'
	list_filter = ['complete', 'players']
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Event, EventAdmin)

class RaceAdmin(admin.ModelAdmin):
	list_display = ('event', 'track', 'player_list')
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Race, RaceAdmin)

class EventResultAdmin(admin.ModelAdmin):
	list_display = ('player', 'event', 'firsts', 'seconds', 'thirds', 'fourths', 'points')
	list_filter = ['player']

admin.site.register(EventResult, EventResultAdmin)

class RaceResultAdmin(admin.ModelAdmin):
	list_display = ('race', 'player', 'position')
	list_filter = ['player']

admin.site.register(RaceResult, RaceResultAdmin)