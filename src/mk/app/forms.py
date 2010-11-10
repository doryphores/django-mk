from mk.app.models import Event, Race, Player, Course
from django.forms import ModelForm, ValidationError, models, widgets
from django.utils.safestring import mark_safe

class CheckboxSelectMultipleNoUl(widgets.CheckboxSelectMultiple):
	def render(self, *args, **kwargs):
		output = super(CheckboxSelectMultipleNoUl, self).render(*args, **kwargs)
		return mark_safe(output.replace(u'<ul>', u'').replace(u'</ul>', u'').replace(u'<li>', u'').replace(u'</li>', u''))

class EventForm(ModelForm):
	players = models.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=CheckboxSelectMultipleNoUl)
	
	class Meta:
		model = Event
		exclude = ('complete',)
		
	def clean_players(self):
		data = self.cleaned_data['players']
		
		if len(data) != 4:
			raise ValidationError("You must select exactly 4 players")
		
		return data
		
class RaceForm(ModelForm):
	class Meta:
		model = Race
		exclude = ('event', 'order')
		widgets = {
			'first': widgets.RadioSelect,
			'second': widgets.RadioSelect,
			'third': widgets.RadioSelect,
			'fourth': widgets.RadioSelect,
		}
	
	def __init__(self, *args, **kwargs):
		super(RaceForm, self).__init__(*args, **kwargs)
		
		player_choices = self.instance.event.players
		course_choices = Course.objects.exclude(pk__in=self.instance.event.race_set.exclude(pk=self.instance.pk).values_list('course'))
		
		self.fields['course'].queryset = course_choices
		self.fields['first'].queryset = player_choices
		self.fields['first'].empty_label = None
		self.fields['second'].queryset = player_choices
		self.fields['second'].empty_label = None
		self.fields['third'].queryset = player_choices
		self.fields['third'].empty_label = None
		self.fields['fourth'].queryset = player_choices
		self.fields['fourth'].empty_label = None
		
	def clean(self):
		cleaned_data = self.cleaned_data
		players = [cleaned_data.get('first'), cleaned_data.get('second'), cleaned_data.get('third'), cleaned_data.get('fourth')]
		
		for player in players:
			if player == None:
				raise ValidationError, "All positions must be selected"
		
		if len(players) < 4:
			raise ValidationError, "All positions must be selected"
		
		if len(set(players)) < 4:
			raise ValidationError, "Can't have multiple players in same position"
		
		return cleaned_data