from abc import ABC, abstractmethod
from typing import Union

from business.entity.user.user_entity import UserEntity
from business.repository.base_repository import BaseRepository


class UserRepository(BaseRepository, ABC):
    @abstractmethod
    def add(self, user: UserEntity, hashed_password: str):
        pass

    @abstractmethod
    def get(self, user_email: str) -> Union[UserEntity, None]:
        pass

    @abstractmethod
    def get_user_password(self, user_email: str) -> Union[str, None]:
        pass

    @abstractmethod
    def update(self, user_email: str, full_name: Union[str, None]):
        pass

    @abstractmethod
    def delete(self, user_email: str) -> bool:
        pass

    @abstractmethod
    def update_profile_picture(self, user_email: str, profile_picture: bytes):
        pass

    @abstractmethod
    def set_user_active(self, user_email: str):
        pass
