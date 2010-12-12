from django.core.management.base import NoArgsCommand
from mk.app.models import Event
from django.db import transaction

class Command(NoArgsCommand):
	help = 'Compute ratings'
	
	def handle_noargs(self, **options):
		events = Event.completed_objects.reverse().all()
		
		k = 2
		
		transaction.commit_unless_managed()
		transaction.enter_transaction_management()
		transaction.managed(True)
		
		for event in events:
			#self.output('Processing event %s' % event)
			
			new_ratings = {}
			for p in event.players.all():
				new_ratings[p] = p.rating
			
			results = event.results.all()
			
			for result in results:
				player = result.player
				for opp_result in results:
					opponent = opp_result.player
					if opponent is not player:
						exp = 1 / (1 + pow(10, float(opponent.rating - player.rating)/400))
						res = 0.5
						if result.points > opp_result.points:
							res = 1
						elif result.points < opp_result.points:
							res = 0
						#delta = float(abs(result.points - opp_result.points)) * (res - exp)
						delta = 32.0 * (res - exp)
						#new_ratings[player] += k * int(round(delta))
						new_ratings[player] += int(round(delta))
						#self.output("%s(%s) vs. %s(%s): %s (%.2f)" % (player.name, ratings[player], opponent.name, ratings[opponent], res, delta))
			
			for stat in event.stats.all():
				if stat.player in new_ratings:
					stat.rating_delta = new_ratings[stat.player] - stat.player.rating;
					stat.rating = new_ratings[stat.player];
					stat.player.rating = new_ratings[stat.player];
					stat.player.save();
				else:
					stat.rating_delta = 0;
					stat.rating = stat.player.rating;
				stat.save();
			
			self.output(str(event.pk) + " ,".join(["%s: %s" % (r.name, new_ratings[r])  for r in new_ratings]))
		
		transaction.commit()
		
	def output(self, msg):
		self.stdout.write("%s\n" % msg)