import json

import flet as ft

from methods.video2ascii import VideoToAscii
from utils import snack_bar, DESKTOP


class ViewPage(ft.Row):
    def __init__(self, page):
        self.input_file = ft.TextField(
            disabled=True, width=300, height=40, content_padding=1
        )
        self.choose_input_file_btn = ft.ElevatedButton(
            "选择视频",
            icon=ft.icons.UPLOAD_FILE,
            on_click=self.choose_video,
        )

        self.output_path = ft.TextField(
            value=DESKTOP, disabled=True, width=300, height=40, content_padding=1
        )
        self.choose_output_path_btn = ft.ElevatedButton(
            "选择保存路径",
            icon=ft.icons.UPLOAD_FILE,
            on_click=self.choose_save_path,
        )
        self.start_btn = ft.FloatingActionButton("开始", on_click=self.start, width=100)
        self.progress = ft.ProgressBar(value=0, width=300, bgcolor=ft.colors.BROWN_100)
        self.choose_dialog = None
        self.save_dialog = None
        self.running = False
        super(ViewPage, self).__init__(
            controls=[
                ft.Column(
                    [
                        ft.Row([self.input_file, self.choose_input_file_btn]),
                        ft.Row([self.output_path, self.choose_output_path_btn]),
                        ft.Row([self.start_btn]),
                        ft.Row([self.progress]),
                    ],
                    alignment="center",
                )
            ],
            alignment="center",
            expand=True,
        )

    def choose_video(self, _):
        def set_text(e: ft.FilePickerResultEvent):
            if e.data:
                data = json.loads(e.data)
                if data["files"]:
                    self.input_file.value = data["files"][0]["path"]
                    self.input_file.tooltip = (
                        data["files"][0]["path"]
                        + " "
                        + str(round(data["files"][0]["size"] / 1048576, 1))
                        + "M"
                    )
                    self.update()

        if self.choose_dialog is None:
            self.choose_dialog = ft.FilePicker(on_result=set_text)
            self.page.overlay.append(self.choose_dialog)
            self.page.update()
        self.choose_dialog.pick_files(file_type="media", allow_multiple=False)

    def choose_save_path(self, _):
        def set_text(e: ft.FilePickerResultEvent):
            if e.data:
                data = json.loads(e.data)
                if data["path"]:
                    self.output_path.value = data["path"]
                    self.update()

        if self.save_dialog is None:
            self.save_dialog = ft.FilePicker(on_result=set_text)
            self.page.overlay.append(self.save_dialog)
            self.page.update()
        self.save_dialog.get_directory_path(dialog_title="保存路径")

    def start(self, e):
        if self.running is True:
            snack_bar(self.page, "程序正在执行")
            return
        self.running = True
        input_file = self.input_file.value
        output_path = self.output_path.value
        self.progress.value = 0
        self.update()
        try:
            VideoToAscii(input_file, output_path, self.update_progress).video_to_ascii()
        except Exception as e:
            snack_bar(self.page, f"转换出错：{e}")
        self.running = False

    def update_progress(self, p):
        self.progress.value = p
        self.update()


# def main(page: ft.Page):
#     page.title = "Flet counter example"
#     page.vertical_alignment = "center"
#     progress_bar = ft.ProgressBar(visible=False)
#     page.splash = progress_bar
#     a = OperationBar()
#     page.add(a)
#     page.update()
#
#
# ft.app(target=main)
