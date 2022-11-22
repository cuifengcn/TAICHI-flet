from enum import Enum
from functools import partial
from random import randint

from flet import (
    Container,
    Stack,
    FloatingActionButton,
    Row,
    alignment,
    Column,
    Image,
    Page,
    margin,
    icons,
)

from utils import snack_bar, download_named_image
from methods.getimages import get_image_urls, IMG_BASE_URL


class Status(Enum):
    none = "none"
    running = "running"
    succeed = "succeed"
    failed = "failed"


class ViewPage(Stack):
    def __init__(self, page: Page):
        self.page = page
        self.content_area = Container(
            margin=10, alignment=alignment.center, expand=True
        )
        self.next_btn = Column(
            [
                Row(
                    [
                        Container(
                            FloatingActionButton(
                                icon=icons.DOUBLE_ARROW_ROUNDED, on_click=self.next_img, width=100
                            ),
                            margin=margin.Margin(0, 0, 0, 100),
                            on_hover=self.btn_opacity,
                        )
                    ],
                    alignment="center",
                )
            ],
            alignment="end",
            opacity=0.3,
            animate_opacity=300,
        )
        super(ViewPage, self).__init__(
            controls=[self.content_area, self.next_btn], expand=True
        )
        self.status = Status.none
        self.base_url = IMG_BASE_URL
        self.curr_page = randint(1, 100)

    def init_event(self):
        if self.content_area.content is None:
            self.next_img(None)

    def next_img(self, e):
        if self.status == Status.none and self.page.client_storage.contains_key("mountain_images"):
            self.page.client_storage.remove("mountain_images")
        if self.images:
            self.show_image()
            if not self.images:
                self.fetch_images()
        else:
            if self.status == Status.running:
                self.snack_bar("正在获取数据...")
                return
            self.fetch_images()
        self.page.update()

    def btn_opacity(self, e):
        if self.next_btn.opacity == 1:
            self.next_btn.opacity = 0.1
        else:
            self.next_btn.opacity = 1
        self.update()

    @property
    def images(self):
        return self.page.client_storage.get("mountain_images") or []

    @images.setter
    def images(self, value):
        self.page.client_storage.set("mountain_images", value)

    def fetch_images(self):
        self.snack_bar("正在获取数据")
        self.status = Status.running
        flag = False
        for src in get_image_urls(self.base_url.format(self.curr_page)):
            if isinstance(src, tuple):
                self.snack_bar(f"接口获取失败：{src[1]}")
                self.curr_page = 1
                return
            else:
                self.images = self.images + [src]
                if not flag:
                    self.show_image()
                    flag = True
        if not self.images:
            self.snack_bar("获取图片失败")
            self.status = Status.failed
            return
        self.curr_page += 1
        self.status = Status.succeed

    def show_image(self):
        image_src = self.images[0]
        image = download_named_image(image_src)
        self.images = self.images[1:]
        self.content_area.content = Image(src=image_src)
        self.page.update()

    def snack_bar(self, message):
        snack_bar(self.page, message)
