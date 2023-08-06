# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Proxy.created'
        db.add_column('proxylist_proxy', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2013, 4, 27, 0, 0), db_index=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Proxy.created'
        db.delete_column('proxylist_proxy', 'created')


    models = {
        'proxylist.mirror': {
            'Meta': {'object_name': 'Mirror'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output_type': ('django.db.models.fields.CharField', [], {'default': "'plm_v1'", 'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'proxylist.proxy': {
            'Meta': {'ordering': "('-last_check',)", 'object_name': 'Proxy'},
            'anonymity_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'elapsed_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'errors': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_check': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'proxy_type': ('django.db.models.fields.CharField', [], {'default': "'http'", 'max_length': '10'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'proxylist.proxycheckresult': {
            'Meta': {'object_name': 'ProxyCheckResult'},
            'check_end': ('django.db.models.fields.DateTimeField', [], {}),
            'check_start': ('django.db.models.fields.DateTimeField', [], {}),
            'forwarded': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_reveal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mirror': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proxylist.Mirror']"}),
            'proxy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proxylist.Proxy']"}),
            'raw_response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'real_ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'response_end': ('django.db.models.fields.DateTimeField', [], {}),
            'response_start': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['proxylist']