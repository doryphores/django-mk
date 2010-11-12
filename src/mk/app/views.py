from django.shortcuts import render_to_response
from mk.app.forms import EventForm, RaceForm
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from mk.app.models import Race, Event, EventResult, Player, RANK_STRINGS,\
	RaceResult, Track, POSITION_POINTS
from operator import itemgetter
from django.db import transaction
from django.contrib import messages

def home(request):
	player_list = Player.objects.all()
	
	return render_to_response('home.html')

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
	
	try:
		race = Race.objects.filter(event=event).get(pk=race_id)
	except Race.DoesNotExist:
		race = Race(event=event, order=event.race_count)
	
	if request.method == 'POST':
		race.track = Track.objects.get(pk=request.POST['track'])
		race.save()
		
		race.results.all().delete()
		
		for i, position in enumerate(RANK_STRINGS):
			RaceResult(race=race, player=Player.objects.get(pk=request.POST[position]), position=i).save()
		
		for result in event.results.all():
			result.points = 0
			
			for i, position in enumerate(RANK_STRINGS):
				count = result.player.race_results.filter(position=i).count()
				result.points += count * POSITION_POINTS[i]
				setattr(result, RANK_STRINGS + "s", count)
			
			result.save()
		
		for i, result in enumerate(event.results.all().order_by('-point')):
			result.rank = i
			result.save()			
		
		return HttpResponseRedirect('/race/')
	else:
		form = RaceForm(instance=race)
	
	view_vars = {
		'event': event,
		'race': race,
	}
	
	return render_to_response('race.html', view_vars, context_instance=RequestContext(request))