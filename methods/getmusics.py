import json
import re
import time
from dataclasses import dataclass, field
from hashlib import md5
from typing import Optional, Generator, List
from urllib.parse import quote

from utils import HTMLSession


@dataclass
class DataSong:
    photo_url: str  # 图片链接
    big_photo_url: str  # 大图链接
    music_name: str  # 歌曲名称
    singer_name: str  # 歌手名称
    music_url: Optional[str] = field(default=None)  # 音乐链接


class HIFINI:
    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        # "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "referer": "https://www.hifini.com",
    }
    search_url = "https://www.hifini.com/search-{target}-{page}.htm"
    recommend_url = "https://www.hifini.com/"
    base_url = "https://www.hifini.com/"

    @classmethod
    def search_musics(cls, target, page=1) -> Generator[DataSong, None, None]:
        if not target:
            for music in cls.recommend_musics():
                yield music
        else:
            session = HTMLSession(cls.headers)
            quota_target = quote(target).replace("%", "_")
            url = cls.search_url.format(target=quota_target, page=page)
            res = session.post(url)
            if res.status_code != 200:
                yield False, res.text
            else:
                body = res.html.xpath('//div[@class="media-body"]/div/a')
                if body:
                    for a in body:
                        if a.absolute_links:
                            detail_url = a.absolute_links.pop()
                            detail = cls.get_detail_music(detail_url, session)
                            if not detail:
                                continue
                            else:
                                yield DataSong(**detail)

    @classmethod
    def recommend_musics(cls) -> List[Generator[DataSong, None, None]]:
        session = HTMLSession(cls.headers)
        res = session.get(cls.recommend_url)
        if res.status_code != 200:
            yield False, res.text
        else:
            body = res.html.xpath('//div[@class="media-body"]/div/a')
            if body:
                for a in body:
                    if a.absolute_links:
                        detail_url = a.absolute_links.pop()
                        detail = cls.get_detail_music(detail_url, session)
                        if not detail:
                            continue
                        else:
                            yield DataSong(**detail)

    @classmethod
    def get_detail_music(cls, url, session=None):
        if session is None:
            session = HTMLSession(cls.headers)
        result = {}
        res = session.get(url)
        aplayer = res.html.xpath('//div[@class="aplayer"]')
        if not aplayer:
            return result
        else:
            strr2 = res.text
            music_url = re.findall(" url: '(.*?)',", strr2, re.S)
            if not music_url:
                return result
            music_name = re.findall(" title: '(.*?)',", strr2, re.S)
            if not music_name:
                return result
            photo_url = re.findall(" pic: '(.*?)'", strr2, re.S)
            if not photo_url:
                return result
            singer_name = re.findall(" author:'(.*?)',", strr2, re.S)
            if not singer_name:
                return result
            result.update(
                {
                    "music_url": cls.base_url + music_url[0],
                    "music_name": music_name[0],
                    "photo_url": photo_url[0],
                    "big_photo_url": photo_url[0],
                    "singer_name": singer_name[0],
                }
            )
            return result


class LiuMingYe:
    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        # "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "origin": "https://tools.liumingye.cn",
    }
    search_url = "https://test.quanjian.com.cn/m/api/search"
    recommend_url = "https://test.quanjian.com.cn/m/api/home/recommend"
    base_music_url = "https://test.quanjian.com.cn/m/api/link/id/{id}/quality/128"

    @classmethod
    def search_musics(cls, target) -> Generator[DataSong, None, None]:
        if not target:
            for music in cls.recommend_musics():
                yield music
        else:
            t = time.time() * 10000
            params = {"_t": t, "type": "YQM", "text": target, "page": 1, "v": "beta"}
            tar_str = json.dumps(params)
            s = md5(tar_str.encode()).hexdigest()
            params["token"] = s
            session = HTMLSession(cls.headers)
            res = session.post(cls.search_url, data=params)
            if res.status_code != 200 or res.json()["code"] != 200:
                yield False, res.text
            else:
                for data in res.json()["data"]["list"]:
                    music_name = data["name"]
                    singer_name = data["artist"] and data["artist"][0]["name"]
                    music_id = data["id"]
                    music_url = cls.base_music_url.format(id=music_id)
                    photo_url = data["pic"].format(size=40)
                    big_photo_url = data["pic"].format(size=500)
                    yield DataSong(
                        photo_url, big_photo_url, music_name, singer_name, music_url
                    )

    @classmethod
    def recommend_musics(cls) -> List[Generator[DataSong, None, None]]:
        t = int(time.time() * 1000)
        params = {"_t": t}
        tar_str = json.dumps(params)
        s = md5(tar_str.encode()).hexdigest()
        params["token"] = s
        session = HTMLSession(cls.headers)
        print(params)
        res = session.post(cls.recommend_url, params=params)
        if res.status_code != 200 or res.json()["code"] != 200:
            yield False, res.text
        else:
            for data in res.json()["data"]["recommendSong"]:
                music_name = data["name"]
                singer_name = data["artist"] and data["artist"][0]["name"]
                _photo_url = (
                    data.get("pic")
                    or data["album"].get("pic")
                    or "https://picsum.photos/{size}"
                )
                photo_url = _photo_url.format(size=40)
                big_photo_url = _photo_url.format(size=500)
                if "url" in data and data["url"]:
                    music_url = data["url"]
                else:
                    if "hash" in data and data["hash"]:
                        music_id = data["hash"]
                    elif "id" in data and data["id"]:
                        music_id = data["id"]
                    else:
                        continue
                    music_url = cls.base_music_url.format(id=music_id)
                yield DataSong(
                    photo_url, big_photo_url, music_name, singer_name, music_url
                )
