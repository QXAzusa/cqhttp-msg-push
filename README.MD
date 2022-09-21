# ！目前所有未上架小米应用商店的应用都被拉进了MiPush的小黑屋，包括“消息接收”以及“FarPush”，此程序暂时无法正常工作！
# cqhttp-msg-push
## 声明
此项目并未对任何版本的腾讯QQ进行任何修改或注入行为，此项目仅围绕go-cqhttp客户端提供的接口开发。<br>
This project does not modify or inject any version of Tencent QQ, this project is only developed around the interface provided by the go-cqhttp client.
## 介绍
这是一个能够对QQ消息通过第三方推送转发的程序，修改自<a href="https://github.com/zhishixiang/tencent-push">zhishixiang/tencent-push</a>
<br>此分支相比原版有以下区别：  
1.补充了Telegram机器人私聊推送渠道<br>
2.解析特殊类型消息（@群成员、消息回复、小程序、链接分享卡片）<br>
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
  - http: # HTTP 通信设置
      address: 127.0.0.1:5700 # HTTP监听地址
      timeout: 5      # 反向 HTTP 超时时间, 单位秒，<5 时将被忽略
      long-polling:   # 长轮询拓展
        enabled: false       # 是否开启
        max-queue-size: 2000 # 消息队列大小，0 表示不限制队列大小，谨慎使用
      middlewares:
        <<: *default # 引用默认中间件
      post:           # 反向HTTP POST地址列表
      - url: http://127.0.0.1:5000/ # 地址
        max-retries: 10             # 最大重试，0 时禁用
        retries-interval: 1000      # 重试时间，单位毫秒，0 时立即
```
### MiPush
前往酷安下载安装“<a href="https://www.coolapk.com/apk/top.tdtt.news">消息接收</a>”，显示注册成功后，点击设置别名，尽量设置复杂一点。设置完后记得设置的别名。
### FCM
前往Google Play搜索安装“<a href="https://play.google.com/store/apps/details?id=com.mrivan.wirepusher">WirePusher</a>”，安装好后打开，记录ID
### Telegram Bot
前往<a href="https://t.me/BotFather">@BotFather</a>，发送/newbot，根据指引创建机器人，保存创建后提供的token，最后发送/start给机器人

### config.py参数填写
<table>
	<tr align="center">
	    <th>名称</th>
	    <th>介绍</th>
	    <th>是否必填</th>
	    <th>可填写的值</th>
	</tr>
	<tr align="center">
	    <td>Mipush</td>
	    <td>MiPush推送选择</td>
	    <td rowspan="3">✔<br/><br/>（三项任意组合）</td>
	    <td rowspan="3">True/其他字符</td>
	</tr>
	<tr align="center">
	    <td>FCM</td>
	    <td>FCM推送选择</td>
	</tr>
	<tr align="center">
	    <td>TG</td>
	    <td>TG推送选择</td>
	</tr>
  	<tr align="center">
	    <td>WhiteList</td>
	    <td>需要推送群消息的群号</td>
	    <td>✔</td>
	    <td>QQ群号</td>
	</tr>
	<tr align="center">
      	    <td>MiPush_KEY</td>
	    <td>应用“消息接收”中设置的别名</td>
	    <td rowspan="2">Mipush为True时必填</td>
	    <td rowspan="7">字符串</td>
	</tr>
  	<tr align="center">
	    <td>MiPush_API</td>
	    <td>MiPush推送接口</td>
	</tr>
	<tr align="center">
      	    <td>FCM_KEY</td>
	    <td>应用“WirePusher”中的ID</td>
	    <td rowspan="2">FCM为True时必填</td>
	</tr>
  	<tr align="center">
	    <td>FCM_API</td>
	    <td>FCM推送接口</td>
	</tr>
	<tr align="center">
	    <td>TG_KEY</td>
	    <td>创建机器人时所提供的token</td>
	    <td rowspan="3">TG为True时必填</td>
	</tr>
  	<tr align="center">
	    <td>TG_API</td>
	    <td>TG推送接口</td>
	</tr>
  	<tr align="center">
	    <td>TG_UID</td>
	    <td>需要接收消息的TG用户ID</td>
	</tr>
	<tr align="center">
	    <td>TG_GroupLink</td>
	    <td>Telegram群组消息绑定关系<br/>格式为：{"群号":"TG群组ID","群号":"TG群组ID"}</td>
	    <td>可选</td>
	    <td>字典</td>
	</tr>
</table>

## JetBrains开源许可
本项目重度依赖于JetBrains™ PyCharm，感谢JetBrains s.r.o为本项目提供[开源许可证](https://www.jetbrains.com/community/opensource/#support)，如果你同样对开发充满热情并且经常使用JetBrains s.r.o的产品，你也可以尝试通过JetBrains官方渠道[申请](https://www.jetbrains.com/shop/eform/opensource)开源许可证以供核心开发者使用


<figure style="width: min-content">
    <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.png" width="200" height="200">
    <figcaption>Copyright © 2022 JetBrains s.r.o. <br>PyCharm and the PyCharm logo are registered trademarks of JetBrains s.r.o.</figcaption>
</figure>
