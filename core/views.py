from django.contrib.auth import authenticate, login, get_user_model
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import User
from core.serializers import UserRegistrationSerializer, UserDetailSerializer


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


class UserDetailUpdateView(RetrieveUpdateAPIView):
    queryset: QuerySet = User.objects.all()
    serializer = UserDetailSerializer
    permission_classes: list = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @method_decorator(ensure_csrf_cookie)
    def retrieve(self, request, *args, **kwargs) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def patch(self, request, *args, **kwargs) -> Response:
        return super().patch(request, *args, **kwargs)
