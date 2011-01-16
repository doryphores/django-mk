"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from mk.app.models import Event, Player, EventResult
from django.test.client import Client

class SimpleTest(TestCase):
	def test_basic_addition(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class RecordEventTestCase(TestCase):
	fixtures = ['test_data',]
	
	def setUp(self):
		self.client = Client()
		
	def test_new_event(self):
		response = self.client.get('/new/')
		
		self.failUnlessEqual(response.status_code, 200)
		
		self.failUnlessEqual(len(response.context['player_list']), 8, '8 players to select from')
		
		try:
			self.client.session['event_pk']
			self.fail("Shouldn't have a session value")
		except KeyError:
			pass
		
		response = self.client.post('/new/', { 'players': ['1','2','4','5'] }, follow=True)
		#self.assertRedirects(response, '/race/')
		self.assertEqual(self.client.session.get('event_pk'), response.context['race'].event.pk)

class EventTestCase(TestCase):
	fixtures = ['test_data',]
	
	def setUp(self):
		self.players = {
			'martin': Player.objects.get(name='Martin'),
			'adam': Player.objects.get(name='Adam'),
			'andy': Player.objects.get(name='Andy'),
			'anton': Player.objects.get(name='Anton'),
		}
	
	def create_event(self):
		self.event = Event()
		self.event.save()
	
	def test_new_event(self):
		"""
		Tests the creation of a new event
		"""
		
		self.create_event()
		
		self.assertEquals(self.event.completed, False)
		self.assertEquals(self.event.players.count(), 0)
		self.assertEquals(self.event.race_count, 0)
		self.assertTrue(self.event.event_date is not None)
		
	def test_add_event_results(self):
		"""
		Tests adding event result records to event
		"""
		
		self.create_event()
		
		for p in self.players:
			EventResult(event=self.event, player=self.players[p]).save()
		
		self.assertEquals(self.event.players.count(), 4)