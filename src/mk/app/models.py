from django.db import models
from operator import itemgetter
from decimal import Decimal

POSITION_POINTS = [15,9,4,1]

FORM_COUNT = 10

class Stats(models.Model):
	player = models.ForeignKey('Player')
	record_date = models.DateTimeField(auto_now_add=True)
	
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
		return self.player.name + " - " + unicode(self.record_date)
	
	class Meta:
		ordering = ['-record_date', '-average']
		get_latest_by = 'record_date'


class Player(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		super(Player, self).save(*args, **kwargs)
		s = Stats(player=self);
		s.save();
	
	class Meta:
		ordering = ['name']


class Course(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['name']


class RaceStats(models.Model):
	player = models.ForeignKey(Player)
	course = models.ForeignKey(Course)
	record_date = models.DateTimeField(auto_now_add=True)
	
	firsts = models.PositiveIntegerField(default=0)
	seconds = models.PositiveIntegerField(default=0)
	thirds = models.PositiveIntegerField(default=0)
	fourths = models.PositiveIntegerField(default=0)
	points = models.PositiveIntegerField(default=0)
	
	def save(self, *args, **kwargs):
		self.points = self.firsts * POSITION_POINTS[0] + self.seconds * POSITION_POINTS[1] + self.thirds * POSITION_POINTS[2] + self.fourths * POSITION_POINTS[3]
		super(RaceStats, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.player.name + " - " + unicode(self.course) + " - " + unicode(self.record_date)
	
	class Meta:
		ordering = ['-record_date', 'player', 'course']
		get_latest_by = 'record_date'


class Event(models.Model):
	event_date = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	players = models.ManyToManyField(Player)
	
	def _get_results(self):
		results = {}.fromkeys([player for player in self.players.all()])
		
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
		
		for player in self.players.all():
			try:
				stats = Stats.objects.filter(player=player).latest()
				stats.pk = None
				stats.record_date = None
			except Stats.DoesNotExist:
				stats = Stats(player=player)
			
			stats.race_count += 8
			
			stats.points += results[player]['points']
			
			stats.race_firsts += results[player]['positions'][0]
			stats.race_seconds += results[player]['positions'][1]
			stats.race_thirds += results[player]['positions'][2]
			stats.race_fourths += results[player]['positions'][3]
			
			rank = results[player]['rank']
			if rank == 1:
				stats.event_firsts += 1
			elif rank == 2:
				stats.event_seconds += 1
			elif rank == 3:
				stats.event_thirds += 1
			else:
				stats.event_fourths += 1
			
			stats.average = Decimal(str(float(stats.points) / float(stats.race_count)))
			
			stats.save()
			
			for race in self.race_set.all():
				try:
					race_stats = RaceStats.objects.filter(course=race.course, player=player).latest()
					race_stats.pk = None
					race_stats.record_date = None
				except RaceStats.DoesNotExist:
					race_stats = RaceStats(player=player, course=race.course)
				
				if race.first == player:
					race_stats.firsts += 1
				elif race.second == player:
					race_stats.seconds += 1
				elif race.third == player:
					race_stats.thirds += 1
				else:
					race_stats.fourths += 1
					
				race_stats.save()
	
	def __unicode__(self):
		return unicode(self.event_date)
	
	class Meta:
		ordering = ['-event_date']
		get_latest_by = 'event_date'


class Race(models.Model):
	event = models.ForeignKey(Event)
	course = models.ForeignKey(Course)
	order = models.PositiveSmallIntegerField()
	first = models.ForeignKey(Player, related_name='firsts')
	second = models.ForeignKey(Player, related_name='seconds')
	third = models.ForeignKey(Player, related_name='thirds')
	fourth = models.ForeignKey(Player, related_name='fourths')
	
	def __unicode__(self):
		return unicode(self.event.event_date) + " - " + self.course.name
	
	def save(self, *args, **kwargs):
		if self.order == None:
			self.order = self.event.race_set.count()
		super(Race, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ['event','-order']