from mk.app.models import Event, Race, Player, Course
from django.forms import ModelForm, ValidationError, models, widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from itertools import chain

class CheckboxControlGroup(widgets.CheckboxSelectMultiple):
	def render(self, name, value, attrs=None, choices=()):
		if value is None: value = []
		has_id = attrs and 'id' in attrs
		final_attrs = self.build_attrs(attrs, name=name)
		output = [u'<fieldset data-role="controlgroup">']
		# Normalize to strings
		str_values = set([force_unicode(v) for v in value])
		for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
			# If an ID attribute was given, add a numeric index as a suffix,
			# so that the checkboxes don't all have the same ID attribute.
			if has_id:
				final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
				label_for = u' for="%s"' % final_attrs['id']
			else:
				label_for = ''

			cb = widgets.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
			option_value = force_unicode(option_value)
			rendered_cb = cb.render(name, option_value)
			option_label = conditional_escape(force_unicode(option_label))
			output.append(u'%s <label%s>%s</label>' % (rendered_cb, label_for, option_label))
		output.append(u'</fieldset>')
		return mark_safe(u'\n'.join(output))


class RadioInputCG(widgets.RadioInput):
	def __unicode__(self):
		if 'id' in self.attrs:
			label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
		else:
			label_for = ''
		choice_label = conditional_escape(force_unicode(self.choice_label))
		return mark_safe(u'%s <label%s>%s</label>' % (self.tag(), label_for, choice_label))


class RadioFieldCGRenderer(widgets.RadioFieldRenderer):
	def __init__(self, name, value, attrs, choices):
		self.name, self.value, self.attrs = name, value, attrs
		self.choices = choices
	
	def __iter__(self):
		for i, choice in enumerate(self.choices):
			yield RadioInputCG(self.name, self.value, self.attrs.copy(), choice, i)
	
	def __getitem__(self, idx):
		choice = self.choices[idx] # Let the IndexError propogate
		return RadioInputCG(self.name, self.value, self.attrs.copy(), choice, idx)
	
	def __unicode__(self):
		return self.render()

	def render(self):
		return mark_safe(u'<fieldset data-role="controlgroup" data-type="horizontal">\n%s\n</fieldset>' % u'\n'.join([u'%s'
			% force_unicode(w) for w in self]))


class RadioSelectControlGroup(widgets.RadioSelect):
	renderer = RadioFieldCGRenderer


class EventForm(ModelForm):
	players = models.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=CheckboxControlGroup, label="Select players for this event")
	
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
			'first': RadioSelectControlGroup,
			'second': RadioSelectControlGroup,
			'third': RadioSelectControlGroup,
			'fourth': RadioSelectControlGroup,
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