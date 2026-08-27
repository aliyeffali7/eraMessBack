from django.urls import path

from .views import RenameSectionView, RenameUnitView, SectionCreateView, UnitListCreateView

urlpatterns = [
    path("units/", UnitListCreateView.as_view(), name="unit-list-create"),
    path("units/<int:unit_id>/rename/", RenameUnitView.as_view(), name="unit-rename"),
    path("sections/", SectionCreateView.as_view(), name="section-create"),
    path("sections/<int:section_id>/rename/", RenameSectionView.as_view(), name="section-rename"),
]
