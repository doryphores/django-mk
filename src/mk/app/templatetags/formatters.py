from django import template
from mk.app.models import RANK_STRINGS
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def percentage(value, arg):
	"Displays value as percentage of given value"
	return "%.1f%%" % (float(value) / float(arg) * 100,)
percentage.is_safe = True

@register.filter
@stringfilter
def position(value):
	"Displays race or event position as string"
	return RANK_STRINGS[int(value)]