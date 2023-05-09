from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBase
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.serializers import UserRegistrationSerializer, UserDetailSerializer, UserChangePasswordSerializer


# ----------------------------------------------------------------
# user views
class UserCreateView(CreateAPIView):
    """
    View to handle registration

    Attrs:
        - queryset: defines queryset for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class UserLoginView(CreateAPIView):
    """
    View to handle login
    """

    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
        Method to redefine post logic

        Params:
            - request: HttpRequest
            - args: positional arguments
            - kwargs: named (keyword) arguments

        Returns:
            - Response: Successful login

        Raises:
            - AuthenticationFailed (in case of invalid username or password)
        """
        user: Any = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        if user:
            login(request, user)
            return Response('Successful login', status=status.HTTP_201_CREATED)
        raise AuthenticationFailed('Invalid username or password')


class UserDetailUpdateLogoutView(RetrieveUpdateDestroyAPIView):
    """
    View to handle profile page, update users info, logout

    Attrs:
        - serializer_class: defines serializer class for this APIView
        - permission_classes: defines permissions for this APIView
    """
    serializer_class = UserDetailSerializer
    permission_classes: list = [IsAuthenticated]

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs) -> HttpResponseBase:
        return super().dispatch(*args, **kwargs)

    def get_object(self) -> Any:
        """
        Method to define User from http request

        Returns:
            - user object
        """
        return self.request.user

    def destroy(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
        Method to redefine DELETE logic

        Params:
            - request: HttpRequest
            - args: positional arguments
            - kwargs: named (keyword) arguments

        Returns:
            - Response: Successful logout
        """
        logout(request)
        return Response('Successful logout', status=status.HTTP_204_NO_CONTENT)


class UserUpdatePasswordView(UpdateAPIView):
    """View to handle password change"""
    serializer_class = UserChangePasswordSerializer
    permission_classes: list = [IsAuthenticated]

    def get_object(self) -> Any:
        return self.request.user
