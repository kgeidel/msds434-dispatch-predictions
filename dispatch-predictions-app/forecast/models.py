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
from lightgbm import LGBMRegressor
from skforecast.preprocessing import RollingFeatures
from skforecast.recursive import ForecasterRecursive

# Intraproject imports
from django.conf import settings
from calls.models import Incident, DISP


class Forecast(models.Model):
    ''' An instance of the class represents forecasted call volume for a specfic date range '''

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

    @classmethod
    def get_forecaster(cls):
        forecaster = ForecasterRecursive(
            regressor = LGBMRegressor(
                random_state=123, 
                verbose=-1
            ),
            lags = 28,
            window_features = RollingFeatures(
                stats=['mean'], window_sizes=10
            ),
        )
        forecaster.fit(y=cls.get_ml_df()['incident_count'])
        return forecaster

    @classmethod
    def create_forecast(cls, steps=28):
        predictions = cls.get_forecaster().predict(steps=steps)
        df = predictions.reset_index()
        df.columns=['date', 'count_predicted']
        df['date'] =df['date'].astype(str)
        df['count_predicted'] = df['count_predicted'].apply(lambda x: round(x, 1))
        predictions_json = df.to_json(orient='records')
        cls.objects.create(predictions_json=predictions_json)