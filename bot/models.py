from django.db import models


# ----------------------------------------------------------------
# bot model
class TgUser(models.Model):
    """
    Model representing telegram user

    Attrs:
        - tg_chat_id: defines id of current chat
        - tg_user_id: defines id of current user
        - user: defines User model
        - verification_code: defines verification code to activate bot on TODOList site
        - status: defines status of bot - verified or not by class Status
        - selected_category: defines category, where tg_user would create new goal
    """
    class Status(models.IntegerChoices):
        not_verified = 1, 'Не подтвержден',
        verified = 2, 'Подтвержден'

    tg_chat_id = models.IntegerField(
        verbose_name='Телеграм чат ID'
    )
    tg_user_id = models.IntegerField(
        verbose_name='Телеграм пользователь ID'
    )
    user = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        null=True,
        verbose_name='Пользователь приложения'
    )
    verification_code = models.CharField(
        verbose_name='Код верификации',
        max_length=10
    )
    status = models.PositiveSmallIntegerField(
        verbose_name='Статус',
        choices=Status.choices,
        default=Status.not_verified
    )
    selected_category = models.ForeignKey(
        'goals.GoalCategory',
        null=True,
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name: str = 'Телеграм пользователь'
        verbose_name_plural: str = 'Телеграм пользователи'
