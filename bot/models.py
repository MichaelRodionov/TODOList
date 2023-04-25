from django.db import models


# ----------------------------------------------------------------
# bot model
class TgUser(models.Model):
    class Status(models.IntegerChoices):
        not_verified = 1, 'Не подтвержден',
        verified = 2, 'Подтвержден'

    tg_chat_id = models.IntegerField(verbose_name='Telegram chat ID')
    tg_user_id = models.IntegerField(verbose_name='Telegram user ID')
    user = models.ForeignKey('core.User', on_delete=models.PROTECT, null=True)
    verification_code = models.CharField(verbose_name='Verification code', max_length=10)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.not_verified)

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'
