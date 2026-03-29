import pytest

from tm_downloader.telegram.auth_manager import AuthManager
from tm_downloader.telegram.download_manager import DownloadManager
from tm_downloader.telegram.runtime import Runtime
from tm_downloader.ui.controller import DownloadController


@pytest.fixture(scope="session")
def download_controller():
    runtime = Runtime()
    runtime.start()

    auth = AuthManager()

    future = runtime.submit(auth.connecting())

    download_manager = DownloadManager(future.result())
    yield DownloadController(runtime, download_manager)

    runtime.stop()
