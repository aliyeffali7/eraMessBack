from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Meeting, MeetingInvite


class MeetingInviteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    reason = serializers.SerializerMethodField()

    class Meta:
        model = MeetingInvite
        fields = ["id", "user", "response", "reason"]

    def get_reason(self, obj):
        # A decline reason is only for the organiser/admins and the person
        # who wrote it — never for other invitees.
        request = self.context.get("request")
        if not request:
            return ""
        me = request.user
        if me.is_staff or me.id == obj.meeting.created_by_id or me.id == obj.user_id:
            return obj.reason
        return ""


class MeetingSerializer(serializers.ModelSerializer):
    invites = MeetingInviteSerializer(many=True, read_only=True)
    my_response = serializers.SerializerMethodField()
    invite_count = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "description",
            "location",
            "starts_at",
            "ends_at",
            "created_by",
            "created_at",
            "invites",
            "my_response",
            "invite_count",
        ]
        read_only_fields = ["created_by", "created_at"]

    def get_my_response(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        invite = next(
            (i for i in obj.invites.all() if i.user_id == request.user.id), None
        )
        return invite.response if invite else None

    def get_invite_count(self, obj):
        return obj.invites.count()


class CreateMeetingSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    location = serializers.CharField(required=False, allow_blank=True, default="")
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField(required=False, allow_null=True, default=None)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    section_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    all_users = serializers.BooleanField(required=False, default=False)


class RespondSerializer(serializers.Serializer):
    response = serializers.ChoiceField(choices=["yes", "no"])
    reason = serializers.CharField(
        max_length=300, required=False, allow_blank=True, default=""
    )
