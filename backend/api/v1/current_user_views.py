from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Возвращаем данные текущего пользователя
        user_data = {
            "id": request.user.id,
            "email": request.user.email,
            "username": request.user.username
        }
        return Response(user_data)

        