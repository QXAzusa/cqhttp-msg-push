# cqhttp-msg-push
## 声明
此项目并未对任何版本的腾讯QQ进行任何修改或注入行为，此项目仅围绕go-cqhttp客户端提供的接口开发。<br>
This project does not modify or inject any version of Tencent QQ, this project is only developed around the interface provided by the go-cqhttp client.
## 介绍
这是一个能够对QQ消息通过第三方推送转发的程序，修改自<a href="https://github.com/zhishixiang/tencent-push">zhishixiang/tencent-push</a>项目。此版本相比原版有以下区别：  
1.补充了Telegram机器人私聊推送渠道<br>
2.能够在Telegram中直接显示图片<br>
3.能够直接显示被At用户的昵称<br>
## 使用方法
### 运行环境
Python 3
### 运行方法
前往Release页面下载项目,在项目目录下执行`pip3 install -r requirements.txt`安装依赖。成下方配置后先打开go-cqhttp，根据提示登录QQ，待提示服务端启动成功时运行此脚本，两个程序必须同时运行。
### go-cqhttp
第一次运行请根据提示选择“http通信”生成配置文件<br>
在配置文件中填写好账号密码 修改结尾服务配置
```yaml
# 连接服务列表
servers:
  # HTTP 通信设置
  - http:
      # 服务端监听地址
      host: 127.0.0.1
      # 服务端监听端口
      port: 5700
      # 反向HTTP超时时间, 单位秒
      # 最小值为5，小于5将会忽略本项设置
      timeout: 5
      middlewares:
        <<: *default # 引用默认中间件
      # 反向HTTP POST地址列表
      post:
      #- url: '' # 地址
      #  secret: ''           # 密钥
      - url: http://127.0.0.1:5000/ # 地址
      #  secret: ''          # 密钥
```
### MiPush
下载安装“<a href="https://github.com/QXAzusa/tencent-push/raw/master/package/top.tdtt.news.apk">消息接收</a>”，显示注册成功后，点击设置别名，尽量设置复杂一点。设置完后记得设置的别名。
### FCM
前往Google Play搜索安装“<a href="https://play.google.com/store/apps/details?id=com.mrivan.wirepusher">WirePusher</a>”，安装好后打开，记录ID
### Telegram Bot
前往<a href="https://t.me/BotFather">@BotFather</a>，发送/newbot，根据指引创建机器人，保存创建后提供的token，最后发送/start给机器人
### config.js参数填写
|    名称     |                                  介绍                                   |    可填写     |   必填项    |
|:---------:|:---------------------------------------------------------------------:|:----------:|:--------:|
|  Mipush   |                               MiPush选择                                | True/False |   ✔ 三选一   |
|    FCM    |                               FCMt推送选择                                | True/False |    ✔ 三选一     |
|    TG     |                              TG Bot推送选择                               | True/False |    ✔ 三选一     |
|    KEY    | MIPush:应用”“消息接收”中别名<br/>FCM：应用“WirePusher”中的ID<br/>TG:创建机器人时所提供的token |         |    ✔     |
| WhiteList |                              需要推送群消息的群号                               |         |    ✔     |
|  TG_UID   |                             需要接收消息的TG用户ID                             |          |  TG推送必填  |
|  TG_API   |                             TG推送时所用API的域名                             |         | 可选，不填为默认 |
|     TG_GroupLink      |        Telegram群组消息绑定关系<br/>格式为：{"群号":"TG群组ID","群号":"TG群组ID"}         |            |     可选     |
## JetBrains开源许可
本项目重度依赖于JetBrains™ PyCharm，感谢JetBrains s.r.o为本项目提供[开源许可证](https://www.jetbrains.com/community/opensource/#support)，如果你同样对开发充满热情并且经常使用JetBrains s.r.o的产品，你也可以尝试通过JetBrains官方渠道[申请](https://www.jetbrains.com/shop/eform/opensource)开源许可证以供核心开发者使用


<figure style="width: min-content">
    <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.png" width="200" height="200">
    <figcaption>Copyright © 2022 JetBrains s.r.o. <br>PyCharm and the PyCharm logo are registered trademarks of JetBrains s.r.o.</figcaption>
</figure>
