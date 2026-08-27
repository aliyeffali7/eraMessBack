from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Section, Unit
from .serializers import SectionSerializer, UnitSerializer
from .services import create_section, create_unit, list_units, rename_section, rename_unit


class UnitListCreateView(generics.ListCreateAPIView):
    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return list_units()

    def perform_create(self, serializer):
        unit = create_unit(name=serializer.validated_data["name"], creator=self.request.user)
        serializer.instance = unit


class SectionCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SectionSerializer

    def perform_create(self, serializer):
        section = create_section(
            unit=serializer.validated_data["unit"],
            name=serializer.validated_data["name"],
            creator=self.request.user,
        )
        serializer.instance = section


class RenameUnitView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, unit_id):
        unit = get_object_or_404(Unit, pk=unit_id)
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"detail": "name is required"}, status=400)
        unit = rename_unit(unit=unit, name=name)
        return Response(UnitSerializer(unit).data)


class RenameSectionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, section_id):
        section = get_object_or_404(Section, pk=section_id)
        name = request.data.get("name", "").strip()
        if not name:
            return Response({"detail": "name is required"}, status=400)
        section = rename_section(section=section, name=name)
        return Response(SectionSerializer(section).data)
