# coding:utf-8
import base64
import os
import re
import time
from pathlib import Path
from threading import Thread
from typing import Optional

from flet import SnackBar, Text, Image as _Image
from requests_html import HTMLSession as _HTMLSession, HTMLResponse

""""""
CURR_PATH = Path(__file__).absolute().parent
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
PICTURE = os.path.join(os.path.expanduser("~"), "Pictures")
CACHE = CURR_PATH.joinpath("Cache")
CACHE.mkdir(parents=True, exist_ok=True)


class CORSImage(_Image):
    cors_url = "https://pc-cors.elitb.com/proxy?url="

    def __init__(self, *args, **kwargs):
        if "src" in kwargs:
            kwargs["src"] = self.cors_url + kwargs["src"]
        else:
            if args:
                args = (self.cors_url + args[0],) + args[1:]
        super(CORSImage, self).__init__(*args, **kwargs)


def snack_bar(page, message):
    page.snack_bar = SnackBar(content=Text(message), action="好的")
    page.snack_bar.open = True
    page.update()


def one_shot_thread(func, timeout=0.0):
    def run(func, timeout):
        time.sleep(timeout)
        try:
            func()
        except Exception as e:
            print(f"one_shot_thread:{func} {e}")

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
    regx = re.compile(r'/([\w\-]*\.[a-zA-Z]*)\??')
    file_name = regx.findall(url)[-1]
    session = HTMLSession()
    p = Path(PICTURE).joinpath("taichi")
    p.mkdir(exist_ok=True)
    resp = session.get(url)
    f = p.joinpath(file_name)
    f.write_bytes(resp.content)
    return f


class SRCImage(_Image):
    session = HTMLSession()

    def __init__(self, *args, **kwargs):
        if "src" not in kwargs:
            kwargs["src"] = args[0]
            args = args[1:]
        try:
            session = HTMLSession()
            resp = session.get(kwargs["src"])
            kwargs["src_base64"] = base64.b64encode(resp.content).decode()
            kwargs.pop("src")
        except:
            pass
        super(SRCImage, self).__init__(*args, **kwargs)


""""""
