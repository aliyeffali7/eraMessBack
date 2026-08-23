from rest_framework import generics, permissions

from .serializers import SectionSerializer, UnitSerializer
from .services import create_section, create_unit, list_units


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
