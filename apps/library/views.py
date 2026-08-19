from rest_framework import generics, permissions

from .models import Document
from .serializers import DocumentSerializer
from .services import list_documents_for_user, upload_document


class DocumentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return list_documents_for_user(user=self.request.user)


class DocumentUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        document = upload_document(
            title=serializer.validated_data["title"],
            file=serializer.validated_data["file"],
            min_degree=serializer.validated_data["min_degree"],
            uploaded_by=self.request.user,
        )
        serializer.instance = document


class AdminDocumentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()
