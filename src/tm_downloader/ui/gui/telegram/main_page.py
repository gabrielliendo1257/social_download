import asyncio
import logging
import flet as ft
from flet.core.types import FontWeight
from telethon import TelegramClient

from tm_downloader.app import AppBootstrap
from tm_downloader.domain.model import (
    AbstractUI,
    AppContext,
    Client,
    DownloadItem,
)
from tm_downloader.telegram.download_manager import DownloadManager
from tm_downloader.ui.controller import (
    DownloadController,
)
from tm_downloader.ui.gui.telegram.components.file_picker import FilePickerComponent
from tm_downloader.ui.gui.telegram.components.url import DownloadCardView


class TelegramGui(ft.Column, AbstractUI):
    """Management de componentes ui, dentro del contexto de telegram"""
    def __init__(self):
        super().__init__()
        self.download_controller = None

        self.height = 600

        self.__file_picker = FilePickerComponent()
        self.selected_path = ft.Text(
            "Ninguna carpeta seleccionada", size=13, color=ft.Colors.GREY_400
        )

        # URL component
        self.add_type_url_component = ft.TextField(
            hint_text="Pega la URL o rango de URLs...", expand=True, autofocus=True
        )
        self._button_add_url_component = ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Row(
                    controls=[
                        self.add_type_url_component,
                        # self.__file_picker,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            tooltip="Agregar URL",
                            on_click=self.click_add_url,
                        ),
                    ]
                ),
            )
        )

        # VIDEO QUEUE
        self.video_queue = ft.ListView(
            height=500, expand=True, spacing=10, padding=10, auto_scroll=True
        )
        self._attribute_download_view = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Videos en cola", size=16, weight=FontWeight.BOLD),
                        self.__file_picker,
                        ft.IconButton(
                            icon=ft.Icons.FOLDER_OPEN,
                            tooltip="Carpeta de descargas",
                            # on_click=self.choose_folder,
                        ),
                    ],
                ),
                self.video_queue,
            ]
        )

        # PROGRESS CONEcTION
        self._progres_connect = ft.Column(
            [ft.ProgressRing(), ft.Text("Connecting...")],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            # height=self.page.window.height
        )

        self.main_page = ft.Column(
            controls=[self._button_add_url_component, self._attribute_download_view],
            expand=True,
        )

        self.main_page.visible = False

        self.controls = [self._progres_connect, self.main_page]

    def did_mount(self):
        def on_show_page():
            self.main_page.visible = True
            self._progres_connect.visible = False

            self.update()

        def on_show_error():
            self.main_page.visible = False
            self._progres_connect.visible = True

            self.update()

        self.main_page.visible = False
        self._progres_connect.visible = True

        app_bootstrap: AppBootstrap | None = None
        if app_bootstrap is None:
            app_bootstrap = AppBootstrap()
            logging.info(f"Loop: {app_bootstrap.loop}")
            asyncio.run_coroutine_threadsafe(
                app_bootstrap.start(), loop=app_bootstrap.loop
            ).result()

        if isinstance(AppContext.clients.get(Client.telegram), TelegramClient):
            download_manager = DownloadManager(AppContext.clients.get(Client.telegram))
            self.download_controller = DownloadController(download_manager, ui=self)
            on_show_page()
        else:
            on_show_error()

        self.update()

    def will_unmount(self):
        print("Called will_unmount")

    def show_new_url_component(self, download_item: DownloadItem):
        assert self.download_controller is not None, "Controller is None"
        url_information_view = DownloadCardView(download_item, self.download_controller)
        self.video_queue.controls.append(url_information_view)
        self.add_type_url_component.value = ""
        self.update()

    def clean_url_component(self):
        self.add_type_url_component.value = ""
        self.update()

    def _folder_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.selected_path.value = e.path
            self.selected_path.color = ft.Colors.WHITE

        else:
            self.selected_path.value = "Ninguna carpeta seleccionada"
            self.selected_path.color = ft.Colors.GREY_400

        self.update()

    async def click_add_url(self, e: ft.ControlEvent):
        logging.info(f"type event {type(e)}")
        logging.info(f"Event flet: {e.control}")
        logging.info(f"Event page: {e.page}")
        url_value = self.add_type_url_component.value

        if url_value is None:
            return

        if self.download_controller is None:
            return

        assert AppContext.loop is not None, "loop is None"

        async def action():
            try:
                future_result = await self.download_controller.request_information(
                    url=url_value
                )
            except Exception as ex:
                self.add_type_url_component.value = ""
                self.update()
                logging.error(ex)
                return

            if hasattr(future_result, "__aiter__"):
                async for item in future_result:
                    assert isinstance(item, DownloadItem)
                    self.show_new_url_component(item)
            else:
                assert isinstance(future_result, DownloadItem)
                self.show_new_url_component(future_result)

        asyncio.run_coroutine_threadsafe(action(), loop=AppContext.loop).result()
