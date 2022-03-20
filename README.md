# nonebot-plugin-setu-now

- 另一个色图插件
- 根据别人的改了亿点点
- 现在可以色图保存到 `WebDAV` 服务器中来节省服务器空间(可选)
- 采用**即时下载**并保存的方式来扩充*自己*色图库(可选)
- 支持私聊获取~~特殊~~色图
- 对临时聊天不生效

## 安装配置

```sh
pip install -U nonebot-plugin-setu-now
```

### .env 默认配置 (爱看不看，不看也能用)

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
```

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
  - 可在 `setu_message_cd` 中添加 `{cd_msg}` 提示CD时间
  ```json
  {
    "setu_message_send": ["abc"],
    "setu_message_cd": ["cba cd: {cd_msg}"]
  }
  ```


~~所有配置都可选了,还能出问题吗?~~

### bot.py

```py
nonebot.load_plugin("nonebot_plugin_setu_now")
```

## 使用

- 指令 `(setu|色图|涩图|来点色色|色色|涩涩)\s?(r18)?\s?(.*)?`
  - 看不懂？
    - `setu|色图|涩图|来点色色|色色|涩涩` 任意关键词
    - `r18` 可选 仅在私聊可用 群聊直接忽视
    - `关键词` 可选
- 例子
  - `来点色色 妹妹`
  - `setur18`
