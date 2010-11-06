from mk.app.models import Event, Race, Player, Course
from django.forms import ModelForm
from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

class EventForm(ModelForm):
	players = ModelMultipleChoiceField(queryset=Player.objects.all(), widget=CheckboxSelectMultiple)
	
	class Meta:
		model = Event
		exclude = ('complete',)
		
class RaceForm(ModelForm):
	class Meta:
		model = Race
		exclude = ('event')