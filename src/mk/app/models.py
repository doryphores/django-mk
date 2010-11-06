from django.db import models

POSITION_POINTS = {
	'firsts': 15,
	'seconds': 9,
	'thirds': 4,
	'fourths': 1,
}


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
	
class Event(models.Model):
	class Meta:
		ordering = ['event_date']
		
	event_date = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	players = models.ManyToManyRel(Player)
	
	def __unicode__(self):
		return unicode(self.event_date)
	
class Race(models.Model):
	event = models.ForeignKey(Event)
	course = models.ForeignKey(Course)
	order = models.IntegerField()
	first = models.ForeignKey(Player, related_name='firsts')
	second = models.ForeignKey(Player, related_name='seconds')
	third = models.ForeignKey(Player, related_name='thirds')
	fourth = models.ForeignKey(Player, related_name='fourths')
	
	def __unicode__(self):
		return unicode(self.event.event_date) + " - " + self.course.name
	