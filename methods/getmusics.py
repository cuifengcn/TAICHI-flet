from dataclasses import dataclass, field
import json
import time
from typing import Optional, Generator, List
from hashlib import md5
from utils import HTMLSession


@dataclass
class DataSong:
    photo_url: str  # 图片链接
    big_photo_url: str  # 大图链接
    music_name: str  # 歌曲名称
    singer_name: str  # 歌手名称
    music_url: Optional[str] = field(default=None)  # 音乐链接


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
        t = time.time() * 10000
        params = {"_t": t}
        tar_str = json.dumps(params)
        s = md5(tar_str.encode()).hexdigest()
        params["token"] = s
        session = HTMLSession(cls.headers)
        res = session.post(cls.recommend_url)
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
