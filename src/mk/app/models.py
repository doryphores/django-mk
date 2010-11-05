from django.db import models

class Player(models.Model):
	class Meta:
		ordering = ['name']
	
	name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name
	
class Course(models.Model):
	class Meta:
		ordering = ['name']
	
	name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name