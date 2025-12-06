import asyncio

from src.mq import RabbitMQ
from src.source_processing.service import SourceProcessing
from src.sources.dependencies import get_source_service


async def main():
    source_service = await get_source_service()
    sources = await source_service.get_active_sources()

    while not sources:
        await asyncio.sleep(60)
        sources = await source_service.get_active_sources()

    async with RabbitMQ() as mq:
        objects = [SourceProcessing(source, mq) for source in sources]
        tasks = [asyncio.create_task(obj.process()) for obj in objects]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            for task in tasks:
                task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
