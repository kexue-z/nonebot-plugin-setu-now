from httpx import AsyncClient, HTTPError
from nonebot.log import logger
from typing import Optional
from .models import SetuApiData


def check_cd(id: str) -> bool:
    pass


async def download_pic(url: str, proxies: Optional[str] = None) -> Optional[bytes]:
    async with AsyncClient(proxies=proxies) as client:  # type: ignore
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        logger.debug(f"正在下载...{url}")
        re = await client.get(url=url, headers=headers, timeout=60)
        if re.status_code == 200:
            logger.debug("成功获取图片")
            return re.content
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return


def setu_info_msg(self, data: SetuApiData):
    for i in data.data:
        if data.error:
            i.msg = data.error
        i.msg = f"标题{i.title}\n" f"画师:{i.author}\n" f"pid:{i.pid}"
