from rest_framework import serializers

from .models import MAX_DEGREE, MIN_DEGREE, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "degree", "is_staff", "joined_at"]
        read_only_fields = ["degree", "is_staff", "joined_at"]


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    degree = serializers.IntegerField(min_value=MIN_DEGREE, max_value=MAX_DEGREE, default=MIN_DEGREE)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "degree"]


class UpdateDegreeSerializer(serializers.Serializer):
    degree = serializers.IntegerField(min_value=MIN_DEGREE, max_value=MAX_DEGREE)
