import flet as ft

from tm_downloader.ui.gui.telegram.main_page import TelegramGui


class UI:

    def __init__(self, title="Downloader Application", width: int = 770, height: int = 770) -> None:
        self.title = title
        self.width = width
        self.height = height

    def prepare_gui(self, page: ft.Page) -> None:
        page.title = self.title
        page.window.width = self.width
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        gui = TelegramGui()

        page.add(gui)
        page.update()

    def boot(self) -> None:
        ft.app(self.prepare_gui)


def main():
    UI().boot()


if __name__ == "__main__":
    main()
