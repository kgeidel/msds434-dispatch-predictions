# Python imports

# Django imports
from django_filters import *

# 3rd party imports
from crispy_forms.layout import *
from crispy_forms.helper import FormHelper
from bootstrap_datepicker_plus.widgets import DatePickerInput

# Intraproject imports
from calls.filters import FilterSetBase
from forecast.models import *

class ForecastFilter(FilterSetBase):
    date_from = DateFilter(
        field_name='dtg_predicted__date', lookup_expr='gte', widget=DatePickerInput()
    )
    date_to = DateFilter(
        field_name='dtg_predicted__date', lookup_expr='lte', widget=DatePickerInput()
    )
    class Meta:
        model = Forecast
        fields = {
            'id': ['exact'],
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['date_from'].label = 'Predicted on/after'
        self.form.fields['date_to'].label = 'Predicted on/before'
        self.form.helper.layout = Layout(
            Fieldset('',
                Row(
                    Div('id', css_class='ml-2 col-flex'),
                    Div('date_from', css_class='ml-2 col-flex'),
                    Div('date_to', css_class='ml-2 col-flex'),
                ),
            ),
        )