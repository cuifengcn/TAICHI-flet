import re
from dataclasses import dataclass, field
from typing import List, Generator, Literal

from utils import HTMLSession


@dataclass
class DataChapter:
    name: str  # 章节名称
    url: str  # 章节链接


class DataNovelInfo:
    def __init__(
        self,
        img_url="",
        name="",
        author="",
        tag="",
        size="",
        introduction="",
        read_url="",
        download_url="",
    ):
        self.img_url = img_url
        self.name = name
        self.author = author
        self.tag = tag
        self.size = size
        self.introduction = introduction
        self.read_url = read_url
        self.download_url = download_url
        if not hasattr(self, "chapters"):
            self.chapters: List[DataChapter] = []  # 章节列表

    def __str__(self):
        return (
            f"img_url={self.img_url},name={self.name},"
            f"author={self.author},introduction={self.introduction},"
            f"readable={self.readable}, downloadable={self.downloadable}"
        )

    @property
    def readable(self):
        raise NotImplementedError

    @property
    def downloadable(self):
        raise NotImplementedError

    def get_size(self):
        raise NotImplementedError

    def parse_chapters(self):
        raise NotImplementedError

    def get_chapter_names(self):
        return [i.name for i in self.chapters]

    def get_chapter_content(self, chapter_name):
        raise NotImplementedError


class ZXCSDataNovelInfo(DataNovelInfo):
    def __init__(
        self,
        img_url,
        name,
        author,
        tag,
        size,
        introduction,
        read_url,
        download_url,
        bid,
    ):
        self.bid = bid
        self.cid = "1"
        self.catalog = "1"
        super(ZXCSDataNovelInfo, self).__init__(
            img_url,
            name,
            author,
            tag,
            size,
            introduction,
            read_url,
            download_url,
        )

    @property
    def readable(self):
        if self.read_url:
            return True
        else:
            return False

    @property
    def downloadable(self):
        if self.download_url:
            return True
        else:
            return False

    def get_size(self):
        regx = re.compile(r"\d+\.+\d+[ ]*[MmgGkbKB]*")
        return " ".join(regx.findall(self.size))

    def parse_chapters(self):
        _chapters: List[DataChapter] = ZXCS.get_chapters_list(self.bid, self.catalog)
        self.chapters.clear()
        self.chapters.extend(_chapters)

    def get_chapter_content(self, chapter_name):
        for chapter in self.chapters:
            if chapter.name == chapter_name:
                return ZXCS.get_chapter_content(chapter.url)
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
        print("zx")
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
        novel = ZXCSDataNovelInfo(
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
        # content = content.replace("\n", "\n\n")
        return content


class DingDianDataNovelInfo(DataNovelInfo):
    def __init__(self, img_url, name, author, introduction, chapters):
        self.chapters = chapters
        super(DingDianDataNovelInfo, self).__init__(
            img_url, name, author, introduction=introduction
        )

    @property
    def readable(self):
        return True

    @property
    def downloadable(self):
        return False

    def get_size(self):
        return ""

    def parse_chapters(self):
        pass

    def get_chapter_content(self, chapter_name):
        for chapter in self.chapters:
            if chapter.name == chapter_name:
                return DingDian.get_chapter_content(chapter.url)
        return ""


class DingDian:
    """顶点小说"""

    rank_url = "https://www.23usp.com/paihangbang/allvote.html"  # 排行榜
    base_url = "https://www.23usp.com/"
    all_books_url = "https://www.23usp.com/quanbuxiaoshuo/"
    session = HTMLSession()

    @classmethod
    def recommend_books(cls) -> Generator[DataNovelInfo, None, None]:
        resp = cls.session.get(cls.rank_url)
        rank_list = resp.html.xpath(
            '//div[@class="box b2"]//li[not(@class="ltitle")]//a[@href]'
        )
        if not rank_list:
            return
        for a in rank_list:
            if a.attrs.get("href") and a.attrs["href"].startswith("http"):
                yield cls.get_book_detail(a.attrs["href"])

    @classmethod
    def search_books(cls, keyword) -> Generator[DataNovelInfo, None, None]:
        if not keyword:
            for book in cls.recommend_books():
                yield book
        else:
            all_books_resp = cls.session.get(cls.all_books_url)
            all_books_resp.encoding = "gbk"
            uls = all_books_resp.html.xpath('//div[@class="novellist"]/ul')
            filter_books = []
            for ul in uls:
                lis = ul.xpath("//ul/li")
                for li in lis:
                    if keyword in li.text:
                        filter_books.append(li.absolute_links.pop())
            for url in filter_books:
                yield cls.get_book_detail(url)

    @classmethod
    def get_book_detail(cls, url) -> DataNovelInfo:
        resp = cls.session.get(url)
        img_url = resp.html.xpath('//div[@id="fmimg"]//img[@src]')[0].attrs["src"]
        book_info = resp.html.xpath('//div[@id="maininfo"]')[0]
        book_name = book_info.xpath('//div[@id="info"]//h1')[0].text
        author_name = book_info.xpath('//div[@id="info"]//p[1]')[0].text.split("：")[-1]
        book_introduction = resp.html.xpath('//div[@id="intro"]')[0].text
        chapters = resp.html.xpath('//div[@id="list"]//a[@href]')
        all_chapters = []
        for c in chapters:
            all_chapters.append(DataChapter(name=c.text, url=c.absolute_links.pop()))
        novel = DingDianDataNovelInfo(
            img_url=img_url,
            name=book_name,
            author=author_name,
            introduction=book_introduction,
            chapters=all_chapters,
        )
        return novel

    @classmethod
    def get_chapter_content(cls, sub_url):
        resp = cls.session.get(sub_url)
        content = resp.html.xpath('//div[@id="content"]')[0].text
        # content = content.replace("\n", "\n\n")
        return content
