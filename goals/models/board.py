from django.db import models

from goals.models.dates_model_mixin import DatesModelMixin


# ----------------------------------------------------------------
# board model
class Board(DatesModelMixin):
    """
    Model representing a board

    Attrs:
        - title: Title of Board
        - is_deleted: This field defines status of board (deleted or not)
    """
    title = models.CharField(
        verbose_name='Название',
        max_length=255
    )
    is_deleted = models.BooleanField(
        verbose_name='Удалена',
        default=False
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"


# ----------------------------------------------------------------
# board participant model
class BoardParticipant(DatesModelMixin):
    """
    Model representing a board participant

    Attrs:
        - board: Related board
        - user: Related user
        - role: Role of board participants. Defines by class Role
    """
    class Role(models.IntegerChoices):
        owner = 1, "Владелец"
        writer = 2, "Редактор"
        reader = 3, "Читатель"

    board = models.ForeignKey(
        Board,
        verbose_name="Доска",
        on_delete=models.PROTECT,
        related_name="participants",
    )
    user = models.ForeignKey(
        'core.User',
        verbose_name="Пользователь",
        on_delete=models.PROTECT,
        related_name="participants",
    )
    role = models.PositiveSmallIntegerField(
        verbose_name="Роль",
        choices=Role.choices,
        default=Role.owner
    )

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ("board", "user")
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
