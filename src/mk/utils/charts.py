import urllib2
import urllib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from urllib2 import HTTPError, URLError

def create(data, file):
	post_data = {
		'chf': 'bg,s,00000000', # Transparent background
	}
	
	# Update defaults with given chart data
	post_data.update(data)
	
	# Setup request
	req = urllib2.Request(url='http://chart.apis.google.com/chart', data=urllib.urlencode(post_data))
	
	path = 'images/charts/%s' % file
	
	try:
		# Do the call to Google Charts
		response = urllib2.urlopen(req)
		
		# Delete previous chart
		if default_storage.exists(path):
			default_storage.delete(path)
		
		# Save new chart
		default_storage.save(path, ContentFile(response.read()))
	except HTTPError, e:
		# TODO: Do some logging
		raise e
	except URLError, e:
		# TODO: Do some logging
		raise e
