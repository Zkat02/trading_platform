from django.contrib.auth import get_user_model

from base.repositories import BaseRepository
from user_management.exceptions import AuthenticationFailedException, SubtractBalanceException

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
        self.model = User

    def get_user_by_username(self, username):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            raise AuthenticationFailedException(f"User with username - <{username}> not found")

    def create_user(self, username, password, email, role):
        user = self.model.objects.create_user(
            username=username, password=password, email=email, role=role
        )
        return user

    def update_user_password(self, user, new_password):
        user.set_password(new_password)
        user.save()
        return user

    def get_all_users(self):
        return self.model.objects.all()

    def get_user_by_id(self, user_id):
        try:
            return self.model.objects.get(id=user_id)
        except self.model.DoesNotExist:
            return None

    def block_user(self, user):
        user.is_active = False
        user.save()

    def unlock_user(self, user):
        user.is_active = True
        user.save()

    def get_user_balance(self, user):
        return user.balance

    def set_new_balance(self, user, new_balance):
        user.balance = new_balance
        user.save()
        print(user.balance)
        return new_balance

    def add_to_balance(self, user, value_to_add):
        new_balance = user.balance + value_to_add
        return self.set_new_balance(user, new_balance)

    def subtract_from_balance(self, user, value_to_subtract):
        if user.balance < value_to_subtract:
            raise SubtractBalanceException("Insufficient balance.")
        new_balance = user.balance - value_to_subtract
        return self.set_new_balance(user, new_balance)
