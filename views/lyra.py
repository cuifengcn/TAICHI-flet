import flet as ft
from flet import padding
from methods.getorrent import DataBTDetail, BTSow, TorrentKitty
from utils import snack_bar


class Title(ft.Row):
    def __init__(self):
        self.text = ft.Text("聚合磁力搜索", width=300, size=30, text_align="center")
        super(Title, self).__init__(
            [self.text], alignment="center", vertical_alignment="center"
        )


class SearchComponent(ft.Row):
    def __init__(self, parent: "ViewPage"):
        self.parent = parent
        self.search_input = ft.TextField(
            label="请输入搜索内容",
            width=300,
            height=40,
            on_submit=self.search,
        )
        self.submit_btn = ft.FloatingActionButton(
            "搜索", on_click=self.search, height=40, width=80, autofocus=True
        )
        super(SearchComponent, self).__init__(
            controls=[self.search_input, self.submit_btn],
            alignment="center",
            vertical_alignment="center",
        )

    def search(self, e):
        target = self.search_input.value
        if not target:
            return
        else:
            self.parent.search(target, 1)


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
        self.detail_area = ft.ListView(controls=[], expand=True, visible=False, animate_size=500)
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


class ShowArea(ft.Column):
    def __init__(self, parent):
        self.parent = parent
        self.tabs = ft.Tabs(tabs=[], width=400)
        self.prev_page_btn = ft.TextButton(
            "上一页", disabled=True, on_click=self.parent.to_prev_page
        )
        self.curr_page = ft.Text(width=100)
        self.next_page_btn = ft.TextButton(
            "下一页", disabled=True, on_click=self.parent.to_next_page
        )
        super(ShowArea, self).__init__(
            [
                ft.Row(
                    [self.prev_page_btn, self.curr_page, self.next_page_btn],
                    alignment="center",
                    expand=1,
                ),
                ft.Row([self.tabs], alignment="center", expand=10),
            ],
            alignment="center",
            expand=True,
        )

    def tab_content(self):
        return ft.ListView(controls=[], expand=True, padding=5)

    def clear_contents(self, tab_name=None):
        # 清楚所有tabs
        if tab_name is None:
            self.tabs.tabs.clear()
        else:
            for i in range(len(self.tabs.tabs)):
                if self.tabs.tabs[i].text == tab_name:
                    self.tabs.tabs[i].content = self.tab_content()
                    break
        self.update()

    def add_tab(self, tab_name, icon=None):
        # 添加一个tab
        tab = ft.Tab(tab_name, icon=icon, content=self.tab_content())
        self.tabs.tabs.append(tab)
        self.update()

    def remove_tab(self, tab_name):
        # 移除一个tab
        for i in range(len(self.tabs.tabs)):
            if self.tabs.tabs[i].text == tab_name:
                self.tabs.tabs.pop(i)
                self.update()
                return

    def add_content(self, tab_name, content: BTContent):
        flag = False
        for i in range(len(self.tabs.tabs)):
            if self.tabs.tabs[i].text == tab_name:
                self.tabs.tabs[i].content.controls.append(content)
                flag = True
        if not flag:
            self.add_tab(tab_name)
            self.add_content(tab_name, content)
        self.update()


class ViewPage(ft.Row):
    def __init__(self, page):
        self.title = Title()
        self.search_component = SearchComponent(self)
        self.show_area = ShowArea(self)

        super(ViewPage, self).__init__(
            [
                ft.Column(
                    [self.title, self.search_component, self.show_area],
                    expand=True,
                    spacing=20,
                    alignment="center",
                    horizontal_alignment="center",
                )
            ],
            alignment="center",
        )
        self.page = page

    def search(self, target, page_count):
        btsow_results = BTSow.search(target, page_count)
        flag = False
        for result in btsow_results.result:
            if not flag:
                self.show_area.clear_contents(BTSow.name)
                flag = True
            self.show_area.add_content(BTSow.name, BTContent(result, self))
        if btsow_results.next_page:
            self.show_area.next_page_btn.disabled = False
        else:
            self.show_area.next_page_btn.disabled = True
        if int(page_count) == 1:
            self.show_area.prev_page_btn.disabled = True
        else:
            self.show_area.prev_page_btn.disabled = False
        self.update()

    def show_details(self, content: BTContent):
        detail_url = content.bt.detail_url
        if content.bt.source == BTSow.name:
            details = BTSow.detail(detail_url)
            content.set_details(details)

    def to_prev_page(self, e):
        pass

    def to_next_page(self, e):
        pass
