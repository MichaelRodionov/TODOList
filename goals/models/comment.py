from django.db import models
from django.db.models import CASCADE

from goals.models.dates_model_mixin import DatesModelMixin
from goals.models.goal import Goal


# ----------------------------------------------------------------
# comment model
class Comment(DatesModelMixin):
    """
    Model representing a board

    Attrs:
        - goal: Related goal
        - user: Related user
        - text: Comment content
    """
    goal = models.ForeignKey(
        Goal,
        verbose_name='Цель',
        on_delete=CASCADE
    )
    user = models.ForeignKey(
        'core.User',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=1000
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
