from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if extra_fields.get("role") is None:
            extra_fields.setdefault("role", "user")
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(username, email, password, **extra_fields)
    
    def create_analyst(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "analyst")
        return self.create_user(username, email, password, **extra_fields)
