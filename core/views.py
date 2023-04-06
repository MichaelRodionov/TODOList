from django.contrib.auth import authenticate, login
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import User
from core.serializers import UserRegistrationSerializer


# ----------------------------------------------------------------
# user views
class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class UserLoginView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        if not user:
            raise ValidationError('Check your username or password')
        login(request, user)
        return super().post(request, *args, **kwargs)
