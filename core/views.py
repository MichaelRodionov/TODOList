from django.contrib.auth import authenticate, login
from django.db.models import QuerySet
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
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


class UserDetailUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset: QuerySet = User.objects.all()
    serializer = UserDetailSerializer
    permission_classes: tuple = (IsAuthenticated, )

    # def get(self, request, *args, **kwargs) -> Response:
    #     return super().get(request, *args, **kwargs)
    #
    # def patch(self, request, *args, **kwargs) -> Response:
    #     return super().patch(request, *args, **kwargs)
    #
    # def put(self, request, *args, **kwargs) -> Response:
    #     return super().put(request, *args, **kwargs)
    #
    # def delete(self, request, *args, **kwargs) -> Response:
    #     return super().delete(request, *args, **kwargs)
