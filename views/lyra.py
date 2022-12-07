import flet as ft
from flet import padding

from methods.getorrent import DataBTDetail, BTSow, TorrentKitty, DataBT
from utils import snack_bar


class SearchComponent(ft.Row):
    def __init__(self, search_callback):
        self.search_callback = search_callback
        self.title = ft.Text("聚合磁力搜索", size=30, text_align="center", expand=5)
        self.search_input = ft.TextField(
            label="请输入搜索内容", height=40, on_submit=self.search, expand=1
        )
        self.submit_btn = ft.FloatingActionButton(
            "搜索", on_click=self.search, height=40, width=80, autofocus=True
        )
        super(SearchComponent, self).__init__(
            controls=[
                ft.Column(
                    [
                        ft.Row([self.title], alignment="center"),
                        ft.Row(
                            [self.search_input, self.submit_btn], alignment="center"
                        ),
                    ],
                    alignment="start",
                    horizontal_alignment="center",
                    expand=True,
                )
            ],
            alignment="center",
            vertical_alignment="center",
            expand=1,
        )

    def search(self, e):
        target = self.search_input.value
        if not target:
            return
        else:
            self.search_callback(target)


class PageRow(ft.Row):
    def __init__(self, prev_page_callback, next_page_callback):
        self.prev_page_callback = prev_page_callback
        self.next_page_callback = next_page_callback
        self.prev_page_btn = ft.TextButton(
            "上一页", disabled=True, on_click=prev_page_callback
        )
        self.curr_page = ft.Text(width=100)
        self.next_page_btn = ft.TextButton(
            "下一页", disabled=True, on_click=next_page_callback
        )
        super(PageRow, self).__init__(
            [self.prev_page_btn, self.next_page_btn],
            expand=True,
            alignment="spaceAround",
        )


class BTContent(ft.Card):
    def __init__(self, bt: DataBTDetail, parent: "ViewPage"):
        self.bt = bt
        self.parent = parent
        self.title = ft.Text(bt.title, tooltip=bt.title, width=300, height=22)
        self.copy_btn = ft.FloatingActionButton("复制", height=22, on_click=self.copy_url)
        self.date = ft.Text(bt.date, width=100, height=22)
        self.size = ft.Text(bt.size, width=100, height=22)
        self.collapse_btn = ft.IconButton(
            icon=ft.icons.KEYBOARD_DOUBLE_ARROW_DOWN_ROUNDED,
            selected_icon=ft.icons.KEYBOARD_DOUBLE_ARROW_UP_ROUNDED,
            height=22,
            style=ft.ButtonStyle(padding=padding.all(0)),
            on_click=self.collapse_select,
        )
        self.detail_area = ft.ListView(
            controls=[], expand=True, visible=False, animate_size=500
        )
        super(BTContent, self).__init__(
            content=ft.Container(
                ft.Column(
                    [
                        ft.Row([self.title, self.copy_btn], alignment="spaceBetween"),
                        ft.Row(
                            [self.date, self.size, self.collapse_btn],
                            alignment="spaceBetween",
                        ),
                        ft.Row([self.detail_area], alignment="spaceBetween"),
                    ],
                    alignment="center",
                ),
                padding=5,
            )
        )

    def copy_url(self, e):
        # 复制下载链接到剪贴板
        self.page.set_clipboard(self.bt.magnet)
        snack_bar(self.page, f"{self.bt.title} 链接已复制")

    def collapse_select(self, e):
        e.control.selected = not e.control.selected
        if e.control.selected:
            self.detail_area.visible = True
        else:
            self.detail_area.visible = False
        if not self.detail_area.controls:
            self.parent.show_details(self)
        self.update()

    def set_details(self, details):
        # 查看详情信息
        index = 0
        for detail in details:
            row = ft.Container(
                ft.Row(
                    [
                        ft.Text(detail.name, tooltip=detail.name, width=300),
                        ft.Text(detail.size, tooltip=detail.size),
                    ],
                    alignment="spaceBetween",
                    expand=True,
                ),
                border_radius=10,
                bgcolor=ft.colors.WHITE60,
                padding=5,
            )
            self.detail_area.controls.append(row)
            index += 1
            if index % 10 == 0:
                # 分批更新
                self.page.update()
        self.page.update()


