import flet as ft

from tm_downloader.infrastructure.controller import TelegramController
from tm_downloader.domain.events.manager import TelegramEventBus
from tm_downloader.presentation.gui.telegram.pages.telegram_page import LayoutTelegramGui


async def initializer_gui(page: ft.Page):
    page.title = "Downloader Tm App"
    page.window.width = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    page.update()

    client_gui = LayoutTelegramGui(
        TelegramController(
            event_bus=TelegramEventBus()
        )
    )

    page.add(client_gui)


def main():
    ft.app(initializer_gui)


if __name__ == "__main__":
    main()
