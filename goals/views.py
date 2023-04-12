from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters
from rest_framework.pagination import LimitOffsetPagination

from goals import models
from goals import serializers
from goals.filters import GoalDateFilter


# ----------------------------------------------------------------
# category views
class CategoryCreateView(generics.CreateAPIView):
    """View to handle POST request to create category entity"""
    model = models.GoalCategory
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CategoryCreateSerializer


class CategoryListView(generics.ListAPIView):
    """View to handle GET request to get list of category entities"""
    model = models.GoalCategory
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends: list = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields: list = ['title', 'created']
    ordering: list = ['title']
    search_fields: list = ['title']

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for category"""
        return models.GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False
        )


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite category entity"""
    model = models.GoalCategory
    serializer_class = serializers.CategorySerializer
    permission_classes: list = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for category
        Check owner and is_deleted flag
        """
        return models.GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def perform_destroy(self, entity: models.GoalCategory) -> models.GoalCategory:
        """
        Method to redefine DELETE request
        The entity is not deleted, the is_deleted flag is set to True
        """
        entity.is_deleted = True
        goals = models.Goal.objects.filter(user=self.request.user, category=entity)
        for goal in goals:
            goal.status = models.Goal.Status.archived
            goal.save()
        entity.save()
        return entity


# ----------------------------------------------------------------
# goals views
class GoalCreateView(generics.CreateAPIView):
    """View to handle POST request to create goal entity"""
    model = models.Goal
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """View to handle GET request to get list of goal entities"""
    model = models.Goal
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: list = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
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
            user=self.request.user
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
            user=self.request.user,
        ).exclude(status=models.Goal.Status.archived)

    def perform_destroy(self, entity: models.Goal) -> models.Goal:
        """
        Method to redefine DELETE request
        The entity is not deleted, status field is set to 'archived'
        """
        entity.status = models.Goal.Status.archived
        entity.save()
        return entity


# ----------------------------------------------------------------
# comments views
class CommentCreateView(generics.CreateAPIView):
    """View to handle POST request to create comment entity"""
    model = models.Comment
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CommentCreateSerializer


class CommentListView(generics.ListAPIView):
    """View to handle GET request to get list of comment entities"""
    model = models.Comment
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = serializers.CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends: list = [
        filters.OrderingFilter,
    ]
    ordering_fields: list = ['created', 'updated']
    ordering: list = ['-created']

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for comment
        Filter owner and definite goal
        """
        goal = self.request.query_params.get('goal')
        return models.Comment.objects.filter(
            user=self.request.user,
            goal=goal
        )


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite comment entity"""
    model = models.Comment
    serializer_class = serializers.CommentSerializer
    permission_classes: list = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for comment"""
        return models.Comment.objects.filter(
            user=self.request.user
        )
