from django.urls import path

from core.views import UserCreateView, UserLoginView, UserDetailUpdateView

# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('signup', UserCreateView.as_view()),
    path('login', UserLoginView.as_view()),
    path('profile', UserDetailUpdateView.as_view(), name='user-retrieve-update'),
]
