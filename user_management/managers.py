from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(username, email, password, **extra_fields)
