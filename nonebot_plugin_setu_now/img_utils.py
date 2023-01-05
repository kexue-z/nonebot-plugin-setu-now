import time
from io import BytesIO
from random import choice, choices, randint
from typing import Union, Optional
from pathlib import Path

from PIL import Image, ImageFilter
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .perf_timer import PerfTimer


def image_param_converter(source: Union[str, Image.Image, bytes]) -> Image.Image:
    if isinstance(source, str):
        return Image.open(Path(source))
    if isinstance(source, Image.Image):
        return source
    if isinstance(source, bytes):
        return Image.open(BytesIO(source))
    raise ValueError(f"Unsopported image type: {type(source)}")


def draw_frame(img: Union[str, Image.Image, bytes]) -> Image.Image:
    """画边框"""
    img = image_param_converter(img)
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


def random_rotate(img: Union[str, Image.Image, bytes]) -> Image.Image:
    """随机旋转角度"""
    img = image_param_converter(img)
    a = float(randint(0, 360))
    img = img.rotate(angle=a, expand=True)
    return img


def random_flip(img: Union[str, Image.Image, bytes]) -> Image.Image:
    """随机翻转"""
    img = image_param_converter(img)
    t = [Image.Transpose.FLIP_TOP_BOTTOM, Image.Transpose.FLIP_LEFT_RIGHT]
    img = img.transpose(choice(t))
    return img


def random_lines(img: Union[str, Image.Image, bytes]) -> Image.Image:
    """随机画黑线"""
    img = image_param_converter(img)
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


def do_nothing(img: str) -> str:
    return img


def image_segment_convert(img: Union[str, Image.Image, bytes]) -> MessageSegment:
    if isinstance(img, str):
        return MessageSegment.image(Path(img))
    if isinstance(img, bytes):
        img = Image.open(BytesIO(img))
    image_bytesio = BytesIO()
    save_timer = PerfTimer.start(f"Save bytes {img.width} x {img.height}")
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(
        image_bytesio,
        format="JPEG",
        quality="keep" if img.format in ("JPEG", "JPG") else 95,
    )
    save_timer.stop()
    return MessageSegment.image(image_bytesio)  # type: ignore


EFFECT_FUNC_LIST = [do_nothing, draw_frame, random_flip, random_lines, random_rotate]
