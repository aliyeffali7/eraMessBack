from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.accounts.models import User

from .models import Conversation
from .serializers import ConversationSerializer, MessageSerializer
from .services import (
    create_group_conversation,
    get_or_create_direct_conversation,
    list_conversations_for_user,
    list_messages,
    send_message,
)


class ConversationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return list_conversations_for_user(user=self.request.user)


class StartDirectConversationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def post(self, request, *args, **kwargs):
        other = get_object_or_404(User, pk=request.data.get("user_id"))
        conversation = get_or_create_direct_conversation(user=request.user, other=other)
        return Response(ConversationSerializer(conversation).data)


class CreateGroupConversationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ConversationSerializer

    def post(self, request, *args, **kwargs):
        conversation = create_group_conversation(
            name=request.data.get("name", ""),
            creator=request.user,
            member_ids=request.data.get("member_ids", []),
        )
        return Response(ConversationSerializer(conversation).data, status=201)


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get_conversation(self) -> Conversation:
        conversation = get_object_or_404(Conversation, pk=self.kwargs["conversation_id"])
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Bu söhbətin üzvü deyilsiniz.")
        return conversation

    def get_queryset(self):
        conversation = self.get_conversation()
        after_id = self.request.query_params.get("after")
        return list_messages(conversation=conversation, after_id=after_id)

    def perform_create(self, serializer):
        conversation = self.get_conversation()
        message = send_message(conversation=conversation, sender=self.request.user, text=serializer.validated_data["text"])
        serializer.instance = message
