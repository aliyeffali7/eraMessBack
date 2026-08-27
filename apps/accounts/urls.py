from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminAssignSectionView,
    AdminUpdateUserDegreeView,
    AdminUserListView,
    CreateUserView,
    MeView,
    SetPublicKeyView,
    UserListView,
)

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("me/public-key/", SetPublicKeyView.as_view(), name="set-public-key"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/create/", CreateUserView.as_view(), name="admin-user-create"),
    path("admin/users/<int:user_id>/degree/", AdminUpdateUserDegreeView.as_view(), name="admin-user-degree"),
    path("admin/users/<int:user_id>/section/", AdminAssignSectionView.as_view(), name="admin-user-section"),
]
