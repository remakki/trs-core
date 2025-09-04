from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext

from src.config import settings


class RabbitMQ:
    def __init__(self):
        self._broker = RabbitBroker(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            security=SASLPlaintext(
                username=settings.RABBITMQ_USERNAME,
                password=settings.RABBITMQ_PASSWORD,
            ),
        )

    async def __aenter__(self) -> RabbitBroker:
        await self._broker.start()
        return self._broker

    async def __aexit__(self, exc_type, exc, tb):
        await self._broker.stop(exc_type, exc, tb)
