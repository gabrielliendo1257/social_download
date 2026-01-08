import threading

import flet as ft
from flet.core.types import FontWeight

from tm_downloader.infrastructure.controller import TelegramController
from tm_downloader.domain.models.media import MediaBase, DownloaderStatus
from tm_downloader.presentation.gui.telegram.components.downloader import DownloadCompletedView


class UriInformation(ft.Column):

    def __init__(self, media: MediaBase, controller: TelegramController):
        super().__init__()
        self.__controller = controller
        self.__status: DownloaderStatus = DownloaderStatus.NO_INITIALIZED
        self.__media: MediaBase = media
        self.__size: int = f"{round(media.size / 1024 / 1024, 2)} MB" if not media.size is None else "No size"

        self.url_text = ft.Text(media.uri, size=12, color=ft.Colors.BLUE_400)
        self.pb = ft.ProgressBar(width=500)
        self.download_process = ft.Container(
            visible=False,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(media.caption, size=16, weight=FontWeight.BOLD),
                    self.pb,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.PAUSE,
                                tooltip="Pause",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CANCEL,
                                tooltip="Cancel",
                                on_click=self.cancel_download_clicked
                            ),
                        ],
                    ),
                ]
            )
        )
        self.download_completed_view = DownloadCompletedView(self.__media.caption, self.__media.size)
        self.url_information = ft.Container(
            visible=True,
            padding=10,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(media.caption, size=16, weight=FontWeight.BOLD),
                    self.url_text,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(str(media.date), size=12, color=ft.Colors.GREY_600),
                            ft.Text(self.__size, size=12, color=ft.Colors.GREY_600),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.CREATE_OUTLINED,
                                tooltip="Editar",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar",
                                icon_color=ft.Colors.RED,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Descargar",
                                on_click=self.init_download_clicked,
                            ),
                        ],
                    ),
                ],
            ),
        )

        self.controls = [
            self.url_information, self.download_process, self.download_completed_view
        ]

    @property
    def media(self) -> MediaBase:
        return self.__media

    @property
    def status(self) -> DownloaderStatus:
        return self.__status

    @status.setter
    def status(self, status: DownloaderStatus):
        self.__status = status

    def progress_callback(self, current: int, total: int) -> None:
        async def update_ui():
            if current == total:
                self.__status = DownloaderStatus.FINISHED

                self.download_completed_view.visible = True
                self.download_process.visible = False
                self.url_information.visible = False

                if self.download_process in self.controls:
                    self.controls.remove(self.download_process)
                if self.url_information in self.controls:
                    self.controls.remove(self.url_information)

            self.pb.value = current / total
            self.update()

        self.page.run_task(update_ui)

    def init_download_clicked(self, e):
        self.url_information.visible = False
        self.download_completed_view.visible = False
        self.download_process.visible = True

        future = self.__controller.download_video(
            url_media=self.url_text.value,
            progress_callback=self.progress_callback
        )

        threading.Thread(target=lambda: future.result()).start()

        self.update()

    def cancel_download_clicked(self, e):
        self.url_information.visible = True
        self.download_process.visible = False
        self.download_completed_view.visible = False

        self.update()
