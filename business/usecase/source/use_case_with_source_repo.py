from abc import ABC

from business.repository.source.source_repository import SourceRepository
from business.usecase.use_case_with_domain_repo import UsecaseWithDomainRepo


class UsecaseWithSourceRepository(UsecaseWithDomainRepo, ABC):

    def __init__(self, source_repo: SourceRepository):
        super().__init__(source_repo)
        self._repo: SourceRepository = source_repo
