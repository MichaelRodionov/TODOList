from django.contrib.auth import authenticate, login, logout
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import User
from core.serializers import UserRegistrationSerializer, UserDetailSerializer, UserChangePasswordSerializer


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
        if user is None:
            raise AuthenticationFailed('Invalid username or password')
        login(request, user)
        return super().post(request, *args, **kwargs)


class UserDetailUpdateLogoutView(RetrieveUpdateDestroyAPIView):
    queryset: QuerySet = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes: list = [IsAuthenticated]

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        logout(request)
        return super().destroy(request, *args, **kwargs)


class UserUpdatePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
