from django.urls import path

from .views import AdminMeetingListView, MeetingCreateView, MeetingListView, RespondToMeetingView

urlpatterns = [
    path("", MeetingListView.as_view(), name="meeting-list"),
    path("create/", MeetingCreateView.as_view(), name="meeting-create"),
    path("admin/", AdminMeetingListView.as_view(), name="admin-meeting-list"),
    path("<int:meeting_id>/respond/", RespondToMeetingView.as_view(), name="meeting-respond"),
]
