from django.contrib import admin

from bot.models import TgUser


# ----------------------------------------------------------------
# admin models
@admin.register(TgUser)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'tg_chat_id', 'tg_user_id')

    fieldsets = (
        ('Info', {
            'fields': ('user', 'tg_chat_id', 'tg_user_id')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
