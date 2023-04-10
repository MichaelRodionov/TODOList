from django.db import models
from django.db.models import CASCADE
from django.utils import timezone


# ----------------------------------------------------------------
# category model
class GoalCategory(models.Model):
    title = models.CharField(
        verbose_name="Название",
        max_length=255
    )
    user = models.ForeignKey(
        'core.User', verbose_name="Автор",
        on_delete=models.PROTECT
    )
    is_deleted = models.BooleanField(
        verbose_name="Удалена",
        default=False
    )
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
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


# ----------------------------------------------------------------
# goal model
class Goal(models.Model):
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

    author = models.ForeignKey(
        'core.User', on_delete=CASCADE
    )
    category = models.ForeignKey(
        GoalCategory, on_delete=CASCADE
    )
    title = models.CharField(
        max_length=500
    )
    description = models.TextField(
        max_length=2000, null=True
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
        null=True, blank=True
    )
    created = models.DateTimeField(
        verbose_name="Дата создания"
    )
    updated = models.DateTimeField(
        verbose_name="Дата последнего обновления"
    )
    is_deleted = models.BooleanField(
        verbose_name="Удалена",
        default=False
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'
