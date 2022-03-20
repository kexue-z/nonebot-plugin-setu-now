import json
from pathlib import Path

from anyio import open_file
from nonebot.log import logger

DATA_DIR = Path("./data/setu_now/").absolute()
CD_DIR = DATA_DIR / "cd.json"

logger.debug(f"SETU DATA: {DATA_DIR}")
logger.debug(f"SETU CD DATA: {CD_DIR}")


async def read_json():
    try:
        async with await open_file(CD_DIR, "r") as f:
            f = await f.read()
            return json.loads(f)
    except FileNotFoundError:
        try:
            import os

            os.makedirs(DATA_DIR)
        except FileExistsError:
            pass
        async with await open_file(CD_DIR, "w") as f:
            data = json.dumps({})
            await f.write(data)
        return {}


async def write_json(qid: str, time: int, mid: int, data: dict):
    data[qid] = [time, mid]
    async with await open_file(CD_DIR, "w") as f:
        f_data = json.dumps(data)
        await f.write(f_data)


async def remove_json(qid: str):
    async with await open_file(CD_DIR, "r") as f:
        f = await f.read()
        data = json.loads(f)
    data.pop(qid)
    async with await open_file(CD_DIR, "w") as f:
        data = json.dumps(data)
        await f.write(data)
