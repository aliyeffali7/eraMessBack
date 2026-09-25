from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import (
    add_members,
    create_group_conversation,
    delete_message,
    edit_message,
    get_or_create_direct_conversation,
    leave_conversation,
    list_conversations_for_user,
    list_messages,
    mark_conversation_read,
    mark_conversations_delivered,
    remove_member,
    rename_conversation,
    send_direct_message,
    send_group_message,
    set_admins_only,
    set_conversation_admin,
)


class ConversationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return list_conversations_for_user(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Compute the response first so this fetch doesn't alter what the
        # caller sees, then record delivery for the caller's conversations.
        response = super().list(request, *args, **kwargs)
        mark_conversations_delivered(
            conversations=self.get_queryset(), user=request.user
        )
        return response


class StartDirectConversationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def post(self, request, *args, **kwargs):
        other = get_object_or_404(User, pk=request.data.get("user_id"))
        conversation = get_or_create_direct_conversation(user=request.user, other=other)
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class CreateGroupConversationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ConversationSerializer

    def post(self, request, *args, **kwargs):
        conversation = create_group_conversation(
            name=request.data.get("name", ""),
            creator=request.user,
            member_ids=request.data.get("member_ids", []),
        )
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data,
            status=201,
        )


class ConversationDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_object(self):
        conversation = get_object_or_404(
            Conversation, pk=self.kwargs["conversation_id"]
        )
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Bu söhbətin üzvü deyilsiniz.")
        return conversation


class BaseGroupManageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_conversation(self, conversation_id) -> Conversation:
        conversation = get_object_or_404(
            Conversation, pk=conversation_id, is_group=True
        )
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Bu qrupun üzvü deyilsiniz.")
        return conversation

    def require_admin(self, conversation: Conversation):
        if not conversation.admins.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Bu əməliyyat üçün qrup admini olmalısınız.")


class RenameConversationView(BaseGroupManageView):
    def patch(self, request, conversation_id):
        conversation = self.get_conversation(conversation_id)
        self.require_admin(conversation)
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"detail": "name is required"}, status=400)
        conversation = rename_conversation(conversation=conversation, name=name)
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class AddMembersView(BaseGroupManageView):
    def post(self, request, conversation_id):
        conversation = self.get_conversation(conversation_id)
        self.require_admin(conversation)
        conversation = add_members(
            conversation=conversation, user_ids=request.data.get("member_ids", [])
        )
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class RemoveMemberView(BaseGroupManageView):
    def delete(self, request, conversation_id, user_id):
        conversation = self.get_conversation(conversation_id)
        self.require_admin(conversation)
        if int(user_id) == request.user.id:
            return Response(
                {"detail": "Özünüzü çıxara bilməzsiniz, qrupdan ayrılın."}, status=400
            )
        target = get_object_or_404(User, pk=user_id)
        conversation = remove_member(conversation=conversation, user=target)
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class SetConversationAdminView(BaseGroupManageView):
    def patch(self, request, conversation_id, user_id):
        conversation = self.get_conversation(conversation_id)
        self.require_admin(conversation)
        target = get_object_or_404(User, pk=user_id)
        if not conversation.participants.filter(id=target.id).exists():
            return Response({"detail": "Bu istifadəçi qrupun üzvü deyil."}, status=400)
        conversation = set_conversation_admin(
            conversation=conversation,
            user=target,
            is_admin=bool(request.data.get("is_admin")),
        )
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class LeaveConversationView(BaseGroupManageView):
    def post(self, request, conversation_id):
        conversation = self.get_conversation(conversation_id)
        leave_conversation(conversation=conversation, user=request.user)
        return Response(status=204)


class ConversationSettingsView(BaseGroupManageView):
    """Group-level toggles set by any admin. Currently: admins_only."""

    def patch(self, request, conversation_id):
        conversation = self.get_conversation(conversation_id)
        self.require_admin(conversation)
        if "admins_only" in request.data:
            conversation = set_admins_only(
                conversation=conversation,
                admins_only=bool(request.data.get("admins_only")),
            )
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class MessageDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get(self, request, conversation_id, message_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if not conversation.participants.filter(id=request.user.id).exists():
            raise PermissionDenied("Bu söhbətin üzvü deyilsiniz.")
        return get_object_or_404(Message, pk=message_id, conversation=conversation)

    def patch(self, request, conversation_id, message_id):
        message = self._get(request, conversation_id, message_id)
        message = edit_message(
            message=message,
            editor=request.user,
            text=request.data.get("text", ""),
            ciphertext=request.data.get("ciphertext", ""),
            nonce=request.data.get("nonce", ""),
        )
        return Response(MessageSerializer(message).data)

    def delete(self, request, conversation_id, message_id):
        message = self._get(request, conversation_id, message_id)
        delete_message(message=message, actor=request.user)
        return Response(status=204)


class MarkConversationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if not conversation.participants.filter(id=request.user.id).exists():
            raise PermissionDenied("Bu söhbətin üzvü deyilsiniz.")
        mark_conversation_read(conversation=conversation, user=request.user)
        return Response(status=204)


class MessageAttachmentView(APIView):
    """Streams a message's attachment to conversation members only."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id, message_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if not conversation.participants.filter(id=request.user.id).exists():
            raise PermissionDenied("Bu söhbətin üzvü deyilsiniz.")
        message = get_object_or_404(Message, pk=message_id, conversation=conversation)
        if not message.attachment:
            return Response({"detail": "Qoşma yoxdur."}, status=404)
        return FileResponse(
            message.attachment.open("rb"), content_type="application/octet-stream"
        )


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_conversation(self) -> Conversation:
        conversation = get_object_or_404(
            Conversation, pk=self.kwargs["conversation_id"]
        )
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Bu söhbətin üzvü deyilsiniz.")
        return conversation

    def get_queryset(self):
        conversation = self.get_conversation()
        after_id = self.request.query_params.get("after")
        mark_conversations_delivered(
            conversations=[conversation], user=self.request.user
        )
        return list_messages(conversation=conversation, after_id=after_id)

    def perform_create(self, serializer):
        conversation = self.get_conversation()
        if conversation.is_group:
            message = send_group_message(
                conversation=conversation,
                sender=self.request.user,
                text=serializer.validated_data.get("text", ""),
                attachment=serializer.validated_data.get("attachment"),
            )
        else:
            message = send_direct_message(
                conversation=conversation,
                sender=self.request.user,
                ciphertext=serializer.validated_data.get("ciphertext", ""),
                nonce=serializer.validated_data.get("nonce", ""),
                attachment=serializer.validated_data.get("attachment"),
            )
        serializer.instance = message
