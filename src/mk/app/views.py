from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from mk.app.models import Race, Event, EventResult, Player,\
	RANK_STRINGS, RaceResult, Track, PlayerStat, RACE_COUNT
from django.db import transaction
from django.contrib import messages
from mk.app.forms import RaceForm

def home(request):
	try:
		player_stats = PlayerStat.objects.filter(event=Event.objects.latest()).all()
	except Event.DoesNotExist:
		player_stats = PlayerStat.objects.none()
	
	return render_to_response('home.djhtml', { 'player_stats': player_stats })

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
	
	return render_to_response('new.djhtml', { 'player_list': player_list, 'selected_players': selected_players }, context_instance=RequestContext(request))

@transaction.commit_on_success()
def race(request, race_id=0):
	event = Event.objects.get(pk=request.session['event_pk'])
	
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
	
	view_vars = {
		'form': form,
		'event': event,
		'race': race,
		'previous_race': previous_race,
	}
	
	return render_to_response('race.djhtml', view_vars, context_instance=RequestContext(request))


def confirm(request):
	event = Event.objects.get(pk=request.session['event_pk'])
	
	view_vars = {
		'event': event,
		'previous_race': event.races.all()[:1].get()
	}
	
	return render_to_response('confirm.djhtml', view_vars)

@transaction.commit_on_success()
def finish(request):
	event = Event.objects.get(pk=request.session['event_pk'])
	
	event.complete()
	
	return HttpResponseRedirect('/')