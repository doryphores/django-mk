from django.shortcuts import get_object_or_404, render, redirect
from app.models import Race, Event, EventResult, Player,\
	RANK_STRINGS, RaceResult, Track, RACE_COUNT
from django.db import transaction
from django.contrib import messages
from app.forms import RaceForm
from django.db.models import Min, Max

def home(request):
	players = Player.active_objects.order_by('-rating')
	
	fanatic = players.order_by('-race_count')[0:1].get()
	topform = players.order_by('-form')[0:1].get()
	birdo = players.order_by('form')[0:1].get()
	total_event_count = Event.completed_objects.count()
	
	return render(request, 'home.html', {
		'players': players,
		'fanatic': fanatic,
		'topform': topform,
		'birdo': birdo,
		'total_event_count': total_event_count,
	})

def players(request):
	player_list = Player.objects.order_by('-rating').all()
	
	return render(request, 'players.html', {
		'player_list': player_list,
	})

def player(request, player_id):
	player = get_object_or_404(Player, pk=player_id)
	
	total_event_count = Event.completed_objects.count()
	
	event_results = EventResult.completed_objects.filter(player=player).select_related('event')
	
	scores = event_results.aggregate(min=Min('points'), max=Max('points'))
	
	return render(request, 'player.html', {
		'total_event_count': total_event_count,
		'player': player,
		'scores': scores,
	})

def player_events(request, player_id):
	player = get_object_or_404(Player, pk=player_id)
	
	total_event_count = Event.completed_objects.count()
	
	event_results = EventResult.completed_objects.filter(player=player).select_related('event')
	
	# Data for event ranking graph (reverse rank values to fit graph)
	recent_rankings = [str(abs(er.rank - 3)+1) for er in event_results[0:100]]
	recent_points = [str(er.points) for er in event_results[0:100]]
	# Reverse order so that recent events are on the left
	recent_rankings.reverse()
	recent_points.reverse()
	
	recent_results = event_results[0:20]
	
	slot_performance = player.get_slot_performance()
	
	# Build data sets for week day performance graph
	
	weekday_labels = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun',)
	lunch_data = ['-1'] * 7 # Lunch averages
	evening_data = ['-1'] * 7 # Evening averages
	for row in slot_performance:
		if row[1] == 0:
			lunch_data[int(row[0])-1] = "%.2f" % row[2]
		else:
			evening_data[int(row[0])-1] = "%.2f" % row[2]
	
	# Convert data sets to formatted string
	weekday_stats = '|'.join([','.join(lunch_data), ','.join(evening_data)])
	
	return render(request, 'player_events.html', {
		'total_event_count': total_event_count,
		'player': player,
		'recent_rankings': recent_rankings,
		'recent_points': recent_points,
		'recent_results': recent_results,
		'weekday_stats': weekday_stats,
		'weekday_labels': '|'.join(weekday_labels),
	})

def player_tracks(request, player_id):
	player = get_object_or_404(Player, pk=player_id)
	
	return render(request, 'player_tracks.html', {
		'player': player,
	})

def tracks(request):
	track_list = Track.objects.all()
	
	return render(request, 'tracks.html', { 'track_list': track_list })

def track(request, track_id):
	track = get_object_or_404(Track, pk=track_id)
	
	players = Player.objects.get_track_rankings(track)
	
	return render(request, 'track.html', {
		'track': track,
		'race_count': track.race_count,
		'player_list': players,
	})

@transaction.commit_on_success()
def new(request):
	selected_players = None
	
	if request.method == 'POST':
		selected_players = Player.objects.filter(pk__in=request.POST.getlist('players'))
		
		if selected_players.count() == 4:
			event = Event()
			event.save()
			
			for player in selected_players:
				EventResult(player=player, event=event).save()
			
			request.session['event_pk'] = event.pk
			
			return redirect("race-start")
		else:
			messages.error(request, 'Please select exactly 4 players')
	
	# Order player list by race_count
	player_list = Player.objects.order_by('-race_count').all()
	if not selected_players:
		# Auto select most fanatic players
		selected_players = player_list[:4]
	
	return render(request, 'new.html', { 'player_list': player_list, 'selected_players': selected_players })

@transaction.commit_on_success()
def race(request, race_id=0):
	if 'event_pk' not in request.session:
		messages.error(request, 'Event not found in session')
		return redirect('home-page')
	try:
		event = Event.objects.get(pk=request.session['event_pk'])
	except Event.DoesNotExist:
		messages.error(request, 'Event not found in session')
		return redirect('home-page')
	
	try:
		race = Race.objects.filter(event=event).get(pk=race_id)
	except Race.DoesNotExist:
		race = Race(event=event, order=event.race_count)
	
	if request.method == 'POST':
		form = RaceForm(request.POST, instance=race)
		
		if form.is_valid():
			race.track = Track.objects.get(pk=form.cleaned_data['track'])
			race.save()
			
			# Delete existing race results
			race.results.all().delete()
			
			# Write new race results
			for i, position in enumerate(RANK_STRINGS):
				RaceResult(race=race, player=Player.objects.get(pk=form.cleaned_data[position]), position=i).save()
			
			if event.race_count == RACE_COUNT:
				return redirect('confirm-results')
			else:
				try:
					next_race = event.races.get(order=race.order + 1)
					return redirect("race", (), { "race_id": next_race.pk })
				except Race.DoesNotExist:
					return redirect("race-start")
	else:
		form = RaceForm(instance=race)
	
	try:
		previous_race = event.races.get(order=race.order - 1)
	except Race.DoesNotExist:
		previous_race = None
	
	ratings = event.get_rating_changes()
	results = [{'player': r.player, 'points': r.points, 'rating': ratings[r.player]} for r in event.results.all()]
	
	view_vars = {
		'form': form,
		'results': results,
		'race': race,
		'previous_race': previous_race,
	}
	
	return render(request, 'race.html', view_vars)


def confirm(request):
	if 'event_pk' not in request.session:
		messages.error(request, 'Event not found in session')
		return redirect('home-page')
	try:
		event = Event.objects.get(pk=request.session['event_pk'])
	except Event.DoesNotExist:
		messages.error(request, 'Event not found in session')
		return redirect('home-page')
	
	ratings = event.get_rating_changes()
	results = [{'player': r.player, 'points': r.points, 'rating': ratings[r.player]} for r in event.results.all()]
		
	view_vars = {
		'results': results,
		'previous_race': event.races.all()[:1].get(),
	}
	
	return render(request, 'confirm.html', view_vars)


@transaction.commit_on_success()
def finish(request):
	if 'event_pk' not in request.session:
		messages.error(request, 'Event not found in session')
		return redirect('home-page')
	try:
		event = Event.objects.get(pk=request.session['event_pk'])
	except Event.DoesNotExist:
		messages.error(request, 'Event not found in session')
		return redirect('home-page')
	
	old_kings = {}
	for track in event.tracks.all():
		old_kings[track.pk] = list(track.kings.values_list('player__name', flat=True))
	
	event.completed = True
	event.save()
	
	event = Event.objects.get(pk=event.pk)
	
	new_kings = []
	for track in event.tracks.all():
		king_names = list(track.kings.values_list('player__name', flat=True))
		if king_names != old_kings[track.pk]:
			new_kings.append({
				'track': track.name,
				'new': king_names,
				'old': old_kings[track.pk],
			})
	
	# Remove event from session
	del request.session['event_pk']
	
	if new_kings:
		view_vars = {
			'new_kings': new_kings,
		}
		return render(request, 'summary.html', view_vars)
	else:
		return redirect('home-page')