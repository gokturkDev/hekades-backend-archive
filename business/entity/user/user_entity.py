import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class UserEntity(BaseModel):
    full_name: str
    email: str
    credits: int
    created_at: datetime.datetime
    profile_picture: Union[str, None]
    is_active: bool
    role: UserRole
    dob: Union[datetime.datetime, None]
    country: Union[str, None]
    city: Union[str, None]
    institution: str
    department: str
    cell_phone: str
    address: Union[str, None]
    occupation: Union[str, None]
    branch: Union[str, None]
    ssn: Union[str, None]
    title: str
