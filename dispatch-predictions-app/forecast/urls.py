from django.urls import path, include
from forecast.views import *


urlpatterns = [
    path("", HomePageView.as_view(), name="forecast-home"),
    path("forecast-lookup", ForecastLookup.as_view(), name="forecast-lookup"),
    path("current-forecast", CurrentForecast.as_view(), name="current-forecast"),
]