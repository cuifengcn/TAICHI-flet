from typing import List
from typing import Optional

from flet import (
    Container,
    Row,
    Text,
    Image,
    ListView,
    colors,
    Stack,
    border,
    TextField,
    FloatingActionButton,
    Column,
    Card,
    IconButton,
    icons,
    Audio,
    audio,
    Slider,
    PopupMenuButton,
    PopupMenuItem,
    Icon,
)

from methods.getmusics import DataSong
from utils import snack_bar, ms_to_time, handle_redirect, download_url_content, DESKTOP
from methods.getmusics import LiuMingYe

_music_url = "https://test.quanjian.com.cn/m/api/link/id/{id}/quality/128"


class Song(Row):
    """
    每首歌的展示条
    """

    def __init__(self, data_song: DataSong, play_callback):
        self.data_song: DataSong = data_song
        self.photo_url = data_song.photo_url
        self.photo = Image(
            src=data_song.photo_url.format(size=40),
            width=40,
            height=40,
            border_radius=10,
            fit="cover",
        )
        if data_song.music_url is None:
            self.music_url = _music_url.format(id=data_song.music_id)
        else:
            self.music_url = data_song.music_url
        self.music = Text(
            data_song.music_name,
            width=200,
            height=20,
            no_wrap=True,
            weight="bold",
            tooltip=data_song.music_name,
        )
        self.singer = Text(
            data_song.singer_name,
            width=80,
            height=20,
            no_wrap=True,
            weight="bold",
            tooltip=data_song.singer_name,
        )
        self.container = Container(
            content=Row([self.photo, self.music, self.singer], spacing=10),
            on_click=self.on_click,
            bgcolor=colors.BLUE_GREY_300,
            padding=5,
            opacity=0.6,
            animate=300,
            border_radius=10,
            border=border.all(width=1),
        )
        self.play_callback = play_callback
        self.clicked = False
        super(Song, self).__init__(
            controls=[self.container],
            alignment="start",
            scroll=None,
            wrap=True,
        )

    def on_click(self, e):
        self.clicked = True
        self.container.bgcolor = colors.BLUE_GREY_700
        self.container.opacity = 1
        self.play_callback(self)
        self.update()

    def not_click(self):
        self.clicked = False
        self.container.bgcolor = colors.BLUE_GREY_300
        self.container.opacity = 0.7
        self.update()


class PlayAudio(Audio):
    def __init__(self, song: Song, *args, **kwargs):
        self.song = song
        self.during: Optional[int] = None
        super(PlayAudio, self).__init__(*args, **kwargs)


class MusicList(Row):
    """
    展示查询音乐列表的区域
    """

    def __init__(self, play_callback):
        self.play_callback = play_callback
        self.list = ListView(width=400, height=450, spacing=10, padding=10)
        super(MusicList, self).__init__(
            controls=[self.list], alignment="center", vertical_alignment="center"
        )

    @property
    def datas(self):
        return self.list.controls

    def show_musics(self, datas: List[DataSong]):
        if not datas:
            snack_bar(self.page, "查询结果为空")
            return
        if self.datas:
            self.datas.clear()
        for data in datas:
            self.datas.append(Song(data, self.click_song))
        self.update()

    def click_song(self, song: Song):
        for _song in self.datas:
            if _song.clicked:
                if _song != song:
                    _song.not_click()
                else:
                    self.play_callback(_song)


class MusicSearch(Row):
    """
    搜索音乐的组件
    """

    def __init__(self, search_callback):
        self.music_api = LiuMingYe
        self.search_callback = search_callback
        self.search_input = TextField(
            label="请输入歌曲名称或歌手名称",
            width=300,
            height=40,
            on_submit=self.search,
        )
        self.submit_btn = FloatingActionButton(
            "搜索", on_click=self.search, height=40, width=80, autofocus=True
        )
        super(MusicSearch, self).__init__(
            controls=[self.search_input, self.submit_btn],
            alignment="center",
            vertical_alignment="center",
        )

    def search(self, e):
        target = self.search_input.value
        if not target:
            datas_generate = self.music_api.recommend_musics()
        else:
            datas_generate = self.music_api.search_musics(target)
        tmp = []
        for data in datas_generate:
            if isinstance(data, tuple):
                snack_bar(self.page, f"获取歌曲失败: {data[1]}")
            else:
                tmp.append(data)
        self.search_callback(tmp)


class AudioInfo(Row):
    """
    展示播放时的图片，名称和歌手名称
    """

    def __init__(self):
        self.audio_photo = Card(
            width=200,
            height=200,
            elevation=5,
        )
        self.audio_name = Text("", size=18)
        self.audio_singer = Text("", size=14)
        self.column = Column(
            controls=[self.audio_photo, self.audio_name, self.audio_singer],
            alignment="center",
            horizontal_alignment="center",
        )
        super(AudioInfo, self).__init__(
            controls=[self.column],
            width=300,
            height=400,
            vertical_alignment="center",
            alignment="center",
        )

    def set_info(self, song: Song):
        self.audio_photo.content = Image(
            song.data_song.photo_url.format(size=500), fit="cover"
        )
        self.audio_name.value = song.data_song.music_name
        self.audio_singer.value = song.data_song.singer_name
        self.update()


