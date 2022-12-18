import time
from io import BytesIO
from random import choice, choices, randint
from typing import Optional

from PIL import Image, ImageFilter
from nonebot.log import logger


def draw_frame(img: Image.Image) -> Image.Image:
    """画边框"""
    BLUR_HEIGHT_QUALITY = 128
    resize_resoluation = (
        int(img.width * (BLUR_HEIGHT_QUALITY / img.height)),
        BLUR_HEIGHT_QUALITY,
    )
    background = img
    background = background.resize(resize_resoluation)
    background = background.filter(ImageFilter.GaussianBlur(6))
    background = background.resize((img.width * 2, img.height * 2))
    background.paste(img, (int(img.width / 2), int(img.height / 2)))
    return background


def random_rotate(img: Image.Image) -> Image.Image:
    """随机旋转角度"""
    a = float(randint(0, 360))
    img = img.rotate(angle=a, expand=True)
    return img


def random_flip(img: Image.Image) -> Image.Image:
    """随机翻转"""
    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return img


def random_lines(img: Image.Image) -> Image.Image:
    """随机画黑线"""
    from PIL import ImageDraw

    x, y = img.size
    draw = ImageDraw.Draw(img)
    line_width = round(min(x, y) * 0.001)

    def random_line():
        start_point = end_point = (0, 0)
        x_y = randint(0, 1)
        if x_y:
            # 横
            start_point = (0, randint(0, y))
            end_point = (y, randint(0, y))
        else:
            # 竖
            start_point = (randint(0, x), 0)
            end_point = (randint(0, x), y)

        draw.line((start_point, end_point), fill=0, width=line_width)

    for _ in range(randint(0, 10)):
        random_line()
    return img


def do_nothing(img: Image.Image) -> Image.Image:
    return img


EFFECT_FUNC_LIST = [do_nothing, draw_frame, random_flip, random_lines, random_rotate]
