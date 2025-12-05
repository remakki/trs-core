from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy.orm import Mapped

from src.database.soft_delete_mixin import SoftDeleteMixin


class SourceModel(SoftDeleteMixin, BigIntAuditBase):
    """Source model."""

    __tablename__ = "sources"

    title: Mapped[str]
    archive_url: Mapped[str]
    archive_token: Mapped[str]
    is_active: Mapped[bool]
    language: Mapped[str] # ru, en ...
    chat_id: Mapped[str]
