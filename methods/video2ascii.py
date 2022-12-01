import os

import cv2
from PIL import Image, ImageFont, ImageDraw

ascii_char = list(
    "$B%314567890*WM#oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:oa+>!:+. "
)


class VideoToAscii:
    # VideoToAscii("../end_video.mp4", "d://", print).video_to_ascii()
    def __init__(
        self, input_file_name, output_path, msg_callback, color_radio=1, scale_scale=100
    ):
        self.input_file_name = input_file_name
        self.output_path = output_path
        self.output_file_name_prefix = (
            self.output_path
            + "/"
            + os.path.basename(self.input_file_name).split(".")[0]
        )
        self.message = msg_callback
        self.color_radio = color_radio  # (1是彩色模式 其他是黑白模式)
        self.scale_scale = scale_scale  # 缩放比例 0-100
        self.total_length = 0

    def video_to_ascii(self):
        if not self.input_file_name:
            return
        vc = self.video2txt_jpg()
        FPS = vc.get(cv2.CAP_PROP_FPS)  # 获取帧率
        vc.release()

        self.jpg2video(FPS)
        # self.message(self.output_file_name_prefix + ".mp3")
        # self.video2mp3(INPUT)
        # self.video_add_mp3(INPUT.split('.')[-2] + '.avi', INPUT.split('.')[-2] + '.mp3', OUTPUT)

        self.remove_dir("Cache")
        # os.remove(self.input_path.split(".")[-2] + ".mp3")
        # os.remove(self.input_path.split(".")[-2] + ".avi")
        self.message(100)

    def video2txt_jpg(self):
        # 将视频拆分成图片
        vc = cv2.VideoCapture(self.input_file_name)
        self.total_length = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        c = 1
        if vc.isOpened():
            r, frame = vc.read()
            if not os.path.exists("Cache"):
                os.mkdir("Cache")
            os.chdir("Cache")
        else:
            r = False
        while r:
            cv2.imwrite(str(c) + ".jpg", frame)
            self.txt2image(str(c) + ".jpg")  # 同时转换为ascii图
            r, frame = vc.read()
            c += 1
        os.chdir("..")
        return vc

    def txt2image(self, file_name):
        # 将txt转换为图片
        im = Image.open(file_name).convert("RGB")
        im_width = im.width
        im_height = im.height
        im = im.resize(
            (
                int(im.width / 100 * self.scale_scale),
                int(im.height / 100 * self.scale_scale),
            ),
            Image.Resampling.NEAREST,
        )
        # gif拆分后的图像，需要转换，否则报错，由于gif分割后保存的是索引颜色
        raw_width = im.width
        raw_height = im.height
        width = int(raw_width / 6)
        height = int(raw_height / 15)
        im = im.resize((width, height), Image.Resampling.NEAREST)

        txt = ""
        colors = []
        for i in range(height):
            for j in range(width):
                pixel = im.getpixel((j, i))
                if self.color_radio == 1:
                    colors.append((pixel[0], pixel[1], pixel[2]))
                else:
                    colors.append((0, 0, 0))
                if len(pixel) == 4:
                    txt += self.get_char(pixel[0], pixel[1], pixel[2], pixel[3])
                else:
                    txt += self.get_char(pixel[0], pixel[1], pixel[2])
            txt += "\n"
            colors.append((255, 255, 255))

        im_txt = Image.new("RGB", (raw_width, raw_height), (255, 255, 255))
        dr = ImageDraw.Draw(im_txt)
        # font = ImageFont.truetype(os.path.join("fonts","timesbi.ttf"),12)
        font = ImageFont.load_default().font

        x = y = 0
        # 获取字体的宽高
        font_w, font_h = font.getsize(txt[1])
        font_h *= 1.37  # 调整后更佳
        # ImageDraw为每个ascii码进行上色
        for i in range(len(txt)):
            if txt[i] == "\n":
                x += font_h
                y = -font_w
            dr.text((y, x), txt[i], fill=colors[i])
            y += font_w

        name = file_name
        self.message(int(name.split(".")[0]) / self.total_length * 0.9)
        im_txt = im_txt.resize((im_width, im_height), Image.Resampling.NEAREST)
        im_txt.save(name)

    def jpg2video(self, fps):
        # 将图片合成视频
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        images = os.listdir("Cache")
        im = Image.open("Cache/" + images[0])
        if os.path.exists(self.output_file_name_prefix + "avi"):
            os.remove(self.output_file_name_prefix + "avi")
        vw = cv2.VideoWriter(
            self.output_file_name_prefix + ".avi", fourcc, fps, im.size
        )

        os.chdir("Cache")
        for image in range(len(images)):
            # Image.open(str(image)+'.jpg').convert("RGB").save(str(image)+'.jpg')
            frame = cv2.imread(str(image + 1) + ".jpg")
            vw.write(frame)
            self.message((image + 1) / self.total_length / 10 * 0.1 + 0.9)
        os.chdir("..")
        vw.release()

    # 将像素点转换为ascii码
    def get_char(self, r, g, b, alpha=256):
        if alpha == 0:
            return ""
        length = len(ascii_char)
        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        unit = (256.0 + 1) / length
        return ascii_char[int(gray / unit)]

    # 递归删除目录
    def remove_dir(self, path):
        if os.path.exists(path):
            if os.path.isdir(path):
                dirs = os.listdir(path)
                for d in dirs:
                    if os.path.isdir(path + "/" + d):
                        self.remove_dir(path + "/" + d)
                    elif os.path.isfile(path + "/" + d):
                        os.remove(path + "/" + d)
                os.rmdir(path)
                return
            elif os.path.isfile(path):
                os.remove(path)
