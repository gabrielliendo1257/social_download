import asyncio
from typing import List


class DownloadQueue:
    def __init__(self, workers=3):
        self.queue = asyncio.Queue(maxsize=20)
        self.workers = workers

    async def put(self, item: object):
        if isinstance(item, List):
            for it in item:
                await self.queue.put(it)

            for _ in range(self.workers):
                await self.queue.put(None)
        else:
            await self.queue.put(item)


class QueuePolicy: ...
