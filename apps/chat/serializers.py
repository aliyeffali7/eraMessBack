from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Conversation, Message

MAX_ATTACHMENT_BYTES = 15 * 1024 * 1024


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachment = serializers.FileField(write_only=True, required=False)
    has_attachment = serializers.SerializerMethodField()

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
            "edited_at",
            "attachment",
            "has_attachment",
        ]
        read_only_fields = ["conversation", "sender", "created_at", "edited_at"]

    def get_has_attachment(self, obj):
        return bool(obj.attachment)

    def validate_attachment(self, value):
        if value.size > MAX_ATTACHMENT_BYTES:
            raise serializers.ValidationError("Fayl 15 MB-dan böyük ola bilməz.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    admin_ids = serializers.PrimaryKeyRelatedField(
        source="admins", many=True, read_only=True
    )
    last_message = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    peer_last_read = serializers.SerializerMethodField()
    peer_last_delivered = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "is_group",
            "name",
            "participants",
            "admin_ids",
            "admins_only",
            "created_by",
            "created_at",
            "last_message",
            "is_admin",
            "unread_count",
            "peer_last_read",
            "peer_last_delivered",
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

    def _peer_floor(self, obj, field):
        """Oldest `field` timestamp across all *other* participants, or None if
        any of them has none yet. A message is delivered/read only once every
        other participant has it (1:1 → the single peer; group → everyone)."""
        request = self.context.get("request")
        if not request:
            return None
        peer_ids = list(
            obj.participants.exclude(id=request.user.id).values_list("id", flat=True)
        )
        if not peer_ids:
            return None
        stamps = {
            m.user_id: getattr(m, field)
            for m in obj.read_markers.filter(user_id__in=peer_ids)
        }
        values = [stamps.get(pid) for pid in peer_ids]
        if any(v is None for v in values):
            return None
        return min(values)

    def get_peer_last_read(self, obj):
        return self._peer_floor(obj, "last_read_at")

    def get_peer_last_delivered(self, obj):
        return self._peer_floor(obj, "last_delivered_at")
