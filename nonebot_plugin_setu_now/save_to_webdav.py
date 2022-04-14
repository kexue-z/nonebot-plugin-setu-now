from io import BytesIO

from nonebot import get_driver
from nonebot.log import logger
from webdav4.client import Client as dav_client

from nonebot_plugin_setu_now.setu_class import SetuData

from .config import Config

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


def upload_file(setu: SetuData):
    client = dav_client(
        setu_dav_url,  # type: ignore
        auth=(setu_dav_username, setu_dav_password),  # type: ignore
    )
    path = f"{setu_path}{'r18' if setu.r18 else '' }/{setu.pid}_{setu.p}_{setu.title}_{setu.author}.jpg"
    client.upload_fileobj(setu.img, to_path=path, overwrite=True)  # type: ignore
    logger.debug(f"WebDAV: {setu_dav_url} 图片已保存{path}")


def convert_file(bytes_file):
    file = BytesIO(bytes_file)
    return file


def save_img(content, pid: str, p: str, r18: bool = False):
    upload_file(convert_file(content), pid, p, r18)
