from django.contrib.auth.models import AbstractUser
from django.db.models import TextChoices, CharField, DateTimeField


class User(AbstractUser):
    class Sex(TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"

    sex = CharField(max_length=7, choices=Sex.choices, null=True)
    last_login = DateTimeField('last login', editable=False, auto_now_add=True)
    date_joined = DateTimeField('date joined', editable=False, auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
