from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path("oauth/", include("social_django.urls", namespace="social")),
    path('goals/', include('goals.urls')),
    path('bot/', include('bot.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
