import flet as ft


class FilePickerComponent(ft.Container):
    def __init__(self):
        super().__init__()
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
                self.button,
                self.selected_path,
            ]
        )

    def open_picker(self, e):
        self.file_picker.pick_files(allow_multiple=False)

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            self.selected_path.value = path
            self.selected_path.color = ft.Colors.GREY_100
        else:
            self.selected_path.value = "No file selected"
            self.selected_path.color = ft.Colors.GREY_400
