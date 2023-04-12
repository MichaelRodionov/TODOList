from django.db import models
from django.db.models import CASCADE
from django.utils import timezone


# ----------------------------------------------------------------
# custom mixin
class DatesModelMixin(models.Model):
    created = models.DateTimeField(
        verbose_name="Дата создания"
    )
    updated = models.DateTimeField(
        verbose_name="Дата последнего обновления"
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


# ----------------------------------------------------------------
# category model
class GoalCategory(DatesModelMixin):
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

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


# ----------------------------------------------------------------
# goal model
class Goal(DatesModelMixin):
    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    user = models.ForeignKey(
        'core.User',
        verbose_name='Автор',
        on_delete=models.PROTECT
    )
    category = models.ForeignKey(
        GoalCategory,
        verbose_name='Категория',
        on_delete=models.PROTECT
    )
    title = models.CharField(
        verbose_name='Название',
        max_length=500
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=2000,
        null=True
    )
    status = models.PositiveSmallIntegerField(
        verbose_name='Статус',
        choices=Status.choices,
        default=Status.to_do
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет',
        choices=Priority.choices,
        default=Priority.medium
    )
    due_date = models.DateTimeField(
        verbose_name='Дедлайн',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'


# ----------------------------------------------------------------
# comment model
class Comment(DatesModelMixin):
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
