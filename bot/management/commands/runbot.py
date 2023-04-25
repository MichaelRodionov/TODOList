from typing import Optional

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from bot.models import TgUser
from bot.tg.client import TgClient
from todolist.settings import TG_BOT_KEY


class Command(BaseCommand):
    help = 'Run bot'

    def handle(self, *args, **options):
        offset = 0
        tg_client = TgClient(TG_BOT_KEY)

        while True:
            updates = tg_client.get_updates(offset=offset)
            if updates.result:
                for item in updates.result:
                    offset = item.update_id + 1
                    user = self.get_tguser(tguser_id=item.message.from_.id)
                    if item.message.text == '/start':

                        if not user:
                            self._user_registration(item=item, client=tg_client)
                            self._send_verification_code(item=item, client=tg_client)

                        elif user and user.status != TgUser.Status.verified:
                            self._send_verification_code(item=item, client=tg_client)

                    elif item.message.text == '/check_verification':

                        if user.status == TgUser.Status.verified:
                            self._tguser_verified_message(item=item, client=tg_client)
                        else:
                            self._tguser_nonverified_message(item=item, client=tg_client)

                    else:
                        tg_client.send_message(
                            chat_id=item.message.chat.id,
                            text=f'Пользуйтесь доступным набором команд'
                        )

    def get_tguser(self, tguser_id) -> Optional[TgUser]:
        try:
            user = TgUser.objects.get(tg_user_id=tguser_id)
        except TgUser.DoesNotExist:
            return None
        return user

    def _create_verification_code(self) -> str:
        code = get_random_string(length=10)
        return code

    def _user_registration(self, item, client) -> TgUser:
        new_user = TgUser.objects.create(
            tg_user_id=item.message.from_.id,
            tg_chat_id=item.message.chat.id
        )
        client.send_message(
            chat_id=item.message.chat.id,
            text='Приветствую в телеграм боте TODOList! Ожидайте ваш код верификации!'
        )
        return new_user

    def _send_verification_code(self, item, client):
        code = self._create_verification_code()
        user = TgUser.objects.filter(tg_user_id=item.message.from_.id).first()
        user.verification_code = code
        user.save(update_fields=('verification_code',))
        client.send_message(
            chat_id=item.message.chat.id,
            text=f'Ваш код верификации: {code}'
        )

    def _tguser_verified_message(self, item, client):
        client.send_message(chat_id=item.message.chat.id, text='Верификация пройдена успешно')

    def _tguser_nonverified_message(self, item, client):
        client.send_message(chat_id=item.message.chat.id, text='Верификация не пройдена')

# TODO: make session class