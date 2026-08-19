from apps.accounts.models import User

from .models import Document


def list_documents_for_user(*, user: User):
    return Document.objects.filter(min_degree__lte=user.degree)


def upload_document(*, title: str, file, min_degree: int, uploaded_by: User) -> Document:
    return Document.objects.create(title=title, file=file, min_degree=min_degree, uploaded_by=uploaded_by)
