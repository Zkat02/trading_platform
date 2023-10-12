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

        username_or_email = payload.get("user_identifier")
        if username_or_email is None:
            raise AuthenticationFailed("User identifier not found in JWT")

        user = User.objects.filter(username=username_or_email).first()
        if user is None:
            user = User.objects.filter(email=username_or_email).first()
            if user is None:
                raise AuthenticationFailed("User not found")

        return user, payload

    def authenticate_header(self, request):
        return settings.JWT_CONF["AUTH_HEADER_TYPES"]

    @classmethod
    def create_jwt(cls, user):
        payload = {
            "user_identifier": user.username,
            "exp": int((datetime.now() + settings.JWT_CONF["TOKEN_LIFETIME"]).timestamp()),
            # set the expiration time for 5 hour from now
            "iat": datetime.now().timestamp(),
            "username": user.username,
            "email": user.email,
        }

        jwt_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.JWT_CONF["ALGORITHM"]
        )

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace(settings.JWT_CONF["AUTH_HEADER_TYPES"], "").replace(" ", "")
        return token
