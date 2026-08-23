from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "text", "created_at"]
        read_only_fields = ["conversation", "sender", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    admin_ids = serializers.PrimaryKeyRelatedField(source="admins", many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

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
        ]

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last).data if last else None

    def get_is_admin(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        return obj.admins.filter(id=request.user.id).exists()
