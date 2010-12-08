from django.db import models, connection, transaction
import datetime
from django.db.utils import IntegrityError
from django.db.models.aggregates import Avg

POSITION_POINTS = [15,9,4,1]

FORM_COUNT = 10

RACE_COUNT = 8

MAX_EVENT_POINTS = sum(POSITION_POINTS) * RACE_COUNT

RANK_STRINGS = ['first', 'second', 'third', 'fourth']

class Player(models.Model):
	name = models.CharField(max_length=200, unique=True)
	avatar = models.ImageField(upload_to='images/avatars', blank=True)
	
	rating = models.IntegerField(default=0)
	
	def _get_latest_stats(self):
		return self.stats.all()[0:1].get()
	latest_stats = property(_get_latest_stats)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['-rating']


class TrackManager(models.Manager):
	def all_by_popularity(self):
		return Track.objects.raw('''
			select		app_track.*, count(app_race.id) as race_count
			from		app_track left outer join app_race on app_race.track_id = app_track.id left outer join app_event on app_event.id = app_race.event_id and app_event.completed = 1
			group by	app_track.id
			order by	race_count desc, app_track.name''')


class Track(models.Model):
	name = models.CharField(max_length=200, unique=True)
	
	objects = TrackManager()
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['name']


class CompletedEventResultManager(models.Manager):
	def get_query_set(self):
		return super(CompletedEventResultManager, self).get_query_set().filter(event__completed=True)


class EventResult(models.Model):
	event = models.ForeignKey('Event', related_name='results')
	player = models.ForeignKey('Player', related_name='event_results')
	
	points = models.PositiveSmallIntegerField(default=0)
	rank = models.PositiveSmallIntegerField(default=0)
	firsts = models.PositiveSmallIntegerField(default=0)
	seconds = models.PositiveSmallIntegerField(default=0)
	thirds = models.PositiveSmallIntegerField(default=0)
	fourths = models.PositiveSmallIntegerField(default=0)
	
	objects = models.Manager()
	completed_objects = CompletedEventResultManager()
	
	def save(self, *args, **kwargs):
		old_points = self.points
		
		# Calculate points
		new_points = 0
		for i, position in enumerate(RANK_STRINGS):
			new_points += getattr(self, '%ss' % position) * POSITION_POINTS[i]
		
		# If points have changed
		if new_points != self.points:
			self.points = new_points
		
		super(EventResult, self).save(*args, **kwargs)
		
		# Update rank for all results in event if points have changed
		if new_points != old_points:
			cursor = connection.cursor()
			
			for i, result in enumerate(self.event.results.all().order_by('-points')):
				cursor.execute('UPDATE app_eventresult SET rank = %s WHERE id = %s', [i, result.pk])
				transaction.commit_unless_managed()
	
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


class CompletedEventManager(models.Manager):
	def get_query_set(self):
		return super(CompletedEventManager, self).get_query_set().filter(completed=True)


