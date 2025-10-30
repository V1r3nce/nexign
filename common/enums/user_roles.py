from enum import Enum


class UserRole(Enum):
    """Роли пользователей в системе NBSS"""

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
    def from_string(cls, role_string: str) -> "UserRole":
        """Преобразует строку в соответствующий элемент UserRole.
        Raises:
            ValueError: если передана неизвестная роль.
        """
        for role in cls:
            if role.value == role_string:
                return role
        raise ValueError(f"Неизвестная роль: {role_string}")

    @classmethod
    def get_default(cls) -> "UserRole":
        """Возвращает роль по умолчанию для тестов и логина."""
        return cls.ADMIN

    @classmethod
    def get_test_roles(cls) -> list["UserRole"]:
        """Возвращает список всех тестовых ролей (исключая базовую ADMIN)."""
        return [role for role in cls if role != cls.ADMIN]

    @classmethod
    def get_seller_roles(cls) -> list["UserRole"]:
        """Возвращает список ролей продавцов."""
        return [cls.SELLER_JR_TEST, cls.SELLER_TEST, cls.SELLER_SR_TEST]

    @classmethod
    def get_management_roles(cls) -> list["UserRole"]:
        """Возвращает список управленческих ролей."""
        return [cls.ADMIN_TEST, cls.SP_MANAGER_TEST, cls.SECURITY_TEST, cls.FINANCE_TEST]
