from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from .models import SourceModel


class SourceRepository(SQLAlchemyAsyncRepository[SourceModel]):
    """Source repository"""

    model_type = SourceModel
