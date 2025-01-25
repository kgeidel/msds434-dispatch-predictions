# Python imports
import logging

# Django imports
from django.db.models import *

# 3rd party imports
from simple_history.models import HistoricalRecords, HistoricForeignKey

# Intraproject imports


class Incident(Model):
    ''' An instance of this model represents a single response to a 911 call. '''

    num = CharField(max_length=11, verbose_name="Call #", unique=True)
    fd_id = CharField(max_length=8, null=True, blank=True)
    dtg_alarm = DateTimeField()
    street_number = CharField(max_length=8, null=True, blank=True)
    route = CharField(max_length=255, null=True, blank=True)
    suite = CharField(max_length=8, null=True, blank=True)
    postal_code = CharField(max_length=16, null=True, blank=True)
    disp = HistoricForeignKey('calls.DISP', on_delete=SET_NULL, blank=True, null=True)
    duration = FloatField(null=True, blank=True)
    history = HistoricalRecords(related_name='log')

    def __str__(self):
        return self.num

class DISP(Model):
    type_str = CharField(max_length=255, unique=True)
    history = HistoricalRecords(related_name='log')

    def __str__(self):
        return self.type_str
