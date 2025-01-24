from django.urls import path, include
from calls.views import *


urlpatterns = [
    path("", HomePageView.as_view(), name="calls-home"),
    path("incident-lookup", IncidentLookup.as_view(), name="incident-lookup"),
]