from enum import Enum

class status(str,Enum):
    OK = "OK"
    CREATED = "CREATED"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"