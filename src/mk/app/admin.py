from django.contrib import admin
from mk.app.models import Player, Track, Event, Race, EventResult, RaceResult,\
	PlayerStat

admin.site.register(Player)

admin.site.register(Track)

class EventResultInline(admin.TabularInline):
	model = EventResult
	extra = 0
	can_delete = False
	max_num = 4

class EventAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'player_list', 'completed')
	date_hierarchy = 'event_date'
	list_filter = ['completed', 'players']
	
	inlines = [
		EventResultInline,
	]
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Event, EventAdmin)

class RaceResultAdmin(admin.ModelAdmin):
	list_display = ('race', 'player', 'position')
	list_filter = ['player']

admin.site.register(RaceResult, RaceResultAdmin)

class RaceResultInline(admin.TabularInline):
	model = RaceResult
	extra = 0
	can_delete = False
	max_num = 4

class RaceAdmin(admin.ModelAdmin):
	list_display = ('event', 'track', 'player_list', 'order')
	
	inlines = [
		RaceResultInline,
	]
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Race, RaceAdmin)

class EventResultAdmin(admin.ModelAdmin):
	list_display = ('player', 'event', 'firsts', 'seconds', 'thirds', 'fourths', 'points', 'rank')
	list_filter = ['player']

admin.site.register(EventResult, EventResultAdmin)

class PlayerStatAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'average', 'form', 'rank', 'form_rank')
	list_filter = ['player']

admin.site.register(PlayerStat, PlayerStatAdmin)