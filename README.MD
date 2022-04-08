## 提醒
master分支是对原项目功能的补充、patch分支仅针对对原项目的bug修复
## 介绍
这是一个能够对QQ消息通过第三方推送转发的程序，修改自<a href="https://github.com/zhishixiang/tencent-push">zhishixiang/tencent-push</a>项目。此版本相比原版有以下区别：  
1.补充了Telegram机器人私聊推送渠道<br>
2.能够在Telegram中直接显示图片<br>
2.使用TG推送时能够将小程序转换为链接<br>
3.能对群组的系统通知进行推送（群成员变动、文件上传）<br>
完整配置教程待编写
## config.js参数说明
|    名称     |                                  介绍                                   |    可填写     |   必填项    |
|:---------:|:---------------------------------------------------------------------:|:----------:|:--------:|
|  Mipush   |                               MiPush选择                                | True/False |    ✔     |
|    FCM    |                               FCMt推送选择                                | True/False |    ✔     |
|    TG     |                              TG Bot推送选择                               | True/False |    ✔     |
|    KEY    | MIPush:应用”“消息接收”中别名<br/>FCM：应用“WirePusher”中的ID<br/>TG:创建机器人时所提供的token |    字符串     |    ✔     |
| WhiteList |                              需要推送群消息的群号                               |     数值     |    ✔     |
|  TG_UID   |                             需要接收消息的TG用户ID                             |     数值     |  TG推送必填  |
|  TG_API   |                             TG推送时所用API的域名                             |    字符串     |  TG推送必填  |


