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

    @action(detail=False, methods=['get'])
    def get_sync_filters(self, request):
        ''' Returns the dtg that should be used for finding incidents that need to be processed '''
        dtg = Incident.objects.order_by('-dtg_alarm').first().dtg_alarm
        return Response(
            {
                'most_recent_incident': str(dtg.astimezone(settings.TIME_ZONE_OBJ))
            }
        )

    @action(detail=False, methods=['post'])
    def bulk_update_or_create(self, request):
        ''' Iterate over JSON objects and update_or_create incidents '''
        results = {'created_calls':0, 'created_disp':0, 'error_calls':0, 'error_disp':0, 'error_msgs':[]}
        for call_dict in request.data:
            # Create the DISP
            disp_str = call_dict.get('type_str')
            if disp_str is not None:
                try:
                    disp, c = DISP.objects.get_or_create(type_str=disp_str.strip())
                    if c:
                        results['created_disp'] += 1
                except Exception as e:
                    disp = None
                    results['error_msgs'].append('DISP: '+str(e))
                    results['error_disp'] += 1
            else:
                disp = None
            # Create the Incident
            try:
                obj, c = Incident.objects.update_or_create(
                    num = call_dict['num'].strip(),
                    dtg_alarm = call_dict.get('dtg_alarm').strip(),
                    defaults = dict(
                        fd_id = call_dict.get('fd_id').strip() if call_dict.get('fd_id') else None,
                        street_number = call_dict.get('street_number').strip() if call_dict.get('street_number') else None,
                        route = call_dict.get('route').strip() if call_dict.get('route') else None,
                        suite = call_dict.get('suite').strip() if call_dict.get('suite') else None,
                        postal_code = call_dict.get('postal_code').strip() if call_dict.get('postal_code') else None,
                        duration = call_dict.get('duration'),
                        disp = disp,
                    )
                )
                if c:
                    results['created_calls'] += 1
            except Exception as e:
                results['error_msgs'].append('Incident: '+str(e))
                results['error_calls'] += 1
        return Response(results)

    def destroy(self, request, pk=None):
        # Do not allow delete from the API
        raise MethodNotAllowed(method='POST')
