from django.db import models
from operator import itemgetter
from decimal import Decimal
from django.db import transaction

POSITION_POINTS = [15,9,4,1]


class Player(models.Model):
	class Meta:
		ordering = ['name']
	
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name

	
class Course(models.Model):
	class Meta:
		ordering = ['name']
	
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name


class Stats(models.Model):
	class Meta:
		ordering = ['-event']
		get_latest_by = '-event__event-date'
		
	player = models.ForeignKey(Player)
	event= models.ForeignKey('Event')
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
		return self.player.name + " - " + unicode(self.event.event_date)


class Event(models.Model):
	class Meta:
		ordering = ['-event_date']
		get_latest_by = 'event_date'
		
	event_date = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	players = models.ManyToManyField(Player)
	
	def _get_results(self):
		results = {}.fromkeys([player.name for player in self.players.all()], 0)
		
		for player in self.players.all():
			results[player.name] = {
				'player': player,
				'points': 0
			}
		
		for race in self.race_set.all():
			results[race.first.name]['points'] += POSITION_POINTS[0]
			results[race.second.name]['points'] += POSITION_POINTS[1]
			results[race.third.name]['points'] += POSITION_POINTS[2]
			results[race.fourth.name]['points'] += POSITION_POINTS[3]
		
		results = [{ 'player': results[key]['player'], 'points': results[key]['points'] } for key in results]
		
		return sorted(results, key=itemgetter('points'), reverse=True)
	results = property(_get_results)
	
	def _get_race_count(self):
		return self.race_set.count()
	race_count = property(_get_race_count)
	
	@transaction.commit_on_success
	def set_complete(self):
		if self.complete:
			return
		
		self.complete = True
		self.save()
		
		results = self.results
		
		for player in self.players.all():
			stats = Stats(event=self, player=player)
			player_stats = Stats.objects.filter(player=player).order_by('-event__event_date')
			if player_stats.exists():
				stats = player_stats[0]
				stats.pk = None
				stats.event = self
			else:
				stats = Stats(event=self, player=player)
			
			stats.race_count += 8
			stats.race_firsts += player.firsts.filter(event=self).count()
			stats.race_seconds += player.seconds.filter(event=self).count()
			stats.race_thirds += player.thirds.filter(event=self).count()
			stats.race_fourths += player.fourths.filter(event=self).count()
			
			for (i, result) in enumerate(results):
				if result['player'] == player:
					f = ['event_firsts', 'event_seconds', 'event_thirds', 'event_fourths'][i]
					stats.__setattr__(f, stats.__getattribute__(f) + 1)
					stats.points += result['points'] 
					break
			
			stats.average = Decimal(str(float(stats.points) / float(stats.race_count)))
			
			stats.save()
	
	def __unicode__(self):
		return unicode(self.event_date)


class Race(models.Model):
	class Meta:
		order_with_respect_to = 'event'
		ordering = ['order']
	
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
		self.order = self.event.race_set.count()
		super(Race, self).save(*args, **kwargs)