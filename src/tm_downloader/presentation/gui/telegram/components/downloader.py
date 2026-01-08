import flet as ft


class DownloadCompletedView(ft.Column):
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
                #ft.Text(f"Tamaño: {round(int(self.file_size) / 1024 / 1024, 2)} MB", size=12, color=ft.Colors.GREY_600),
                #ft.Text(f"Tamaño: {self.file_size}", size=14, color=ft.Colors.GREY),
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
            content=ft.Column([icon, title, details, buttons], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
            padding=40,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.GREEN_200),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=2, color="rgba(0,0,0,0.15)"),
        )

        self.controls = [card]

    def on_close_windows_finished(self, event) -> None:
        self.visible = False
        self.controls.clear()

        self.update()
