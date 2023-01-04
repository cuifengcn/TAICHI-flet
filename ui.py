from importlib import import_module

import flet

try:
    from views import cense, immortality, lyra, main, mountain, rain, treasure, buddhist
    from views.treasure_dialogs import pdf2word
except:
    pass
from flet import Tabs, Tab, Page, Stack, ProgressBar

from settings import navigation_tabs


class NavigationBar(Stack):
    def __init__(self, page: Page):
        self.page = page
        self.tabs = Tabs(expand=1)
        self.tabs_list = []
        for navigation in navigation_tabs:
            content = self.get_page(navigation[2])
            if not content:
                continue
            icon = navigation[0]
            text = navigation[1]
            self.tabs_list.append(Tab(content=content, icon=icon, text=text))
        self.tabs.tabs.extend(self.tabs_list)
        self.tabs.on_change = lambda e: self.tab_init_event(e.data)
        super(NavigationBar, self).__init__(controls=[self.tabs], expand=True)

    def tab_init_event(self, index):
        index = int(index)
        if hasattr(self.tabs_list[index].content, "init_event"):
            getattr(self.tabs_list[index].content, "init_event")()

    def get_page(self, module_name):
        try:
            module_file = import_module("views." + module_name)
            return module_file.ViewPage(self.page)
        except Exception as e:
            print("getpage", e)


def main(page: Page):
    page.title = "太·极"
    progress_bar = ProgressBar(visible=False)
    page.splash = progress_bar
    t = NavigationBar(page)
    page.add(t)


flet.app(target=main, assets_dir="assets")
