from django.shortcuts import render_to_response
from mk.app.forms import EventForm, RaceForm
from django.template.context import RequestContext
from django.http import HttpResponseRedirect

def home(request):
	return render_to_response('home.html')

def new(request):
	if request.method == 'POST':
		form = EventForm(request.POST)
		
		if form.is_valid():
			event = form.save()
			
			request.session['event'] = event
			
			return HttpResponseRedirect('/race/')
	else:
		form = EventForm()
	
	return render_to_response('new.html', { 'form': form }, context_instance=RequestContext(request))

def race(request):
	if request.method == 'POST':
		form = RaceForm(request.POST)
		
		if form.is_valid():
			form.save()
			
			return HttpResponseRedirect('/race/')
	else:
		form = RaceForm()
	
	return render_to_response('race.html')