from rest_framework import serializers

from .models import MAX_DEGREE, MIN_DEGREE, User


class UserSerializer(serializers.ModelSerializer):
    section_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "degree",
            "is_staff",
            "joined_at",
            "section",
            "section_name",
            "unit_name",
            "public_key",
        ]
        read_only_fields = ["degree", "is_staff", "joined_at", "section", "section_name", "unit_name", "public_key"]

    def get_section_name(self, obj):
        return obj.section.name if obj.section else None

    def get_unit_name(self, obj):
        return obj.section.unit.name if obj.section else None


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    degree = serializers.IntegerField(min_value=MIN_DEGREE, max_value=MAX_DEGREE, default=MIN_DEGREE)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "degree"]


class UpdateDegreeSerializer(serializers.Serializer):
    degree = serializers.IntegerField(min_value=MIN_DEGREE, max_value=MAX_DEGREE)


class AssignSectionSerializer(serializers.Serializer):
    section_id = serializers.IntegerField()


class SetPublicKeySerializer(serializers.Serializer):
    public_key = serializers.CharField()
