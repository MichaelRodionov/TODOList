from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from rest_framework import generics, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from goals.models.board import Board
from goals.models.goal import Goal
from goals.permissions import BoardPermissions
from goals.serializers.board import BoardCreateSerializer, BoardListSerializer, BoardSerializer


# ----------------------------------------------------------------
# board views
class BoardCreateView(generics.CreateAPIView):
    """View to handle POST request to create board entity"""
    model = Board
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = BoardCreateSerializer


class BoardListView(generics.ListAPIView):
    """View to handle GET request to get list of board entities"""
    permission_classes: tuple = (permissions.IsAuthenticated,)
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination
    ordering: tuple = ('title',)

    def get_queryset(self) -> QuerySet:
        """Method to redefine queryset for board"""
        return Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to handle GET, PUT, DELETE requests of definite board entity"""
    permission_classes: tuple = (permissions.IsAuthenticated, BoardPermissions)
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )

    def update(self, request, *args, **kwargs):
        """Method to redefine PUT request"""
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, entity: Board):
        """Method to redefine DELETE logic"""
        with transaction.atomic():
            entity.is_deleted = True
            entity.save()
            entity.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=entity).update(
                status=Goal.Status.archived
            )
        return entity
