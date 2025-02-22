# Python imports
from io import BytesIO
import base64

# Django imports
from django.views.generic import TemplateView

# Third party imports
from django_aux.views import SaveFilterMixin
from django_filters.views import FilterView
import matplotlib.pyplot as plt

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
class CurrentForecast(ForecastBase, TemplateView):
    template_name = 'forecast/current-forecast.html'
    
    def get_fig(self):
        fig, ax = plt.subplots(figsize=(11.5, 7))
        data_historical = Forecast.get_ml_df(
            date_start = timezone.now().date() - dt.timedelta(60)
        )
        data_historical.plot(ax=ax, label="Historical")
        forecast = Forecast.objects.order_by('-dtg_predicted').first()
        if forecast is not None:
            predictions = pd.read_json(StringIO(forecast.predictions_json))
            predictions.set_index(['date'], inplace=True)
            predictions.plot(ax=ax, label='Forecast')
        ax.legend();
        fig.set_layout_engine('tight')
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        return encoded

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fig_img'] = self.get_fig()
        return context    

class ForecastLookup(ForecastBase, SaveFilterMixin, FilterView):
    model = Forecast
    filterset_class = ForecastFilter
    table_class = ForecastTable