from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from mk.app.models import Race, Event, EventResult, Player,\
	RANK_STRINGS, RaceResult, Track, PlayerStat
from django.db import transaction
from django.contrib import messages

def home(request):
	try:
		player_stats = PlayerStat.objects.filter(event=Event.objects.latest()).all()
	except Event.DoesNotExist:
		player_stats = PlayerStat.objects.none()
	
	return render_to_response('home.djhtm', { 'player_stats': player_stats })

@transaction.commit_on_success()
def new(request):
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
	else:
		selected_players = Player.objects.none()
	
	player_list = Player.objects.all()
	
	return render_to_response('new.html', { 'player_list': player_list, 'selected_players': selected_players }, context_instance=RequestContext(request))

@transaction.commit_on_success()
def race(request, race_id=0):
	event = Event.objects.get(pk=request.session['event_pk'])
	
	form_data = {
		'track': None,
		'first': None,
		'second': None,
		'third': None,
		'fourth': None,
	}
	
	try:
		race = Race.objects.filter(event=event).get(pk=race_id)
		form_data['track'] = race.track
		form_data['first'] = race.first
		form_data['second'] = race.second
		form_data['third'] = race.third
		form_data['fourth'] = race.fourth
	except Race.DoesNotExist:
		race = Race(event=event, order=event.race_count)
	
	if request.method == 'POST':
		player_list = []
		valid = True
		for position in RANK_STRINGS:
			player_pk = request.POST.get(position, 0)
			if valid and player_pk == 0:
				messages.error(request, "All positions must be selected")
				valid = False
			else:
				form_data[position] = Player.objects.get(pk=player_pk)
				player_list.append(form_data[position])
		
		if len(player_list) == 4 and len(set(player_list)) < 4:
			messages.error(request, "Can't have multiple players in same position")
			valid = False
		
		form_data['track'] = Track.objects.get(pk=request.POST.get('track', 0))
		
		if valid:
			race.track = form_data['track']
			
			# Save the race
			race.save()
			
			# Delete existing race results
			race.results.all().delete()
			
			# Write new race results
			for i, position in enumerate(RANK_STRINGS):
				RaceResult(race=race, player=Player.objects.get(pk=request.POST[position]), position=i).save()
			
			# Update event results
			event.update_results()
			
			if event.completed:
				return HttpResponseRedirect('/confirm/')
			else:
				return HttpResponseRedirect('/race/')
	
	try:
		previous_race = event.races.get(order=race.order - 1)
	except Race.DoesNotExist:
		previous_race = None
	
	view_vars = {
		'event': event,
		'race': race,
		'form_data': form_data,
		'previous_race': previous_race,
	}
	
	return render_to_response('race.html', view_vars, context_instance=RequestContext(request))


def confirm(request):
	event = Event.objects.get(pk=request.session['event_pk'])
	
	view_vars = {
		'event': event,
		'previous_race': event.races.all()[:1].get()
	}
	
	return render_to_response('confirm.html', view_vars)