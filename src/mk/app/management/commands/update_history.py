from django.core.management.base import NoArgsCommand
from django.db import transaction
from mk.app.models import Player, Event, PlayerHistory

class Command(NoArgsCommand):
	help = 'Re-runs player history from the start'
	
	def handle_noargs(self, **options):
		self.output("Running history update...")
		
		transaction.commit_unless_managed()
		transaction.enter_transaction_management()
		transaction.managed(True)
		
		for p in Player.objects.all():
			try:
				first_state = PlayerHistory.objects.filter(player=p).order_by('-event')[0:1].get()
				first_state.restore()
			except PlayerHistory.DoesNotExist:
				pass
		
		PlayerHistory.objects.all().delete()
		
		if raw_input("Set initial ratings manually? (y/n): ") == 'y':
			for p in Player.objects.all():
				p.rating = raw_input("New rating for %s: " % p.name)
				p.save()
		
		try:
			first_event = Event.completed_objects.order_by('event_date')[0:1].get()
			first_event.update_stats()
			self.output("Done")
		except Event.DoesNotExist:
			self.output("No history to update")
		except:
			transaction.rollback()
			transaction.leave_transaction_management()
			self.output("An error occurred while updating history")
		
		transaction.commit()
		transaction.leave_transaction_management()
	
	def output(self, msg):
		self.stdout.write("%s\n" % msg)