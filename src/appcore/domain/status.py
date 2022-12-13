from enum import Enum

class Status(str,Enum):
    OK = "OK"
    CREATED = "CREATED"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"