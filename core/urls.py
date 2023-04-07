from django.urls import path

from core.views import UserCreateView, UserLoginView, UserDetailUpdateLogoutView

# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', UserLoginView.as_view()),
    path('profile', UserDetailUpdateLogoutView.as_view(), name='user-retrieve-update-destroy'),
]
