from django_tables2 import tables

from calls.models import *


class IncidentTable(tables.Table):
    class Meta:
        model = Incident
        exclude = []

class DISPTable(tables.Table):
    call_count = tables.Column()
    class Meta:
        model = DISP
        exclude = []