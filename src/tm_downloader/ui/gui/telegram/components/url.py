from __future__ import annotations

import asyncio
from typing import Callable

import flet as ft
from flet.core.types import FontWeight

from tm_downloader.domain.model import (
    AppContext,
    DownloadItem,
    MessageViewModel,
    DownloadJob,
    DownloadState,
)
from tm_downloader.ui.controller import DownloadController


class DownloadCardView(ft.Container):

    def __init__(
        self,
        download_item: DownloadItem,
        telegram_component: DownloadController,
    ):
        super().__init__()
        self.__telegram_component = telegram_component
        self.download_item = download_item
        self._context = None

        self.key = download_item.job.id_job

        self.__size: int | str = (
            f"{round(download_item.data.size / 1024 / 1024, 2)} MB"
            if not download_item.data.size is None
            else "No size"
        )

        self.download_idle_view = DownloadIdleView(
            file_type="Document",
            item_information=self.download_item,
            telegram_component=self.__telegram_component,
            view_context=self,
        )
        self.download_state = self.download_idle_view
        self.content = self.download_state

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def media(self) -> DownloadItem:
        return self.download_item

    def change_state(self, state: BaseDownloadStateView):
        self.download_state = state
        self.download_state.context = self
        self.content = state
        from tm_downloader.ui.gui.telegram.main_page import TelegramGui

        assert isinstance(self._context, TelegramGui), "_context is not TelegramGui"
        state.show()  # Action service
        self._context.update()

    def click_download(
        self, item_information: DownloadItem, progress_callback: Callable
    ):
        assert isinstance(self.download_state, DownloadProcessingViewNew) or isinstance(
            self.download_state, DownloadProcessingView
        ), "Download state is not a DownloadProcessingView"
        asyncio.run_coroutine_threadsafe(
            self.__telegram_component.download(
                item=item_information,
                progress_callback=progress_callback,
                file=item_information.data.file
            ),
            loop=AppContext.loop,
        )

    def cancel_download_clicked(self, e):
        pass

    def close_card_view(self, e):
        self.content = None
        self.update()
        self._context.update()


class BaseDownloadStateView(ft.Container):
    """Configuracion base para componentes de url"""

    def __init__(self):
        super().__init__()
        self.state: DownloadState = DownloadState.FAILED
        self.padding = 20
        self.border_radius = 20
        self.bgcolor = "#0b0f10"
        self.margin = ft.Margin(top=0, bottom=10, right=0, left=0)
        self._context = None

    def show(self): ...

    @property
    def context(self) -> DownloadCardView:
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    async def click_cancel(self, e): ...

    async def click_delete_view(self, e):
        assert isinstance(self._context, DownloadCardView)
        self._context.close_card_view()

    async def click_paused(self, e): ...

    async def click_retrie(self, e): ...

    async def click_open_source(self, e): ...

    async def click_view_message(self): ...


