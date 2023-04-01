<p align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://user-images.githubusercontent.com/44545625/209862575-acdc9feb-3c76-471d-ad89-cc78927e5875.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
</p>

<div align="center">

# nonebot-plugin-setu-now

_✨ NoneBot2 涩图插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/kexue-z/nonebot-plugin-setu-now/master/LICENSE">
    <img src="https://img.shields.io/github/license/kexue-z/nonebot-plugin-setu-now.svg" alt="license">
  </a>
  <a href="https://pypi.org/project/nonebot-plugin-setu-now/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-setu-now" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</p>


## 简介

可通过群聊或私聊获取 Pixiv 涩图的 NoneBot2 插件


## 特色

- **极高的涩图发送成功率（仅限0.5.0以上新版本）**

- 通过回复获取图片信息

- 自动撤回涩图

- R18白名单群组

- 自动撤回涩图

- 独立的下载发送任务结构，速度更快


## 安装

**使用 `nb-cli` 安装（推荐）：**
```
nb plugin install nonebot-plugin-setu-now
```

使用 `pip` 安装：
```
pip install nonebot-plugin-setu-now
```

使用 `git clone` 安装（不推荐喵）：
```
git clone https://github.com/kexue-z/nonebot-plugin-setu-now.git
```


### .env 默认配置

> 只有要用到的才填写，如果用不到或者不知道怎么设置，就不用写配置也能用

```ini
setu_cd=
setu_path=
setu_porxy=
setu_withdraw=
setu_reverse_proxy=
setu_size=
setu_api_url=
setu_max=
```


- `setu_cd` CD(单位秒) 可选 默认`60`秒
- `setu_path` 保存路径 可选 按需填写, 可不填使用默认
- `setu_porxy` 代理地址 可选 当 pixiv 反向代理不能使用时可自定义
- `setu_reverse_proxy` pixiv 反向代理 可选 默认 `i.pixiv.re`
- `setu_withdraw` 撤回发送的色图消息的时间, 单位: 秒 可选 默认`关闭` 填入数字来启用, 建议 `10` ~ `120` **仅对于非合并转发使用**
- `setu_size` 色图质量 默认 `regular` 可选 `original` `regular` `small` `thumb` `mini`
- `setu_api_url` 色图信息 api 地址 默认`https://api.lolicon.app/setu/v2` 如果有 api 符合类型也能用
- `setu_max` 一次获取色图的数量 默认 `30` 如果你的服务器/主机内存吃紧 建议调小

所有配置均可选，按需填写


## 使用

如果你能读懂正则就不用看了

```r
^(setu|色图|涩图|来点色色|色色|涩涩|来点色图)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?\s?(tag)?\s?(.*)?
```

- 指令 以 `setu|色图|涩图|来点色色|色色|涩涩` 为开始
  - 然后接上可选数量 `x10` `10张|个|份`
  - 再接上可选 `r18`
  - 可选 `tag`
  - 最后是关键词
- 说明
  - 数量 可选 默认为 1
  - `r18` 可选 仅在私聊可用 群聊直接忽视
  - `tag` 可选 如有 关键词参数会匹配 `pixiv 标签 tag`
  - 关键词 可选 匹配任何 `标题` `作者` 或 `pixiv 标签`
- 例子
  - `来点色色 妹妹`
  - `setur18`
  - `色图 x20 tag 碧蓝航线 妹妹`
  - `涩涩10份魅魔`

# 在吗？

- 这个是 `on_regex` 而不是 `on_command`（不需要带命令前缀）
- 本插件一般都经过测试后才发版，如果遇到了任何问题，请先自行解决
- 任何`不正确使用插件`的 issue 将会直接关闭
