from base.services import BaseService
from user_management.authentication import JWTAuthentication
from user_management.exceptions import AuthenticationFailedException, ChangeBalanceException, DoNotBlockException, DoNotUnblockException
from user_management.repositories import UserRepository
from django.contrib.auth import get_user_model
from typing import Union

User = get_user_model()

class UserService(BaseService):
    """
    Service for handling user-related operations.
    """
    def __init__(self):
        super().__init__(model=User, repository=UserRepository)

    def create(self, **kwargs) -> User:
        """
        Create a new user.

        Args:
        - **kwargs: Keyword arguments for creating the user.

        Returns:
        - User: The created user.
        """
        user = self.repository.create_user(**kwargs)
        return user

    def register_user(self, username: str, password: str, email: str, role: str) -> User:
        """
        Register a new user.

        Args:
        - username (str): The username of the user.
        - password (str): The password of the user.
        - email (str): The email of the user.
        - role (str): The role of the user.

        Returns:
        - User: The registered user.
        """
        user = self.repository.create_user(username=username, password=password, email=email, role=role)
        return user

    def reset_password(self, username: str, old_password: str, new_password: str, confirm_new_password: str) -> User:
        """
        Reset the user's password.

        Args:
        - username (str): The username of the user.
        - old_password (str): The old password.
        - new_password (str): The new password.
        - confirm_new_password (str): The confirmation of the new password.

        Returns:
        - User: The user with the updated password.

        Raises:
        - AuthenticationFailedException: If the old password is invalid or other password-related issues.
        """
        user = self.repository.get_user_by_username(username)
        if user and user.check_password(old_password):
            if new_password != confirm_new_password:
                raise AuthenticationFailedException("Invalid <new_password> not equal <confirm_new_password>.")
            if new_password == old_password:
                raise AuthenticationFailedException("Invalid <new_password> is equal <old_password>.")
            return self.repository.update_user_password(user, new_password)
        raise AuthenticationFailedException("Invalid old_password.")

    def get_all(self) -> User:
        """
        Get all users.

        Returns:
        - User: The list of all users.
        """
        return self.repository.get_all()

    def get_user_by_username(self, username: str) -> User:
        """
        Get a user by their username.

        Args:
        - username (str): The username of the user.

        Returns:
        - User: The user object.
        """
        return self.repository.get_user_by_username(username)

    def block_user(self, user_id: int) -> None:
        """
        Block a user by their user ID.

        Args:
        - user_id (int): The ID of the user to be blocked.

        Raises:
        - DoNotBlockException: If the user is already blocked.
        """
        user = self.repository.get_by_id(user_id)
        if not user.is_active:
            raise DoNotBlockException("User already is blocked.")
        self.repository.block_user(user)

    def unblock_user(self, user_id: int) -> None:
        """
        Unblock a user by their user ID.

        Args:
        - user_id (int): The ID of the user to be unblocked.

        Raises:
        - DoNotUnblockException: If the user is already unblocked.
        """
        user = self.repository.get_by_id(user_id)
        if user.is_active:
            raise DoNotUnblockException("User already is unblocked.")
        self.repository.unblock_user(user)

    def get_user_balance(self, user_id: int) -> Union[int, float]:
        """
        Get the balance of a user by their user ID.

        Args:
        - user_id (int): The ID of the user.

        Returns:
        - Union[int, float]: The balance of the user.
        """
        user = self.repository.get_by_id(user_id)
        balance = self.repository.get_user_balance(user)
        return balance

    def change_balance(self, user_id: int, new_balance: Union[int, float] = None, value_to_add: Union[int, float] = None) -> Union[int, float]:
        """
        Change the balance of a user.

        Args:
        - user_id (int): The ID of the user.
        - new_balance (Union[int, float], optional): The new balance to be set.
        - value_to_add (Union[int, float], optional): The value to be added to the balance.

        Returns:
        - Union[int, float]: The updated balance of the user.
        """
        if new_balance is not None:
            balance = self.set_new_balance(user_id, new_balance)
        if value_to_add is not None:
            balance = self.add_to_balance(user_id, value_to_add)
        return balance

    def set_new_balance(self, user_id: int, new_balance: Union[int, float]) -> Union[int, float]:
        """
        Set a new balance for a user by their user ID.

        Args:
        - user_id (int): The ID of the user.
        - new_balance (Union[int, float]): The new balance to be set.

        Returns:
        - Union[int, float]: The new balance of the user.
        """
        user = self.repository.get_by_id(user_id)
        balance = self.repository.set_new_balance(user, new_balance)
        return balance

    def add_to_balance(self, user_id: int, value_to_add: Union[int, float]) -> Union[int, float]:
        """
        Add a value to the balance of a user by their user ID.

        Args:
        - user_id (int): The ID of the user.
        - value_to_add (Union[int, float]): The value to be added to the balance.

        Returns:
        - Union[int, float]: The updated balance of the user.
        """
        user = self.repository.get_by_id(user_id)
        balance = self.repository.add_to_balance(user, value_to_add)
        return balance

    def subtract_from_balance(self, user_id: int, value_to_subtract: Union[int, float]) -> Union[int, float]:
        """
        Subtract a value from the balance of a user by their user ID.

        Args:
        - user_id (int): The ID of the user.
        - value_to_subtract (Union[int, float]): The value to be subtracted from the balance.

        Returns:
        - Union[int, float]: The updated balance of the user.

        Raises:
        - SubtractBalanceException: If the user has an insufficient balance.
        """
        user = self.repository.get_by_id(user_id)
        balance = self.repository.subtract_from_balance(user, value_to_subtract)
        return balance

    def authentificate_user(self, username: str, password: str) -> str:
        """
        Authenticate a user by their username and password.

        Args:
        - username (str): The username of the user.
        - password (str): The password of the user.

        Returns:
        - str: The JWT token for authentication.

        Raises:
        - AuthenticationFailedException: If the authentication fails.
        """
        user = self.get_user_by_username(username=username)
        if not user.check_password(password):
            raise AuthenticationFailedException("Invalid password.")
        jwt_token = JWTAuthentication.create_jwt(user)
        return jwt_token
