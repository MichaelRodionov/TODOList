from rest_framework import serializers

from bot.models import TgUser


# ----------------------------------------------------------------
# tguser serializer
class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = '__all__'
        read_only_fields = ('id', 'tg_user_id', 'tg_chat_id')
