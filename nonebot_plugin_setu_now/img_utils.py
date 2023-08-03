from io import BytesIO
from random import choice, randint
from typing import Union
from pathlib import Path

from PIL import Image, ImageFilter
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import SEND_AS_BYTES
from .perf_timer import PerfTimer


def image_param_converter(source: Union[Path, Image.Image, bytes]) -> Image.Image:
    FORCE_RESIZE = True
    IMAGE_RESIZE_RES = 1080  # 限制被处理图片最大为1080P

    def resize_converter(img: Image.Image):
        if not FORCE_RESIZE:
            return img
        image_landscape = img.width >= img.height
        if min(*img.size) <= IMAGE_RESIZE_RES:
            return img
        if image_landscape:
            resize_res = (
                int(IMAGE_RESIZE_RES / img.height * img.width),
                IMAGE_RESIZE_RES,
            )
        else:
            resize_res = (
                IMAGE_RESIZE_RES,
                int(IMAGE_RESIZE_RES / img.width * img.height),
            )
        logger.debug(f"Effect force resize: {img.size} -> {resize_res}")
        return img.resize(resize_res)

    if isinstance(source, Path):
        return resize_converter(Image.open(source))
    if isinstance(source, Image.Image):
        return resize_converter(source)
    if isinstance(source, bytes):
        return resize_converter(Image.open(BytesIO(source)))
    raise ValueError(f"Unsopported image type: {type(source)}")


def draw_frame(img: Union[Path, Image.Image, bytes]) -> Image.Image:
    """画边框"""
    img = image_param_converter(img)
    BLUR_HEIGHT_QUALITY = 128
    FRAME_RATIO = 1.5
    resize_resoluation = (
        int(img.width * (BLUR_HEIGHT_QUALITY / img.height)),
        BLUR_HEIGHT_QUALITY,
    )
    background = img
    background = background.resize(resize_resoluation)
    background = background.filter(ImageFilter.GaussianBlur(6))
    background = background.resize(
        (int(img.width * FRAME_RATIO), int(img.height * FRAME_RATIO))
    )
    background.paste(
        img,
        (
            int((background.width - img.width) / 2),
            int((background.height - img.height) / 2),
        ),
    )
    return background


def random_rotate(img: Union[Path, Image.Image, bytes]) -> Image.Image:
    """随机旋转角度"""
    img = image_param_converter(img)
    a = float(randint(0, 360))
    img = img.rotate(angle=a, expand=True)
    return img


def random_flip(img: Union[Path, Image.Image, bytes]) -> Image.Image:
    """随机翻转"""
    img = image_param_converter(img)
    t = [Image.Transpose.FLIP_TOP_BOTTOM, Image.Transpose.FLIP_LEFT_RIGHT]
    img = img.transpose(choice(t))
    return img


def random_lines(img: Union[Path, Image.Image, bytes]) -> Image.Image:
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


def do_nothing(img: Path) -> Path:
    return img


def image_segment_convert(img: Union[Path, Image.Image, bytes]) -> MessageSegment:
    if isinstance(img, Path):
        # 将图片读取
        if SEND_AS_BYTES:
            img = Image.open(img)
        else:
            return MessageSegment.image(img)
    elif isinstance(img, bytes):
        img = Image.open(BytesIO(img))
    elif isinstance(img, Image.Image):
        pass
    else:
        raise ValueError(f"Unsopported image type: {type(img)}")
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
