from django.contrib.auth import authenticate, login
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView

from core.models import User
from core.serializers import UserRegistrationSerializer, UserLoginSerializer


# ----------------------------------------------------------------
# user views
class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class UserLoginView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        if not user:
            raise ValidationError('Check your username or password')
        login(request, user)
        return super().create(request, *args, **kwargs)
