from django.db import models

from goals.models.board import Board
from goals.models.dates_model_mixin import DatesModelMixin


# ----------------------------------------------------------------
# category model
class GoalCategory(DatesModelMixin):
    """
    Model representing a category

    Attrs:
        - board: Related board
        - title: Title of category
        - user: Related user
        - is_deleted: This field defines status of category (deleted or not)
    """
    board = models.ForeignKey(
        Board,
        verbose_name='Доска',
        on_delete=models.PROTECT,
        related_name='categories'
    )
    title = models.CharField(
        verbose_name="Название",
        max_length=255
    )
    user = models.ForeignKey(
        'core.User',
        verbose_name="Автор",
        on_delete=models.PROTECT
    )
    is_deleted = models.BooleanField(
        verbose_name="Удалена",
        default=False
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
