# nonebot-plugin-setu-now

- 另一个色图插件
- 根据别人的改了亿点点
- 支持私聊获取~~特殊~~色图
- 对临时聊天不生效
- 每个图逐个发送 (支持撤回)
- 在发送不成功时，尝试添加边框，防止风控（不防封号
- CD 计算方式为: 设置的 CD 时间 \* 获取图片的数量
  - 如果设置了 60s 那么，\*20 后就是 1200s ≈ 0.33h
- 支持r18白名单，发送 `不可以涩涩` 或 `可以涩涩` 来在群聊中关闭/开启 

## 安装配置

```sh
pip install -U nonebot-plugin-setu-now
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
- `setu_add_random_effect` 添加随机特效，防止风控，默认开。可设置为 false 关掉

所有配置均可选，按需填写

## 载入插件 bot.py

```py
nonebot.load_plugin("nonebot_plugin_setu_now")
```

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

- 这个是 `on_regex` 而不是 `on_commend`
- 本插件一般都经过测试后才发版，如果遇到了任何问题，请先自行解决
- 任何`不正确使用插件`的 issue 将会直接关闭
