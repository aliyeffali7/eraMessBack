from rest_framework import serializers

from .models import Section, Unit


class SectionSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ["id", "unit", "unit_name", "name", "conversation", "member_count", "created_at"]
        read_only_fields = ["conversation", "created_at"]

    def get_member_count(self, obj):
        return obj.members.count()


class UnitSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ["id", "name", "conversation", "sections", "member_count", "created_at"]
        read_only_fields = ["conversation", "created_at"]

    def get_member_count(self, obj):
        return sum(section.members.count() for section in obj.sections.all())
