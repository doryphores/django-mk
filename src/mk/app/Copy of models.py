from django.db import models
from operator import itemgetter
from decimal import Decimal

POSITION_POINTS = [15,9,4,1]

FORM_COUNT = 10

RANK_STRINGS = ['first', 'second', 'third', 'fourth']

class Stats(models.Model):
	player = models.ForeignKey('Player')
	record_date = models.DateTimeField()
	
	points = models.IntegerField(default=0)
	race_count = models.PositiveIntegerField(default=0)
	race_firsts = models.PositiveIntegerField(default=0) 
	race_seconds = models.PositiveIntegerField(default=0)
	race_thirds = models.PositiveIntegerField(default=0)
	race_fourths = models.PositiveIntegerField(default=0)
	event_firsts = models.PositiveIntegerField(default=0)
	event_seconds = models.PositiveIntegerField(default=0)
	event_thirds = models.PositiveIntegerField(default=0)
	event_fourths = models.PositiveIntegerField(default=0)
	average = models.DecimalField(max_digits=2, decimal_places=1, default=0)
	form = models.DecimalField(max_digits=2, decimal_places=1, default=0)
	
	def __unicode__(self):
		return "%s (%s)" % (self.player.name,  self.record_date.strftime("%a. %b. %d %Y"))
	
	class Meta:
		ordering = ['-record_date', '-average']
		get_latest_by = 'record_date'


class EventResult(models.Model):
	event = models.ForeignKey('Event', related_name='event_results')
	player = models.ForeignKey('Player')
	
	points = models.PositiveSmallIntegerField(default=0)
	rank = models.PositiveSmallIntegerField(default=0)
	firsts = models.PositiveSmallIntegerField(default=0)
	seconds = models.PositiveSmallIntegerField(default=0)
	thirds = models.PositiveSmallIntegerField(default=0)
	fourths = models.PositiveSmallIntegerField(default=0)
	
	def __unicode__(self):
		return u'%s %s (%s)' % (self.player.name, self.event, RANK_STRINGS[self.rank])
	
	class Meta:
		ordering = ['event','rank']


class RaceResult(models.Model):
	race = models.ForeignKey('Race', related_name='race_results')
	player = models.ForeignKey('Player')
	
	position = models.PositiveSmallIntegerField(default=0)
	
	def __unicode__(self):
		return u'%s %s (%s)' % (self.player.name, self.race, RANK_STRINGS[self.position])
	
	class Meta:
		ordering = ['race','position']


class Player(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		super(Player, self).save(*args, **kwargs)
		s = Stats(player=self)
		s.save()
	
	class Meta:
		ordering = ['name']


class Course(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['name']


class Event(models.Model):
	event_date = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	players = models.ManyToManyField(Player)
	
	def _get_slot(self):
		if abs(self.event_date.hour - 12) < 3:
			return 'lunch'
		else:
			return 'evening'
	slot = property(_get_slot)
	
	def _get_results(self):
		results = {}
		
		for player in self.players.all():
			results[player] = {
				'rank': 0,
				'points': 0,
				'positions': [0, 0, 0, 0]
			}
		
		for race in self.race_set.all():
			results[race.first]['points'] += POSITION_POINTS[0]
			results[race.first]['positions'][0] += 1
			results[race.second]['points'] += POSITION_POINTS[1]
			results[race.second]['positions'][1] += 1
			results[race.third]['points'] += POSITION_POINTS[2]
			results[race.third]['positions'][2] += 1
			results[race.fourth]['points'] += POSITION_POINTS[3]
			results[race.fourth]['positions'][3] += 1
		
		for i, p in enumerate(sorted([(player, results[player]['points']) for player in results], key=itemgetter(1), reverse=True)):
			results[p[0]]['rank'] = i
		
		return results
	results = property(_get_results)
	
	def get_player_result(self, player):
		if player not in self.players:
			raise "Player didn't take part in this event"
		
		return self.results[player]
	
	def _get_race_count(self):
		return self.race_set.count()
	race_count = property(_get_race_count)
	
	def set_complete(self):
		if self.complete:
			return
		
		self.complete = True
		self.save()
		
		results = self.results
		
		self.event_results.all().delete()
		
		for race in self.races.all():
			for i, position in enumerate(RANK_STRINGS):
				RaceResult(race=race, player=getattr(self, position), position=i).save()
		
		for player in self.players.all():
			er = EventResult(event=self, player=player)
			er.rank = results[player]['rank']
			er.points = results[player]['points']
			er.firsts = results[player]['positions'][0]
			er.seconds = results[player]['positions'][1]
			er.thirds = results[player]['positions'][2]
			er.fourths = results[player]['positions'][3]
			er.save()
			
			try:
				stats = Stats.objects.filter(player=player).latest()
				stats.pk = None
			except Stats.DoesNotExist:
				stats = Stats(player=player)
			
			stats.record_date = self.event_date
			
			stats.race_count += 8
			
			stats.points += results[player]['points']
			
			stats.race_firsts += results[player]['positions'][0]
			stats.race_seconds += results[player]['positions'][1]
			stats.race_thirds += results[player]['positions'][2]
			stats.race_fourths += results[player]['positions'][3]
			
			rank = results[player]['rank']
			if rank == 0:
				stats.event_firsts += 1
			elif rank == 1:
				stats.event_seconds += 1
			elif rank == 2:
				stats.event_thirds += 1
			else:
				stats.event_fourths += 1
			
			stats.average = Decimal(str(float(stats.points) / float(stats.race_count)))
			
			recent_results = EventResult.objects.filter(player=player)[0:FORM_COUNT]
			
			stats.form = Decimal(str(float(sum([r.points for r in recent_results])) / float(recent_results.count() * 8)))
			
			stats.save()
	
	def save(self, *args, **kwargs):
		requires_complete = False
		
		if self.pk is not None:
			orig = Event.objects.get(pk=self.pk)
			requires_complete = orig.complete != self.complete
		
		super(Race, self).save(*args, **kwargs)
		
		if requires_complete:
			self.set_complete()
	
	def __unicode__(self):
		return u'%s (%s slot)' % (self.event_date.strftime("%a. %b. %d %Y"), self.slot)
	
	class Meta:
		ordering = ['-event_date']
		get_latest_by = 'event_date'


class Race(models.Model):
	event = models.ForeignKey(Event, related_name="races")
	course = models.ForeignKey(Course)
	order = models.PositiveSmallIntegerField()
	first = models.ForeignKey(Player, related_name='firsts')
	second = models.ForeignKey(Player, related_name='seconds')
	third = models.ForeignKey(Player, related_name='thirds')
	fourth = models.ForeignKey(Player, related_name='fourths')
	
	def __unicode__(self):
		return u'%s on %s' % (self.course.name, self.event) 
	
	def save(self, *args, **kwargs):
		if self.order == None:
			self.order = self.event.race_set.count()
		super(Race, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ['event','-order']