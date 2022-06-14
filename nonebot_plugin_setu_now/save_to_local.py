import os
from pathlib import Path

from anyio import open_file
from nonebot import get_driver
from nonebot.log import logger

from .config import Config
from .models import Setu

plugin_config = Config.parse_obj(get_driver().config.dict())

setu_path = plugin_config.setu_path

if not setu_path:
    setu_path = Path("./data/setu").absolute()
if os.path.exists(setu_path):
    logger.success(f"setu将保存到 {setu_path}")
else:
    os.makedirs(setu_path, exist_ok=True)
    logger.success(f"创建文件夹 {setu_path}")
    logger.info(f"setu将保存到 {setu_path}")


async def save_img(setu: Setu):
    info = "{}_{}_{}_{}".format(setu.pid, setu.p, setu.title, setu.author).replace(
        "/", "-"
    )
    path = Path(f"{setu_path}{'r18' if setu.r18 else '' }/{info}.jpg")
    async with await open_file(path, "wb+") as f:
        await f.write(setu.img)  # type: ignore
    logger.info(f"图片已保存 {path}")
