from django.urls import path

from goals import views


# ----------------------------------------------------------------
# urlpatterns
urlpatterns = [
    path("goal_category/create", views.CategoryCreateView.as_view()),
    path("goal_category/list", views.CategoryListView.as_view()),
    path("goal_category/<int:pk>", views.CategoryRetrieveUpdateDestroyView.as_view()),
    path('goal/create', views.GoalCreateView.as_view()),
    path('goal/list', views.GoalListView.as_view()),
    path('goal/<int:pk>', views.GoalRetrieveUpdateDestroyView.as_view()),
    path('goal_comment/create', views.CommentCreateView.as_view()),
    path('goal_comment/list', views.CommentListView.as_view()),
    path('goal_comment/<int:pk>', views.CommentRetrieveUpdateDestroyView.as_view()),
    path('board/create', views.BoardCreateView.as_view()),
    path('board/list', views.BoardListView.as_view()),
    path('board/<int:pk>', views.BoardRetrieveUpdateDestroyView.as_view())
]
