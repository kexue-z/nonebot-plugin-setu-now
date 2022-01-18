# nonebot-plugin-setu-now

- 另一个色图插件
- 根据别人的改了亿点点
- 现在可以色图保存到 `WebDAV` 服务器中来节省服务器空间
- 采用**即时下载**并保存的方式来扩充*自己*色图库
- 支持私聊获取~~特殊~~色图

# 安装配置
```
pip install -U nonebot-plugin-setu-now
```

## .env

```ini
setu_cd=60
setu_save=
setu_path=
setu_porxy=
setu_reverse_proxy=
setu_dav_url=
setu_dav_username=
setu_dav_password=
```

- `setu_cd` 单位：秒
- `setu_save` 保存模式 可选 webdav 或 空 为本地
- `setu_path` 保存路径 
  - webdav 默认 `/setu` `/setur18`  
  - 本地  `./data/setu` `./data/setur18`
- `setu_porxy` 代理地址
- `setu_reverse_proxy` pixiv代理 默认 `i.pixiv.re`
- webdav 设置
  - `setu_dav_username` 用户名
  - `setu_dav_password` 密码
  - `setu_dav_url` webdav服务器地址

## bot.py

```
nonebot.load_plugin("nonebot_plugin_setu_now")
```

# 使用

- 指令 `(setu|色图|涩图|来点色色|色色)\s?(r18)?\s?(.*)?`
  - 看不懂？
    - `setu|色图|涩图|来点色色|色色` 任意关键词
    - `r18` 可选 仅在私聊可用 群聊直接忽视
    - `关键词` 可选
- 例子
  - `来点色色 妹妹`
  - `setur18`
