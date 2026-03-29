from telethon.tl.types import Message

from tm_downloader.ui.controller import DownloadController


def test_download(download_controller: DownloadController):
    future = download_controller.download_unit(
        "https://t.me/c/3353920644/12663", file="/home/backdev"
    )
    path_saved = future.result()
    assert isinstance(path_saved, str)
    assert path_saved.startswith("/home/backdev")


def test_request(download_controller: DownloadController):
    future = download_controller.request_information_unit(
        "https://t.me/c/3353920644/12663"
    )
    message = future.result()  # pyright: ignore[reportAny]

    assert isinstance(message, Message)


def test_request_range(download_controller: DownloadController):
    def callback(item) -> None:
        assert isinstance(item, Message)

    future = download_controller.request_information_range(
        "https://t.me/c/3353920644/12658-12663", callback
    )
    messages = future.result()

    assert messages is None


def test_download_range(download_controller: DownloadController):
    def callback(item) -> None:
        assert isinstance(item, int)

    future = download_controller.download_range(
        "https://t.me/c/3353920644/12836-12867",
        callback_done=callback,
        file="/home/backdev/Pictures/",
    )
    future.result()
