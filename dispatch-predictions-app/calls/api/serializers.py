# Django imports

# 3rd part imports
from rest_framework import serializers

# Intraproject imports
from calls.models import *


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'
        depth = 1

class DISPSerializer(serializers.ModelSerializer):
    class Meta:
        model = DISP
        fields = '__all__'