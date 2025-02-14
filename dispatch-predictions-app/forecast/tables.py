from django_tables2 import tables
import pandas as pd
from django.utils.safestring import mark_safe

from forecast.models import *


class ForecastTable(tables.Table):
    predictions = tables.Column(accessor='predictions_json')
    class Meta:
        model = Forecast
        exclude = ['predictions_json']

    def render_predictions(self, value):
        return mark_safe(pd.read_json(value).to_html())

