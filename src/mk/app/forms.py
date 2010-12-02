from django import forms
from django.forms import widgets, ValidationError
import re
from django.utils.safestring import mark_safe

class RadioSelectPlain(widgets.RadioSelect):
	def render(self, name, value, attrs=None, choices=()):
		output = self.get_renderer(name, value, attrs, choices).render()
		p = re.compile(r'</?(ul|li)>')
		output = p.sub('', output)
		p = re.compile(r'<label(.*?)>(<input.*?>)(.*?)</label>')
		output = p.sub(r'\2<label\1>\3</label>', output)
		return mark_safe(unicode(output))

class RaceForm(forms.Form):
	track = forms.ChoiceField(required=True, widget=widgets.Select({ 'data-inline': 'true' }))
	first = forms.ChoiceField(widget=RadioSelectPlain, required=True)
	second = forms.ChoiceField(widget=RadioSelectPlain, required=True)
	third = forms.ChoiceField(widget=RadioSelectPlain, required=True)
	fourth = forms.ChoiceField(widget=RadioSelectPlain, required=True)
	
	def __init__(self, *args, **kwargs):
		instance = kwargs['instance']
		del kwargs['instance']
		
		super(RaceForm, self).__init__(*args, **kwargs)
		
		self.fields['track'].choices = [(track.pk, track.name) for track in instance.get_available_tracks()]
		if (instance.track != None):
			self.fields['track'].initial = instance.track.pk
		player_choices = [(player.pk, player.name) for player in instance.event.players.all()]
		self.fields['first'].choices = player_choices
		self.fields['first'].initial = instance.first.pk
		self.fields['second'].choices = player_choices
		self.fields['second'].initial = instance.second.pk
		self.fields['third'].choices = player_choices
		self.fields['third'].initial = instance.third.pk
		self.fields['fourth'].choices = player_choices
		self.fields['fourth'].initial = instance.fourth.pk
	
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