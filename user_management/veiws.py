from django.contrib.auth import get_user_model
from rest_framework import permissions, status, views
from rest_framework.response import Response

from user_management.models import CustomUser

from .authentication import JWTAuthentication
from .serializers import ObtainTokenSerializer, UserRegistrationSerializer

User = get_user_model()


class ObtainTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ObtainTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_or_email = serializer.validated_data.get("username_or_email")
        password = serializer.validated_data.get("password")

        user = User.objects.filter(username=username_or_email).first()
        if user is None:
            user = User.objects.filter(email=username_or_email).first()

        if user is None or not user.check_password(password):
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        jwt_token = JWTAuthentication.create_jwt(user)

        return Response({"token": jwt_token})


# class UserRegistrationView(views.APIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserRegistrationSerializer
#     permission_classes = [permissions.AllowAny]


#     def post(self, request):
#         serializer = UserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             user.set_password(user.password)
#             user.save()
#             jwt_token = JWTAuthentication.create_jwt(user)
#             return Response(
#                 {"message": "User registered successfully.", "user": user, "token": jwt_token},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserRegistrationView(views.APIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.save()
            jwt_token = JWTAuthentication.create_jwt(user)
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": serializer.data,
                    "token": jwt_token,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
