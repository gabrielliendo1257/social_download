import asyncio
import threading
from concurrent.futures import Future
from typing import Callable, Coroutine, Any


class Runtime:
    def __init__(self):
        self.loop = asyncio.new_event_loop()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def consume_async_generator(self, agent, callback: Callable[..., ...]):
        async for item in agent:
            callback(item)

    def submit(self, coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        return asyncio.run_coroutine_threadsafe(coro, self.loop)
