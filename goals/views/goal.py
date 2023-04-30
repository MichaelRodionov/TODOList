from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models.goal import Goal
from goals.permissions import GoalPermissions
from goals.serializers.goal import GoalCreateSerializer, GoalSerializer


# ----------------------------------------------------------------
# goals views
class GoalCreateView(generics.CreateAPIView):
    """View to handle POST request to create goal entity"""
    model = Goal
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """View to handle GET request to get list of goal entities"""
    permission_classes: tuple = (permissions.IsAuthenticated, GoalPermissions)
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: tuple = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_fields: tuple = ('category__board', 'category')
    filterset_class = GoalDateFilter
    ordering_fields: tuple = ('priority', 'due_date')
    ordering: tuple = ('title',)
    search_fields: tuple = ('title',)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for goal"""
        return Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite goal entity"""
    model = Goal
    serializer_class = GoalSerializer
    permission_classes: tuple = (permissions.IsAuthenticated, GoalPermissions)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for goal"""
        return Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)

    def perform_destroy(self, entity: Goal) -> Goal:
        """
        Method to redefine DELETE request
        """
        with transaction.atomic():
            entity.status = Goal.Status.archived
            entity.save(update_fields=('status',))
            for comment in entity.comment_set.all():
                comment.delete()
        return entity
