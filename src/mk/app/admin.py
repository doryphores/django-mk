from django.contrib import admin
from mk.app.models import Player, Course, Event, Race, Stats, RaceStats

admin.site.register(Player)

admin.site.register(Course)

admin.site.register(Event)

admin.site.register(Race)

admin.site.register(Stats)

admin.site.register(RaceStats)