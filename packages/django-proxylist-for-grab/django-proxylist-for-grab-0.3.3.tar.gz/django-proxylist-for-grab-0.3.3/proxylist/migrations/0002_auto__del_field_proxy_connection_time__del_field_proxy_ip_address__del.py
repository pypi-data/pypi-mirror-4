# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Proxy.connection_time'
        db.delete_column('proxylist_proxy', 'connection_time')

        # Deleting field 'Proxy.ip_address'
        db.delete_column('proxylist_proxy', 'ip_address')

        # Deleting field 'Proxy.speed'
        db.delete_column('proxylist_proxy', 'speed')

        # Adding field 'Proxy.hostname'
        db.add_column('proxylist_proxy', 'hostname',
                      self.gf('django.db.models.fields.CharField')(default='8.8.8.8', unique=True, max_length=75),
                      keep_default=False)

        # Adding field 'Proxy.user'
        db.add_column('proxylist_proxy', 'user',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Proxy.password'
        db.add_column('proxylist_proxy', 'password',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'ProxyCheckResult.ip_address'
        db.delete_column('proxylist_proxycheckresult', 'ip_address')

        # Adding field 'ProxyCheckResult.hostname'
        db.add_column('proxylist_proxycheckresult', 'hostname',
                      self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Proxy.connection_time'
        db.add_column('proxylist_proxy', 'connection_time',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Proxy.ip_address'
        db.add_column('proxylist_proxy', 'ip_address',
                      self.gf('django.db.models.fields.IPAddressField')(default='8.8.8.8', max_length=15),
                      keep_default=False)

        # Adding field 'Proxy.speed'
        db.add_column('proxylist_proxy', 'speed',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Proxy.hostname'
        db.delete_column('proxylist_proxy', 'hostname')

        # Deleting field 'Proxy.user'
        db.delete_column('proxylist_proxy', 'user')

        # Deleting field 'Proxy.password'
        db.delete_column('proxylist_proxy', 'password')

        # Adding field 'ProxyCheckResult.ip_address'
        db.add_column('proxylist_proxycheckresult', 'ip_address',
                      self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'ProxyCheckResult.hostname'
        db.delete_column('proxylist_proxycheckresult', 'hostname')


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