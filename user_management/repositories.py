from django.contrib.auth import get_user_model
from base.repositories import BaseRepository
from user_management.exceptions import AuthenticationFailedException, SubtractBalanceException
from django.core.exceptions import ObjectDoesNotExist
from typing import Union

User = get_user_model()

class UserRepository(BaseRepository):
    """
    Repository handling database operations related to the User model.
    """
    def __init__(self):
        super().__init__(model=User)

    def get_user_by_username(self, username: str) -> User:
        """
        Retrieve a user by their username.

        Args:
        - username (str): The username of the user.

        Returns:
        - User: The user object.

        Raises:
        - AuthenticationFailedException: If the user with the specified username is not found.
        """
        try:
            return self.model.objects.get(username=username)
        except ObjectDoesNotExist:
            raise AuthenticationFailedException(f"User with username - <{username}> not found")

    def create_user(self, username: str, password: str, role: str, email: str = None) -> User:
        """
        Create a new user.

        Args:
        - username (str): The username of the user.
        - password (str): The password of the user.
        - role (str): The role of the user.
        - email (str, optional): The email of the user.

        Returns:
        - User: The created user object.
        """
        user = self.model.objects.create_user(username=username, password=password, email=email, role=role)
        return user

    def update_user_password(self, user: User, new_password: str) -> User:
        """
        Update the password of a user.

        Args:
        - user (User): The user object.
        - new_password (str): The new password.

        Returns:
        - User: The user object with the updated password.
        """
        user.set_password(new_password)
        user.save()
        return user

    def block_user(self, user: User) -> None:
        """
        Block a user.

        Args:
        - user (User): The user object to be blocked.
        """
        user.is_active = False
        user.save()

    def unblock_user(self, user: User) -> None:
        """
        Unblock a user.

        Args:
        - user (User): The user object to be unblocked.
        """
        user.is_active = True
        user.save()

    def get_user_balance(self, user: User) -> float:
        """
        Get the balance of a user.

        Args:
        - user (User): The user object.

        Returns:
        - Union[int, float]: The balance of the user.
        """
        return user.balance

    def set_new_balance(self, user: User, new_balance: float) -> float:
        """
        Set a new balance for a user.

        Args:
        - user (User): The user object.
        - new_balance (Union[int, float]): The new balance to be set.

        Returns:
        - Union[int, float]: The new balance of the user.
        """
        user.balance = new_balance
        user.save()
        return new_balance

    def add_to_balance(self, user: User, value_to_add: float) -> float:
        """
        Add a value to the balance of a user.

        Args:
        - user (User): The user object.
        - value_to_add (Union[int, float]): The value to be added to the balance.

        Returns:
        - Union[int, float]: The updated balance of the user.
        """
        new_balance = user.balance + value_to_add
        return self.set_new_balance(user, new_balance)

    def subtract_from_balance(self, user: User, value_to_subtract: float) -> float:
        """
        Subtract a value from the balance of a user.

        Args:
        - user (User): The user object.
        - value_to_subtract (Union[int, float]): The value to be subtracted from the balance.

        Returns:
        - Union[int, float]: The updated balance of the user.

        Raises:
        - SubtractBalanceException: If the user has an insufficient balance.
        """
        if user.balance < value_to_subtract:
            raise SubtractBalanceException("Insufficient balance.")
        new_balance = user.balance - value_to_subtract
        return self.set_new_balance(user, new_balance)
