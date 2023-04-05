from django.urls import path

from core.views import UserCreateView


# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('signup', UserCreateView.as_view()),
]