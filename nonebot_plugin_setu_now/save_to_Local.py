import os
from nonebot import get_driver, logger

setu_path = get_driver().config.setu_path

if not setu_path:
    setu_path = os.path.abspath("data/setu")
if os.path.exists(setu_path):
    logger.success(f"setu将保存到 {setu_path}")
else:
    os.makedirs(setu_path)
    logger.success(f"创建文件夹 {setu_path}")
    logger.success(f"setu将保存到 {setu_path}")


def save_img(content, pid: str, p: str, r18: bool = False):
    path = f"{setu_path}{'r18' if r18 else '' }/{pid}_{p}.jpg"
    with open(path, "wb") as f:
        f.write(content)
    logger.success(f"图片已保存{path}")
