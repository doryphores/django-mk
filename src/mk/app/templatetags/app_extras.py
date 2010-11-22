from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def buildlink(value):
	return "%s%s" % (settings.BASE_URL, value)
buildlink.is_safe = True