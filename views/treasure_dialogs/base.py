import flet as ft


class BaseDialog(ft.AlertDialog):
    def open_dlg(self, e):
        self.open = True
        self.update()

    def close_dlg(self, e):
        self.open = False
        self.update()
