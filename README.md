# nonebot-plugin-setu-now

- 另一个色图插件
- 根据别人的改了亿点点
- 现在可以色图保存到 `WebDAV` 服务器中来节省服务器空间(可选)
- 采用**即时下载**并保存的方式来扩充*自己*图库(可选)
- 支持私聊获取~~特殊~~色图
- 对临时聊天不生效
- 多个图在群聊中 > 3 图时合并发送 (不支持撤回)
- 单个图逐个发送 (支持撤回)
- CD 计算方式为: 设置的 CD 时间 \* 获取图片的数量
  - 如果设置了 60s 那么，\*20 后就是 1200s = 2h

## 安装配置

```sh
pip install -U nonebot-plugin-setu-now
```

### .env 默认配置

> 如果你不知道你要做什么 直接安装好插件 然后直接载入

> 本章内容可以不看

> 在吗？在读下去之前能不能告诉什么叫可选配备？

是像这样写全都写上但是都留空吗？
 
```ini
setu_cd=60
setu_save=
setu_path=
setu_porxy=
setu_reverse_proxy=
setu_dav_url=
setu_dav_username=
setu_dav_password=
setu_send_info_message=
setu_send_custom_message_path=
setu_withdraw=
setu_size=
setu_api_url=
setu_max=
```

很明显不是这个意思

可选的意思是像这样：

```ini
setu_cd=60
setu_save=local
setu_path=/data/setu
```

明白了吗？

下面是配置的说明


- `setu_cd` CD(单位秒) 可选 默认`60`秒
- `setu_save` 保存模式 可选 `webdav`(保存到 webdav 服务器中) 或 `local`(本地) 或 留空,不保存
- `setu_path` 保存路径 可选 当选择保存模式时可按需填写, 可不填使用默认
  - webdav 可选 默认`/setu` `/setur18`
  - 本地 可选 默认`./data/setu` `./data/setur18`
- `setu_porxy` 代理地址 可选 当 pixiv 反向代理不能使用时可自定义
- `setu_reverse_proxy` pixiv 反向代理 可选 默认 `i.pixiv.re`
- webdav 设置 当选择保存保存模式为 `webdav` 时必须填写
  - `setu_dav_username` 用户名
  - `setu_dav_password` 密码
  - `setu_dav_url` webdav 服务器地址
- `setu_send_info_message` 是否发送图片信息 可选 默认 `ture` 填写 `false` 可关闭
- `setu_send_custom_message_path` 自定义发送消息路径 可选 当填写路径时候开启 可以为相对路径
  - 文件应该为 `json` 格式如下
  - 可在 `setu_message_cd` 中添加 `{cd_msg}` 提示 CD 时间
  ```json
  {
    "send": ["abc"],
    "cd": ["cba cd: {cd_msg}"]
  }
  ```
- `setu_withdraw` 撤回发送的色图消息的时间, 单位: 秒 可选 默认`关闭` 填入数字来启用, 建议 `10` ~ `120` **仅对于非合并转发使用**
- `setu_size` 色图质量 默认 `regular` 可选 `original` `regular` `small` `thumb` `mini`
- `setu_api_url` 色图信息 api 地址 默认`https://api.lolicon.app/setu/v2` 如果有 api 符合类型也能用
- `setu_max` 一次获取色图的数量 默认 `30` 如果你的服务器/主机内存吃紧 建议调小
`
~~所有配置都可选了,还能出问题吗?~~


那你可以告诉我，下面这个设置出现了什么问题吗？

```ini
setu_send_custom_message_path={
    "send": ["abc"],
    "cd": ["cba cd: {cd_msg}"]
  }
setu_porxy=127.0.0。1:1234
setu_reverse_proxy=
setu_max=0
```

## 载入插件 bot.py

```py
nonebot.load_plugin("nonebot_plugin_setu_now")
```

## 使用

如果你能读懂正则就不用看了

```r
^(setu|色图|涩图|来点色色|色色|涩涩|来点色图)\s?([x]?\d+[张|个|份]?)?\s?(r18)?\s?\s?(tag)?\s?(.*)?
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
