from enum import Enum


class UserTypes(str, Enum):
    admin = "admin"
    regular = "regular"
