from django.db import models
from decimal import Decimal

POSITION_POINTS = [15,9,4,1]

FORM_COUNT = 10

RANK_STRINGS = ['first', 'second', 'third', 'fourth']

class Player(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['name']


class Track(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['name']


class EventResult(models.Model):
	event = models.ForeignKey('Event', related_name='results')
	player = models.ForeignKey('Player', related_name='event_results')
	
	points = models.PositiveSmallIntegerField(default=0)
	rank = models.PositiveSmallIntegerField(default=0)
	firsts = models.PositiveSmallIntegerField(default=0)
	seconds = models.PositiveSmallIntegerField(default=0)
	thirds = models.PositiveSmallIntegerField(default=0)
	fourths = models.PositiveSmallIntegerField(default=0)
	
	def __unicode__(self):
		return u'%s %s (rank: %s)' % (self.player, self.event, RANK_STRINGS[self.rank])
	
	class Meta:
		ordering = ['event','rank']


class RaceResult(models.Model):
	race = models.ForeignKey('Race', related_name='results')
	player = models.ForeignKey('Player', related_name='race_results')
	
	position = models.PositiveSmallIntegerField(default=0)
	
	def __unicode__(self):
		return u'%s %s (rank: %s)' % (self.player, self.race, RANK_STRINGS[self.position])
	
	class Meta:
		ordering = ['race','position']


class Event(models.Model):
	event_date = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	players = models.ManyToManyField(Player, through='EventResult')
	
	def _get_slot(self):
		if abs(self.event_date.hour - 12) < 3:
			return 'lunch'
		else:
			return 'evening'
	slot = property(_get_slot)
	
	def _get_race_count(self):
		return self.races.count()
	race_count = property(_get_race_count)
	
	def get_tracks(self):
		return self.races.values_list('track')
	
	def __unicode__(self):
		return u'%s (%s slot)' % (self.event_date.strftime("%a. %b. %d %Y"), self.slot)
	
	class Meta:
		ordering = ['-event_date']
		get_latest_by = 'event_date'


class Race(models.Model):
	event = models.ForeignKey(Event, related_name='races')
	track = models.ForeignKey(Track)
	players = models.ManyToManyField(Player, through='RaceResult')
	order = models.PositiveSmallIntegerField()
	
	def __unicode__(self):
		return u'%s on %s' % (self.track, self.event) 
	
	def save(self, *args, **kwargs):
		if self.order == None:
			self.order = self.event.races.count()
		super(Race, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ['event','-order']