# coding:utf-8
import os
import time
from pathlib import Path
from threading import Thread
from typing import Optional

from flet import SnackBar, Text
from requests_html import HTMLSession as _HTMLSession, HTMLResponse

""""""
CURR_PATH = Path(__file__).absolute().parent
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
CACHE = CURR_PATH.joinpath("Cache")
CACHE.mkdir(parents=True, exist_ok=True)


def snack_bar(page, message):
    page.snack_bar = SnackBar(content=Text(message), action="好的")
    page.snack_bar.open = True
    page.update()


def one_shot_thread(func, timeout=0.0):
    def run(func, timeout):
        time.sleep(timeout)
        func()

    Thread(target=run, args=(func, timeout), daemon=True).start()


Threads = []


def cycle_thread(func, timeout=None):
    def run(func, timeout):
        if timeout is not None:
            time.sleep(timeout)
        func()

    thread = Thread(target=run, args=(func, timeout), daemon=True)
    Threads.append(thread)
    thread.start()


class HTMLSession(_HTMLSession):
    def __init__(self, headers: Optional[dict] = None, **kwargs):
        super(HTMLSession, self).__init__(**kwargs)
        if headers:
            self.headers.update(headers)


def ms_to_time(ms):
    # 毫秒转换为时间格式
    ms = int(ms)
    minute, second = divmod(ms / 1000, 60)
    minute = min(99, minute)
    return "%02d:%02d" % (minute, second)


def handle_redirect(url, session=None):
    if session is None:
        session = HTMLSession()
    resp = session.get(url, stream=True)
    return resp.url


def download_url_content(url) -> HTMLResponse:
    session = HTMLSession()
    resp = session.get(url)
    return resp


def download_named_image(url):
    print(url)
    session = HTMLSession()
    file_name = url.split("/")[-1]

    resp = session.get(url)


""""""
