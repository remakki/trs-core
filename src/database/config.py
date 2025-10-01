from advanced_alchemy.config import SQLAlchemyAsyncConfig, AsyncSessionConfig

from src.config import settings

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DB_URL,
    session_config=session_config,
)
