import flet as ft


class FilePickerComponent(ft.Container):
    def __init__(self, on_change=None):
        super().__init__()
        self.on_change = on_change

        self.selected_path = ft.Text(
            value="No file selected",
            color=ft.Colors.GREY_400,
            expand=True,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)

        self.button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Select file",
            on_click=self.open_picker,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_900,
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
        )

        self.content = ft.Row(
            controls=[
                self.selected_path,
                self.button,
                self.file_picker,
            ]
        )

    def open_picker(self, e):
        self.file_picker.get_directory_path()

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.selected_path.value = e.path
            self.selected_path.color = ft.Colors.GREY_100
            self.update()

            if self.on_change:
                self.on_change(e.path)