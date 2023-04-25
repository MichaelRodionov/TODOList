from django.urls import path

from bot.views import TgUserUpdateView


# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path('verify', TgUserUpdateView.as_view(), name='tg_user-update'),
]
