from django.contrib import admin

from goals import models


# ----------------------------------------------------------------
# admin register
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user')


admin.site.register(models.GoalCategory, GoalCategoryAdmin)
