## 提醒
master分支是对原项目功能的补充和Bug修复、patch分支仅针对原项目的bug修复
## 介绍
这是一个能够对QQ消息通过第三方推送转发的程序，修改自<a href="https://github.com/zhishixiang/tencent-push">zhishixiang/tencent-push</a>项目。此版本相比原版有以下区别：  
1.补充了Telegram机器人私聊推送渠道<br>
2.能够在Telegram中直接显示图片<br>
！未测试，切勿依赖！3.使用TG推送时能够将小程序转换为链接<br>
！未完善，切勿依赖！4.能对群组的系统通知进行推送（群成员变动）<br>
## 使用方法
### MiPush
前往酷安下载安装“<a href="https://www.coolapk.com/apk/top.tdtt.news">消息接收</a>”，显示注册成功后，点击设置别名，尽量设置复杂一点。设置完后记得设置的别名。
### FCM
前往Google Play搜索安装“<a href="https://play.google.com/store/apps/details?id=com.mrivan.wirepusher">WirePusher</a>”，安装好后打开，记录ID
### Telegram Bot
前往<a href="https://t.me/BotFather">@BotFather</a>，发送/newbot，根据指引创建机器人，保存创建后提供的token，最后发送/start给机器人
## config.js参数说明
|    名称     |                                  介绍                                   |    可填写     |   必填项    |
|:---------:|:---------------------------------------------------------------------:|:----------:|:--------:|
|  Mipush   |                               MiPush选择                                | True/False |   ✔ 三选一   |
|    FCM    |                               FCMt推送选择                                | True/False |    ✔ 三选一     |
|    TG     |                              TG Bot推送选择                               | True/False |    ✔ 三选一     |
|    KEY    | MIPush:应用”“消息接收”中别名<br/>FCM：应用“WirePusher”中的ID<br/>TG:创建机器人时所提供的token |    字符串     |    ✔     |
| WhiteList |                              需要推送群消息的群号                               |     数值     |    ✔     |
|  TG_UID   |                             需要接收消息的TG用户ID                             |     数值     |  TG推送必填  |
|  TG_API   |                             TG推送时所用API的域名                             |    字符串     | 可选，不填为默认 |
