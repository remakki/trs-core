from src.database.config import sqlalchemy_config
from src.sources import SourceService


async def get_source_service() -> SourceService:
    async with SourceService.new(config=sqlalchemy_config) as service:
        return service
