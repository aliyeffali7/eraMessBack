from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import register_token


class RegisterPushTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"detail": "token is required"}, status=status.HTTP_400_BAD_REQUEST)
        register_token(user=request.user, token=token)
        return Response(status=status.HTTP_204_NO_CONTENT)
