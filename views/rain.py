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
)

from methods.getmusics import DataSong
from methods.getmusics import HIFINI
from utils import snack_bar, ms_to_time, handle_redirect, download_url_content, DESKTOP


class Song(Row):
    """
    每首歌的展示条
    """

    def __init__(self, song: DataSong, select_callback):
        self.song: DataSong = song
        self.select_callback = select_callback
        self.photo = Image(
            src=song.photo_url,
            width=40,
            height=40,
            border_radius=10,
            fit="cover",
        )
        self.music = Text(
            song.music_name,
            width=200,
            height=20,
            no_wrap=True,
            weight="bold",
            tooltip=song.music_name,
        )
        self.singer = Text(
            song.singer_name,
            width=80,
            height=20,
            no_wrap=True,
            weight="bold",
            tooltip=song.singer_name,
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
        super(Song, self).__init__(
            controls=[self.container],
            alignment="start",
            scroll=None,
            wrap=True,
        )
        self.__selected = False

    @property
    def selected(self):
        return self.__selected

    @selected.setter
    def selected(self, value: bool):
        self.__selected = value
        if value is True:
            self.container.bgcolor = colors.BLUE_GREY_700
            self.container.opacity = 1
            self.update()
            self.select_callback(self)
        else:
            self.container.bgcolor = colors.BLUE_GREY_300
            self.container.opacity = 0.7
            self.update()

    def on_click(self, e):
        self.selected = True

    def un_select(self):
        self.selected = False


class PlayAudio(Audio):
    def __init__(self, song: DataSong, *args, **kwargs):
        self.song = song
        self.during: Optional[int] = None
        super(PlayAudio, self).__init__(*args, **kwargs)

    def update_during(self, during):
        # 将总时长记录下来，就不需要每次重新获取了
        self.during = during


class SearchCompoment(Row):
    """
    搜索音乐的组件
    """

    def __init__(self, search_callback):
        self.music_api = HIFINI
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
        super(SearchCompoment, self).__init__(
            controls=[self.search_input, self.submit_btn],
            alignment="center",
            vertical_alignment="center",
        )

    def search(self, e):
        self.search_callback(self.search_input.value)


class MusicList(Row):
    """
    展示查询音乐列表的区域
    """

    def __init__(self, select_callback):
        self.select_callback = select_callback
        self.list = ListView(width=400, height=450, spacing=10, padding=10)
        super(MusicList, self).__init__(
            controls=[self.list], alignment="center", vertical_alignment="center"
        )

    def set_musics(self, data: DataSong, first=False):
        if first:
            self.list.controls.clear()
        self.list.controls.append(Song(data, self.middle_select_callback))
        self.update()

    def next_music(self):
        c = self.list.controls
        for i in range(len(c) - 1):
            if c[i].selected:
                c[i + 1].on_click(None)
                return
        c[0].on_click(None)

    def middle_select_callback(self, song: Song):
        for _song in self.list.controls:
            if _song.selected:
                if _song != song:
                    _song.un_select()
        self.select_callback(song)


class AudioInfo(Row):
    """
    展示播放时的图片，名称和歌手名称
    """

    def __init__(self):
        self.audio_photo = Card(
            width=200,
            height=200,
            elevation=10,
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

    def set_info(self, song: DataSong):
        self.audio_photo.content = Image(song.big_photo_url, fit="cover")
        self.audio_name.value = song.music_name
        self.audio_singer.value = song.singer_name
        self.update()


class AudioBar(Row):
    """
    播放进度条和控制按钮
    """

    def __init__(self, root: 'ViewPage'):
        self.root = root
        self.song: Optional[DataSong] = None
        self.playing_audio: Optional[PlayAudio] = None
        self.is_sliding = False
        self.curr_time = Text("00:00")
        self.control_bar = Slider(
            on_change_start=self.on_change_start,
            on_change=self.on_change,
            on_change_end=self.on_change_end,
            on_focus=lambda e: print("on focus", e.data),
            disabled=False,
        )
        self.total_time = Text("00:00")
        self.popup_menu = PopupMenuButton(
            items=[PopupMenuItem(text="下载歌曲", on_click=self.download_music)]
        )
        self.play_btn = IconButton(
            icon=icons.PLAY_CIRCLE,
            selected_icon=icons.PAUSE_CIRCLE,
            on_click=self.toggle_play,
            icon_size=40,
        )
        self.play_type_btn = IconButton(
            icon=icons.PLAYLIST_PLAY_ROUNDED,
            selected_icon=icons.REPLAY_CIRCLE_FILLED_ROUNDED,
            on_click=self.toggle_play_type,
            icon_size=40,
        )
        self.row1 = Row(
            controls=[
                self.curr_time,
                self.control_bar,
                self.total_time,
                self.popup_menu,
            ]
        )
        self.row2 = Row(controls=[self.play_btn, self.play_type_btn])
        super(AudioBar, self).__init__(
            controls=[Column([self.row1, self.row2], horizontal_alignment="center")],
            alignment="center",
            vertical_alignment="center",
        )

    def play(self, song: Optional[DataSong] = None):
        if song is None:
            if self.song is not None:
                self.playing_audio.play()
                self.play_btn.selected = True
                self.update()
                return
            else:
                return
        if self.song and self.song.music_url == song.music_url:
            self.playing_audio.play()
        else:
            self.song = song
            if self.playing_audio in self.page.overlay:
                self.page.overlay.remove(self.playing_audio)
            # 双重保险
            for i in self.page.overlay[:]:
                if isinstance(i, PlayAudio):
                    self.page.overlay.remove(i)

            self.playing_audio = PlayAudio(
                song=song,
                src=handle_redirect(song.music_url),
                autoplay=False,
                volume=100,
                balance=0,
                release_mode=audio.ReleaseMode.STOP,
                on_loaded=self.loaded,
                on_duration_changed=self.during_changed,
                on_position_changed=self.position_changed,
                on_state_changed=self.state_changed,
                on_seek_complete=self.seek_complete,
            )

            self.page.overlay.append(self.playing_audio)
            self.page.update()
            self.playing_audio.play()

    def resume(self):
        self.playing_audio.resume()
        self.play_btn.selected = False
        self.update()

    def pause(self):
        self.playing_audio.pause()
        self.play_btn.selected = True
        self.update()

    def next_music(self, e=None):
        self.root.right_widget.music_list.next_music()

    def release(self):
        self.playing_audio.release()
        self.play_btn.selected = False
        self.update()

    def loaded(self, e):
        # print("on loaded", e.data)
        pass

    def during_changed(self, e):
        # 歌曲总时长发生了改变
        during = int(e.data)
        self.playing_audio.update_during(during)
        self.total_time.value = ms_to_time(during)
        self.update()

    def position_changed(self, e):
        during = float(e.data)
        self.curr_time.value = ms_to_time(during)
        percent = (
            during / self.playing_audio.during
            if self.playing_audio.during
            else self.playing_audio.get_duration()
        )
        if not self.is_sliding:
            self.control_bar.value = percent
            # if during == self.playing_audio.during != 0:
            #         print(during)
            #         print(self.playing_audio.during)
            #         self.next_music(None)

        self.update()

    def state_changed(self, e):
        status = e.data
        if status == "playing":
            self.play_btn.selected = True
        else:
            if status == "completed":
                if self.play_type_btn.selected:
                    self.playing_audio.play()
                else:
                    self.next_music(None)
            self.play_btn.selected = False
        self.update()

    def seek_complete(self, e):
        pass

    def toggle_play(self, e):
        if e.control.selected:
            self.pause()
        else:
            self.resume()

    def toggle_play_type(self, e):
        self.play_type_btn.selected = not e.control.selected
        self.update()

    def on_change_start(self, e):
        self.is_sliding = True

    def on_change(self, e):
        target_during = float(e.data) * self.playing_audio.during
        self.playing_audio.seek(int(target_during))
        self.update()

    def on_change_end(self, e):
        self.is_sliding = False

    def download_music(self, e):
        if self.song is None:
            return
        music_name = self.song.music_name
        music_singer = self.song.singer_name
        name = music_name + "_" + music_singer + ".mp3"
        url = self.song.music_url
        resp = download_url_content(url)
        with open(DESKTOP + "/" + name, "wb") as f:
            f.write(resp.content)
        snack_bar(self.page, f"{name} 已保存至桌面")


class RightSearchSection(Column):
    """右侧区域"""

    def __init__(self, parent: "ViewPage"):
        self.parent = parent
        self.music_list = MusicList(self.parent.select_callback)
        self.search_content = SearchCompoment(self.parent.search_callback)
        super(RightSearchSection, self).__init__(
            controls=[self.search_content, self.music_list],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        )


class LeftPlaySection(Column):
    """左侧区域"""

    def __init__(self, parent):
        self.parent = parent
        self.playing_song: Optional[PlayAudio] = None
        self.audio_info = AudioInfo()
        self.audio_bar = AudioBar(self.parent)
        super(LeftPlaySection, self).__init__(
            controls=[self.audio_info, self.audio_bar],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        )

    def play_music(self, song: Song):
        self.audio_info.set_info(song.song)
        self.audio_bar.play(song.song)


class ViewPage(Stack):
    def __init__(self, page):
        self.music_api = HIFINI
        self.left_widget = LeftPlaySection(self)
        self.right_widget = RightSearchSection(self)
        self.row = Row(
            controls=[self.left_widget, self.right_widget],
            alignment="spaceAround",
            vertical_alignment="center",
            expand=True,
        )
        super(ViewPage, self).__init__(controls=[self.row], expand=True)
        self.page = page

    def init_event(self):
        if not self.right_widget.music_list.list.controls:
            self.right_widget.search_content.search(None)

    def select_callback(self, song: Song):
        self.left_widget.play_music(song)

    def search_callback(self, target):
        flag = False
        for song in self.music_api.search_musics(target):
            if isinstance(song, tuple):
                snack_bar(self.page, f"音乐api出错: {song[1]}")
                return
            else:
                if not flag:
                    self.right_widget.music_list.set_musics(song, first=True)
                    flag = True
                else:
                    self.right_widget.music_list.set_musics(song)

# def main(page: Page):
#     page.vertical_alignment = "center"
#     page.horizontal_alignment = "center"
#
#     page.add(ViewPage(page))
#
#
# flet.app(target=main)
