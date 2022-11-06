from io import BytesIO

from nonebot import get_driver
from nonebot.log import logger
from webdav4.client import Client as dav_client, HTTPError

from .config import Config
from .models import Setu
from .aioutils import asyncify

plugin_config = Config.parse_obj(get_driver().config.dict())

setu_dav_url = plugin_config.setu_dav_url
setu_dav_username = plugin_config.setu_dav_username
setu_dav_password = plugin_config.setu_dav_password
setu_path = plugin_config.setu_path

logger.info(
    "setu将会保存在 WebDAV 服务器中, URL: {}, UserName: {}, Path: {}".format(
        setu_dav_url, setu_dav_username, setu_path
    )
)


@asyncify
def upload_file(img: BytesIO, pid, p, r18, title, author):
    client = dav_client(
        setu_dav_url,  # type: ignore
        auth=(setu_dav_username, setu_dav_password),  # type: ignore
        timeout=None,
    )
    path = f"{setu_path}{'r18' if r18 else ''}/{pid}_{p}.jpg"
    client.upload_fileobj(img, to_path=path, overwrite=True)  # type: ignore
    logger.debug(f"WebDAV: {setu_dav_url} 图片已保存{path}")


def convert_file(bytes_file):
    file = BytesIO(bytes_file)
    return file


async def save_img(setu: Setu):
    try:
        await upload_file(
            convert_file(setu.img), setu.pid, setu.p, setu.r18, setu.title, setu.author
        )
    except HTTPError as e:
        logger.warning(f"涩图 {setu.title} webdav保存失败: {e}")
