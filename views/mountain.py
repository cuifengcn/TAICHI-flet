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
    Dropdown,
    dropdown,
)

from methods.getimages import CiYuanDao, ToMeinv
from utils import snack_bar


class ViewPage(Stack):
    def __init__(self, page: Page):
        self.page = page
        self.urls = {
            "ciyuandao": {"index": -1, "values": []},
            "2meinv": {"index": -1, "values": []},
        }
        self.resource_select = Dropdown(
            text_size=10,
            width=80,
            height=50,
            content_padding=10,
            value="ciyuandao",
            options=[dropdown.Option("ciyuandao"), dropdown.Option("2meinv")],
            on_change=self.fresh_image,
        )
        self.content_area = Container(
            margin=10, alignment=alignment.center, expand=True
        )
        self.back_look_btn = Container(
            FloatingActionButton(
                icon=icons.SETTINGS_BACKUP_RESTORE_ROUNDED,
                on_click=self.back_look_image,
                width=50,
            ),
            opacity=0.3,
            left=20,
            top=20,
            on_hover=self.back_btn_opacity,
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
            controls=[
                self.content_area,
                self.back_look_btn,
                self.next_btn,
                Container(self.resource_select, top=10, right=10),
            ],
            expand=True,
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
            _type = self.resource_select.value
            if _type == "2meinv":
                img_url = next(self.tomeinv_generator)
            else:
                img_url = next(self.ciyuandao_generator)
            self.urls[_type]["values"].append(img_url)
            self.urls[_type]["index"] += 1
            self.content_area.content = Image(
                src=self.urls[_type]["values"][self.urls[_type]["index"]]
            )
            self.update()
        except Exception as e:
            snack_bar(self.page, f"获取失败: {e}")
        self.page.splash.visible = False
        self.page.update()

    def back_look_image(self, e):
        self.page.splash.visible = True
        self.page.update()
        try:
            _type = self.resource_select.value
            self.urls[_type]["index"] -= 1
            if self.urls[_type]["index"] >= 0:
                self.content_area.content = Image(
                    src=self.urls[_type]["values"][self.urls[_type]["index"]]
                )
                self.update()
        except Exception as e:
            snack_bar(self.page, f"获取失败: {e}")
        self.page.splash.visible = False
        self.page.update()

    def btn_opacity(self, e):
        if self.next_btn.opacity == 0.5:
            self.next_btn.opacity = 0.05
        else:
            self.next_btn.opacity = 0.5
        self.update()

    def back_btn_opacity(self, e):
        if self.back_look_btn.opacity == 1:
            self.back_look_btn.opacity = 0.05
        else:
            self.back_look_btn.opacity = 1
        self.update()
