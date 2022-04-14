from asyncio import gather
from typing import Optional, List

from httpx import AsyncClient
from nonebot import get_driver

from .config import Config
from .models import SetuApiData, Setu, SetuData
from .utils import download_pic
from .setu_message import SetuMessage

plugin_config = Config.parse_obj(get_driver().config.dict())
SETU_SIZE = plugin_config.setu_size
API_URL = plugin_config.setu_api_url
SAVE = plugin_config.setu_save
REVERSE_PROXY = plugin_config.setu_reverse_proxy
PROXY = plugin_config.setu_proxy


class SetuLoader:
    def __init__(
        self,
        size: str = SETU_SIZE,
        api_url: str = API_URL,
        reverse_proxy_url: Optional[str] = REVERSE_PROXY,
        save: Optional[str] = SAVE,
        proxy: Optional[str] = PROXY,
    ):
        """初始化

        Args:
            size (str, optional): 图像大小. Defaults to "regular".
            api_url (str, optional): api地址. Defaults to "https://api.lolicon.app/setu/v2".
            reverse_proxy_url (str, optional): 图片反向代理地址. Defaults to "i.pixiv.re".
            save (Optional[str], optional): 是否保存. None 表示不保存 WebDAV 表示保存到WebDAV服务器, local 表示保存到本地. 默认 None 不保存.
            proxy (Optional[str], optional): 代理地址. 是否使用代理, 用于 api 请求和图片下载. Defaults to None.
        """
        self.size = size
        self.api_url = api_url
        self.reverse_proxy_url = reverse_proxy_url
        self.save = save
        self.proxy = proxy

    async def get_setu(
        self,
        keyword: Optional[str] = None,
        tags: Optional[list] = None,
        r18: bool = False,
        num: int = 1,
    ) -> "Setu":
        api_data = await self._get_info_from_setu_api(keyword, tags, r18, num)
        setu_data = Setu(data=api_data.data)
        data = await self._download_img_from_reverse_proxy(setu_data)

    async def _get_info_from_setu_api(
        self,
        keyword: Optional[str] = None,
        tags: Optional[list] = None,
        r18: bool = False,
        num: int = 1,
    ) -> "SetuApiData":
        data = {
            "keyword": keyword,
            "tags": tags,
            "r18": r18,
            "proxy": self.reverse_proxy_url,
            "num": num,
            "size": self.size,
        }
        headers = {"Content-Type": "application/json"}

        async with AsyncClient(proxies=self.proxy) as client:  # type: ignore
            res = await client.post(
                self.api_url, data=data, headers=headers, timeout=60
            )

        return SetuApiData(**res.json())

    async def _download_img_from_reverse_proxy(
        self,
        data: Setu,
    ) -> Setu:

        # data = Setu(data=data.data)
        tasks = []
        for setu in data.data:
            tasks.append(download_pic(setu.urls[self.size]))
        results = await gather(*tasks)
        data.img = []
        for i in range(len(data.data)):
            data.img.append(results[i])
        return data

    def _setu_info_msg(self, data: Setu) -> Setu:
        data.msg = []
        for i in range(len(data.data)):
            data.msg.append(
                f"标题{data.data[i].title}\n"
                f"画师:{data.data[i].author}\n"
                f"pid:{data.data[i].pid}"
            )
        return data

    def save_img(self):
        pass
