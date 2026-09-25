from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Meeting
from .serializers import CreateMeetingSerializer, MeetingSerializer, RespondSerializer
from .services import (
    create_meeting,
    list_all_meetings,
    list_meetings_for_user,
    respond_to_meeting,
)


class MeetingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return list_meetings_for_user(user=self.request.user)


class MeetingCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CreateMeetingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = create_meeting(creator=request.user, **serializer.validated_data)
        return Response(
            MeetingSerializer(meeting, context={"request": request}).data, status=201
        )


class AdminMeetingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return list_all_meetings()


class RespondToMeetingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        serializer = RespondSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = respond_to_meeting(
            meeting=meeting,
            user=request.user,
            response=serializer.validated_data["response"],
            reason=serializer.validated_data["reason"],
        )
        if invite is None:
            raise PermissionDenied("Bu iclasa dəvət olunmamısınız.")
        return Response(MeetingSerializer(meeting, context={"request": request}).data)
