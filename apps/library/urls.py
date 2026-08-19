from django.urls import path

from .views import AdminDocumentListView, DocumentListView, DocumentUploadView

urlpatterns = [
    path("", DocumentListView.as_view(), name="document-list"),
    path("upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("admin/", AdminDocumentListView.as_view(), name="admin-document-list"),
]
