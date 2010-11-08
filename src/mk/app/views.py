from django.shortcuts import render_to_response
from mk.app.forms import EventForm, RaceForm
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from mk.app.models import Race, Event

def home(request):
	return render_to_response('home.html')

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

def race(request):
	event = Event.objects.get(pk=request.session['event_pk'])
	race = Race(event=event)
		
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
	
	return render_to_response('race.html', { 'form': form, 'race_number': event.race_count + 1, 'results': event.results }, context_instance=RequestContext(request))