from django.db import models
from operator import itemgetter

POSITION_POINTS = [15,9,4,1]


class Player(models.Model):
	class Meta:
		ordering = ['name']
	
	name = models.CharField(max_length=200, unique=True)
	
	#def _get_points(self):
	#	return sum(self.__getattribute__(key).count() * POSITION_POINTS[key] for key in POSITION_POINTS)
	#points = property(_get_points)
	
	def __unicode__(self):
		return self.name

	
class Course(models.Model):
	class Meta:
		ordering = ['name']
	
	name = models.CharField(max_length=200, unique=True)
	
	def __unicode__(self):
		return self.name


class Event(models.Model):
	class Meta:
		ordering = ['-event_date']
		
	event_date = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	players = models.ManyToManyField(Player)
	
	def _get_results(self):
		results = {}.fromkeys([player.name for player in self.players.all()], 0)
		
		for race in self.race_set.all():
			results[race.first.name] += POSITION_POINTS[0]
			results[race.second.name] += POSITION_POINTS[1]
			results[race.third.name] += POSITION_POINTS[2]
			results[race.fourth.name] += POSITION_POINTS[3]
		
		results = [{ 'player': key, 'points': results[key] } for key in results]
		
		return sorted(results, key=itemgetter('points'), reverse=True)
	results = property(_get_results)
	
	def _get_race_count(self):
		return self.race_set.count()
	race_count = property(_get_race_count)
	
	def set_complete(self):
		self.complete = True
		self.save()
	
	def __unicode__(self):
		return unicode(self.event_date)


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
		self.order = self.event.race_set.count()
		super(Race, self).save(*args, **kwargs)


class Stats(models.Model):
	player = models.ForeignKey(Player)
	event= models.ForeignKey(Event)
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
	average = models.DecimalField(max_digits=2, decimal_places=1)
	form = models.DecimalField(max_digits=2, decimal_places=1)
	