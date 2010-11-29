from django.core.management.base import NoArgsCommand
from django.db import connections, transaction
from mk.app.models import Player, Event, EventResult, MAX_EVENT_POINTS
from django.db.models.aggregates import Sum

class Command(NoArgsCommand):
	help = 'Import events from legacy DB'
	
	def handle_noargs(self, **options):
		cursor = connections['import'].cursor()
		
		cursor.execute('SELECT ID, Name FROM Player')
		row = cursor.fetchone()
		players = {}
		while True:
			if row is None:
				break
			try:
				player = Player.objects.get(name=row[1])
			except Player.DoesNotExist:
				player = Player(name=row[1])
				player.save()
			
			players[row[0]] = player
			
			row = cursor.fetchone()
		
		cursor.execute('''
			SELECT	EventID, Event.Date, PlayerID, [1st], [2nd], [3rd], [4th]
			FROM	Result INNER JOIN Event on Event.ID = Result.EventID
			WHERE	EventID > 3
			ORDER BY Event.Date ASC
		''')
		
		event_id = 0
		event = None
		row = cursor.fetchone()
		
		transaction.commit_unless_managed()
		transaction.enter_transaction_management()
		transaction.managed(True)
		
		try:
			while row:
				if event_id != row[0]:
					event = Event(event_date=row[1])
					event.save()
					event_id = row[0]
					event_points = 0
					self.stdout.write("Importing event %s\n" % event)
				
				result = EventResult(event=event, player=players[row[2]], firsts=row[3], seconds=row[4], thirds=row[5], fourths=row[6])
				result.save()
				event_points += result.points
				
				if event.results.count() == 4:
					if event_points != MAX_EVENT_POINTS:
						# Discard invalid events
						event.delete()
						self.stdout.write("Discarding event %s[%s] (invalid number of points: %s)\n" % (event, event_id, event_points))
					else:
						# Complete event
						event.completed = True
						event.save()
				
				row = cursor.fetchone()
			
		except:
			transaction.rollback()
			transaction.leave_transaction_management()
			self.stdout.write("Unexpected error importing events")
			raise
			return
		
		transaction.commit()
		transaction.leave_transaction_management()
				