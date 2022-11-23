from json import load
from pathlib import Path

from nonebot import get_driver
from nonebot.log import logger

from nonebot_plugin_setu_now.config import Config
from nonebot_plugin_setu_now.models import SetuMessage

plugin_config = Config.parse_obj(get_driver().config.dict())
if plugin_config.setu_send_custom_message_path:
    MSG_PATH = Path(str(plugin_config.setu_send_custom_message_path)).absolute()
else:
    MSG_PATH = None


DEFAULT_MSG = {
    "send": [
        "哦呀~这个大叔居然要色图哦？好变态哦~",
        "嚯嚯嚯，臭大叔又来色图了哦，好恶心",
        "有什么好色图有给发出来让大伙看看！",
        "咱没有色图（骗你的~）",
        "哈？你的脑子一天都在想些什么呢，咱才没有这种东西啦♡~",
        "Hen....Hentai！。",
        "哈？？？就这？？大叔根本都忍不住呢~",
        "变态baka死宅？",
        "已经可以了，现在很多死宅也都没你这么恶心了",
        "噫…你这个死变态想干嘛！居然想叫咱做这种事，死宅真恶心！快离我远点，我怕你污染到周围空气了（嫌弃脸）",
        "这么喜欢看色图哦？变态？",
        "eee，死肥宅不要啦！恶心心！",
        "又忍不住来看色图了吗？果然根~~~~本没有忍耐力呢♡~你这白痴臭大叔~",
        "啊啦？有来看这种东西哦~我看啊，你根本就不行嘛~♡",
        "哎呀，废材大叔又在要色图哦~！别人都自己画的~~你不会画不来吧~~",
        "看这些东西，会变成笨蛋的哦~诶，不过大叔本来就是大笨蛋吧~",
    ],
    "cd": [
        "注意身体，色图看太多对身体不好 (╯‵□′)╯︵┻━┻ 你还需要 {cd_msg} 才能再次发送哦",
        "憋再冲了！{cd_msg}",
        "呃...好像冲了好多次...感觉不太好呢...{cd_msg}后再冲吧",
        "你这么喜欢色图，{cd_msg}后再给你看哦",
        "被我玩弄了吧♡~",
        "不给你看色图 {cd_msg} 不会真的生气的，对吧？✧(≖ ◡ ≖✿)",
        "不是把，不给你看就要哭出来吗？快哭一个出来给我看看~",
        "再看的话，就会变成淫~~~~~虫的哦~这样下去可是找不到女朋友的哦。",
        "你还真是可怜恶心哦~就 {cd_msg} 没看这种东西就忍不住了吗？",
    ],
}


def load_setu_message():
    if MSG_PATH:
        logger.info(f"加载自定义色图消息 路径: {MSG_PATH}")
        with MSG_PATH.open("r") as f:
            msg = load(f)
        return SetuMessage(**msg)
    else:
        return SetuMessage(**DEFAULT_MSG)


SETU_MSG: SetuMessage = load_setu_message()
