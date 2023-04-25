from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer


# ----------------------------------------------------------------
# TgUserUpdateView
class TgUserUpdateView(generics.GenericAPIView):
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        current_user = request.user
        tg_user = TgUser.objects.filter(
            verification_code=request.data.get('verification_code')
        ).first()
        if not tg_user:
            return Response('Invalid verification code', status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(tg_user, data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user.user = current_user
        tg_user.status = TgUser.Status.verified
        tg_user.save()

        return Response('Success verification', status=status.HTTP_200_OK)

