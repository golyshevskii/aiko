from core.schema.base import CEnum


class UserStatus(CEnum):
    """Available user statuses."""

    ACTIVE = 1
    INACTIVE = 0
    BANNED = -1


class DBInitStrategy(CEnum):
    """Database initialization strategies."""

    CREATE = "create"
    RECREATE = "recreate"
