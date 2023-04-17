# Generated by Django 4.1.7 on 2023-04-17 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goals', '0008_alter_goalcategory_board'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boardparticipant',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='board_participants', to='goals.board', verbose_name='Доска'),
        ),
        migrations.AlterField(
            model_name='boardparticipant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_participants', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]