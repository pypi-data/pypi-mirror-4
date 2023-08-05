# -*- coding: utf-8 -*-
import os
from south.db import db
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        path = lambda p: os.path.join(os.path.dirname(__file__), p)

        db.execute_many(open(path('zone.sql')).read())
        db.execute_many(open(path('country.sql')).read())
        db.execute_many(open(path('state.sql')).read())

    def backwards(self, orm):
        db.execute_many('delete * from shipping_zone;')
        db.execute_many('delete * from shipping_country;')
        db.execute_many('delete * from state;')

    complete_apps = ['shipping']
