import asyncio
import logging

import flet as ft
from flet.core.types import FontWeight

from tm_downloader.domain.model import AppContext, DownloadItem
from tm_downloader.ui.controller import DownloadController


class UrlCardStateView(ft.Column):

    def __init__(
        self,
        download_item: DownloadItem,
        download_controller: DownloadController,
    ):
        super().__init__()
        self.__download_controller = download_controller
        self.download_item = download_item
        self.key = download_item.job.id_job
        self.__size: int | str = (
            f"{round(download_item.data.size / 1024 / 1024, 2)} MB"
            if not download_item.data.size is None
            else "No size"
        )

        self.url_text = ft.Text(
            download_item.data.url, size=12, color=ft.Colors.BLUE_400
        )
        self.pb = ft.ProgressBar(width=500)
        self.download_process = ft.Container(
            visible=False,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(download_item.data.url, size=16, weight=FontWeight.BOLD),
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
                                on_click=self.cancel_download_clicked,
                            ),
                        ],
                    ),
                ],
            ),
        )

        self.download_completed_view = UrlCardDownloadCompletedView(
            self.download_item.data.url, self.download_item.data.size
        )

        self.url_information = ft.Container(
            visible=True,
            padding=10,
            bgcolor="#262525",
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(download_item.data.url, size=16, weight=FontWeight.BOLD),
                    self.url_text,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                str(download_item.data.date),
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
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
                                on_click=self.click_download,
                            ),
                        ],
                    ),
                ],
            ),
        )

        self.controls = [
            self.url_information,
            self.download_process,
            self.download_completed_view,
        ]

    @property
    def media(self) -> DownloadItem:
        return self.download_item

    def progress_callback(self, current: int, total: int) -> None:
        if current == total:
            self.show_download_state_finished()
        else:
            self.pb.value = current / total
            self.update()

    def show_download_state_finished(self):
        self.download_completed_view.visible = True
        self.download_process.visible = False
        self.url_information.visible = False

        self.update()

    async def click_download(self, e):
        self.url_information.visible = False
        self.download_completed_view.visible = False
        self.download_process.visible = True

        url = self.url_text.value
        if url is None:
            logging.error("url value is None")
            return

        asyncio.run_coroutine_threadsafe(
            self.__download_controller.download_new(
                item=self.download_item, progress_callback=self.progress_callback
            ),
            loop=AppContext.loop,
        )

        self.update()

    def cancel_download_clicked(self, e):
        pass


class UrlInformationView(ft.Column):
    def __init__(self):
        self.__init__()


class UrlCardDownloadCompletedView(ft.Column):
    def __init__(self, file_name: str, file_size: str, on_close=None, on_open=None):
        super().__init__()

        self.file_name = file_name
        self.file_size = file_size
        self.on_close = on_close
        self.on_open = on_open

        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        self.visible = False

        # Icono grande de éxito
        icon = ft.Icon(name=ft.Icons.CHECK_CIRCLE_OUTLINED, color="green", size=80)

        # Título principal
        title = ft.Text(
            "Descarga completada",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="green",
        )

        # Detalles del archivo descargado
        details = ft.Column(
            [
                ft.Text(f"Archivo: {self.file_name}", size=16),
                # ft.Text(f"Tamaño: {round(int(self.file_size) / 1024 / 1024, 2)} MB", size=12, color=ft.Colors.GREY_600),
                # ft.Text(f"Tamaño: {self.file_size}", size=14, color=ft.Colors.GREY),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Botones de acción
        buttons = ft.Row(
            [
                ft.ElevatedButton(
                    text="Abrir archivo",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=self.on_open,
                ),
                ft.OutlinedButton(
                    text="Cerrar",
                    icon=ft.Icons.CLOSE,
                    on_click=self.on_close_windows_finished,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Decoración visual
        card = ft.Container(
            content=ft.Column(
                [icon, title, details, buttons],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=40,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.GREEN_200),
            shadow=ft.BoxShadow(
                blur_radius=10, spread_radius=2, color="rgba(0,0,0,0.15)"
            ),
        )

        self.controls = [card]

    def on_close_windows_finished(self, event) -> None:
        self.visible = False
        self.controls.clear()

        self.update()