class Event(models.Model):
	event_date = models.DateTimeField(unique=True)
	completed = models.BooleanField(default=False)
	players = models.ManyToManyField(Player, through='EventResult')
	
	objects = models.Manager()
	completed_objects = CompletedEventManager()
	
	def _get_slot(self):
		if self.event_date.hour < 16:
			return 'lunch'
		else:
			return 'evening'
	slot = property(_get_slot)
	
	def _get_race_count(self):
		return self.races.count()
	race_count = property(_get_race_count)
	
	def get_next_event(self):
		next_events = Event.completed_objects.exclude(pk=self.pk).filter(event_date__gt=self.event_date).order_by('event_date')
		if next_events.exists():
			return next_events[0:1].get()
		else:
			raise Event.DoesNotExist
	
	def update_results(self):
		# Update points and position counts
		for result in self.results.all():
			for i, position in enumerate(RANK_STRINGS):
				count = result.player.race_results.filter(race__event=self, position=i).count()
				setattr(result, position + "s", count)
			result.save()
		
		if self.completed:
			self.update_stats()
	
	def update_stats(self):
		# Delete any stats previously created for this event 
		PlayerStat.objects.filter(event=self).delete()
		
		# Write a new stats object for each event participant
		for result in self.results.all():
			previous_stats = PlayerStat.objects.filter(player=result.player, event__event_date__lt=self.event_date)
			
			if previous_stats.exists():
				# Get previous stats for player
				stats = previous_stats[0:1].get()
			else:
				stats = PlayerStat(player=result.player)
			
			stats.event = self
			stats.pk = None
			
			# Update points and race count
			stats.points += result.points
			stats.race_count += RACE_COUNT
			
			# Calculate overall average
			stats.average = float(stats.points) / float(stats.race_count)
			
			# Calculate form average
			previous_results = EventResult.completed_objects.filter(player=result.player, event__event_date__lte=self.event_date).order_by('-event__event_date')[0:FORM_COUNT]
			
			if previous_results.count() < FORM_COUNT:
				# Not enough events for form calculation
				stats.form = stats.average
			else:
				stats.form = sum([er.points for er in previous_results]) / float(FORM_COUNT * RACE_COUNT)
			
			# Update race position counts
			stats.race_firsts += result.firsts
			stats.race_seconds += result.seconds
			stats.race_thirds += result.thirds
			stats.race_fourths += result.fourths
			
			# Update event position counts
			setattr(stats, 'event_%ss' % RANK_STRINGS[result.rank], getattr(stats, 'event_%ss' % RANK_STRINGS[result.rank]) + 1)
			
			stats.save()
		
		# Write a stats record for players not in this event
		for player in Player.objects.exclude(pk__in=self.players.all()):
			previous_stats = PlayerStat.objects.filter(player=player)
			
			if previous_stats.exists():
				# Get previous stats for player
				stats = previous_stats[0]
			else:
				stats = PlayerStat(player=player)
			
			stats.event = self
			stats.pk = None
			
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
			next_event = self.get_next_event()
			next_event.update_stats()
		except Event.DoesNotExist:
			# This the latest completed event, so do nothing
			pass
	
	def save(self, *args, **kwargs):
		if self.event_date is None:
			self.event_date = datetime.datetime.today()
		
		require_stats_update = False
		if self.pk is not None:
			old_record = Event.objects.get(pk=self.pk)
			require_stats_update = not old_record.completed and self.completed
		
		super(Event, self).save(*args, **kwargs)
		
		if require_stats_update:
			self.update_stats()
	
	def delete(self, *args, **kwargs):
		require_update = False
		if self.pk is not None and self.completed:
			try:
				next_event = self.get_next_event()
				require_update = True
			except Event.DoesNotExist:
				pass
		
		super(Event, self).delete(*args, **kwargs)
		
		if require_update:
			next_event.update_stats()
	
	def __unicode__(self):
		return u'%s (%s slot)' % (self.event_date.strftime("%a. %b. %d %Y"), self.slot)
	
	class Meta:
		ordering = ['-event_date']
		get_latest_by = 'event_date'


class PlayerStat(models.Model):
	player = models.ForeignKey(Player, related_name='stats')
	event = models.ForeignKey(Event, related_name='stats')
	
	rank = models.PositiveSmallIntegerField(default=0)
	form_rank = models.PositiveSmallIntegerField(default=0)
	points = models.PositiveIntegerField(default=0)
	race_count = models.PositiveIntegerField(default=0)
	
	average = models.FloatField(default=0.0)
	form = models.FloatField(default=0.0)
	
	event_firsts = models.PositiveIntegerField(default=0)
	event_seconds = models.PositiveIntegerField(default=0)
	event_thirds = models.PositiveIntegerField(default=0)
	event_fourths = models.PositiveIntegerField(default=0)
	
	race_firsts = models.PositiveIntegerField(default=0)
	race_seconds = models.PositiveIntegerField(default=0)
	race_thirds = models.PositiveIntegerField(default=0)
	race_fourths = models.PositiveIntegerField(default=0)
	
	def _get_event_count(self):
		return self.race_count / RACE_COUNT
	event_count = property(_get_event_count)
	
	def __unicode__(self):
		return u'%s on %s' % (self.player.name, self.event)
	
	class Meta:
		ordering =['event', 'form_rank', 'rank']


class Race(models.Model):
	event = models.ForeignKey(Event, related_name='races')
	track = models.ForeignKey(Track, null=True, related_name='races')
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