from django.contrib import admin

from goals import models


# ----------------------------------------------------------------
# admin models
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_deleted')
    search_fields = ('title', 'user')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Info', {
            'fields': ('title', 'user')
        }),
        ('Dates', {
            'fields': ('created', 'updated')
        }),
        ('Status', {
            'fields': ('is_deleted',)
        }),
    )


class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status')
    search_fields = ('title', 'user', 'category', 'priority', 'status')
    readonly_fields = ('created', 'updated', 'due_date')

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
    list_display = ('text', 'user', 'goal')
    search_fields = ('text', 'user', 'goal')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Info', {
            'fields': ('text', 'user', 'goal')
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
