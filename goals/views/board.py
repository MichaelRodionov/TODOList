from typing import Optional, Union

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from goals.models.board import Board
from goals.models.goal import Goal
from goals.permissions import BoardPermissions
from goals.serializers.board import BoardCreateSerializer, BoardListSerializer, BoardSerializer


# ----------------------------------------------------------------
# board views
@extend_schema(tags=['Board'])
class BoardCreateView(generics.CreateAPIView):
    """
    View to handle POST request to create board entity

    Attrs:
        - model: Board model
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    model = Board
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer

    @extend_schema(
        description="Create new board instance",
        summary="Create board",
    )
    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['Board'])
class BoardListView(generics.ListAPIView):
    """
    View to handle GET request to get list of board entities

    Attrs:
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
        - pagination_class: defines pagination type for this APIView
        - ordering: defines output ordering by title field
    """
    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination
    ordering: tuple = ('title',)

    def get_queryset(self) -> QuerySet[Board]:
        """
        Method to define queryset to get board by some filters

        Returns:
            - QuerySet
        """
        return Board.objects.filter(
            participants__user=self.request.user,  # type: ignore
            is_deleted=False
        )

    @extend_schema(
        description="Get list of boards",
        summary="Boards list",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Board'])
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to handle GET, PUT, DELETE requests of definite board entity

    Attrs:
        - permission_classes: defines permissions for this APIView
        - serializer_class: defines serializer class for this APIView
    """
    permission_classes: tuple = (permissions.IsAuthenticated, BoardPermissions)
    serializer_class = BoardSerializer

    def get_queryset(self) -> QuerySet[Board]:
        """
        Method to define queryset to get board by some filters

        Returns:
            - QuerySet
        """
        return Board.objects.filter(
            participants__user=self.request.user,  # type: ignore
            is_deleted=False
        )

    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
        Method to redefine PUT request

        Params:
            - request: HttpRequest
            - args: positional arguments
            - kwargs: named (keyword) arguments

        Returns:
            - Response with status 200 or 400

        Raises:
            IntegrityError
        """
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, entity: Board) -> None:
        """
        Method to redefine DELETE logic

        Params:
            - entity: Board entity

        Returns:
            - Board entity with updated field is_deleted and updated related entities (delete status fields)
        """
        with transaction.atomic():
            entity.is_deleted = True
            entity.save()
            entity.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=entity).update(
                status=Goal.Status.archived
            )

    @extend_schema(
        description="Get one board",
        summary="Retrieve board",
    )
    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Full update board instance",
        summary="Full update board",
    )
    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="Partial update board instance",
        summary="Partial update board",
        deprecated=True
    )
    def patch(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        description="Set 'is_deleted' status to board",
        summary="Delete goal instance",
    )
    def delete(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().delete(request, *args, **kwargs)
