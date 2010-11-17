from django.contrib import admin
from mk.app.models import Player, Track, Event, Race, EventResult, RaceResult,\
	PlayerStat

admin.site.register(Player)

admin.site.register(Track)

class EventAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'player_list', 'completed')
	date_hierarchy = 'event_date'
	list_filter = ['completed', 'players']
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Event, EventAdmin)

class RaceAdmin(admin.ModelAdmin):
	list_display = ('event', 'track', 'player_list', 'order')
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Race, RaceAdmin)

class EventResultAdmin(admin.ModelAdmin):
	list_display = ('player', 'event', 'firsts', 'seconds', 'thirds', 'fourths', 'points', 'rank')
	list_filter = ['player']

admin.site.register(EventResult, EventResultAdmin)

class RaceResultAdmin(admin.ModelAdmin):
	list_display = ('race', 'player', 'position')
	list_filter = ['player']

admin.site.register(RaceResult, RaceResultAdmin)

admin.site.register(PlayerStat)