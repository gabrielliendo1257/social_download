from __future__ import annotations

import asyncio
import logging

import flet as ft
from flet.core.types import FontWeight

from tm_downloader.domain.model import (
    AppContext,
    DownloadItem,
    MessageViewModel,
    DownloadJob,
)
from tm_downloader.ui.controller import DownloadController


class DownloadCardView(ft.Column):

    def __init__(
        self,
        download_item: DownloadItem,
        telegram_component: DownloadController,
    ):
        super().__init__()
        self.__telegram_component = telegram_component
        self.download_item = download_item
        self.key = download_item.job.id_job
        self.__size: int | str = (
            f"{round(download_item.data.size / 1024 / 1024, 2)} MB"
            if not download_item.data.size is None
            else "No size"
        )

        self.download_state: BaseDownloadStateView = None

        self.url_information = DownloadInformationView(
            self.download_item,
            telegram_component=self.__telegram_component,
            container_view=self,
        )
        self.download_process = DownloadProcessingView(
            self.download_item, telegram_component=self.__telegram_component
        )
        self.download_completed_view = DownloadCompletedView(
            file_name=self.download_item.data.url,
            file_size=self.download_item.data.size,
            telegram_component=self.__telegram_component,
        )

        self.controls = [
            self.url_information,
            self.download_process,
            self.download_completed_view,
        ]

    @property
    def media(self) -> DownloadItem:
        return self.download_item

    def change_state(self, state: BaseDownloadStateView):
        self.download_state = state

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

    def click_download(self, e):
        self.url_information.visible = False
        self.download_completed_view.visible = False
        self.download_process.visible = True

        url = self.url_text.value
        if url is None:
            logging.error("url value is None")
            return

        asyncio.run_coroutine_threadsafe(
            self.__telegram_component.download(
                item=self.download_item, progress_callback=self.progress_callback
            ),
            loop=AppContext.loop,
        )

        self.update()

    def cancel_download_clicked(self, e):
        pass


class BaseDownloadStateView(ft.Container):

    def __init__(self): ...


class DownloadRequestingView(ft.Container, BaseDownloadStateView):
    def __init__(self, url: str):
        super().__init__()

        self.url = url

        self.padding = 20
        self.border_radius = 20
        self.bgcolor = "#0b0f10"

        # Glow sutil amarillo (requesting)
        # self.shadow = ft.BoxShadow(
        #     blur_radius=30,
        #     spread_radius=1,
        #     color="#FFC10733"  # amber glow
        # )

        self.content = ft.Column(
            controls=[
                # URL (igual que tus cards)
                ft.Text(
                    self.url, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
                ),
                # Barra indeterminada (REQUESTING)
                ft.ProgressBar(
                    value=None,  # <- clave: indeterminado
                    color=ft.Colors.AMBER_400,
                    bgcolor="#1a1f21",
                ),
                # Estado + acciones
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.CLOUD_SYNC, color=ft.Colors.AMBER_400),
                                ft.Text(
                                    "Solicitando información...",
                                    size=12,
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                        ),
                        # acciones (cancelar request)
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Cancelar",
                        ),
                    ],
                ),
            ],
            spacing=15,
        )


