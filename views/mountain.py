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

from methods.getimages import CiYuanDao, ToMeinv, APIS
from utils import snack_bar, download_named_image


class ViewPage(Stack):
    def __init__(self, page: Page):
        self.page = page
        self.urls = {
            k: {"index": -1, "values": []} for k in APIS
        }
        self.resource_select = Dropdown(
            text_size=10,
            width=80,
            height=50,
            content_padding=10,
            value=list(APIS.keys())[0],
            options=[dropdown.Option(k) for k in APIS],
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
        self.save_btn = Container(
            FloatingActionButton(
                icon=icons.SAVE_ALT_ROUNDED,
                on_click=self.save_img,
                width=50,
            ),
            opacity=0.2,
            right=20,
            bottom=20
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
                self.save_btn,
                self.next_btn,
                Container(self.resource_select, top=10, right=10),
            ],
            expand=True,
        )
        self.generators = {k: v.image_url_generator() for k, v in APIS.items()}
        # self.ciyuandao_generator = CiYuanDao.image_url_generator()
        # self.tomeinv_generator = ToMeinv.image_url_generator()

    def init_event(self):
        if self.content_area.content is None:
            self.fresh_image(None)

    def fresh_image(self, e):
        self.page.splash.visible = True
        self.page.update()
        try:
            _type = self.resource_select.value
            img_url = next(self.generators[_type])
            # if _type == "2meinv":
            #     img_url = next(self.tomeinv_generator)
            # else:
            #     img_url = next(self.ciyuandao_generator)
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

    def save_img(self, e):
        try:
            _type = self.resource_select.value
            _index = self.urls[_type]["index"]
            if _index >= 0:
                f = download_named_image(self.urls[_type]["values"][self.urls[_type]["index"]])
                snack_bar(self.page, f"{f}已保存")
        except Exception as e:
            snack_bar(self.page, f"保存失败: {e}")

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
