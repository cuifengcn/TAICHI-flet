# --coding:utf-8--
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote

from utils import HTMLSession


class Base:
    name = ""
    base_url = ""

    @classmethod
    def search(cls, keyword, page_count, fuzzy_match=False):
        raise NotImplementedError

    @classmethod
    def detail(cls, url):
        pass


@dataclass
class DataBTDetail:
    title: str  # 标题
    magnet: str  # 下载链接
    size: str  # 文件总大小
    date: str  # 更新日期
    detail_url: str = ""
    source: str = "磁力猫"


@dataclass
class DataBTDetailSubDetail:
    name: str  # 标题
    size: str  # 文件总大小


@dataclass
class DataBT:
    result: List[DataBTDetail] = field(default_factory=lambda: [])
    name: str = ""
    keyword: str = ""
    curr_page: int = 0
    next_page: bool = False


class BTSow(Base):
    name = "磁力猫"
    base_url = "https://btsow.beauty/search/{keyword}/page/{page_count}"

    @classmethod
    def search(cls, keyword, page_count, fuzzy_match=False):
        res = DataBT(name=cls.name, keyword=keyword, curr_page=page_count)
        session = HTMLSession()
        page = session.get(cls.base_url.format(keyword=keyword, page_count=page_count))
        page_list = page.html.xpath('//ul[@class="pagination pagination-lg"]')
        if page_list:
            next_page = page_list[0].xpath('//a[@name="nextpage"]')
            if next_page:
                next_page = True
            else:
                next_page = False
        else:
            next_page = False
        res.next_page = next_page

        result = page.html.xpath('/html/body/div[2]/div[4]/div[@class="row"]')
        for x in result:
            tmp = x.xpath("//a[@title]")[0]
            title = tmp.attrs["title"]
            if not fuzzy_match:  # 需要精确匹配
                if keyword not in title:
                    continue
            detail_url = tmp.attrs.get("href")
            size = x.xpath(
                '//div[contains(@class, "size") and contains(@class, "hidden-xs")]'
            )[0].text
            date = x.xpath(
                '//div[contains(@class, "date") and contains(@class, "hidden-xs")]'
            )[0].text
            _hash = detail_url.split("/")[-1]
            magnet = "magnet:?xt=urn:btih:" + _hash + "&dn=" + quote(title)

            res.result.append(
                DataBTDetail(
                    title=title,
                    magnet=magnet,
                    size=size,
                    date=date,
                    detail_url=detail_url,
                    source=cls.name,
                )
            )
        return res

    @classmethod
    def detail(cls, url):
        res: List[DataBTDetailSubDetail] = []
        session = HTMLSession()
        page = session.get("http:" + url)
        detail_list = page.html.xpath('//div[@class="detail data-list"]')[1].xpath(
            '//div[@class="row"]'
        )[1:]
        for detail in detail_list:
            name, size = detail.text.split("\n")[:2]
            res.append(DataBTDetailSubDetail(name, size))
        return res


class TorrentKitty(Base):
    name = "torrentkitty"
    url = "https://www.torrentkitty.red/"
    base_url = "https://www.torrentkitty.red/search/{keyword}/{page_count}"

    @classmethod
    def search(cls, keyword, page_count, fuzzy_match=False):
        res = DataBT(name=cls.name, keyword=keyword, curr_page=page_count)
        session = HTMLSession()

        page = session.get(cls.base_url.format(keyword=keyword, page_count=page_count))
        html = page.html
        page_list = html.xpath('//div[@class="pagination"]')
        if page_list:
            page_btn = page_list[0].xpath('//span[@class="disabled"]')
            if page_btn and page_btn[0].text == "»":
                next_page = False
            else:
                next_page = True
        else:
            next_page = False
        res.next_page = next_page

        results = html.xpath('//table[@id="archiveResult"]/tr')[1:]
        for tr in results:
            if "No result" in tr.text:
                return res
            title, size, date = tr.text.split("\n")[:3]
            magnet = tr.xpath('//a[@rel="magnet"]')[0].attrs.get("href")
            detail_url = cls.url + tr.xpath('//a[@rel="information"]')[0].attrs.get(
                "href"
            )

            res.result.append(
                DataBTDetail(
                    title=title,
                    magnet=magnet,
                    size=size,
                    date=date,
                    detail_url=detail_url,
                    source=cls.name,
                )
            )
        return res

    @classmethod
    def detail(cls, url):
        res: List[DataBTDetailSubDetail] = []
        session = HTMLSession()
        page = session.get(url)
        detail_list = page.html.xpath('//table[@id="torrentDetail"]//tr')[1:]
        for detail in detail_list:
            name, size = detail.text.split("\n")
            res.append(DataBTDetailSubDetail(name, size))
        return res
