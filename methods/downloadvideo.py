import re
import json
import uuid
import shutil
import m3u8
import base64
from uuid import uuid4
from typing import List
from pathlib import Path
from utils import HTMLSession
from utils import CURR_PATH


class YSGC:
    """影视工厂"""

    session = HTMLSession()

    @classmethod
    def download(cls, url):
        video_name, m3u8_true_url = cls.get_m3u8_url(url)
        target_dir = CURR_PATH.joinpath(video_name)
        cls.download_video(m3u8_true_url, target_dir, video_name)

    @classmethod
    def download_video(cls, m3u8_url: str, save_path: Path, video_name: str):
        print(m3u8_url)
        obj = m3u8.load(m3u8_url)
        temp_path = save_path.joinpath(uuid4().hex)
        temp_path.mkdir(exist_ok=True, parents=True)
        files = []
        for i in range(len(obj.files)):
            f = obj.files[i]
            f_name = temp_path.joinpath(f"{i}.ts")
            r = cls.session.get(f)
            f_name.write_bytes(r.content)
            files.append(f_name)
        target_file = save_path.joinpath(video_name + ".mp4")
        files = sorted(files)
        with open(target_file, "ab") as f:
            for sub_f in files:
                f.write(sub_f.read_bytes())
        shutil.rmtree(temp_path)
        print("wancheng")

    @classmethod
    def get_m3u8_url(cls, url: str):
        response = cls.session.get(url)
        video_json = json.loads(
            re.findall(
                r"var player_aaaa=(.*?)</script><script type=", response.text, re.I
            )[0]
        )
        # 获取视频名称
        video_name = (
            video_json.get("vod_data").get("vod_name")
            + " 第"
            + str(video_json.get("nid"))
            + "集"
        )
        # 将得到的字符串进行组合，得到完整的真实网页视频播放界面
        url_value = f"https://www.ysgc.vip/static/player/dplayer.php?url={video_json.get('url')}"
        # 获取真实网页里的 URL 加密数据，后面解密就可以得到m3u8文件了
        base64_str = re.findall(
            "(?<!//)var urls = (.*?);", cls.session.get(url=url_value).text, re.I
        )[0]
        # 解密  [14:-8] 的意思是删除前面14个字符，和后面8个字符
        m3u8_true_url = (base64.b64decode(base64_str.encode()))[14:-8].decode("utf-8")
        response.close()
        # ('蜡笔小新第一季 第1集', 'https://cache.m3u8.dabazuotao.com/ufile/347cc860a70a83560d4ab7b81d7d58a5
        # /e071f84ae747348b559c6ff92f5a7883.m3u8?auth_token=1670348890-2022-100917771
        # -3b4653d0938fcfd7d9fa260bee8120c0')
        return video_name, m3u8_true_url


# print(YSGC.download("https://www.ysgc.vip/vodplay/965-2-1.html"))
# 顺序不对