class DownloadRequestingView(BaseDownloadStateView):
    def __init__(
        self,
        item_information: DownloadItem | None = None,
        telegram_component: DownloadController | None = None,
    ):
        super().__init__()
        self.state: DownloadState = DownloadState.PROCESSING
        self.__telegram_component = telegram_component
        self.item_information = item_information
        self.url = item_information.data.url

        self.progress = ft.ProgressBar(
            value=None,  # <- clave: indeterminado
            color=ft.Colors.AMBER_400,
            bgcolor="#1a1f21",
        )
        self.request_info = ft.Text(
            "Solicitando información...",
            size=12,
            color=ft.Colors.GREY_400,
        )
        self.content = ft.Column(
            controls=[
                # URL (igual que tus cards)
                ft.Text(
                    self.url, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
                ),
                # Barra indeterminada (REQUESTING)
                self.progress,
                # Estado + acciones
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.CLOUD_SYNC, color=ft.Colors.AMBER_400),
                                self.request_info,
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

    async def click_cancel(self, e): ...


class DownloadProcessingViewNew(BaseDownloadStateView):

    def __init__(
        self,
        item_information: DownloadItem,
        telegram_component: DownloadController | None = None,
    ):
        super().__init__()
        self.__telegram_component = telegram_component
        self.item_information = item_information
        self.url = item_information.data.url

        self.filename = item_information.data.filename

        self.file_type = "Document"

        self.progress = ft.ProgressBar(
            value=None,
            color=ft.Colors.AMBER_400,
            bgcolor="#1a1f21",
        )
        self.file_size = (
            f"{round(item_information.data.size / 1024 / 1024, 2)} MB"
            if item_information.data.size
            else "0 MB"
        )
        self.currently_downloaded = ft.Text(
            "0 MB",
            size=12,
            color=ft.Colors.GREY_400,
        )
        self.request_info = ft.Text(
            "Descargando...",
            size=12,
            color=ft.Colors.GREY_400,
        )
        self.content = ft.Column(
            controls=[
                # URL
                ft.Text(self.url, size=14, color=ft.Colors.GREY_400),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Título / nombre del contenido
                        ft.Text(
                            self.filename,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        self.currently_downloaded
                    ]
                ),
                self.progress,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.CLOUD_SYNC, color=ft.Colors.AMBER_400),
                                self.request_info,
                            ],
                        ),
                        # Metadata
                        ft.Row(
                            spacing=20,
                            controls=[
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.INSERT_DRIVE_FILE,
                                            size=16,
                                            color=ft.Colors.BLUE_300,
                                        ),
                                        ft.Text(
                                            self.file_type,
                                            size=11,
                                            color=ft.Colors.GREY_400,
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.DATA_USAGE,
                                            size=16,
                                            color=ft.Colors.BLUE_300,
                                        ),
                                        ft.Text(
                                            self.file_size,
                                            size=11,
                                            color=ft.Colors.GREY_400,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.PAUSE,
                                    icon_color=ft.Colors.GREEN_400,
                                    tooltip="Pausar",
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Cancelar",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            spacing=15,
        )

    def progress_callback(self, current: int, total: int) -> None:
        if current == total:
            self._context.change_state(
                state=DownloadCompletedViewNew(
                    item_information=self.item_information,
                    telegram_component=self.__telegram_component,
                )
            )
        else:
            self.progress.value = current / total
            self.currently_downloaded.value = (
                f"{round(current / 1024 / 1024, 2)} MB"
                if current
                else "0 MB"
            )
            self.update()

    def show(self):
        self._context.click_download(
            item_information=self.item_information,
            progress_callback=self.progress_callback,
        )


class DownloadProcessingView(BaseDownloadStateView):

    def __init__(
        self,
        item_information: DownloadItem,
        telegram_component: DownloadController | None = None,
    ):
        super().__init__()
        self.state = DownloadState.PROCESSING

        self.item_information = item_information
        self.__telegram_component = telegram_component

        self.url = item_information.data.url

        self.pb = ft.ProgressBar(width=500)
        self.content = ft.Column(
            controls=[
                ft.Text(self.url, size=16, weight=FontWeight.BOLD),
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
                            on_click=self.click_cancel,
                        ),
                    ],
                ),
            ],
        )

    def progress_callback(self, current: int, total: int) -> None:
        if current == total:
            self._context.change_state(
                state=DownloadCompletedViewNew(
                    item_information=self.item_information,
                    telegram_component=self.__telegram_component,
                )
            )
        else:
            self.pb.value = current / total
            self.update()

    async def click_cancel(self, e): ...

    async def click_paused(self, e): ...

    def show(self):
        self._context.click_download(
            item_information=self.item_information,
            progress_callback=self.progress_callback,
        )


class DownloadFailedView(BaseDownloadStateView):
    def __init__(self, url: str, error_message: str = "Error en la descarga"):
        super().__init__()
        self.state = DownloadState.FAILED
        self.url = url
        self.error_message = error_message

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

    async def click_delete_view(self, e): ...

    async def click_retrie(self, e): ...


class DownloadCanceledView(BaseDownloadStateView):
    def __init__(self, url: str):
        super().__init__()
        self.state = DownloadState.CANCELLED
        self.url = url
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

    async def click_retrie(self, e): ...

    async def click_delete_view(self, e): ...


