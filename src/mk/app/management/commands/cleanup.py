from django.core.management.base import NoArgsCommand, BaseCommand
from django.db import transaction
from mk.app.models import Event, OLD_EVENT_AGE
from optparse import make_option
import datetime

class Command(NoArgsCommand):
	option_list = BaseCommand.option_list + (
		make_option('--noinput', action='store_true', default=False, dest='noinput', help='Prevent user input'),
	)
	help = 'Cleanup task'
	
	def handle_noargs(self, **options):
		noinput = options.get('noinput')
		
		transaction.commit_unless_managed()
		transaction.enter_transaction_management()
		transaction.managed(True)
		
		self.output("Cleaning up old incomplete events")
		
		expire_date = datetime.datetime.today() - datetime.timedelta(days=OLD_EVENT_AGE)
		
		old_events = Event.objects.filter(completed=False, event_date__lt=expire_date)
		
		self.output("Deleting %s old events" % old_events.count())
		
		old_events.delete()
		
		transaction.commit()
		transaction.leave_transaction_management()
	
	def output(self, msg):
		self.stdout.write("%s\n" % msg)