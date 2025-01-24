# Python imports

# Django imports
from django_filters import *

# 3rd party imports
from crispy_forms.layout import *
from crispy_forms.helper import FormHelper
from bootstrap_datepicker_plus.widgets import DatePickerInput

# Intraproject imports
from calls.models import *


class FilterSetBase(FilterSet):
    ''' A BaseFilter class that initializes a crispy form helper 
    with submit and clear filter buttons '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.disable_csrf = True
        self.form.helper.add_input(
            Submit('submit', 'Apply Filter')
        )
        self.form.helper.add_input(
            Submit('clear_filter', 'Clear Filter', css_class='btn-warning')
        )

class IncidentFilter(FilterSetBase):
    date_from = DateFilter(
        field_name='dtg_alarm__date', lookup_expr='gte', widget=DatePickerInput()
    )
    date_to = DateFilter(
        field_name='dtg_alarm__date', lookup_expr='lte', widget=DatePickerInput()
    )
    class Meta:
        model = Incident
        fields = {
            'num': ['exact'],
            'route': ['icontains'],
            'disp__type_str': ['icontains'],
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['date_from'].label = 'Date on/after'
        self.form.fields['date_to'].label = 'Date on/before'
        self.form.fields['disp__type_str__icontains'].label = 'Disposition contains'
        self.form.helper.layout = Layout(
            Fieldset('',
                Row(
                    Div('num', css_class='ml-2 col-flex'),
                    Div('date_from', css_class='ml-2 col-flex'),
                    Div('date_to', css_class='ml-2 col-flex'),
                    Div('route__icontains', css_class='ml-2 col-flex'),
                    Div('disp__type_str__icontains', css_class='ml-2 col-flex'),
                ),
            ),
        )