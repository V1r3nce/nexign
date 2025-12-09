from enum import Enum


class User(Enum):
    """Пользователи с разными ролями в системе NBSS"""

    ADMIN = "Admin"
    ADMIN_TEST = "ADMIN_TEST"
    SELLER_JR_TEST = "SELLER_JR_TEST"
    SELLER_TEST = "SELLER_TEST"
    SELLER_SR_TEST = "SELLER_SR_TEST"
    CUSTOMER_CARE_TEST = "CUSTOMER_CARE_TEST"
    SP_MANAGER_TEST = "SP_MANAGER_TEST"
    SECURITY_TEST = "SECURITY_TEST"
    FINANCE_TEST = "FINANCE_TEST"

    def __str__(self) -> str:
        """Возвращает строковое представление роли (значение Enum)."""
        return self.value

    @classmethod
    def from_string(cls, user_string: str) -> "User":
        """Преобразует строку в соответствующий элемент User.
        Raises:
            ValueError: если передан неизвестный пользователь.
        """
        for user in cls:
            if user.value == user_string:
                return user
        raise ValueError(f"Неизвестный пользователь: {user_string}")

    @classmethod
    def get_default(cls) -> "User":
        """Возвращает роль по умолчанию для тестов и логина."""
        return cls.ADMIN

    @classmethod
    def get_test_users(cls) -> list["User"]:
        """Возвращает список всех тестовых пользователей (исключая базового ADMIN)."""
        return [user for user in cls if user != cls.ADMIN]

    @classmethod
    def get_seller_users(cls) -> list["User"]:
        """Возвращает список пользователей продавцов."""
        return [cls.SELLER_JR_TEST, cls.SELLER_TEST, cls.SELLER_SR_TEST]

    @classmethod
    def get_management_users(cls) -> list["User"]:
        """Возвращает список управленческих пользователей."""
        return [cls.ADMIN_TEST, cls.SP_MANAGER_TEST, cls.SECURITY_TEST, cls.FINANCE_TEST]
