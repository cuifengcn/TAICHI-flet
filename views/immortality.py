# --coding:utf-8--
from typing import List, Optional

import flet as ft
from flet import (
    Container,
    Column,
    Row,
    TextField,
    Stack,
    FloatingActionButton,
    ElevatedButton,
    TextButton,
    ListView,
    Dropdown,
    dropdown,
    Text,
    Card,
    alignment,
)

from methods.getbooks import DataNovelInfo, ZXCS, DingDian
from utils import SRCImage, snack_bar


class Novel(Row):
    def __init__(self, novel_info: DataNovelInfo, read_callback, download_callback):
        self.novel_info = novel_info
        self.read_callback = read_callback
        self.download_callback = download_callback
        self.image = SRCImage(
            src=novel_info.img_url, width=30, height=30, border_radius=5, fit="cover"
        )
        self.name = Text(
            novel_info.name,
            weight="bold",
            tooltip=novel_info.name,
            width=200,
            overflow="ellipsis",
        )
        self.author = Text(
            novel_info.author,
            size=12,
            tooltip=novel_info.author,
            width=150,
            overflow="ellipsis",
        )
        self.tag = Text(
            novel_info.tag,
            tooltip=novel_info.tag,
            size=11,
            width=240,
            overflow="ellipsis",
        )
        self.size = Text(novel_info.get_size(), size=11, width=120, overflow="ellipsis")
        self.introduction = Text(
            novel_info.introduction,
            max_lines=2,
            size=12,
            width=330,
            overflow="ellipsis",
            tooltip=novel_info.introduction,
        )
        self.read_btn = ElevatedButton(
            "阅读", height=30, on_click=lambda _: self.read_callback(self)
        )
        if not novel_info.readable:
            self.read_btn.visible = False
        self.download_btn = ElevatedButton(
            "下载", height=30, on_click=lambda _: self.download_callback(self)
        )
        if not self.novel_info.downloadable:
            self.download_btn.visible = False
        self.row1 = Row(
            controls=[self.image, self.name, self.author],
            alignment="start",
            expand=True,
        )
        self.row2 = Row(
            controls=[self.tag, self.size], alignment="start", expand=True, height=5
        )
        self.row3 = Row(controls=[self.introduction], alignment="start", expand=True)
        self.row4 = Row(
            controls=[self.read_btn, self.download_btn],
            alignment="spaceEvenly",
            expand=True,
        )
        self.content = Container(
            Column([self.row1, self.row2, self.row3, self.row4], spacing=0),
            margin=10,
            alignment=alignment.top_center,
        )
        super(Novel, self).__init__(
            controls=[Card(self.content, expand=True, width=300)],
            width=300,
            height=195,
            alignment="center",
            vertical_alignment="center",
        )


class SearchComponent(Stack):
    def __init__(self, search_event_callback):
        self.callback = search_event_callback
        self.search_input = TextField(
            label="请输入作者或小说名",
            width=300,
            height=40,
            on_submit=self.search,
        )
        self.submit_btn = FloatingActionButton(
            "搜索", on_click=self.search, width=80, height=40, autofocus=True
        )
        super(SearchComponent, self).__init__(
            controls=[
                Row(
                    controls=[self.search_input, self.submit_btn],
                    alignment="center",
                    vertical_alignment="center",
                )
            ]
        )

    def search(self, e=None):
        self.callback(self.search_input.value)


class SearchDisplay(ListView):
    def __init__(self, read_callback, download_callback):
        self.read_callback = read_callback
        self.download_callback = download_callback
        super(SearchDisplay, self).__init__(width=400, height=500, padding=20)

    @property
    def empty(self):
        if len(self.controls) > 0:
            return False
        else:
            return True

    def add_novel(self, data: DataNovelInfo):
        novel = Novel(data, self.read_callback, self.download_callback)
        self.controls.append(novel)
        self.update()

    def clear_novels(self):
        self.controls.clear()
        self.update()

    def update_novels(self, datas: List[DataNovelInfo]):
        flag = False
        for data in datas:
            if not flag:
                self.clear_novels()
                flag = True
            self.add_novel(data)


