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
    Page,
    margin,
    icons,
    Dropdown,
    dropdown,
)

from utils import snack_bar, CORSImage
from methods.getimages import CiYuanDao, ToMeinv


class ViewPage(Stack):
    def __init__(self, page: Page):
        self.page = page
        self.resource_select = Dropdown(
            width=150,
            value="ciyuandao",
            options=[dropdown.Option("ciyuandao"), dropdown.Option("2meinv")],
            on_change=self.fresh_image
        )
        self.content_area = Container(
            margin=10, alignment=alignment.center, expand=True
        )
        self.next_btn = Column(
            [
                Row(
                    [
                        Container(
                            FloatingActionButton(
                                icon=icons.DOUBLE_ARROW_ROUNDED,
                                on_click=self.fresh_image,
                                width=100,
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
            controls=[self.content_area, self.next_btn, Container(self.resource_select, top=10, right=10)], expand=True
        )
        self.ciyuandao_generator = CiYuanDao.image_url_generator()
        self.tomeinv_generator = ToMeinv.image_url_generator()

    def init_event(self):
        if self.content_area.content is None:
            self.fresh_image(None)

    def fresh_image(self, e):
        self.page.splash.visible = True
        self.page.update()
        try:
            if self.resource_select.value == "2meinv":
                img_url = next(self.tomeinv_generator)
            else:
                img_url = next(self.ciyuandao_generator)
            self.content_area.content = CORSImage(src=img_url)
        except Exception as e:
            snack_bar(self.page, f"获取失败: {e}")
        self.page.splash.visible = False
        self.page.update()

    def btn_opacity(self, e):
        if self.next_btn.opacity == 1:
            self.next_btn.opacity = 0.1
        else:
            self.next_btn.opacity = 1
        self.update()
