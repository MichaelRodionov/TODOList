from django.db import transaction, IntegrityError
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from goals import models
from goals import serializers
from goals.filters import GoalDateFilter
from goals.permissions import BoardPermissions, CategoryPermissions, GoalPermissions, CommentPermissions


# ----------------------------------------------------------------
# board views
class BoardCreateView(generics.CreateAPIView):
    """View to handle POST request to create board entity"""
    model = models.Board
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = serializers.BoardCreateSerializer


class BoardListView(generics.ListAPIView):
    """View to handle GET request to get list of board entities"""
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = serializers.BoardListSerializer
    pagination_class = LimitOffsetPagination
    ordering: tuple = ('title',)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for board"""
        return models.Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )


class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite board entity"""
    permission_classes: tuple = (permissions.IsAuthenticated, BoardPermissions)
    serializer_class = serializers.BoardSerializer

    def get_queryset(self):
        return models.Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )

    def update(self, request, *args, **kwargs):
        """Method to redefine PUT request"""
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, entity: models.Board):
        """Method to redefine DELETE logic"""
        with transaction.atomic():
            entity.is_deleted = True
            entity.save()
            entity.categories.update(is_deleted=True)
            models.Goal.objects.filter(category__board=entity).update(
                status=models.Goal.Status.archived
            )
        return entity


# ----------------------------------------------------------------
# category views
class CategoryCreateView(generics.CreateAPIView):
    """View to handle POST request to create category entity"""
    model = models.GoalCategory
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CategoryCreateSerializer


class CategoryListView(generics.ListAPIView):
    """View to handle GET request to get list of category entities"""
    permission_classes: tuple = (permissions.IsAuthenticated, CategoryPermissions)
    serializer_class = serializers.CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends: tuple = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_fields: tuple = ('board',)
    ordering_fields: tuple = ('title', 'created')
    ordering: tuple = ('title',)
    search_fields: tuple = ('title', 'board__title')

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for category"""
        return models.GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite category entity"""
    serializer_class = serializers.CategorySerializer
    permission_classes: tuple = (permissions.IsAuthenticated, CategoryPermissions)

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for category
        """
        return models.GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )

    def perform_destroy(self, entity: models.GoalCategory) -> models.GoalCategory:
        """
        Method to redefine DELETE request
        """
        with transaction.atomic():
            entity.is_deleted = True
            entity.save(update_fields=('is_deleted',))
            entity.goal_set.update(status=models.Goal.Status.archived)
        return entity


# ----------------------------------------------------------------
# goals views
class GoalCreateView(generics.CreateAPIView):
    """View to handle POST request to create goal entity"""
    model = models.Goal
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = serializers.GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """View to handle GET request to get list of goal entities"""
    permission_classes: tuple = (permissions.IsAuthenticated, GoalPermissions)
    serializer_class = serializers.GoalSerializer
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
        return models.Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=models.Goal.Status.archived)


class GoalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite goal entity"""
    model = models.Goal
    serializer_class = serializers.GoalSerializer
    permission_classes: tuple = (permissions.IsAuthenticated, GoalPermissions)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for goal"""
        return models.Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=models.Goal.Status.archived)

    def perform_destroy(self, entity: models.Goal) -> models.Goal:
        """
        Method to redefine DELETE request
        """
        with transaction.atomic():
            entity.status = models.Goal.Status.archived
            entity.save(update_fields=('status',))
            entity.comment_set.delete()
        return entity


# ----------------------------------------------------------------
# comments views
class CommentCreateView(generics.CreateAPIView):
    """View to handle POST request to create comment entity"""
    model = models.Comment
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = serializers.CommentCreateSerializer


class CommentListView(generics.ListAPIView):
    """View to handle GET request to get list of comment entities"""
    permission_classes: tuple = (permissions.IsAuthenticated, CommentPermissions)
    serializer_class = serializers.CommentSerializer
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
        return models.Comment.objects.select_related('goal').filter(
            goal__category__board__participants__user=self.request.user,
            goal__category__board__is_deleted=False,
            goal__category__is_deleted=False,
        ).exclude(goal__status=models.Goal.Status.archived)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite comment entity"""
    serializer_class = serializers.CommentSerializer
    permission_classes: tuple = (permissions.IsAuthenticated, CommentPermissions)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for comment"""
        return models.Comment.objects.select_related('goal').filter(
            goal__category__board__participants__user=self.request.user,
            goal__category__board__is_deleted=False,
            goal__category__is_deleted=False,
        ).exclude(goal__status=models.Goal.Status.archived)
