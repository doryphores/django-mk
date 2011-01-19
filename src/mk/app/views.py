from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from mk.app.models import Race, Event, EventResult, Player,\
	RANK_STRINGS, RaceResult, Track, RACE_COUNT
from django.db import transaction
from django.contrib import messages
from mk.app.forms import RaceForm
from django.db.models import Min, Max

def home(request):
	players = Player.active_objects.order_by('-rating')
	
	fanatic = players.order_by('-race_count')[0:1].get()
	topform = players.order_by('-form')[0:1].get()
	birdo = players.order_by('form')[0:1].get()
	total_event_count = Event.completed_objects.count()
	
	return render_to_response('home.djhtml', {
		'players': players,
		'fanatic': fanatic,
		'topform': topform,
		'birdo': birdo,
		'total_event_count': total_event_count,
	}, context_instance=RequestContext(request))

def players(request):
	player_list = Player.objects.order_by('-rating').all()
	
	return render_to_response('players.djhtml', {
		'player_list': player_list,
	}, context_instance=RequestContext(request))

def player(request, player_id):
	player = get_object_or_404(Player, pk=player_id)
	
	total_event_count = Event.completed_objects.count()
	
	event_results = EventResult.completed_objects.filter(player=player).select_related('event')
	
	# Data for event ranking graph (reverse rank values to fit graph)
	recent_rankings = [str(abs(er.rank - 3)+1) for er in event_results[0:100]]
	# Reverse order so that recent events are on the left
	recent_rankings.reverse()
	
	scores = event_results.aggregate(min=Min('points'), max=Max('points'))
	
	recent_results = event_results[0:20]
	
	return render_to_response('player.djhtml', {
		'total_event_count': total_event_count,
		'player': player,
		'recent_rankings': recent_rankings,
		'scores': scores,
		'recent_results': recent_results,
	}, context_instance=RequestContext(request))

def tracks(request):
	track_list = Track.objects.all()
	
	return render_to_response('tracks.djhtml', { 'track_list': track_list }, context_instance=RequestContext(request))

def track(request, track_id):
	track = get_object_or_404(Track, pk=track_id)
	
	players = Player.objects.get_track_rankings(track)
	
	return render_to_response('track.djhtml', {
		'track': track,
		'race_count': track.race_count,
		'player_list': players,
	}, context_instance=RequestContext(request))

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
			
			return HttpResponseRedirect('/race/')
		else:
			messages.error(request, 'Please select exactly 4 players')
	
	# Order player list by race_count
	player_list = Player.objects.order_by('-race_count').all()
	if not selected_players:
		# Auto select most fanatic players
		selected_players = player_list[:4]
	
	return render_to_response('new.djhtml', { 'player_list': player_list, 'selected_players': selected_players }, context_instance=RequestContext(request))

@transaction.commit_on_success()
def race(request, race_id=0):
	if 'event_pk' not in request.session:
		messages.error(request, 'Event not found in session')
		return HttpResponseRedirect('/')
	try:
		event = Event.objects.get(pk=request.session['event_pk'])
	except Event.DoesNotExist:
		messages.error(request, 'Event not found in session')
		return HttpResponseRedirect('/')
	
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
				return HttpResponseRedirect('/confirm/')
			else:
				try:
					next_race = event.races.get(order=race.order + 1)
					return HttpResponseRedirect('/race/%s/' % next_race.pk)
				except Race.DoesNotExist:
					return HttpResponseRedirect('/race/')
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
	
	return render_to_response('race.djhtml', view_vars, context_instance=RequestContext(request))


def confirm(request):
	if 'event_pk' not in request.session:
		messages.error(request, 'Event not found in session')
		return HttpResponseRedirect('/')
	try:
		event = Event.objects.get(pk=request.session['event_pk'])
	except Event.DoesNotExist:
		messages.error(request, 'Event not found in session')
		return HttpResponseRedirect('/')
	
	ratings = event.get_rating_changes()
	results = [{'player': r.player, 'points': r.points, 'rating': ratings[r.player]} for r in event.results.all()]
		
	view_vars = {
		'results': results,
		'previous_race': event.races.all()[:1].get(),
	}
	
	return render_to_response('confirm.djhtml', view_vars, context_instance=RequestContext(request))


@transaction.commit_on_success()
def finish(request):
	if 'event_pk' not in request.session:
		messages.error(request, 'Event not found in session')
		return HttpResponseRedirect('/')
	try:
		event = Event.objects.get(pk=request.session['event_pk'])
	except Event.DoesNotExist:
		messages.error(request, 'Event not found in session')
		return HttpResponseRedirect('/')
	
	event.completed = True
	event.save()
	
	# Remove event from session
	del request.session['event_pk']
	
	return HttpResponseRedirect('/')