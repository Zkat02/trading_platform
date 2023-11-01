from base.services import BaseService
from user_management.authentication import JWTAuthentication
from user_management.exceptions import AuthenticationFailedException, ChangeBalanceException
from user_management.repositories import UserRepository


class UserService(BaseService):
    def __init__(self):
        self.repository = UserRepository()

    def register_user(self, username, password, email, role):
        user = self.repository.create_user(username, password, email, role)
        return user

    def reset_password(self, username, old_password, new_password, confirm_new_password):
        user = self.repository.get_user_by_username(username)
        if user and user.check_password(old_password):
            if new_password != confirm_new_password:
                raise AuthenticationFailedException(
                    "Invalid <new_password> not equal <confirm_new_password>."
                )
            if new_password == old_password:
                raise AuthenticationFailedException(
                    "Invalid <new_password> is equal <old_password>."
                )
            return self.repository.update_user_password(user, new_password)
        raise AuthenticationFailedException("Invalid old_password.")

    def get_all_users(self):
        return self.repository.get_all_users()

    def get_user_by_id(self, user_id):
        return self.repository.get_user_by_id(user_id)

    def get_user_by_username(self, username):
        return self.repository.get_user_by_username(username)

    def block_user(self, user_id):
        user = self.repository.get_user_by_id(user_id)
        if user:
            self.repository.block_user(user)
            return True
        return False

    def unlock_user(self, user_id):
        user = self.repository.get_user_by_id(user_id)
        if user:
            self.repository.unlock_user(user)
            return True
        return False

    def get_user_balance(self, user_id):
        user = self.repository.get_user_by_id(user_id)
        balance = self.repository.get_user_balance(user)
        return balance

    def change_balance(self, user_id, new_balance=None, value_to_add=None):
        if new_balance is not None and value_to_add is not None:
            raise ChangeBalanceException(
                "You must provide something one: 'new_balance' or 'value_to_add', but not both."
            )
        if new_balance and value_to_add:
            raise ChangeBalanceException(
                "You must provide something one: 'new_balance' or 'value_to_add', but not both."
            )

        if new_balance is not None:
            balance = self.set_new_balance(user_id, new_balance)
            message = "Balance was changed successfully."
        if value_to_add is not None:
            balance = self.add_to_balance(user_id, value_to_add)
            message = "Balance was increased successfully."
        return message, balance

    def set_new_balance(self, user_id, new_balance):
        user = self.repository.get_user_by_id(user_id)
        balance = self.repository.set_new_balance(user, new_balance)
        return balance

    def add_to_balance(self, user_id, value_to_add) -> int:
        user = self.repository.get_user_by_id(user_id)
        balance = self.repository.add_to_balance(user, value_to_add)
        return balance

    def subtract_from_balance(self, user_id, value_to_subtract):
        user = self.repository.get_user_by_id(user_id)
        balance = self.repository.subtract_from_balance(user, value_to_subtract)
        return balance

    def authentificate_user(self, username, password):
        user = self.get_user_by_username(username=username)
        if user.check_password(password):
            jwt_token = JWTAuthentication.create_jwt(user)
            return jwt_token
        raise AuthenticationFailedException("Invalid password.")
