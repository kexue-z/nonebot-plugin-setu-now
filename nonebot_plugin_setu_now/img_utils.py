from io import BytesIO
from random import choice, choices, randint
from typing import Optional

from PIL import Image


def randon_rotate(img: Image.Image) -> Image.Image:
    """随机旋转角度"""
    a = float(randint(0, 360))
    img = img.rotate(angle=a, expand=True)
    return img


def randon_flip(img: Image.Image) -> Image.Image:
    """随机翻转"""
    t = [Image.Transpose.FLIP_TOP_BOTTOM, Image.Transpose.FLIP_TOP_BOTTOM]
    img = img.transpose(choice(t))
    return img


def randon_lines(img: Image.Image) -> Image.Image:
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


def randon_effect(img: bytes, effect: Optional[int] = None) -> BytesIO:
    """
    :说明: `randon_effect`
    > 随机处理图片，可指定方法

    :参数:
      * `img: bytes`: 图片
      * `effect: Optional[int]`: 特效: 0 啥也不做 1 随机旋转 2 随机翻转 3 随机画线

    :返回:
      - `BytesIO`: 处理好的图
    """

    f = BytesIO(img)
    _img = Image.open(f)

    funcs = {
        1: [do_nothing, randon_rotate, randon_flip, randon_lines],
        2: [0.1, 0.3, 0.3, 0.3],
    }

    if effect:
        func = funcs[1][effect]
    else:
        func = choices(population=funcs[1], weights=funcs[2], k=1)
    output: Image.Image = func[0](_img)
    buffer = BytesIO()
    output.convert("RGB").save(buffer, "jpeg")

    return buffer
