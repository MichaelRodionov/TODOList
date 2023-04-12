from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters
from rest_framework.pagination import LimitOffsetPagination

from goals import models
from goals import serializers
from goals.filters import GoalDateFilter


# ----------------------------------------------------------------
# category views
class CategoryCreateView(generics.CreateAPIView):
    model = models.GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CategoryCreateSerializer


class CategoryListView(generics.ListAPIView):
    model = models.GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return models.GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False
        )


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    model = models.GoalCategory
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def perform_destroy(self, instance: models.GoalCategory):
        instance.is_deleted = True
        goals = models.Goal.objects.filter(user=self.request.user, category=instance)
        for goal in goals:
            goal.status = models.Goal.Status.archived
            goal.save()
        instance.save()
        return instance


# ----------------------------------------------------------------
# goals views
class GoalCreateView(generics.CreateAPIView):
    model = models.Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    model = models.Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalDateFilter
    ordering_fields = ['priority', 'due_date']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return models.Goal.objects.filter(
            user=self.request.user
        ).exclude(status=models.Goal.Status.archived)


class GoalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    model = models.Goal
    serializer_class = serializers.GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Goal.objects.filter(
            user=self.request.user,
        ).exclude(status=models.Goal.Status.archived)

    def perform_destroy(self, instance: models.Goal):
        instance.status = models.Goal.Status.archived
        instance.save()
        return instance


# ----------------------------------------------------------------
# comments views
class CommentCreateView(generics.CreateAPIView):
    model = models.Comment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CommentCreateSerializer


class CommentListView(generics.ListAPIView):
    model = models.Comment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
    ]
    ordering_fields = ['created', 'updated']
    ordering = ['-created']

    def get_queryset(self):
        goal = self.request.query_params.get('goal')
        return models.Comment.objects.filter(goal=goal)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    model = models.Comment
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Comment.objects.filter(
            user=self.request.user
        )
