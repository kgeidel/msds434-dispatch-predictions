# Python imports

# Django imports
from django.views.generic import TemplateView

# Third party imports
from django_aux.views import SaveFilterMixin
from django_filters.views import FilterView

# Intraproject imports
from forecast.models import *
from forecast.tables import *
from forecast.filters import *

class ForecastBase:
    ''' A base view for Forecast app '''
    paginate_by = 50
    template_name = "standard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = '------- Forecast Portal --------'
        context['title'] = 'HFDDC'
        context['extend_str'] = 'forecast/base.html'
        return context

class HomePageView(ForecastBase, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_header'] = 'Select option from navbar above'
        return context

#### Forecast views
########################
class ForecastLookup(ForecastBase, SaveFilterMixin, FilterView):
    model = Forecast
    filterset_class = ForecastFilter
    table_class = ForecastTable