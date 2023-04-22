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
    """View to handle POST request to create comment entity"""
    model = Comment
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = CommentCreateSerializer


class CommentListView(generics.ListAPIView):
    """View to handle GET request to get list of comment entities"""
    permission_classes: tuple = (permissions.IsAuthenticated, CommentPermissions)
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: tuple = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_fields: tuple = ('goal__category__board', 'goal')
    ordering_fields: tuple = ('created', 'updated')
    ordering: tuple = ('-created',)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for comment"""
        return Comment.objects.select_related('goal').filter(
            goal__category__board__participants__user=self.request.user,
            goal__category__board__is_deleted=False,
            goal__category__is_deleted=False,
        ).exclude(goal__status=Goal.Status.archived)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite comment entity"""
    serializer_class = CommentSerializer
    permission_classes: tuple = (permissions.IsAuthenticated, CommentPermissions)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for comment"""
        return Comment.objects.select_related('goal').filter(
            goal__category__board__participants__user=self.request.user,
            goal__category__board__is_deleted=False,
            goal__category__is_deleted=False,
        ).exclude(goal__status=Goal.Status.archived)
