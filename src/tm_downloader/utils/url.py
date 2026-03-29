import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Tuple, Any

from tm_downloader.domain.model import LinkType

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


async def monitor_tasks() -> None:
    while True:
        tasks = [t for t in asyncio.all_tasks() if not t.done()]
        print(f"Tareas activas: {len(tasks)}")
        for t in tasks:
            coro = t.get_coro()
            assert coro is not None, "coro is None"
            print(f" - {coro.__name__} -> {t._state}")
        await asyncio.sleep(1)


telegram_patterns = [
    (LinkType.PRIVATE, re.compile(r"^https://t\.me/c/(\d+)/(\d+)$")),
    (LinkType.RANGE, re.compile(r"^https://t\.me/c/(\d+)/(\d+)(?:-(\d+))?$")),
    (
        LinkType.PUBLIC_THREAD,
        re.compile(r"^https://t\.me/([a-zA-Z0-9_]{5,32})/(\d+)/(\d+)$"),
    ),
    (
        LinkType.RANGE,
        re.compile(r"^https://t\.me/([a-zA-Z0-9_]{5,32})/(\d+)/(\d+)(?:-(\d+))?$"),
    ),
    (LinkType.PUBLIC, re.compile(r"^https://t\.me/([a-zA-Z0-9_]{5,32})/(\d+)$")),
    (
        LinkType.RANGE,
        re.compile(r"^https://t\.me/([a-zA-Z0-9_]{5,32})/(\d+)(?:-(\d+))?$"),
    ),
    (LinkType.INVITE, re.compile(r"^https://t\.me/\+([A-Za-z0-9_-]+)$")),
    (LinkType.RANGE, re.compile(r"^https://t\.me/\+([A-Za-z0-9_-]+)(?:-(\d+))?$")),
    (LinkType.PROFILE, re.compile(r"^https://t\.me/([a-zA-Z0-9_]{5,32})$")),
    (LinkType.RANGE, re.compile(r"^https://t\.me/([a-zA-Z0-9_]{5,32})(?:-(\d+))?$")),
]


@dataclass
class ParserResult:
    link_type: LinkType
    groups: Tuple[Any, ...]


def parse_telegram_url(url: str):
    for link_type, pattern in telegram_patterns:
        m = pattern.match(url)
        if m:
            return ParserResult(link_type, m.groups())
    return None

def expand_range_url(url: str) -> list[str]:
    match = re.match(r"(https://t\.me/(?:c/)?[^/]+/)(\d+)-(\d+)$", url)

    if not match:
        raise ValueError("URL no contiene un rango válido")

    base, start, end = match.groups()

    start, end = int(start), int(end)
    print(f"Start {start}, end {end}")

    if start > end:
        raise ValueError("Rango inválido: start > end")

    return [f"{base}{i}" for i in range(start, end + 1)]



def expand_telegram_media_url(url: str):
    
    if re.match(r"https://t\.me/\+", url):
        return None

    patterns = [
        r"(https://t\.me/(?:c/)?[^/]+/\d+/)(\d+)-(\d+)$",
        r"(https://t\.me/(?:c/)?[^/]+/)(\d+)-(\d+)$",
        r"(https://t\.me/(?:c/)?[^/]+/\d+/)(\d+)$",
        r"(https://t\.me/(?:c/)?[^/]+/)(\d+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if not match:
            continue

        groups = match.groups()

        if len(groups) == 3:
            base, start, end = groups
            start, end = int(start), int(end)
            print(f"start {start}, end {end}")

            if start > end:
                raise ValueError("Rango inválido")

            return [f"{base}{i}" for i in range(start, end + 1)]

        elif len(groups) == 2:
            base, msg_id = groups
            return [f"{base}{msg_id}"]

    logging.warning("Pattern url not supported")
    return None


if __name__ == "__main__":
    # print(parse_telegram_url("https://t.me/Curso_vip/140927/140930-150051"))
    # print(parse_telegram_url("https://t.me/Curso_vip/140927/140930"))
    # print(parse_telegram_url("https://t.me/c/3692335392/1564-8000"))
    # print(parse_telegram_url("https://t.me/c/2066575278/6494"))
    # print(parse_telegram_url("https://t.me/androforever_oficial/13690"))

    print("Expand")
    print(expand_telegram_media_url("https://t.me/Curso_vip/140927/150040-150051"))
    print(expand_telegram_media_url("https://t.me/Curso_vip/140927/150040"))
