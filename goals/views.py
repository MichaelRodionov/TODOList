from django.db import transaction, IntegrityError
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from goals import models
from goals import serializers
from goals.filters import GoalDateFilter
from goals.permissions import BoardPermissions


# ----------------------------------------------------------------
# board views
class BoardCreateView(generics.CreateAPIView):
    model = models.Board
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.BoardCreateSerializer


class BoardListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BoardListSerializer
    pagination_class = LimitOffsetPagination
    ordering = ['title']

    def get_queryset(self):
        return models.Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )


class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    model = models.Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = serializers.BoardSerializer

    def get_queryset(self):
        return models.Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, entity: models.Board):
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
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends: list = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ['board']
    ordering_fields: list = ['title', 'created']
    ordering: list = ['title']
    search_fields: list = ['title', 'board__title']

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for category"""
        return models.GoalCategory.objects.filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite category entity"""
    serializer_class = serializers.CategorySerializer
    permission_classes: list = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for category
        Check owner and is_deleted flag
        """
        return models.GoalCategory.objects.filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )

    def perform_destroy(self, entity: models.GoalCategory) -> models.GoalCategory | Response:
        """
        Method to redefine DELETE request
        Call serializers method perform destroy to check users role
        """
        try:
            self.serializer_class().check_role(entity, current_user=self.request.user)
            with transaction.atomic():
                entity.is_deleted = True
                entity.save(update_fields=('is_deleted',))
                entity.goal_set.update(status=models.Goal.Status.archived)
        except ValidationError:
            return Response(
                {'error': 'You are allowed only to read, not to delete'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response({'success': 'Category deleted'}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        entity: models.GoalCategory = self.get_object()
        return self.perform_destroy(entity)


# ----------------------------------------------------------------
# goals views
class GoalCreateView(generics.CreateAPIView):
    """View to handle POST request to create goal entity"""
    model = models.Goal
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """View to handle GET request to get list of goal entities"""
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: list = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ['category__board']
    filterset_class = GoalDateFilter
    ordering_fields: list = ['priority', 'due_date']
    ordering: list = ['title']
    search_fields: list = ['title']

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for goal
        Filter owner and goal status
        """
        return models.Goal.objects.filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=models.Goal.Status.archived)


class GoalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite goal entity"""
    model = models.Goal
    serializer_class = serializers.GoalSerializer
    permission_classes: list = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for goal
        Filter owner and goal status
        """
        return models.Goal.objects.filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=models.Goal.Status.archived)

    def perform_destroy(self, entity: models.Goal) -> models.Goal| Response:
        """
        Method to redefine DELETE request
        Call serializers method perform destroy to check users role
        """
        try:
            self.serializer_class().check_role(entity, current_user=self.request.user)
            with transaction.atomic():
                entity.status = models.Goal.Status.archived
                entity.save()
        except ValidationError:
            return Response(
                {'error': 'You are allowed only to read, not to delete'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response({'success': 'Category deleted'}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        entity: models.Goal = self.get_object()
        return self.perform_destroy(entity)


# ----------------------------------------------------------------
# comments views
class CommentCreateView(generics.CreateAPIView):
    """View to handle POST request to create comment entity"""
    model = models.Comment
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CommentCreateSerializer


class CommentListView(generics.ListAPIView):
    """View to handle GET request to get list of comment entities"""
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: list = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields: list = ['goal']
    ordering_fields: list = ['created', 'updated']
    ordering: list = ['-created']

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for comment
        Filter owner and definite goal
        """
        return models.Comment.objects.select_related('user').filter(
            user=self.request.user
        )


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite comment entity"""
    serializer_class = serializers.CommentSerializer
    permission_classes: list = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for comment"""
        return models.Comment.objects.select_related('user').filter(
            user=self.request.user
        )
