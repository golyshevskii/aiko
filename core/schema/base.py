from enum import Enum


class CEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
