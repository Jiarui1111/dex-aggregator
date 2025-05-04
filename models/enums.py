from enum import Enum

class OrderStatus(str, Enum):
    OPEN = "OPEN"
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