class MyTab(ft.Tab):
    def __init__(self, parent: "DisplayComponent", page_name):
        self.page_name = page_name
        self.keyword = ""
        self.curr_page_num = 0
        self.parent = parent
        self.page_manage = PageRow(self.prev_page_callback, self.next_page_callback)
        self.content_list = ft.ListView(
            controls=[self.page_manage], expand=True, padding=5
        )
        super(MyTab, self).__init__(text=page_name, content=self.content_list)

    def prev_page_callback(self, e):
        self.parent.prev_page_callback(self.keyword, self.curr_page_num - 1)

    def next_page_callback(self, e):
        self.parent.prev_page_callback(self.keyword, self.curr_page_num + 1)

    def add_content(self, content: DataBT):
        if not content:
            return
        self.content_list.controls = self.content_list.controls[:1]  # 只保留上下页
        self.curr_page_num = content.curr_page
        self.keyword = content.keyword
        if content.next_page:
            self.page_manage.next_page_btn.disabled = False
        else:
            self.page_manage.next_page_btn.disabled = True
        if content.curr_page == 1:
            self.page_manage.prev_page_btn.disabled = True
        else:
            self.page_manage.prev_page_btn.disabled = False
        for c in content.result:
            row = BTContent(c, self.parent.parent)
            self.content_list.controls.append(row)
            self.page.update()


class DisplayComponent(ft.Row):
    def __init__(self, parent: "ViewPage"):
        self.parent = parent
        self.Tabs = ft.Tabs(tabs=[], width=400)
        super(DisplayComponent, self).__init__(
            [self.Tabs], expand=5, alignment="center", vertical_alignment="start"
        )

    def set_content(self, content: DataBT):
        tab_names = [i.page_name for i in self.Tabs.tabs]
        if content.name in tab_names:
            index = tab_names.index(content.name)
            self.Tabs.tabs[index].add_content(content)
        else:
            tab = MyTab(self, content.name)
            self.Tabs.tabs.append(tab)
            self.update()
            tab.add_content(content)
        self.update()

    def next_page_callback(self, keyword, page_num):
        for content in self.parent.to_page(keyword, page_num):
            self.set_content(content)

    def prev_page_callback(self, keyword, page_num):
        for content in self.parent.to_page(keyword, page_num):
            self.set_content(content)


class ViewPage(ft.ResponsiveRow):
    def __init__(self, page):
        self.apis = [BTSow, TorrentKitty]
        self.search_component = SearchComponent(self.search_callback)
        self.display_component = DisplayComponent(self)
        super(ViewPage, self).__init__(
            [
                ft.Column(
                    [self.search_component, self.display_component],
                    col={"xs": 12, "sm": 6},
                    alignment="start",
                    spacing=10,
                    run_spacing=10,
                    horizontal_alignment="center",
                    expand=True,
                )
            ],
            alignment="center",
            vertical_alignment="start",
        )

    def search_callback(self, target):
        self.page.splash.visible = True
        self.page.update()
        for api in self.apis:
            result = api.search(target, 1)  # 1表示搜索第一页
            self.display_component.set_content(result)
        self.page.splash.visible = False
        self.page.update()

    def to_page(self, keyword, name):
        self.page.splash.visible = True
        self.page.update()
        for api in self.apis:
            result = api.search(keyword, name)
            yield result
        self.page.splash.visible = False
        self.page.update()

    def show_details(self, content: BTContent):
        if content.bt.source == "磁力猫":
            api = self.apis[0]
        elif content.bt.source == "torrentkitty":
            api = self.apis[1]
        else:
            api = self.apis[0]
        details = api.detail(content.bt.detail_url)
        content.set_details(details)


# def main(page: ft.Page):
#     page.vertical_alignment = "center"
#     page.horizontal_alignment = "center"
#
#     page.add(ViewPage(page))
#
#
# ft.app(target=main)
