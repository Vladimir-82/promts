from enum import Enum

class StrEnum(str, Enum):
    """Enum where members are also (and must be) strings"""
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

status = Status.ACTIVE
print(str(status))  # "active"
print(isinstance(status, str))  # True
