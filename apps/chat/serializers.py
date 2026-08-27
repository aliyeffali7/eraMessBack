from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "text",
            "ciphertext",
            "nonce",
            "created_at",
        ]
        read_only_fields = ["conversation", "sender", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    admin_ids = serializers.PrimaryKeyRelatedField(
        source="admins", many=True, read_only=True
    )
    last_message = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "is_group",
            "name",
            "participants",
            "admin_ids",
            "created_by",
            "created_at",
            "last_message",
            "is_admin",
            "unread_count",
        ]

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last).data if last else None

    def get_is_admin(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        return obj.admins.filter(id=request.user.id).exists()

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request:
            return 0
        marker = obj.read_markers.filter(user=request.user).first()
        qs = obj.messages.exclude(sender=request.user)
        if marker and marker.last_read_at:
            qs = qs.filter(created_at__gt=marker.last_read_at)
        return qs.count()
