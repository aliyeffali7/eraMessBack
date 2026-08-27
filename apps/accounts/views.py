from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.org.models import Section
from apps.org.services import assign_user_to_section

from .models import User
from .serializers import (
    AssignSectionSerializer,
    CreateUserSerializer,
    SetPublicKeySerializer,
    UpdateDegreeSerializer,
    UserSerializer,
)
from .services import create_user, list_all_users, search_users, set_user_degree, set_user_public_key


class CreateUserView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        user = create_user(**serializer.validated_data)
        serializer.instance = user


class MeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SetPublicKeyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = SetPublicKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = set_user_public_key(user=request.user, public_key=serializer.validated_data["public_key"])
        return Response(UserSerializer(user).data)


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return search_users(query=self.request.query_params.get("search", ""), exclude=self.request.user)


class AdminUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        return list_all_users()


class AdminUpdateUserDegreeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, user_id):
        serializer = UpdateDegreeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, pk=user_id)
        user = set_user_degree(user=user, degree=serializer.validated_data["degree"])
        return Response(UserSerializer(user).data)


class AdminAssignSectionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, user_id):
        serializer = AssignSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, pk=user_id)
        section = get_object_or_404(Section, pk=serializer.validated_data["section_id"])
        user = assign_user_to_section(user=user, section=section)
        return Response(UserSerializer(user).data)
