from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from goals.models.comment import Comment
from goals.models.goal import Goal
from goals.permissions import CommentPermissions
from goals.serializers.comment import CommentCreateSerializer, CommentSerializer


# ----------------------------------------------------------------
# comments views
@extend_schema(tags=['Comment'])
class CommentCreateView(generics.CreateAPIView):
    """
    View to handle POST request to create comment entity

    Attrs:
        - model: Comment model
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    model = Comment
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = CommentCreateSerializer

    @extend_schema(
        description="Create new comment instance",
        summary="Create comment",
    )
    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['Comment'])
class CommentListView(generics.ListAPIView):
    """
    View to handle GET request to get list of comment entities

    Attrs:
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
        - pagination_class: defines pagination type for this APIView
        - filter_backends: defines collection of filtering options for this APIView
        - filterset_fields: defines collection of fields to filter
        - ordering_fields: defines collection of ordering options for this APIView
        - ordering: defines base ordering for this APIView
    """
    permission_classes: list = [permissions.IsAuthenticated, CommentPermissions]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: tuple = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_fields: tuple = ('goal__category__board', 'goal')
    ordering_fields: tuple = ('created', 'updated')
    ordering: tuple = ('-created',)

    def get_queryset(self) -> QuerySet[Comment]:
        """
        Method to define queryset to get comment by some filters

        Returns:
            - QuerySet
        """
        return Comment.objects.select_related('goal').filter(
            goal__category__board__participants__user=self.request.user,
            goal__category__board__is_deleted=False,
            goal__category__is_deleted=False,
        ).exclude(goal__status=Goal.Status.archived)

    @extend_schema(
        description="Get list of comments",
        summary="Comments list",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Comment'])
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to handle GET, PUT, DELETE requests of definite comment entity

    Attrs:
        - serializer_class: defines serializer class for this APIView
        - permission_classes: defines permissions for this APIView
    """
    serializer_class = CommentSerializer
    permission_classes: list = [permissions.IsAuthenticated, CommentPermissions]

    def get_queryset(self) -> QuerySet[Comment]:
        """
        Method to define queryset to get comment by some filters

        Returns:
            - QuerySet
        """
        return Comment.objects.select_related('goal').filter(
            goal__category__board__participants__user=self.request.user,
            goal__category__board__is_deleted=False,
            goal__category__is_deleted=False,
        ).exclude(goal__status=Goal.Status.archived)

    @extend_schema(
        description="Get one comment",
        summary="Retrieve comment",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Full update comment instance",
        summary="Full update comment",
    )
    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="Partial update comment instance",
        summary="Partial update comment",
        deprecated=True
    )
    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        description="Full delete comment",
        summary="Delete comment instance",
    )
    def delete(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().delete(request, *args, **kwargs)