class DownloadInformationView(ft.Container, BaseDownloadStateView):
    def __init__(
        self,
        item_information: DownloadItem,
        telegram_component: DownloadController | None = None,
        container_view: DownloadCardView | None = None,
    ):
        super().__init__()
        self.__telegram_component = telegram_component
        self.__item_information = item_information
        self.__container_view = container_view

        self.visible = True
        self.padding = 40
        self.margin = ft.Margin(top=0, bottom=10, right=0, left=0)
        self.border_radius = 20
        self.bgcolor = "#0b0f10"
        # self.shadow = ft.BoxShadow(
        #     blur_radius=10, spread_radius=2, color="rgba(0,0,0,0.15)"
        # )

        self.url_text = ft.Text(
            item_information.data.url, size=14, color=ft.Colors.BLUE_400
        )
        self.size: str = (
            f"{round(item_information.data.size / 1024 / 1024, 2)} MB"
            if not item_information.data.size is None
            else "No size"
        )
        self.content = ft.Column(
            spacing=5,
            controls=[
                ft.Text(item_information.data.url, size=16, weight=FontWeight.BOLD),
                self.url_text,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            str(item_information.data.date),
                            size=13,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(self.size, size=13, color=ft.Colors.GREY_600),
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
        )

    async def click_download(self, e):
        assert self.__container_view is not None, ""
        self.__container_view.click_download(e)

        url = self.url_text.value
        if url is None:
            logging.error("url value is None")
            return

        asyncio.run_coroutine_threadsafe(
            self.__telegram_component.download(
                item=self.download_item, progress_callback=self.progress_callback
            ),
            loop=AppContext.loop,
        )

        self.update()


class DownloadProcessingView(ft.Container, BaseDownloadStateView):

    def __init__(
        self,
        item_information: DownloadItem,
        telegram_component: DownloadController | None = None,
        container_view: DownloadCardView | None = None,
    ):
        super().__init__()
        self.visible = False
        self.padding = 40
        self.margin = ft.Margin(top=0, bottom=10, right=0, left=0)
        self.border_radius = 20
        self.bgcolor = "#0b0f10"
        # self.shadow = ft.BoxShadow(
        #     blur_radius=10, spread_radius=2, color="rgba(0,0,0,0.15)"
        # )
        self.pb = ft.ProgressBar(width=500)
        self.content = ft.Column(
            controls=[
                ft.Text(item_information.data.url, size=16, weight=FontWeight.BOLD),
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
        )

    def cancel_download_clicked(self, e): ...


class DownloadCompletedView(ft.Container, BaseDownloadStateView):

    def __init__(
        self,
        telegram_component: DownloadController | None = None,
        container_view: DownloadCardView | None = None,
        file_name: str = None,
        file_size: str = None,
        on_close=None,
        on_open=None,
    ):
        super().__init__()

        self.__telegram_component = telegram_component
        self.__container_view = container_view
        self.file_name = file_name
        self.file_size = file_size
        self.on_close = on_close
        self.on_open = on_open

        self.padding = 40
        self.margin = ft.Margin(top=0, bottom=10, right=0, left=0)
        self.border_radius = 20
        self.bgcolor = "#0b0f10"

        self.alignment = ft.alignment.center
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
            controls=[
                ft.Text(f"Archivo: {self.file_name}", size=16),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Botones de acción
        buttons = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
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
        )

        # Decoración visual
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    controls=[
                        icon,
                        ft.Column(
                            controls=[title, details],
                            spacing=20,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ]
                ),
                buttons,
            ],
        )

    def on_close_windows_finished(self, event) -> None:
        self.visible = False

        self.update()


class DownloadFailedView(ft.Container):
    def __init__(self, url: str, error_message: str = "Error en la descarga"):
        super().__init__()

        self.url = url
        self.error_message = error_message

        self.padding = 20
        self.border_radius = 20
        self.bgcolor = "#0b0f10"

        # Glow rojo (estado de error)
        self.shadow = ft.BoxShadow(blur_radius=30, spread_radius=1, color="#ff525233")

        self.content = ft.Column(
            spacing=15,
            controls=[
                # URL
                ft.Text(
                    self.url, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
                ),
                # Mensaje de error
                ft.Text(self.error_message, size=12, color=ft.Colors.RED_300),
                # Fila inferior (estado + acciones)
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Estado visual
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400),
                                ft.Text(
                                    "Descarga fallida",
                                    size=12,
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                        ),
                        # Acciones
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.TextButton(
                                    "Reintentar",
                                    style=ft.ButtonStyle(color=ft.Colors.RED_200),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Eliminar",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )


class DownloadCanceledView(ft.Container):
    def __init__(self, url: str):
        super().__init__()

        self.url = url

        self.padding = 20
        self.border_radius = 20
        self.bgcolor = "#0b0f10"

        # Glow gris (estado neutral / detenido)
        self.shadow = ft.BoxShadow(blur_radius=30, spread_radius=1, color="#9e9e9e33")

        self.content = ft.Column(
            spacing=15,
            controls=[
                # URL
                ft.Text(
                    self.url, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
                ),
                # Estado cancelado
                ft.Text("Descarga cancelada", size=12, color=ft.Colors.GREY_400),
                # Fila inferior (estado + acciones)
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Indicador visual
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.CANCEL, color=ft.Colors.GREY_500),
                                ft.Text(
                                    "Proceso detenido",
                                    size=12,
                                    color=ft.Colors.GREY_500,
                                ),
                            ],
                        ),
                        # Acción principal
                        ft.TextButton(
                            "Reintentar", style=ft.ButtonStyle(color=ft.Colors.BLUE_200)
                        ),
                    ],
                ),
            ],
        )

