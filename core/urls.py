from django.urls import path

from core.views import UserCreateView, UserLoginView


# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', UserLoginView.as_view())
]
