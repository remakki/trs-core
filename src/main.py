import asyncio

from src.flow_processing.service import FlowProcessing
from src.mq import RabbitMQ


async def main():
    flows = [
        {
            "id": "bbc",
            "title": "BBC News",
            "archive_url": "https://news.mediacdn.ru/bbc_rec",
            "archive_token": "media5c0p",
            "channel": "@syn_trs_demo",
        }
    ]

    async with RabbitMQ() as mq:
        objects = [FlowProcessing(flow, mq) for flow in flows]

        async with asyncio.TaskGroup() as tg:
            for obj in objects:
                tg.create_task(obj.process())


if __name__ == "__main__":
    asyncio.run(main())
