import asyncio

import flet as ft
from flet.core.types import FontWeight

from tm_downloader.domain.models.media import MediaBase
from tm_downloader.infrastructure.controller import TelegramController
from tm_downloader.presentation.gui.telegram.components.uri import UriInformation


class LayoutTelegramGui(ft.Column):
    __urls = []

    def __init__(self, controller: TelegramController):
        super().__init__()
        self.__controller = controller

        self.height = 600

        # URL component
        self._add_type_url_component = ft.TextField(
            hint_text="Pega la URL o rango de URLs...",
            expand=True,
        )
        self._new_url_component = ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Row(
                    controls=[
                        self._add_type_url_component,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            tooltip="Agregar URL",
                            on_click=self.add_click,
                        )
                    ]
                )
            )
        )

        # VIDEO QUEUE
        self._video_queue = ft.ListView(
            height=400,
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=True
        )
        self._download_view = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Videos en cola", size=16, weight=FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.FOLDER_OPEN,
                            tooltip="Carpeta de descargas",
                            # on_click=self.choose_folder,
                        ),
                    ],
                ),
                self._video_queue,
            ]
        )

        # PROGRESS CONEcTION
        self._progres_connect = ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Connecting...")
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.main_page = ft.Column(
            controls=[
                self._new_url_component,
                self._download_view
            ]
        )

        self.main_page.visible = False

        self.controls = [
            self._progres_connect,
            self.main_page
        ]

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

        asyncio.run_coroutine_threadsafe(
            self.__controller.create_client(
                on_success=on_show_page,
                on_error=on_show_error
            ),
            loop=self.__controller.loop
        )

        self.update()

    def will_unmount(self):
        print("Called will_unmount")

    async def add_click(self, e):
        print("Flet Event: ", e)
        if "-" in self._add_type_url_component.value:
            messages = self.__controller.get_information_from_url_pattern(self._add_type_url_component.value)
            for message in messages:
                url_information_gui = UriInformation(message, self.__controller)

                self._video_queue.controls.insert(0, url_information_gui)
        else:
            def on_add_new_url(media_base: MediaBase) -> None:
                url_information_gui = UriInformation(media_base, self.__controller)
                self._video_queue.controls.insert(0, url_information_gui)

                self.update()

            self.__controller.get_information_video(self._add_type_url_component.value, on_success=on_add_new_url)

        self._add_type_url_component.value = ""
        self.update()
