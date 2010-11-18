from django.db import models
from django.db.models.fields import PositiveSmallIntegerField,\
	PositiveIntegerField

POSITION_POINTS = [15,9,4,1]

FORM_COUNT = 10

RACE_COUNT = 8

RANK_STRINGS = ['first', 'second', 'third', 'fourth']

class Player(models.Model):
	name = models.CharField(max_length=200, unique=True)
	avatar = models.ImageField(upload_to='images/avatars', blank=True)
	
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
		return u'%s on %s (rank: %s)' % (self.player, self.event, RANK_STRINGS[self.rank])
	
	class Meta:
		ordering = ['event','-points']


class RaceResult(models.Model):
	race = models.ForeignKey('Race', related_name='results')
	player = models.ForeignKey('Player', related_name='race_results')
	
	position = models.PositiveSmallIntegerField(default=0)
	
	def save(self, *args, **kwargs):
		self.race.event.update_results()
		super(RaceResult, self).save(*args, **kwargs)
	
	def delete(self, *args, **kwargs):
		self.race.event.update_results()
		super(RaceResult, self).delete(*args, **kwargs)
	
	def __unicode__(self):
		return u'%s %s (rank: %s)' % (self.player, self.race, RANK_STRINGS[self.position])
	
	class Meta:
		ordering = ['race','position']


class Event(models.Model):
	event_date = models.DateTimeField(auto_now_add=True)
	completed = models.BooleanField(default=False)
	players = models.ManyToManyField(Player, through='EventResult')
	
	def _get_slot(self):
		if self.event_date.hour < 16:
			return 'lunch'
		else:
			return 'evening'
	slot = property(_get_slot)
	
	def _get_race_count(self):
		return self.races.count()
	race_count = property(_get_race_count)
	
	def update_results(self):
		# Update points and position counts
		for result in self.results.all():
			result.points = 0
			
			for i, position in enumerate(RANK_STRINGS):
				count = result.player.race_results.filter(race__event=self, position=i).count()
				result.points += count * POSITION_POINTS[i]
				setattr(result, position + "s", count)
				result.save()
		
		# Update rank
		for i, result in enumerate(self.results.all().order_by('-points')):
			result.rank = i
			result.save()
	
	def complete(self):
		# Mark event as completed
		self.completed = True
		self.save()
		
		# Delete any stats previously created for this event 
		PlayerStat.objects.filter(event=self).delete()
		
		# Write a new stats object for each event participant
		for result in self.results.all():
			try:
				# Get previous stats for player
				stats = PlayerStat.objects.filter(player=result.player, event__event_date__lt=self.event_date).order_by('-event__event_date')[0:1].get()
			except PlayerStat.DoesNotExist:
				# First event for player (get an empty stats model)
				stats = PlayerStat(player=result.player)
			
			stats.event = self
			stats.pk = None
			
			# Update points and race count
			stats.points += result.points
			stats.race_count += RACE_COUNT
			
			# Calculate overall and form averages and deltas
			new_average = EventResult.objects.filter(event__completed=True, player=result.player).aggregate(avg=models.Avg('points'))['avg'] / RACE_COUNT
			stats.average_delta = new_average - stats.average
			stats.average = new_average
			new_form = EventResult.objects.filter(event__completed=True, player=result.player)[0:FORM_COUNT].aggregate(avg=models.Avg('points'))['avg'] / RACE_COUNT
			stats.form_delta = new_form - stats.form
			stats.form = new_form
			
			# Update race position counts
			stats.race_firsts += result.firsts
			stats.race_seconds += result.seconds
			stats.race_thirds += result.thirds
			stats.race_fourths += result.fourths
			
			# Update event position counts
			setattr(stats, 'event_%ss' % RANK_STRINGS[result.rank], getattr(stats, 'event_%ss' % RANK_STRINGS[result.rank]) + 1)
			
			stats.save()
		
		for i, stats in enumerate(PlayerStat.objects.filter(event=self).order_by('-average')):
			stats.rank = i
			stats.save()
		
		for i, stats in enumerate(PlayerStat.objects.filter(event=self).order_by('-form')):
			stats.form_rank = i
			stats.save()
		
		# Now we need to update any subsequent stats records as they depend on eachother
		try:
			# Get the next completed event
			next_event = Event.objects.filter(completed=True, event_date__gt=self.event_date).order_by('event_date')[0:1].get()
			next_event.complete()
		except Event.DoesNotExist:
			# This the latest completed event, so stop
			pass
	
	def __unicode__(self):
		return u'%s (%s slot)' % (self.event_date.strftime("%a. %b. %d %Y"), self.slot)
	
	class Meta:
		ordering = ['-event_date']
		get_latest_by = 'event_date'


class PlayerStat(models.Model):
	player = models.ForeignKey(Player)
	event = models.ForeignKey(Event, related_name='stats')
	
	rank = PositiveSmallIntegerField(default=0)
	form_rank = PositiveSmallIntegerField(default=0)
	points = PositiveIntegerField(default=0)
	race_count = PositiveIntegerField(default=0)
	
	average = models.FloatField(default=0.0)
	average_delta = models.FloatField(default=0.0)
	form = models.FloatField(default=0.0)
	form_delta = models.FloatField(default=0.0)
	
	event_firsts = PositiveIntegerField(default=0)
	event_seconds = PositiveIntegerField(default=0)
	event_thirds = PositiveIntegerField(default=0)
	event_fourths = PositiveIntegerField(default=0)
	
	race_firsts = PositiveIntegerField(default=0)
	race_seconds = PositiveIntegerField(default=0)
	race_thirds = PositiveIntegerField(default=0)
	race_fourths = PositiveIntegerField(default=0)
		
	def __unicode__(self):
		return u'%s on %s' % (self.player.name, self.event)
	
	class Meta:
		ordering =['event', 'form_rank', 'rank']
		get_latest_by = 'record_date'


class Race(models.Model):
	event = models.ForeignKey(Event, related_name='races')
	track = models.ForeignKey(Track, null=True)
	players = models.ManyToManyField(Player, through='RaceResult')
	order = models.PositiveSmallIntegerField()
	
	def get_available_tracks(self):
		return Track.objects.exclude(pk__in=self.event.races.exclude(pk=self.pk).values_list("track"))
	available_tracks = property(get_available_tracks)
	
	def get_first(self):
		try:
			return self.results.get(position=0).player
		except RaceResult.DoesNotExist:
			return Player()
	first = property(get_first)
	
	def get_second(self):
		try:
			return self.results.get(position=1).player
		except RaceResult.DoesNotExist:
			return Player()
	second = property(get_second)
	
	def get_third(self):
		try:
			return self.results.get(position=2).player
		except RaceResult.DoesNotExist:
			return Player()
	third = property(get_third)
	
	def get_fourth(self):
		try:
			return self.results.get(position=3).player
		except RaceResult.DoesNotExist:
			return Player()
	fourth = property(get_fourth)
	
	def __unicode__(self):
		return u'%s on %s' % (self.track, self.event) 
	
	def save(self, *args, **kwargs):
		if self.order == None:
			self.order = self.event.races.count()
		super(Race, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ['event','-order']