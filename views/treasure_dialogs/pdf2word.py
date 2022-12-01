import json
import os.path

import flet as ft
import pdf2docx

from utils import snack_bar, DESKTOP
from views.treasure_dialogs.base import BaseDialog


class Dialog(BaseDialog):
    def __init__(self):
        self.close_btn = ft.IconButton(
            icon=ft.icons.CLOSE_OUTLINED, on_click=self.close_dlg
        )
        self.choose_file_dialog = None
        self.choose_file_btn = ft.FloatingActionButton(
            "请选择pdf文件", on_click=self.open_dialog, width=300
        )
        self.hint = ft.Text(
            "· 目前暂不支持扫描PDF文字识别\n"
            "· 仅支持从左向右书写的语言（因此不支持阿拉伯语）\n"
            "· 不支持旋转的文字\n"
            "· 基于规则的解析无法保证100%还原PDF样式\n"
        )
        self.content = ft.Column([self.choose_file_btn, self.hint])
        super(Dialog, self).__init__(
            title=ft.Text("pdf转word"),
            content=self.content,
            actions=[self.close_btn],
            actions_alignment="center",
        )

    def open_dialog(self, e):
        if self.choose_file_dialog is None:
            self.choose_file_dialog = ft.FilePicker(on_result=self.pdf2word_action)
            self.page.overlay.append(self.choose_file_dialog)
            self.page.update()
        self.choose_file_dialog.pick_files(dialog_title="选择pdf", file_type="any")

    def pdf2word_action(self, e: ft.FilePickerResultEvent):
        if e.data:
            data = json.loads(e.data)
            if data["files"]:
                file_path = data["files"][0]["path"]
                if not file_path.endswith("pdf"):
                    snack_bar(self.page, "请选择pdf文件")
                else:
                    self.close_dlg(None)
                    self.page.splash.visible = True
                    self.page.update()
                    file_name = os.path.basename(file_path)
                    to_name = os.path.join(DESKTOP, file_name.split(".")[0] + ".docx")
                    pdf2docx.parse(file_path, to_name)
                    self.page.splash.visible = False
                    self.page.update()
                    snack_bar(self.page, f"转换完成，已保存至桌面 {to_name}")