class DownloadCompletedViewNew(ft.Container):
    def __init__(self, url: str):
        super().__init__()

        self.url = url

        self.padding = 20
        self.border_radius = 20
        self.bgcolor = "#0b0f10"

        # Glow verde (éxito)
        self.shadow = ft.BoxShadow(
            blur_radius=30,
            spread_radius=1,
            color="#4caf5033"
        )

        self.content = ft.Column(
            spacing=15,
            controls=[
                # URL
                ft.Text(
                    self.url,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),

                # Estado completado
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Indicador visual
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    color=ft.Colors.GREEN_400
                                ),
                                ft.Text(
                                    "Descarga completada",
                                    size=12,
                                    color=ft.Colors.GREY_400
                                ),
                            ]
                        ),

                        # Acción principal
                        ft.TextButton(
                            "Abrir",
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREEN_200
                            )
                        )
                    ]
                )
            ]
        )

class DownloadIdleView(ft.Container):
    def __init__(
        self,
        url: str,
        title: str = "Contenido disponible",
        file_size: str = "—",
        file_type: str = "—",
        message_preview: str = "Sin descripción"
    ):
        super().__init__()

        self.url = url
        self.title = title
        self.file_size = file_size
        self.file_type = file_type
        self.message_preview = message_preview

        self.padding = 20
        self.border_radius = 20
        self.bgcolor = "#0b0f10"

        # Glow azul (estado listo)
        self.shadow = ft.BoxShadow(
            blur_radius=30,
            spread_radius=1,
            color="#2196f333"
        )

        self.content = ft.Column(
            spacing=15,
            controls=[
                # URL
                ft.Text(
                    self.url,
                    size=14,
                    color=ft.Colors.GREY_400
                ),

                # Título / nombre del contenido
                ft.Text(
                    self.title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),

                # Metadata (más info útil)
                ft.Row(
                    spacing=20,
                    controls=[
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=16, color=ft.Colors.BLUE_300),
                                ft.Text(self.file_type, size=11, color=ft.Colors.GREY_400),
                            ]
                        ),
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(ft.Icons.DATA_USAGE, size=16, color=ft.Colors.BLUE_300),
                                ft.Text(self.file_size, size=11, color=ft.Colors.GREY_400),
                            ]
                        ),
                    ]
                ),

                # Preview del mensaje (recortado)
                ft.Text(
                    self.message_preview,
                    size=12,
                    color=ft.Colors.GREY_500,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),

                # Acciones
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Estado visual
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.START,
                                    color=ft.Colors.BLUE_400
                                ),
                                ft.Text(
                                    "Listo para descargar",
                                    size=12,
                                    color=ft.Colors.GREY_400
                                ),
                            ]
                        ),

                        # Botones de acción
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.PLAY_ARROW,
                                    icon_color=ft.Colors.BLUE_400,
                                    tooltip="Descargar"
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY,
                                    icon_color=ft.Colors.GREY_400,
                                    tooltip="Ver mensaje completo"
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Cancelar"
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Eliminar"
                                ),
                            ]
                        )
                    ]
                )
            ]
        )

if __name__ == "__main__":
    import datetime

    def prepare_gui(page: ft.Page) -> None:
        page.title = "Test"
        page.window.width = 770
        page.window.height = 770
        page.bgcolor = "#212623"
        page.padding = 20
        page.scroll = ft.ScrollMode(ft.ScrollMode.AUTO)
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        item = DownloadItem(
            data=MessageViewModel(
                url="https://telegram.org/",
                date=datetime.datetime(2020, 1, 1),
                size=1600000,
            ),
            job=DownloadJob(url="https://telegram.org/", id_job="test_id"),
            message=None,
        )

        download_requesting_view = DownloadRequestingView("https://telegram.org/")
        download_failed_view = DownloadFailedView("https://telegram.org/")
        download_canceled_view = DownloadCanceledView("https://telegram.org/")
        download_completed_view_new = DownloadCompletedViewNew("https://telegram.org/")
        download_idle_view = DownloadIdleView("https://telegram.org/", file_type="Document", file_size="1.2G")

        download_information_view = DownloadInformationView(item_information=item)
        download_processing_view = DownloadProcessingView(item_information=item)
        download_processing_view.visible = True
        download_finished_view = DownloadCompletedView(
            file_name="download_completed.txt", file_size="1.2Mb"
        )
        download_finished_view.visible = True

        main_page = ft.Column(
            controls=[
                download_information_view,
                download_processing_view,
                download_finished_view,
                download_requesting_view,
                download_failed_view,
                download_canceled_view,
                download_completed_view_new,
                download_idle_view,
            ],
        )

        page.add(main_page)
        page.update()

    ft.app(prepare_gui)
