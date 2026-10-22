from typing import List

from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo
from business.usecase.source.use_case_with_source_repo import UsecaseWithSourceRepository


class GetSourcesInfoUsecase(UsecaseWithSourceRepository):

    def execute(self) -> List[SourceInfo]:
        return self._repo.get_all_sources_info()
