from advanced_alchemy import service

from .models import SourceModel
from .repositories import SourceRepository


class SourceService(service.SQLAlchemyAsyncRepositoryService[SourceModel, SourceRepository]):
    """Source Service"""

    repository_type = SourceRepository

    def __init__(self, session, **kwargs):
        kwargs.setdefault("auto_commit", True)
        super().__init__(session=session, **kwargs)

    async def get_active_sources(self) -> list[SourceModel]:
        return list(
            await self.list(
                SourceModel.is_active.is_(True),
                SourceModel.deleted_at.is_(None),
            )
        )
