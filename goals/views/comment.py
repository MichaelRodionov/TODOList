from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.models.comment import Comment
from goals.models.goal import Goal
from goals.permissions import CommentPermissions
from goals.serializers.comment import CommentCreateSerializer, CommentSerializer


# ----------------------------------------------------------------
# comments views
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
