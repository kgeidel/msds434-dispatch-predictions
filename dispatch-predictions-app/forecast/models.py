# Python imports
import os
import datetime as dt
from io import StringIO
from itertools import product

# Django imports
from django.utils import timezone
from django.db import models

# 3rd party imports
import pandas as pd
from tqdm import tqdm

# Intraproject imports
from django.conf import settings
from calls.models import Incident, DISP


class Forecast(models.Model):
    ''' An instance of the class represents forecasted call volume for a specfic date range '''

    class Settings:
        ml_auto_experiment_name = 'dispatch-predictions-automl'
        sagemaker_role_arn = os.getenv('SAGEMAKER_ROLE_ARN')
        sagemaker_kms_arn = os.getenv('SAGEMAKER_KMS_ARN')
        s3_bucket_name = 'dispatch-predictions'
        data_file_name = 'incidents_per_day.csv'
        target_attr = 'incident_count'

    dtg_predicted = models.DateTimeField(auto_now_add=True)
    predictions_json = models.JSONField(null=True, blank=True)

    @staticmethod
    def get_ml_df(date_start=None, date_end=None):
        fkwargs = {}
        # add date filters if supplied
        if date_start is not None:
            assert isinstance(date_start, dt.date), f"If date_start is supplied, it must be type datetime.date, not {type(date_start)}"
            fkwargs.update({'dtg_alarm__date__gte': date_start})
        if date_end is not None:
            assert isinstance(date_end, dt.date), f"If date_end is supplied, it must be type datetime.date, not {type(date_end)}"
            fkwargs.update({'dtg_alarm__date__lte': date_end})
        # get df from base qs
        df = pd.DataFrame(Incident.objects.filter(**fkwargs).values('dtg_alarm'))
        # Aggregate calls into a count by date
        df = df.groupby(df['dtg_alarm'].dt.date).count()
        # fill in missing dates with zero counts
        all_dates = pd.date_range(df.index.min(), date_end or timezone.now().date())
        df = df.reindex(all_dates).fillna(0)
        df = df.astype(int)
        df.columns = ['incident_count']
        df = df.sort_index()
        return df
