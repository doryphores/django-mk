from django.contrib import admin
from mk.app.models import *

class PlayerAdmin(admin.ModelAdmin):
	list_display = ('name','rating')
	list_editable = ('rating',)
	list_per_page = 20

admin.site.register(Player, PlayerAdmin)

admin.site.register(Track)

admin.site.register(King)

class EventResultInline(admin.TabularInline):
	model = EventResult
	extra = 0
	can_delete = False
	max_num = 4

class EventAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'player_list', 'completed')
	date_hierarchy = 'event_date'
	list_filter = ['completed', 'players']
	list_per_page = 20
	
	inlines = [
		EventResultInline,
	]
	
	actions=['really_delete_selected']
	
	def get_actions(self, request):
		actions = super(EventAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions
	
	def really_delete_selected(self, request, queryset):
		for obj in queryset:
			obj.delete()
		
		if queryset.count() == 1:
			message_bit = "1 event was"
		else:
			message_bit = "%s events were" % queryset.count()
		self.message_user(request, "%s successfully deleted." % message_bit)
	really_delete_selected.short_description = "Deleted selected events"
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Event, EventAdmin)

class RaceResultAdmin(admin.ModelAdmin):
	list_display = ('race', 'player', 'position')
	list_filter = ['player']
	list_per_page = 20

admin.site.register(RaceResult, RaceResultAdmin)

class RaceResultInline(admin.TabularInline):
	model = RaceResult
	extra = 0
	can_delete = False
	max_num = 4

class RaceAdmin(admin.ModelAdmin):
	list_display = ('event', 'track', 'player_list', 'order')
	list_filter = ['track']
	list_per_page = 20
	
	inlines = [
		RaceResultInline,
	]
	
	def player_list(self, obj):
		return ", ".join([player.name for player in obj.players.all()])

admin.site.register(Race, RaceAdmin)

class EventResultAdmin(admin.ModelAdmin):
	list_display = ('player', 'event', 'firsts', 'seconds', 'thirds', 'fourths', 'points', 'rank')
	list_filter = ['player']
	list_per_page = 20

admin.site.register(EventResult, EventResultAdmin)

class PlayerHistoryAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'points', 'race_count', 'average', 'form', 'rating')
	list_filter = ['player']
	list_per_page = 20

admin.site.register(PlayerHistory, PlayerHistoryAdmin)