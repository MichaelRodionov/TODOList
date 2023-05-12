from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBase
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
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
@extend_schema(tags=['User'])
class UserCreateView(CreateAPIView):
    """
    View to handle registration

    Attrs:
        - queryset: defines queryset for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        description="Create new user instance",
        summary="Registrate user",
    )
    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['User'])
class UserLoginView(CreateAPIView):
    """
    View to handle login
    """

    @extend_schema(
        description="Authenticate user instance",
        summary="Login user",
    )
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


@extend_schema(tags=['User'])
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

    @extend_schema(
        description="Get one user",
        summary="Retrieve user",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Full update user instance",
        summary="Full update user",
    )
    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="Partial update user instance",
        summary="Partial update user",
        deprecated=True
    )
    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        description="Logout from web app",
        summary="Logout user",
    )
    def delete(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().delete(request, *args, **kwargs)


@extend_schema(tags=['User'])
class UserUpdatePasswordView(UpdateAPIView):
    """View to handle password change"""
    serializer_class = UserChangePasswordSerializer
    permission_classes: list = [IsAuthenticated]

    def get_object(self) -> Any:
        return self.request.user

    @extend_schema(
        description="Update users password",
        summary="Update password",
    )
    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        deprecated=True
    )
    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().patch(request, *args, **kwargs)

