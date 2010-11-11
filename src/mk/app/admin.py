from django.contrib import admin
from mk.app.models import Player, Course, Event, Race, Stats, RaceStats

admin.site.register(Player)

admin.site.register(Course)

class EventAdmin(admin.ModelAdmin):
	list_display = ('event_date', 'player_list', 'complete')
	date_hierarchy = 'event_date'
	list_filter = ['complete', 'players']
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Event, EventAdmin)

class RaceAdmin(admin.ModelAdmin):
	list_display = ('event', 'course')

admin.site.register(Race, RaceAdmin)

class StatsAdmin(admin.ModelAdmin):
	list_display = ('player', 'record_date', 'average')
	list_filter = ['player']
	date_hierarchy = 'record_date'

admin.site.register(Stats, StatsAdmin)

class RaceStatsAdmin(admin.ModelAdmin):
	list_display = ('player', 'course', 'record_date', 'points')
	list_filter = ['player', 'course']
	date_hierarchy = 'record_date'

admin.site.register(RaceStats, RaceStatsAdmin)