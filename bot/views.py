from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer


# ----------------------------------------------------------------
# TgUserUpdateView
class TgUserUpdateView(generics.GenericAPIView):
    """
    View to update telegram users field in case of bot activation

    Attrs:
        - queryset: defines queryset for this APIView
        - serializer_class: defines serializer class for this APIView
        - permissions: defines permissions for this APIView
    """
    queryset: QuerySet[TgUser] = TgUser.objects.all()
    serializer_class = TgUserSerializer
    permission_classes: list = [IsAuthenticated]

    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
        Method to handle PATCH request and call update method

        Params:
            - request: HttpRequest
            - args: positional arguments
            - kwargs: named (keyword) arguments

        Returns:
            - Response: Successful verification or invalid verification code
        """
        return self.update(request, *args, **kwargs)

    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
        Method to update users info such as status and current user field

        Params:
            - request: HttpRequest
            - args: positional arguments
            - kwargs: named (keyword) arguments

        Returns:
            - Response: Successful verification or invalid verification code
        """
        current_user = request.user
        tg_user = TgUser.objects.filter(
            verification_code=request.data.get('verification_code')
        ).first()
        if not tg_user:
            return Response('Invalid verification code', status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(tg_user, data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user.user = current_user  # type: ignore
        tg_user.status = TgUser.Status.verified
        tg_user.save()

        return Response('Success verification', status=status.HTTP_200_OK)
