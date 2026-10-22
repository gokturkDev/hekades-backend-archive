from abc import ABC

from business.repository.base_repository import BaseRepository
from business.usecase.base_use_case import BaseUsecase


class UsecaseWithDomainRepo(BaseUsecase, ABC):
    def __init__(self, domain_repo: BaseRepository):
        self._repo: BaseRepository = domain_repo
