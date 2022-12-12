import flet as ft

from views.treasure_dialogs.pdf2word import Dialog as pdf2wordDialog
from views.treasure_dialogs.checkcovareas import Dialog as covAreaDialog


class ViewPage(ft.Stack):
    def __init__(self, page):
        self.grid = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
            padding=100,
        )
        self.pdf2word = ft.Stack(
            [
                ft.OutlinedButton(
                    "pdf转word",
                    icon=ft.icons.PICTURE_AS_PDF_OUTLINED,
                    width=200,
                    height=50,
                    on_click=self.open_pdf2word,
                )
            ]
        )
        self.cov_area = ft.Stack(
            [
                ft.OutlinedButton(
                    "高风险地区",
                    icon=ft.icons.PICTURE_AS_PDF_OUTLINED,
                    width=200,
                    height=50,
                    on_click=self.open_cov_area,
                )
            ]
        )
        self.grid.controls.extend([self.pdf2word, self.cov_area])
        super(ViewPage, self).__init__([self.grid])

    def open_pdf2word(self, e):
        self.page.dialog = pdf2wordDialog()
        self.page.update()
        self.page.dialog.open_dlg(None)

    def open_cov_area(self, e):
        self.page.dialog = covAreaDialog()
        self.page.update()
        self.page.dialog.open_dlg(None)
