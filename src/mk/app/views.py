from django.shortcuts import render_to_response
from mk.app.forms import EventForm, RaceForm
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from mk.app.models import Race, Event, Stats, Player
from operator import itemgetter
from django.db import transaction

def home(request):
	player_list = Player.objects.all()
	
	stats = []
	
	for player in player_list:
		player_stats = Stats.objects.filter(player=player)[0:2]
		if player_stats.count() > 0:
			stats.append({
				'player': player,
				'rank': player_stats[0].average,
				'current': player_stats[0],
				'previous': player_stats[1]
			})
	
	stats.sort(key=itemgetter('rank'), reverse=True)
	
	return render_to_response('home.html', { 'stats': stats })

def new(request):
	if request.method == 'POST':
		form = EventForm(request.POST)
		
		if form.is_valid():
			event = form.save()
			
			request.session['event_pk'] = event.pk
			
			return HttpResponseRedirect('/race/')
	else:
		form = EventForm()
	
	return render_to_response('new.html', { 'form': form }, context_instance=RequestContext(request))

@transaction.commit_on_success
def race(request, race_id=0):
	event = Event.objects.get(pk=request.session['event_pk'])
	
	try:
		race = Race.objects.get(pk=race_id)
	except Race.DoesNotExist:
		race = Race(event=event, order=event.race_count)
	
	if request.method == 'POST':
		form = RaceForm(request.POST, instance=race)
		
		if form.is_valid():
			form.save()
			
			if event.race_count == 8:
				event.set_complete()
				return HttpResponseRedirect('/')
			
			return HttpResponseRedirect('/race/')
	else:
		form = RaceForm(instance=race)
	
	# Format event results as list of sorted tuples (player_name, points)
	results = sorted([(result.name, event.results[result]['points']) for result in event.results], key=itemgetter(1), reverse=True)
	
	try:
		previous_race = event.race_set.get(order=race.order - 1)
		previous_url = '/race/' + str(previous_race.pk) + '/'
	except Race.DoesNotExist:
		previous_url = '/new/'
	
	view_vars = {
		'form': form,
		'race': race,
		'results': results,
		'previous_url': previous_url,
	}
	
	return render_to_response('race.html', view_vars, context_instance=RequestContext(request))