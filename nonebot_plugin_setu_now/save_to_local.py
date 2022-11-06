import os
from pathlib import Path

from anyio import open_file
from nonebot import get_driver
from nonebot.log import logger

from nonebot_plugin_setu_now.config import Config
from nonebot_plugin_setu_now.models import Setu

plugin_config = Config.parse_obj(get_driver().config.dict())

setu_path = Path(plugin_config.setu_path) if plugin_config.setu_path else None

if not setu_path:
    setu_path = Path("./data/setu").absolute()
    
setur18_path = setu_path / "r18"

if setu_path.exists() and setur18_path.exists():
    logger.success(f"setu将保存到 {setu_path}")
else:
    os.makedirs(setu_path, exist_ok=True)
    logger.success(f"创建文件夹 {setu_path}")
    logger.info(f"setu将保存到 {setu_path}")


async def save_img(setu: Setu):
    info = "{}_{}".format(setu.pid, setu.p)
    path = Path(f"{setu_path}{'r18' if setu.r18 else '' }/{info}.jpg")
    async with await open_file(path, "wb+") as f:
        await f.write(setu.img)  # type: ignore
    logger.info(f"图片已保存 {path}")
