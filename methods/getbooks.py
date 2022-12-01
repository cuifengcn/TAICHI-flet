import re
from dataclasses import dataclass, field
from typing import List, Generator

from utils import HTMLSession


@dataclass
class DataChapter:
    name: str
    url: str


@dataclass
class DataNovelInfo:
    img_url: str = ""
    name: str = ""
    author: str = ""
    tag: str = ""
    size: str = ""
    introduction: str = ""
    read_url: str = ""
    download_url: str = ""
    bid: str = ""
    cid: str = "1"
    catalog: str = "1"
    chapters: List[DataChapter] = field(default_factory=lambda: [])

    def read_available(self):
        if self.read_url:
            return True
        else:
            return False

    def download_available(self):
        if self.download_url:
            return True
        else:
            return False

    def get_size(self):
        regx = re.compile(r"\d+\.+\d+[ ]*[MmgGkbKB]*")
        return " ".join(regx.findall(self.size))

    def chapter_list_param(self):
        # 获取章节列表的链接
        return self.bid, 1

    def set_chapters(self, chapters):
        self.chapters.clear()
        self.chapters.extend(chapters)

    def get_chapters_name(self):
        return [i.name for i in self.chapters]

    def get_chapter_url(self, chapter_name):
        for chapter in self.chapters:
            if chapter.name == chapter_name:
                return chapter.url
        return ""


class ZXCS:
    """知轩藏书"""

    rank_url = "https://www.zxcs.info/rank/3.html"  # 排行榜
    base_url = "https://www.zxcs.info/"
    content_url = "https://www.zxcs.info/ajax/ajax_read.php"  # 章节内容,是的跟章节列表相同请求方式不同
    search_url = "https://www.zxcs.info/index.php?keyword={keyword}"  # 搜索
    chapter_list_url = "https://www.zxcs.info/ajax/ajax_read.php"  # 章节列表

    @classmethod
    def recommend_books(cls) -> Generator[DataNovelInfo, None, None]:
        session = HTMLSession()
        resp = session.get(cls.rank_url)
        rank_list = resp.html.xpath('//div[@class="rank-list sort-list"]')
        if not rank_list:
            return
        if len(rank_list) >= 2:
            target_rank = rank_list[1]
        else:
            target_rank = rank_list[-1]

        for url in target_rank.links:
            if url[-1].isdigit():
                yield cls.get_book_detail(url)

    @classmethod
    def search_books(cls, keyword):
        if not keyword:
            for book in cls.recommend_books():
                yield book
        else:
            url = cls.search_url.format(keyword=keyword)
            session = HTMLSession()
            resp = session.get(url)
            data_list = resp.html.xpath('//dl[@id="plist"]/dt[1]/a')
            for data in data_list:
                href = data.attrs.get("href", "")
                if href[-1].isdigit():
                    yield cls.get_book_detail(href)

    @classmethod
    def get_book_detail(cls, url):
        session = HTMLSession()
        resp = session.get(url)
        img_url = resp.html.xpath('//a[@id="bookImg"]')[0].attrs.get("href")
        img_url = cls.base_url + img_url
        book_info = resp.html.xpath('//div[@class="book-info"]')
        if not book_info:
            return False
        else:
            book_info = book_info[0]
        book_name = book_info.xpath("//h1")[0].text
        author_name = book_info.xpath('//p[@class="intro"]/text()[1]')[0]
        book_tag = book_info.xpath('//p[@class="tag"]')[0].text
        book_size = book_info.xpath('//p[@class="intro"]/text()[2]')[0].strip()
        book_introduction = resp.html.xpath('//div[@class="book-info-detail"]')[0].text
        book_introduction = "\n".join(book_introduction.split("\n")[:-1])
        read_url = resp.html.xpath(
            '//a[@class="blue-btn J-getJumpUrl" and @id="readBtn"]'
        )
        if read_url:
            read_url = cls.base_url + read_url[0].attrs.get("href")
        else:
            read_url = ""
        download_url = resp.html.xpath(
            '//a[@class="blue-btn J-getJumpUrl" and @title]'
        )[0].attrs.get("href")
        download_url = cls.base_url + download_url
        bid: str = download_url.split("=")[-1]
        if not bid.isdigit():
            bid = ""
        novel = DataNovelInfo(
            img_url=img_url,
            name=book_name,
            author=author_name,
            tag=book_tag,
            size=book_size,
            introduction=book_introduction,
            read_url=read_url,
            download_url=download_url,
            bid=bid,
        )
        return novel

    @classmethod
    def get_chapters_list(cls, bid, catalog):
        session = HTMLSession()
        resp = session.post(cls.chapter_list_url, data={"bid": bid, "catalog": catalog})
        a = resp.html.xpath("//a[@href]")
        chapters_list = []
        for tmp in a:
            href = tmp.attrs.get("href")
            chapter_name = tmp.text
            if href:
                chapters_list.append(DataChapter(name=chapter_name, url=href))
        return chapters_list

    @classmethod
    def get_chapter_content(cls, sub_url):
        bid, cid = re.compile(r"bid=(\d+)&cid=(\d+)").findall(sub_url)[0]
        url = cls.content_url
        session = HTMLSession()
        resp = session.post(url, data={"bid": bid, "cid": cid})
        content = resp.html.full_text
        content = content.replace("\n", "\n\n")
        return content
