from django.contrib import admin

from goals import models


# ----------------------------------------------------------------
# admin models
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated', 'is_deleted')
    search_fields = ('title', 'user')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Info', {
            'fields': ('title', 'user', 'created', 'updated')
        }),
        ('Dates', {
            'fields': ('created', 'updated')
        }),
        ('Status', {
            'fields': ('is_deleted',)
        }),
    )


class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated', 'category', 'due_date', 'priority', 'status')
    search_fields = ('title', 'user', 'category', 'due_date', 'priority', 'status')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Info', {
            'fields': ('title', 'user', 'category', 'priority')
        }),
        ('Dates', {
            'fields': ('created', 'updated', 'due_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'created', 'updated', 'goal')
    search_fields = ('text', 'user', 'goal')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Info', {
            'fields': ('text', 'user', 'created', 'updated', 'goal')
        }),
        ('Dates', {
            'fields': ('created', 'updated')
        }),
    )


# ----------------------------------------------------------------
# admin register
admin.site.register(models.GoalCategory, GoalCategoryAdmin)
admin.site.register(models.Goal, GoalAdmin)
admin.site.register(models.Comment, CommentAdmin)
