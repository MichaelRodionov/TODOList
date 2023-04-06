from django.urls import path

from core.views import UserCreateView, UserLoginView, UserDetailUpdateDestroyView

# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', UserLoginView.as_view()),
    path('profile', UserDetailUpdateDestroyView.as_view()),
]
