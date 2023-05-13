from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from goals.filters import GoalDateFilter
from goals.models.goal import Goal
from goals.permissions import GoalPermissions
from goals.serializers.goal import GoalCreateSerializer, GoalSerializer


# ----------------------------------------------------------------
# goals views
@extend_schema(tags=['Goal'])
class GoalCreateView(generics.CreateAPIView):
    """
    View to handle POST request to create goal entity

    Attrs:
        - model: Category model
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    model = Goal
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer

    @extend_schema(
        description="Create new goal instance",
        summary="Create goal",
    )
    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['Goal'])
class GoalListView(generics.ListAPIView):
    """
    View to handle GET request to get list of goal entities

    Attrs:
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
        - pagination_class: defines pagination type for this APIView
        - filter_backends: defines collection of filtering options for this APIView
        - filterset_fields: defines collection of fields to filter
        - ordering_fields: defines collection of ordering options for this APIView
        - ordering: defines base ordering for this APIView
        - search_fields: defines collection of search options for this APIView
    """
    permission_classes: list = [permissions.IsAuthenticated, GoalPermissions]
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

    def get_queryset(self) -> QuerySet[Goal]:
        """
        Method to define queryset to get goal by some filters

        Returns:
            - QuerySet
        """
        return Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)

    @extend_schema(
        description="Get list of goals",
        summary="Goals list",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Goal'])
class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to handle GET, PUT, DELETE requests of definite goal entity

    Attrs:
        - serializer_class: defines serializer class for this APIView
        - permission_classes: defines permissions for this APIView
    """
    serializer_class = GoalSerializer
    permission_classes: list = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self) -> QuerySet[Goal]:
        """Method to redefine queryset for goal"""
        return Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)

    def perform_destroy(self, entity: Goal) -> None:
        """
        Method to define queryset to get goal by some filters

        Params:
            - entity: Goal entity

        Returns:
            - QuerySet
        """
        with transaction.atomic():
            entity.status = Goal.Status.archived
            entity.save(update_fields=('status',))
            for comment in entity.comment_set.all():
                comment.delete()

    @extend_schema(
        description="Get one goal",
        summary="Retrieve goal",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Full update goal instance",
        summary="Full update goal",
    )
    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="Partial update goal instance",
        summary="Partial update goal",
        deprecated=True
    )
    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        description="Set 'archived' status to goal",
        summary="Delete goal instance",
    )
    def delete(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().delete(request, *args, **kwargs)
