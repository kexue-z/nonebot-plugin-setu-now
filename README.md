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

- **极高的涩图发送成功率**
- 支持多种参数选项的命令式交互
- 自动撤回涩图
- 私聊R18支持
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
setu_proxy=
setu_withdraw=
setu_reverse_proxy=
setu_size=
setu_api_url=
setu_max=
setu_add_random_effect=
setu_minimum_send_interval=
setu_send_as_bytes=
setu_excludeAI=
```


- `setu_cd` CD(单位秒) 可选 默认`60`秒
- `setu_path` 保存路径 可选 可不填使用默认
- `setu_proxy` 代理地址 可选 当 pixiv 反向代理不能使用时可自定义
- `setu_reverse_proxy` pixiv 反向代理 可选 默认 `i.pixiv.re`
- `setu_withdraw` 撤回发送的色图消息的时间, 单位: 秒 可选 默认 `关闭` 填入数字来启用, 建议 `10` ~ `120`
- `setu_size` 色图质量 默认 `regular` 可选 `original` `regular` `small` `thumb` `mini`
- `setu_api_url` 色图信息 api 地址 默认`https://api.lolicon.app/setu/v2` 如果有 api 符合类型也能用
- `setu_max` 一次获取色图的数量 默认 `30` 如果你的服务器/主机内存吃紧 建议调小
- `setu_add_random_effect` 在发送失败时，添加特效以尝试重新发送 默认 `True`
- `setu_minimum_send_interval` 连续发送最小间隔（秒） 可选 默认 `3` 
- `setu_send_as_bytes` 以bytes方式发送到客户端，默认 `True` ，
  - `True` ：Nonebot将会读取临时路径下的图片，并传到客户端。兼容性更好
  - `False` : 将会直接传输文件路径到客户端，并让客户端来读取。速度较快。如果客户端与 Nonebot 处于容器中，并且没有设定共享路径，则客户端将会无法读取图片，导致发送失败。
- `setu_excludeAI` 排除 AI 生成的图片 默认 `False`
  - `True` ：排除 AI 生成的图片
  - `False` : 不排除 AI 生成的图片

> 有配置均可选，按需填写


## 使用

### 获取色图

使用命令式交互获取色图

```
setu [-r|--r18] [-t|--tag 标签] [数量] [关键词]
```

**解释:**

- 支持的命令头：`setu`、`色图`、`涩图`、`来点色色`、`色色`、`涩涩`、`来点色图`
- 参数说明：
  - `-r` 或 `--r18`：获取R18内容，仅在私聊可用
  - `-t` 或 `--tag`：指定标签，多个标签需要连续使用 `-t 标签1 -t 标签2`
  - `数量`：获取的图片数量，默认1张，最多不超过配置的`setu_max`值
  - `关键词`：搜索关键词，匹配标题、作者或标签
- 注意：
  - 如果同时指定了标签和关键词，将优先使用标签搜索
  - R18模式下强制只发送1张图片
- 例子
  - `色图 妹妹` - 获取1张包含"妹妹"关键词的图片
  - `setu --r18` - 私聊中获取1张R18图片
  - `涩图 -t 碧蓝航线 5` - 获取5张带有"碧蓝航线"标签的图片
  - `来点色图 -t 可爱 -t 猫耳 3` - 获取3张同时带有"可爱"和"猫耳"标签的图片

### 获取图片信息

> 注：当前版本暂未实现此功能，敬请期待后续更新


### R18 设置

- 如果要求发送 R18 图片时，则数量会被忽略，仅发送单张
- 私聊中可以正常使用 R18 功能
- 当前版本群聊中暂不支持 R18 内容

> 注：白名单相关功能正在开发中，敬请期待后续更新

# 在吗？

- 色图 `on_regex` 而不是 `on_command`（不需要带命令前缀）

