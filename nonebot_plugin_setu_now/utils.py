from typing import Optional

from httpx import AsyncClient
from nonebot.log import logger


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