class DownloadCompletedViewNew(BaseDownloadStateView):
    def __init__(
        self,
        item_information: DownloadItem | None = None,
        telegram_component: DownloadController | None = None,
    ):
        super().__init__()
        self.state = DownloadState.COMPLETED
        self.__telegram_component = telegram_component
        self.url = item_information.data.url
        self.filename = item_information.data.filename

        # Glow verde (éxito)
        #self.shadow = ft.BoxShadow(blur_radius=30, spread_radius=1, color="#4caf5033")

        self.content = ft.Column(
            spacing=15,
            controls=[
                # URL
                ft.Text(
                    self.filename, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
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
                                    ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400
                                ),
                                ft.Text(
                                    "Descarga completada",
                                    size=12,
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                        ),
                        # Acción principal
                        ft.TextButton(
                            "Abrir", style=ft.ButtonStyle(color=ft.Colors.GREEN_200)
                        ),
                    ],
                ),
            ],
        )

    async def click_delete_view(self, e):
        isinstance(self._context, DownloadCardView)
        self._context.close_card_view()

    async def click_open_source(self, e): ...


class DownloadIdleView(BaseDownloadStateView):
    def __init__(
        self,
        file_type: str = "—",
        item_information: DownloadItem | None = None,
        telegram_component: DownloadController | None = None,
        view_context: DownloadCardView | None = None,
    ):
        super().__init__()
        self.state = DownloadState.IDLE
        self.__telegram_component = telegram_component
        self.item_information = item_information
        self.view_context = view_context

        self.message_preview = item_information.data.message if item_information.data.message else "Empty message"
        self.url = item_information.data.url
        self.filename = item_information.data.filename
        self.file_size = (
            f"{round(item_information.data.size / 1024 / 1024, 2)} MB"
            if not item_information.data.size is None
            else "No size"
        )
        self.file_type = file_type

        self.content = ft.Column(
            spacing=15,
            controls=[
                # URL
                ft.Text(self.url, size=14, color=ft.Colors.GREY_400),
                # Título / nombre del contenido
                ft.Text(
                    self.filename,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                # Metadata (más info útil)
                ft.Row(
                    spacing=20,
                    controls=[
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(
                                    ft.Icons.INSERT_DRIVE_FILE,
                                    size=16,
                                    color=ft.Colors.BLUE_300,
                                ),
                                ft.Text(
                                    self.file_type, size=11, color=ft.Colors.GREY_400
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(
                                    ft.Icons.DATA_USAGE,
                                    size=16,
                                    color=ft.Colors.BLUE_300,
                                ),
                                ft.Text(
                                    self.file_size, size=11, color=ft.Colors.GREY_400
                                ),
                            ],
                        ),
                    ],
                ),
                # Preview del mensaje (recortado)
                ft.Text(
                    self.message_preview,
                    size=12,
                    color=ft.Colors.GREY_500,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                # Acciones
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Estado visual
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.START, color=ft.Colors.BLUE_400),
                                ft.Text(
                                    "Listo para descargar",
                                    size=12,
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                        ),
                        # Botones de acción
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.PLAY_ARROW,
                                    icon_color=ft.Colors.BLUE_400,
                                    tooltip="Descargar",
                                    on_click=self.click_download,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY,
                                    icon_color=ft.Colors.GREY_400,
                                    tooltip="Ver mensaje completo",
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Cancelar",
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Eliminar",
                                    on_click=self.view_context.close_card_view,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    async def click_download(self, e):
        process_view = DownloadProcessingViewNew(
            item_information=self.item_information,
            telegram_component=self.__telegram_component,
        )
        self.view_context.change_state(state=process_view)

    async def click_cancel(self, e): ...

    async def click_view_message(self): ...


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

        download_requesting_view = DownloadRequestingView(item_information=item)
        download_failed_view = DownloadFailedView("https://telegram.org/")
        download_canceled_view = DownloadCanceledView("https://telegram.org/")
        download_completed_view_new = DownloadCompletedViewNew(item_information=item)
        download_idle_view = DownloadIdleView(item_information=item)

        download_processing_view = DownloadProcessingView(item_information=item)
        download_processing_view.visible = True

        main_page = ft.Column(
            controls=[
                download_processing_view,
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
