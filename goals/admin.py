from django.contrib import admin

from goals import models


# ----------------------------------------------------------------
# admin models
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user')


class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated', 'category')
    search_fields = ('title', 'user', 'category')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'created', 'updated', 'goal')
    search_fields = ('text', 'user', 'goal')


# ----------------------------------------------------------------
# admin register
admin.site.register(models.GoalCategory, GoalCategoryAdmin)
admin.site.register(models.Goal, GoalAdmin)
admin.site.register(models.Comment, CommentAdmin)