class AudioBar(Row):
    """
    播放进度条和控制按钮
    """

    def __init__(self):
        self.playing_song: Optional[PlayAudio] = None
        self.setting_position = False
        self.curr_time = Text("00:00")
        self.control_bar = Slider(
            on_change=self.set_position,
            on_focus=lambda e: print("on focus", e.data),
            disabled=True,
        )
        self.total_time = Text("00:00")
        self.popup_menu = PopupMenuButton(
            items=[
                PopupMenuItem(text="下载歌曲", on_click=self.download_music)
            ]
        )
        self.play_btn = IconButton(
            icon=icons.PLAY_CIRCLE,
            selected_icon=icons.PAUSE_CIRCLE,
            on_click=self.toggle_play,
            icon_size=40,
        )
        self.row1 = Row(controls=[self.curr_time, self.control_bar, self.total_time, self.popup_menu])
        self.row2 = Row(controls=[self.play_btn])
        super(AudioBar, self).__init__(
            controls=[Column([self.row1, self.row2], horizontal_alignment="center")],
            alignment="center",
            vertical_alignment="center",
        )

    def set_playing_song(self, song: PlayAudio):
        self.playing_song = song

    def toggle_play(self, e):
        if self.playing_song is None:
            return
        try:
            if not e.control.selected:
                self.playing_song.resume()
            else:
                self.playing_song.pause()
            e.control.selected = not e.control.selected
            self.update()
        except Exception as e:
            print("Error: toggle_play:", e)

    def update_status(self, status):
        if status == "playing":
            try:
                total_during = self.playing_song.get_duration()
            except Exception as e:
                print(e)
                return
            else:
                self.total_time.value = ms_to_time(total_during)
                self.play_btn.selected = True
                self.update()
        else:
            self.play_btn.selected = False
            self.update()

    def update_during(self, e):
        # 更新总时长
        during = int(e.data)
        self.playing_song.during = during
        self.total_time.value = ms_to_time(during)
        self.update()

    def set_during(self, e):
        # 设置总时长
        total_during = int(e.data)
        self.total_time.value = ms_to_time(total_during)
        self.update()

    def update_position(self, e):
        # 更新当前播放位置
        if self.setting_position:
            return
        during = float(e.data)
        self.curr_time.value = ms_to_time(during)
        percent = during / self.playing_song.during
        self.control_bar.value = percent
        self.update()

    def set_position(self, e):
        self.setting_position = True
        if self.playing_song is not None and self.playing_song.during is not None:
            target_during = float(e.data) * self.playing_song.during
            curr_during = self.playing_song.get_current_position()
            self.playing_song.seek(int(target_during - curr_during))
            self.curr_time.value = ms_to_time(target_during)
            self.update()
        self.setting_position = False

    def set_playing(self):
        # 切换为播放状态
        self.play_btn.selected = True
        self.playing_song.resume()
        self.update()

    def download_music(self, e):
        if self.playing_song is None:
            return
        music_name = self.playing_song.song.data_song.music_name
        music_singer = self.playing_song.song.data_song.singer_name
        name = music_name + "_" + music_singer + ".mp3"
        url = self.playing_song.song.music_url
        resp = download_url_content(url)
        with open(DESKTOP + "/" + name, "wb") as f:
            f.write(resp.content)
        snack_bar(self.page, f"{name} 已保存至桌面")


class RightSearchSection(Column):
    """右侧区域"""

    def __init__(self, play_song_func):
        self.music_list = MusicList(play_song_func)
        self.search_content = MusicSearch(search_callback=self.music_list.show_musics)
        super(RightSearchSection, self).__init__(
            controls=[self.search_content, self.music_list],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        )


class LeftPlaySection(Column):
    """左侧区域"""

    def __init__(self, page):
        self.page = page
        self.playing_song: Optional[PlayAudio] = None
        self.audio_info = AudioInfo()
        self.audio_bar = AudioBar()
        super(LeftPlaySection, self).__init__(
            controls=[self.audio_info, self.audio_bar],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        )

    def play_new_song(self, song: Song):
        if not song.music_url:
            snack_bar(self.page, "歌曲源未找到")
            return
        self.audio_info.set_info(song)
        if self.playing_song is not None:
            if song.music_url == self.playing_song.song.music_url:
                self.playing_song.play()
                return
            else:
                self.playing_song.release()
            if self.playing_song in self.page.overlay:
                self.page.overlay.remove(self.playing_song)
        music_url = handle_redirect(song.music_url)
        self.playing_song = PlayAudio(
            song=song,
            src=music_url,
            autoplay=True,
            volume=100,
            balance=0,
            release_mode=audio.ReleaseMode.LOOP,
            on_loaded=self.loaded,
            on_duration_changed=self.during_changed,
            on_position_changed=self.position_changed,
            on_state_changed=self.state_changed,
            on_seek_complete=self.seek_complete,
        )
        self.audio_bar.set_playing_song(self.playing_song)
        self.page.overlay.append(self.playing_song)
        self.page.update()
        self.playing_song.play()

    def loaded(self, e):
        print("on loaded", e.data)

    def during_changed(self, e):
        self.audio_bar.update_during(e)

    def position_changed(self, e):
        self.audio_bar.update_position(e)

    def state_changed(self, e):
        status = e.data
        self.audio_bar.update_status(status)

    def seek_complete(self, e):
        pass


class ViewPage(Stack):
    def __init__(self, page):
        self.left_widget = LeftPlaySection(page)
        self.right_widget = RightSearchSection(self.left_widget.play_new_song)
        self.row = Row(
            controls=[self.left_widget, self.right_widget],
            alignment="spaceAround",
            vertical_alignment="center",
            expand=True,
        )
        super(ViewPage, self).__init__(controls=[self.row], expand=True)
        self.page = page

    def init_event(self):
        self.right_widget.search_content.search(None)

# def main(page: Page):
#     page.vertical_alignment = "center"
#     page.horizontal_alignment = "center"
#
#     page.add(ViewPage(page))
#
#
# flet.app(target=main)
