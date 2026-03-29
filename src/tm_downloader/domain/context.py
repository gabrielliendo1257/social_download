import asyncio
import logging
from typing import Callable

from telethon import TelegramClient

from tm_downloader.domain.model import AppContext, Client, ContextPlatform, DownloadItem, IResolver
from tm_downloader.telegram.service import TelegramService
from tm_downloader.utils.url import parse_telegram_url


class DefaultContext(IResolver):
    def resolve(self, url: str) -> ContextPlatform | None:
        logging.info("DefaultContext is active")
        logging.warning(f"Url {url} not supported.")
        return None


class AbstractPlatformResolveContext(IResolver):

    def __init__(self, wrapper: IResolver):
        self.wrapper = wrapper

    def resolve(self, url: str) -> ContextPlatform | None:
        return self.wrapper.resolve(url)


class TelegramContext(AbstractPlatformResolveContext):

    def resolve(self, url: str) -> ContextPlatform | None:
        if parse_telegram_url(url) is None:
            return self.wrapper.resolve(url)
        client = AppContext.clients.get(Client.telegram)
        assert isinstance(client, TelegramClient)
        return ContextPlatform(
            url=url,
            connection=client,
            loop=AppContext.loop,
            service=TelegramService(client=client),
        )


def resolve_context(func) -> Callable:
    async def wrapper(*args, **kwargs) -> ContextPlatform | None:
        assert AppContext.resolver is not None, "resolver is None"
        param_item = kwargs.get("item")
        param_url = kwargs.get("url")
        if param_item is not None and param_url is None:
            assert isinstance(param_item, DownloadItem), "item not is instance of DownloadItem"
            param_url = param_item.job.url
        assert isinstance(param_url, str), "url is None, not resolve"
        try:
            context_platform = AppContext.resolver.resolve(url=param_url)
        except ValueError:
            return None
        assert context_platform is not None, "context_platform is None"
        assert context_platform.loop is not None, "loop is None"
        func_result = await func(ctx=context_platform, *args, **kwargs)
        return func_result

    return wrapper


if __name__ == "__main__":
    from tm_downloader.app import AppBootstrap

    app_bootstrap: AppBootstrap | None = None
    if app_bootstrap is None:
        app_bootstrap = AppBootstrap()
        logging.info(f"Loop: {app_bootstrap.loop}")
        asyncio.run(app_bootstrap.start())

    @resolve_context
    async def test(ctx: ContextPlatform | None = None, url: str | None = None):
        assert url is not None, "Parameter url is required"
        assert ctx is not None, "context is None"
        assert ctx.service is not None, "service is None"
        # message = await ctx.service.request_information(url)
        logging.info(f"Context: {ctx.__dict__}")
        # logging.info(f"Message: {message}")

    # test(url="https://t.me/Curso_vip/140927/140930-150051")
    assert AppContext.loop is not None, "loop is None"
    try:
        asyncio.run(test(url="https://t.me/Curso_vip/140927/140930"))
        tasks = asyncio.all_tasks(AppContext.loop)
        logging.info(f"Tasks: {tasks}")
    except Exception as ex:
        logging.exception(ex)
        # wait = [asyncio.wait_for(tp, 3) for tp in tasks]
        # asyncio.gather(*wait)
