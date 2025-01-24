# Django imports

# 3rd party imports
from rest_framework import viewsets

# Intraproject imports
from calls.models import *
from calls.api.serializers import *

class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Incident instances.

    Example usage:
    ```python
    import requests, json
    from pprint import pprint

    # Query the first page of incidents 
    r = requests.get('http://localhost:8000/api/calls/')

    # display the json response
    pprint(json.loads(r.content))
    ```
    """
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer