# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        db.execute("UPDATE app_player SET avatar = REPLACE(avatar, 'images/avatars', 'avatars')")


    def backwards(self, orm):
        "Write your backwards methods here."
        db.execute("UPDATE app_player SET avatar = REPLACE(avatar, 'avatars', 'images/avatars')")


    models = {
        'app.event': {
            'Meta': {'ordering': "['-event_date']", 'object_name': 'Event'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Player']", 'through': "orm['app.EventResult']", 'symmetrical': 'False'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Track']", 'through': "orm['app.Race']", 'symmetrical': 'False'})
        },
        'app.eventresult': {
            'Meta': {'ordering': "['event', '-points']", 'object_name': 'EventResult'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['app.Event']"}),
            'firsts': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'fourths': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_results'", 'to': "orm['app.Player']"}),
            'points': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'seconds': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'thirds': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'app.king': {
            'Meta': {'ordering': "['track', '-race_count']", 'object_name': 'King'},
            'average': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'titles'", 'to': "orm['app.Player']"}),
            'race_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'kings'", 'to': "orm['app.Track']"})
        },
        'app.player': {
            'Meta': {'ordering': "['name']", 'object_name': 'Player'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'average': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'event_firsts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event_fourths': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event_seconds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event_thirds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'form': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_firsts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_fourths': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_seconds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_thirds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'app.playerhistory': {
            'Meta': {'ordering': "['event']", 'object_name': 'PlayerHistory'},
            'average': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Event']"}),
            'event_firsts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event_fourths': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event_seconds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event_thirds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'form': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': "orm['app.Player']"}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_firsts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_fourths': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_seconds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'race_thirds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'app.race': {
            'Meta': {'ordering': "['event', '-order']", 'object_name': 'Race'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'races'", 'to': "orm['app.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Player']", 'through': "orm['app.RaceResult']", 'symmetrical': 'False'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'races'", 'null': 'True', 'to': "orm['app.Track']"})
        },
        'app.raceresult': {
            'Meta': {'ordering': "['race', 'position']", 'object_name': 'RaceResult'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'race_results'", 'to': "orm['app.Player']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['app.Race']"})
        },
        'app.track': {
            'Meta': {'ordering': "['name']", 'object_name': 'Track'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        }
    }

    complete_apps = ['app']
