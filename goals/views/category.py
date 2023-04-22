from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.models.category import GoalCategory
from goals.models.goal import Goal
from goals.permissions import CategoryPermissions
from goals.serializers.category import CategoryCreateSerializer, CategorySerializer


# ----------------------------------------------------------------
# category views
class CategoryCreateView(generics.CreateAPIView):
    """View to handle POST request to create category entity"""
    model = GoalCategory
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = CategoryCreateSerializer


class CategoryListView(generics.ListAPIView):
    """View to handle GET request to get list of category entities"""
    permission_classes: tuple = (permissions.IsAuthenticated, CategoryPermissions)
    serializer_class = CategorySerializer
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
        return GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite category entity"""
    serializer_class = CategorySerializer
    permission_classes: tuple = (permissions.IsAuthenticated, CategoryPermissions)

    def get_queryset(self) -> QuerySet:
        """
        Method to redefine queryset for category
        """
        return GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )

    def perform_destroy(self, entity: GoalCategory) -> GoalCategory:
        """
        Method to redefine DELETE request
        """
        with transaction.atomic():
            entity.is_deleted = True
            entity.save(update_fields=('is_deleted',))
            entity.goal_set.update(status=Goal.Status.archived)
        return entity
