import flet as ft

from methods.getbuddhist import buddhist_dict
from utils import snack_bar


class Card(ft.Card):
    def __init__(self, **kwargs):
        self.tag = kwargs.get("tag", "")
        self.img = kwargs.get("img", "")
        self.name = kwargs.get("name", "")
        self.short_describe = kwargs.get("short_describe", "")
        self.describe = kwargs.get("describe", "")
        self.guide = kwargs.get("guide", "")
        self.download_page_url = kwargs.get("download_page_url", "")
        self.ft_img = ft.Image(
            src=self.img if self.img else "None",
            width=20,
            height=20,
        )
        self.ft_tag = ft.Text(self.tag, overflow="clip", size=10)
        self.ft_name = ft.Text(self.name, weight="w900", overflow="clip")
        self.ft_short_describe = ft.Container(
            ft.Markdown(self.short_describe, tooltip=self.describe, expand=1), margin=10
        )
        self.ft_download_page_btn = ft.FloatingActionButton(
            "跳转下载", width=80, height=40, on_click=self.open_url
        )
        super().__init__(
            ft.Column(
                [
                    ft.Row(
                        [self.ft_img, self.ft_name, self.ft_tag],
                        alignment="spaceEvenly",
                    ),
                    self.ft_short_describe,
                    self.ft_download_page_btn,
                ],
                alignment="spaceEvenly",
                horizontal_alignment="center",
            ),
            margin=10,
            col={"xs": 12, "sm": 6, "lg": 4},
            height=200,
            elevation=10,
        )

    def open_url(self, e):
        if self.page.can_launch_url(self.download_page_url):
            self.page.launch_url(self.download_page_url)
        else:
            snack_bar(self.page, f"无法打开链接：{self.download_page_url}")


class ViewPage(ft.Stack):
    def __init__(self, page: ft.Page):
        self.page = page
        self.contents = self.get_contents()
        self.row = ft.ResponsiveRow(self.contents, spacing=20, run_spacing=20)
        super(ViewPage, self).__init__(
            controls=[self.row],
            expand=True,
        )

    def init_event(self):
        pass

    def get_contents(self):
        tmp = []
        for entity in buddhist_dict:
            card = Card(**entity)
            tmp.append(card)
        return tmp


# def main(page: ft.Page):
#     page.title = "aaaa"
#     a = ViewPage(page)
#     page.add(a)
#
#
# ft.app(
#     target=main,
# )
