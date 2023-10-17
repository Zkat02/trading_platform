from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None:
            return None
        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError as exc:
            raise AuthenticationFailed("Invalid signature") from exc
        except Exception as exc:
            raise ParseError() from exc
        username = payload.get("user_identifier")
        if username is None:
            raise AuthenticationFailed(f"user_identifier is empty in JWT")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed(f"User with username - {username} not found")
        return user, payload

    @staticmethod
    def create_jwt(user):
        payload = {
            "user_identifier": user.username,
            "exp": int((datetime.now() + settings.JWT_CONF["TOKEN_LIFETIME"]).timestamp()),
            "iat": datetime.now().timestamp(),
        }

        jwt_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.JWT_CONF["ALGORITHM"]
        )
        return jwt_token

    @staticmethod
    def get_auth_header():
        return str(settings.JWT_CONF["AUTH_HEADER_TYPES"])

    @staticmethod
    def get_the_token_from_header(token):
        token = token.replace(JWTAuthentication.get_auth_header(), "").replace(" ", "")
        return token
