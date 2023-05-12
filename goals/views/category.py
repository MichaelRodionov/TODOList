from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from goals.models.category import GoalCategory
from goals.models.goal import Goal
from goals.permissions import CategoryPermissions
from goals.serializers.category import CategoryCreateSerializer, CategorySerializer


# ----------------------------------------------------------------
# category views
@extend_schema(tags=['Category'])
class CategoryCreateView(generics.CreateAPIView):
    """
    View to handle POST request to create category entity

    Attrs:
        - model: Category model
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    model = GoalCategory
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = CategoryCreateSerializer

    @extend_schema(
        description="Create new category instance",
        summary="Create category",
    )
    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['Category'])
class CategoryListView(generics.ListAPIView):
    """
    View to handle GET request to get list of category entities

    Attrs:
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
        - pagination_class: defines pagination type for this APIView
        - filter_backends: defines collection of filtering options for this APIView
        - filterset_fields: defines collection of fields to filter
        - ordering_fields: defines collection of ordering options for this APIView
        - search_fields: defines collection of search options for this APIView
    """
    permission_classes: list = [permissions.IsAuthenticated, CategoryPermissions]
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

    def get_queryset(self) -> QuerySet[GoalCategory]:
        """
        Method to define queryset to get category by some filters

        Returns:
            - QuerySet
        """
        return GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )

    @extend_schema(
        description="Get list of categories",
        summary="Categories list",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Category'])
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to handle GET, PUT, DELETE requests of definite category entity

    Attrs:
        - serializer_class: defines serializer class for this APIView
        - permission_classes: defines permissions for this APIView
    """
    serializer_class = CategorySerializer
    permission_classes: list = [permissions.IsAuthenticated, CategoryPermissions]

    def get_queryset(self) -> QuerySet[GoalCategory]:
        """
        Method to define queryset to get category by some filters

        Returns:
            - QuerySet
        """
        return GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False
        )

    def perform_destroy(self, entity: GoalCategory) -> None:
        """
        Method to redefine DELETE logic

        Params:
            - entity: Category entity

        Returns:
            - Category entity with updated field is_deleted and updated related entities (delete status fields)
        """
        with transaction.atomic():
            entity.is_deleted = True
            entity.save(update_fields=('is_deleted',))
            entity.goal_set.update(status=Goal.Status.archived)

    @extend_schema(
        description="Get one category",
        summary="Retrieve category",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Full update category instance",
        summary="Full update category",
    )
    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="Partial update category instance",
        summary="Partial update category",
        deprecated=True
    )
    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        description="Set 'is_deleted' status to category",
        summary="Delete category instance",
    )
    def delete(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().delete(request, *args, **kwargs)
