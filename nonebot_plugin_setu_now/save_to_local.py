import os
from anyio import open_file
from nonebot import get_driver
from nonebot.log import logger
from PIL import Image
from io import BytesIO
from .models import SetuData

from .config import Config

plugin_config = Config.parse_obj(get_driver().config.dict())

setu_path = plugin_config.setu_path

if not setu_path:
    setu_path = os.path.abspath("data/setu")
if os.path.exists(setu_path):
    logger.success(f"setu将保存到 {setu_path}")
else:
    os.makedirs(setu_path, exist_ok=True)
    logger.success(f"创建文件夹 {setu_path}")
    logger.info(f"setu将保存到 {setu_path}")


async def save_img(setu: SetuData):
    path = f"{setu_path}{'r18' if setu.r18 else '' }/{setu.pid}_{setu.p}_{setu.title}_{setu.author}.jpg"
    async with await open_file(path, "wb") as f:
        await f.write(setu.img)  # type: ignore
    logger.info(f"图片已保存{path}")
