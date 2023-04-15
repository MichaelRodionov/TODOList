import django_filters
from django.db import models
from django_filters import rest_framework

from goals.models import Goal


# ----------------------------------------------------------------
# filters
class GoalDateFilter(rest_framework.FilterSet):
    """filterset defining fields for sorting, filtering, searching"""
    class Meta:
        model = Goal
        fields: dict = {
            "due_date": ("lte", "gte"),
            "category": ("exact", "in"),
            "status": ("exact", "in"),
            "priority": ("exact", "in"),
        }

    filter_overrides: dict = {
        models.DateTimeField: {"filter_class": django_filters.IsoDateTimeFilter},
    }
