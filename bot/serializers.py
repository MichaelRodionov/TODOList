from rest_framework import serializers

from bot.models import TgUser


# ----------------------------------------------------------------
# tguser serializer
class TgUserSerializer(serializers.ModelSerializer):
    """
    Telegram user serializer
    """
    class Meta:
        model = TgUser
        fields: str = '__all__'
        read_only_fields: tuple[str, str, str] = ('id', 'tg_user_id', 'tg_chat_id')
