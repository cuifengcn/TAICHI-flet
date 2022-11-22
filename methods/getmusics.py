from dataclasses import dataclass, field
from typing import Optional
from utils import HTMLSession


@dataclass
class DataSong:
    photo_url: str
    music_name: str
    singer_name: str
    music_id: Optional[str] = field(default=None)
    music_url: Optional[str] = field(default=None)


class LiuMingYe:
    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        # "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "origin": "https://tools.liumingye.cn",
    }
    search_url = "https://test.quanjian.com.cn/m/api/search"
    recommend_url = "https://test.quanjian.com.cn/m/api/home/recommend"

    @classmethod
    def search_musics(cls, target):
        params = {"page": 1, "text": target, "type": "YQM", "v": "beta"}
        session = HTMLSession(cls.headers)
        res = session.post(cls.search_url, data=params)
        if res.status_code != 200 or res.json()["code"] != 200:
            yield False, res.text
        else:
            for data in res.json()["data"]["list"]:
                music_name = data["name"]
                singer_name = data["artist"] and data["artist"][0]["name"]
                music_id = data["id"]
                photo_url = data["pic"]
                yield DataSong(photo_url, music_name, singer_name, music_id=music_id)

    @classmethod
    def recommend_musics(cls):
        session = HTMLSession(cls.headers)
        res = session.post(cls.recommend_url)
        if res.status_code != 200 or res.json()["code"] != 200:
            yield False, res.text
        else:
            for data in res.json()["data"]["recommendSong"]:
                music_name = data["name"]
                singer_name = data["artist"] and data["artist"][0]["name"]
                photo_url = (
                    data.get("pic")
                    or data["album"].get("pic")
                    or "https://picsum.photos/{size}"
                )
                music_url = None
                music_id = None
                if "url" in data and data["url"]:
                    music_url = data["url"]
                elif "hash" in data and data["hash"]:
                    music_id = data["hash"]
                elif "id" in data and data["id"]:
                    music_id = data["id"]
                else:
                    continue
                yield DataSong(
                    photo_url,
                    music_name,
                    singer_name,
                    music_url=music_url,
                    music_id=music_id,
                )
