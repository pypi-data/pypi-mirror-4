# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import DataMigration
from shipping.models import UPSCarrier, CorreiosCarrier, Bin


class Migration(DataMigration):

    def forwards(self, orm):
        carrier = UPSCarrier.objects.create(name='UPS', status=1)

        # Large-18" x 13" x 3"
        Bin.objects.create(name='UPS Express Box - Large',
            height=45.72, width=33.02, length=7.62, weight=0,
            carrier=carrier)

        # Medium-15" x 11" x 3"
        Bin.objects.create(name='UPS Express Box - Medium',
            height=38.1, width=27.94, length=7.62, weight=0,
            carrier=carrier)

        # Small- 13" x 11" x 2"
        Bin.objects.create(name='UPS Express Box - Small',
            height=33.02, width=27.94, length=5.08, weight=0,
            carrier=carrier)

        carrier = CorreiosCarrier.objects.create(name='Correios',
            status=1)

    def backwards(self, orm):
        db.execute_many('delete * from carrier;')
        db.execute_many('delete * from bin;')

    complete_apps = ['shipping']