class RightDisplaySection(Column):
    def __init__(self, parent: "_ViewPage"):
        self.parent = parent
        self.search_area = SearchComponent(self.search_callback)
        self.show_area = SearchDisplay(self.read_callback, self.download_callback)
        super(RightDisplaySection, self).__init__(
            controls=[self.search_area, self.show_area],
            expand=True,
            alignment="center",
            horizontal_alignment="center",
            col={"xs": 0, "sm": 0, "md": 6},
        )

    def search_callback(self, search_target):
        # 执行搜索操作
        self.page.splash.visible = True
        self.page.update()
        flag = False
        try:
            for book in self.parent.book_api.search_books(search_target):
                if not flag:
                    self.page.splash.visible = False
                    self.show_area.clear_novels()
                    self.page.update()
                    flag = True
                self.show_area.add_novel(book)
        except Exception as e:
            snack_bar(self.page, f"搜索小说出错：{e}")
        if not flag:
            snack_bar(self.page, f"没有搜索到小说：{search_target}")
        self.page.splash.visible = False
        self.page.update()

    def read_callback(self, novel: Novel):
        self.parent.start_read(novel.novel_info)

    def download_callback(self, novel: Novel):
        self.parent.open_url(novel.novel_info.download_url)


class NovelTip(Row):
    def __init__(self):
        self.novel_name = Text("", width=250)
        self.author_name = Text("", width=150)
        super(NovelTip, self).__init__(
            controls=[self.novel_name, self.author_name],
            expand=1,
            height=30,
            alignment="center",
            vertical_alignment="center",
        )

    def update_tip(self, novel_name, author_name):
        self.novel_name.value = novel_name
        self.author_name.value = author_name
        self.update()

    def clear_tip(self):
        self.update_tip("", "")


class ControlChapter(Row):
    def __init__(self, content_callback, collapse_callback):
        self.content_callback = content_callback
        self.collapse_callback = collapse_callback
        self.prev_chapter_btn = TextButton("上一章", on_click=self.to_prev_chapter)
        self.chapters = Dropdown(
            # prefix_icon=ft.icons.LIST,
            content_padding=1,
            border_width=0,
            width=300,
            expand=True,
            on_change=self.select_chapter,
        )
        self.next_chapter_btn = TextButton("下一章", on_click=self.to_next_chapter)
        self.collapse_btn = ft.IconButton(
            icon=ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,
            selected_icon=ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
            on_click=self.collapse_callback_event,
        )
        super(ControlChapter, self).__init__(
            controls=[
                self.prev_chapter_btn,
                self.chapters,
                self.next_chapter_btn,
                self.collapse_btn,
            ],
            expand=2,
            width=400,
            alignment="center",
            vertical_alignment="center",
        )

    def update_chapters(self, values: List[str]):
        # 更新章节目录
        self.chapters.options.clear()
        self.chapters.value = values[0]
        for v in values:
            self.chapters.options.append(dropdown.Option(v))
        self.update()

    def select_chapter(self, e=None):
        # 跳转选择的章节
        if e is None:
            c_name = self.chapters.value
        else:
            c_name = e.data
        self.content_callback(c_name)

    def to_prev_chapter(self, e):
        # 跳转上一章节
        chapters: List[dropdown.Option] = self.chapters.options
        if not chapters:
            return
        curr_chapter = self.chapters.value
        if curr_chapter == chapters[0].key:
            return
        else:
            for i in range(1, len(chapters)):
                if curr_chapter == chapters[i].key:
                    self.chapters.value = chapters[i - 1].key
                    self.select_chapter()
                    self.update()

    def to_next_chapter(self, e):
        # 跳转下一章节
        chapters: List[dropdown.Option] = self.chapters.options
        if not chapters:
            return
        curr_chapter = self.chapters.value
        if curr_chapter == chapters[-1].key:
            return
        else:
            for i in range(len(chapters) - 1):
                if curr_chapter == chapters[i].key:
                    self.chapters.value = chapters[i + 1].key
                    self.select_chapter()
                    self.update()

    def collapse_callback_event(self, e):
        e.control.selected = not e.control.selected
        e.control.update()
        self.collapse_callback(e.control.selected)


