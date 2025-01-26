# Django imports
from django.conf import settings

# 3rd party imports
from rest_framework import viewsets, permissions
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.response import Response

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
    r = requests.get('http://[hostname:port]/api/calls/')

    # display the json response
    pprint(json.loads(r.content))
    ```
    """
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_update_or_create(self, request):
        ''' Iterate over JSON objects and update_or_create incidents '''
        results = []
        for call_dict in request.data:
            obj, c = Incident.objects.update_or_create(
                num = obj['num'],
                dtg_alarm = obj.get('dtg_alarm'),
                defaults = dict(
                    fd_id = obj.get('fd_id')
                )
            )



        return Response({'status': 'the action ran!'})

    def destroy(self, request, pk=None):
        # Do not allow delete from the API
        raise MethodNotAllowed(method='POST')
