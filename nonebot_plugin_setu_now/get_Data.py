import base64
from re import findall
from sys import exc_info
from nonebot.adapters.cqhttp import MessageSegment
import httpx
from httpx import AsyncClient
from nonebot import logger
from nonebot import get_driver

proxies = (
    "http://127.0.0.1:7890"
    if not get_driver().config.setu_porxy
    else get_driver().config.setu_porxy
)

save = get_driver().config.setu_save
if save == "webdav":
    from .save_to_WebDAV import *
else:
    from .save_to_Local import *


async def get_setu(keyword="", r18=False) -> list:
    """获取色图并返回一堆东西

    Args:
        keyword (str, optional): 关键词. Defaults to "".
        r18 (bool, optional): 是否r18. Defaults to False.

    Returns:
        list[0]: base64编码图片或"Error:"
        list[1]: 图片信息或错误详情
        list[2]: 获取到图片 True, 否则 False
    """
    async with AsyncClient() as client:
        req_url = "https://api.lolicon.app/setu/v2"
        params = {"keyword": keyword, "r18": 1 if r18 else 0, "size": "regular"}
        try:
            res = await client.get(req_url, params=params, timeout=120)
            logger.info(res.json())
        except httpx.HTTPError as e:
            logger.warning(e)
            return "Error:", f"API异常{e}", False
        try:
            setu_title = res.json()["data"][0]["title"]
            setu_url = res.json()["data"][0]["urls"]["regular"]
            content = await downPic(setu_url)
            setu_pid = res.json()["data"][0]["pid"]
            setu_author = res.json()["data"][0]["author"]
            p = res.json()["data"][0]["p"]

            base64 = convert_b64(content)

            # 保存图片
            save_img(content, pid=setu_pid, p=p, r18=r18)

            if type(base64) == str:
                pic = MessageSegment.image(base64)
                data = (
                    "标题:"
                    + setu_title
                    + "\npid:"
                    + str(setu_pid)
                    + "\n画师:"
                    + setu_author
                )
            return pic, data, True, setu_url
        except httpx.ProxyError as e:
            logger.warning(e)
            return "Error:", f"代理错误: {e}", False
        except IndexError as e:
            logger.warning(e)
            return "Error:", f"图库中没有搜到关于{keyword}的图。", False
        except:
            logger.warning(f"{exc_info()[0]}, {exc_info()[1]}")
            return "Error:", f"{exc_info()[0]} {exc_info()[1]}。", False


async def downPic(url):
    async with AsyncClient(proxies=proxies) as client:
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        re = await client.get(url=url, headers=headers, timeout=120)
        if re.status_code == 200:
            logger.success("成功获取图片")
            return re.content
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return re.status_code


def convert_b64(content) -> str:
    ba = str(base64.b64encode(content))
    pic = findall(r"\'([^\"]*)\'", ba)[0].replace("'", "")
    return pic
