from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from rest_framework.routers import DefaultRouter
from calls.api.views import IncidentViewSet

router = DefaultRouter()
router.register(r'calls', IncidentViewSet)

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path("api/", include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),

    path('calls/', include('calls.urls')),
    path('forecast/', include('forecast.urls')),

] + static(settings.STATIC_URL, documents_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, documents_root=settings.MEDIA_ROOT)
