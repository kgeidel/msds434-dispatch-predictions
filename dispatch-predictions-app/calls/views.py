# Python imports

# Django imports
from django.views.generic import TemplateView

# Third party imports
from django_aux.views import SaveFilterMixin
from django_filters.views import FilterView

# Intraproject imports
from calls.models import *
from calls.filters import *
from calls.tables import *

class CallsBase:
    ''' A base view for calls app '''
    paginate_by = 50
    template_name = "standard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = '------- Calls Portal --------'
        context['title'] = 'HFDDC'
        context['extend_str'] = 'calls/base.html'
        return context

class HomePageView(CallsBase, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Select option from navbar above'
        return context

#### Incident views
########################
class IncidentLookup(CallsBase, SaveFilterMixin, FilterView):
    model = Incident
    filterset_class = IncidentFilter
    table_class = IncidentTable