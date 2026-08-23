from django.urls import path

from .views import SectionCreateView, UnitListCreateView

urlpatterns = [
    path("units/", UnitListCreateView.as_view(), name="unit-list-create"),
    path("sections/", SectionCreateView.as_view(), name="section-create"),
]
