import random
from typing import List, Generator, Optional

from utils import HTMLSession


class _Base:
    base_url = ""
    page_url = ""
    page_num = None
    max_page = 0
    page_list = Optional[list]  # 默认如果是个列表的话，子类会继承父类的列表，所以父类用None表示，子类重新初始化为列表

    @classmethod
    def set_page(cls, page_num: int):
        cls.page = page_num

    @classmethod
    def image_url_generator(cls):
        while True:
            if cls.page_num is None:
                # 初始化，随机选择一个开始页面
                cls.page_num = random.randint(1, cls.max_page)
            else:
                if cls.page_num > cls.max_page:
                    cls.page_num = 1
            if not cls.page_list:
                cls.page_list.extend(cls._get_page_list(cls.page_num))
            detail_url = cls.page_list.pop(0)
            for src in cls._get_image_url(detail_url):
                yield src
            cls.page_num += 1

    @classmethod
    def _get_image_url(cls, detail_url) -> Generator[str, None, None]:
        raise NotImplementedError

    @classmethod
    def _get_page_list(cls, page_num: int) -> List[str]:
        raise NotImplementedError


# class VMGirls:
#     page_url = "https://www.vmgirls.com/page/{}/"
#
#     @classmethod
#     def get_image_urls(cls, base_url):
#         session = HTMLSession()
#         res = session.get(base_url)
#         if res.status_code != 200:
#             yield False, res.text
#         else:
#             elems = res.html.xpath('//a[@class="media-content"]')
#             for elem in elems:
#                 s = elem.attrs.get("href")
#                 if s:
#                     detail = session.get(s)
#                     detail_imgs = detail.html.xpath(
#                         '//div[@class="nc-light-gallery"]//img[@src]'
#                     )
#                     for detail_img in detail_imgs:
#                         d = detail_img.attrs.get("src")
#                         if d:
#                             yield d


class CiYuanDao(_Base):
    base_url = "http://ciyuandao.com"
    page_url = "http://ciyuandao.com/photo/list/0-0-{page_num}"
    max_page = 451
    page_list = []

    @classmethod
    def _get_image_url(cls, detail_url):
        # 获取里面的图片
        session = HTMLSession()
        resp = session.get(detail_url)
        a_list = resp.html.xpath('//div[@class="talk_pic hauto"]//img[@src]')
        for img in a_list:
            img_src = img.attrs.get("src")
            if img_src:
                yield img_src

    @classmethod
    def _get_page_list(cls, page_num: int):
        # 获取此page下面的所有相关url
        url = cls.page_url.format(page_num=page_num)
        session = HTMLSession()
        resp = session.get(url)
        hrefs = resp.html.xpath('//div[@class="pics"]//a[@class="tits grey" and @href]')
        res = []
        for a in hrefs:
            a = a.attrs.get("href", "")
            if a:
                res.append(cls.base_url + a)
        return res


class ToMeinv(_Base):
    base_url = "https://www.2meinv.com/"
    page_url = "https://www.2meinv.com/index-{page_num}.html"
    max_page = 212
    page_list = []

    @classmethod
    def _get_image_url(cls, detail_url):
        # 获取里面的图片
        detail_url_prefix = detail_url[:-5] + "-"
        session = HTMLSession()
        resp = session.get(detail_url)
        total_page_list = resp.html.xpath(
            '//div[@class="page-show"]//a[@href and not(@class)]/text()'
        )
        if len(total_page_list) > 2:
            total_sub_page = total_page_list[-2]
        else:
            total_sub_page = 1
        curr_sub_page = 1
        while curr_sub_page <= int(total_sub_page):
            sub_page_url = detail_url_prefix + str(curr_sub_page) + ".html"
            sub_page_content = session.get(sub_page_url)
            src = sub_page_content.html.xpath(
                '//div[@class="pp hh"]//img[@src and @alt]'
            )[0].attrs.get("src")
            if src:
                yield src
            curr_sub_page += 1

    @classmethod
    def _get_page_list(cls, page_num: int):
        # 获取此page下面的所有相关url
        url = cls.page_url.format(page_num=page_num)
        session = HTMLSession()
        resp = session.get(url, timeout=10, verify=False)
        hrefs = resp.html.xpath(
            '//ul[@class="detail-list"]//a[@class="dl-pic" and  @href]'
        )
        res = []
        for a in hrefs:
            a = a.attrs.get("href", "")
            if a:
                res.append(a)
        return res


class VMGirls(_Base):
    base_url = "https://www.vmgirls.net/"
    page_url = "https://www.vmgirls.net/page/{page_num}"
    max_page = 132
    page_list = []

    @classmethod
    def _get_image_url(cls, detail_url):
        # 获取里面的图片
        session = HTMLSession()
        resp = session.get(detail_url)
        photos = resp.html.xpath('//div[@class="nc-light-gallery"]//img[@alt and @src]')
        for photo in photos:
            yield photo.attrs["src"]

    @classmethod
    def _get_page_list(cls, page_num: int):
        # 获取此page下面的所有相关url
        url = cls.page_url.format(page_num=page_num)
        session = HTMLSession()
        resp = session.get(url, timeout=10, verify=False)
        hrefs = resp.html.xpath(
            '//div[@class="site-main"]//a[@class="media-content" and @href]'
        )
        res = []
        for a in hrefs:
            a = a.attrs["href"]
            res.append(a)
        return res


# g = VMGirls.image_url_generator()
# for i in range(200):
#     print(next(g))

APIS = {
    "vmgirls": VMGirls,
    "ciyuandao": CiYuanDao,
    "2meinv": ToMeinv,
}