class ReadContent(Row):
    def __init__(self):
        self.content = ft.Markdown(
            aspect_ratio=3,
            selectable=True,
            extension_set="gitHubWeb",
        )
        self.column = Column(
            [self.content],
            scroll=True,
        )
        self.container = Container(
            self.column,
            expand=True,
            border_radius=10,
            alignment=ft.alignment.center,
            margin=10,
            padding=10,
        )
        super(ReadContent, self).__init__(controls=[self.container], expand=20)

    def put_content(self, content):
        self.column.clean()
        self.page.update()
        self.content = ft.Markdown(
            value=content,
            selectable=True,
            extension_set="gitHubWeb",
            code_theme="atom-one-dark",
        )
        self.column.controls.append(self.content)
        # self.content.visible = False
        # self.update()
        # self.content.visible = True
        # self.content.value = content
        self.page.update()


class LeftWatchSection(Column):
    def __init__(self, parent):
        self.parent = parent
        self.tip = NovelTip()
        self.content = ReadContent()
        self.control = ControlChapter(
            self.content_callback, self.parent.collapse_callback
        )
        self.curr_novel: Optional[DataNovelInfo] = None
        super(LeftWatchSection, self).__init__(
            controls=[self.tip, self.control, self.content],
            expand=True,
            alignment="center",
            horizontal_alignment="center",
            spacing=10,
            col={"xs": 12, "sm": 12, "md": 6},
        )

    def content_callback(self, chapter_name):
        content = self.curr_novel.get_chapter_content(chapter_name)
        self.content.put_content(content)


class _ViewPage(ft.ResponsiveRow):
    def __init__(self, page):
        self.book_api = DingDian
        self.left_section = LeftWatchSection(self)
        self.right_section = RightDisplaySection(self)
        super(_ViewPage, self).__init__(
            controls=[self.left_section, self.right_section],
            expand=True,
            alignment="spaceAround",
            vertical_alignment="center",
            spacing=10,
        )

    def init_event(self):
        if self.right_section.show_area.empty:
            flag = False
            for book in self.book_api.recommend_books():
                if not flag:
                    self.right_section.show_area.clear_novels()
                    flag = True
                self.right_section.show_area.add_novel(book)

    def start_read(self, novel: DataNovelInfo):
        # 开始阅读
        self.left_section.curr_novel = novel
        novel.parse_chapters()

        self.left_section.tip.update_tip(novel.name, novel.author)
        self.left_section.control.update_chapters(novel.get_chapter_names())
        self.left_section.control.select_chapter()
        self.update()

    def open_url(self, url):
        self.page.launch_url(url)

    def collapse_callback(self, collapse: bool):
        if collapse:
            self.right_section.visible = False
        else:
            self.right_section.visible = True
        self.update()


class ViewPage(ft.Stack):
    def __init__(self, page):
        self.content = _ViewPage(page)
        self.resource_select = Dropdown(
            text_size=10,
            width=80,
            height=50,
            content_padding=10,
            value="顶点小说",
            options=[dropdown.Option("顶点小说"), dropdown.Option("知轩藏书")],
            on_change=self.change_resource,
        )
        super(ViewPage, self).__init__(
            controls=[
                self.content,
                Container(self.resource_select, top=10, right=10),
            ],
            expand=True,
        )

    def init_event(self):
        self.content.init_event()

    def change_resource(self, e):
        if self.resource_select.value == "顶点小说":
            if self.content.book_api != DingDian:
                self.content.book_api = DingDian
                self.content.right_section.search_area.search()
        elif self.resource_select.value == "知轩藏书":
            if self.content.book_api != ZXCS:
                self.content.book_api = ZXCS
                self.content.right_section.search_area.search()


# def main(page: Page):
#     page.title = "Flet counter example"
#     page.vertical_alignment = "center"
#     a = ViewPage()
#     page.add(a)
#
#
# flet.app(target=main)
