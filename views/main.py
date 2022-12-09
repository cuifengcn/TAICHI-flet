from functools import partial
from math import pi
from random import randint

from flet import Container, alignment, animation, transform, Stack, Text
from flet import Switch, Page

from statics import BIG_TAICHI, CLOUD, GONGZHONGHAO
from utils import one_shot_thread

LIGHT = ("light", "光明")
DARK = ("dark", "黑暗")


class ThemeSwitch(Switch):
    def __init__(self, page: Page):
        super(ThemeSwitch, self).__init__(on_change=self.switch_theme, top=5, right=30)
        self.page = page
        self.mode = page.client_storage.get("theme_mode") or LIGHT
        self.page.theme_mode = self.mode[0]
        self.label = self.mode[1]
        self.update()

    def switch_theme(self, e):
        if self.page.theme_mode == DARK[0]:
            self.mode = LIGHT
        else:
            self.mode = DARK
        self.set_theme()

    def set_theme(self):
        self.page.client_storage.set("theme_mode", self.mode)
        self.page.theme_mode = self.mode[0]
        self.label = self.mode[1]
        self.page.update()


class ViewPage(Stack):
    def __init__(self, page):
        self.page = page
        self.bg = Container(
            content=BIG_TAICHI,
            alignment=alignment.center,
            rotate=transform.Rotate(0, alignment=alignment.center),
            animate_rotation=animation.Animation(duration=2000, curve="linear"),
            on_animation_end=self.auto_animate,
            expand=True,
        )
        self.clouds = []
        for i in range(randint(10, 20)):
            left = randint(1, int(self.page.width))
            top = randint(1, int(self.page.height))
            width = randint(20, 80)
            height = int(width / 1.125)
            CLOUD.width = width
            CLOUD.height = height
            _cloud = Container(
                content=CLOUD,
                width=width,
                height=height,
                left=left,
                top=top,
                animate_opacity=randint(1800, 20000),
                on_animation_end=partial(self.auto_cloud_animate, index=i),
                opacity=0,
            )
            self.clouds.append(_cloud)
        self.theme_switch = ThemeSwitch(self.page)
        self.gzh_img = Container(content=GONGZHONGHAO, right=5, bottom=5)
        self.warn_text = Text("数据均来源于网络，与本人无关！请自行判断数据的准确性！", right=20, bottom=1)
        super(ViewPage, self).__init__(
            controls=[self.bg, self.theme_switch, self.gzh_img, self.warn_text]
            + self.clouds,
            expand=True,
        )
        self.init_animate()

    def init_event(self):
        self.auto_animate(None)
        for i in range(len(self.clouds)):
            self.auto_cloud_animate(None, i)

    def init_animate(self):
        one_shot_thread(partial(self.auto_animate, None), 5)
        for i in range(len(self.clouds)):
            one_shot_thread(partial(self.auto_cloud_animate, None, i), 5)

    def auto_animate(self, e):
        self.bg.rotate.angle -= pi
        self.page.update()

    def auto_cloud_animate(self, e, index):
        cloud = self.clouds[index]
        if cloud.opacity == 0:
            cloud.opacity = 1
        elif cloud.opacity == 1:
            cloud.opacity = 0
        self.page.update()
