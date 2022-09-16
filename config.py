# coding=utf-8

# 配置更改后实时生效

# 推送方式选择，可以多选
# True为启用，False为禁用
MiPush = "True"
FCM = "False"
TG = "False"

# 以下三项请根据上述三项的值选择性填写
# MIPush:应用“消息接收”中设置的别名
MiPush_KEY = "000000"
# FCM：应用“WirePusher”中的ID
FCM_KEY = "000000"
# TG:创建机器人时所提供的token
TG_KEY = "000000"

# QQ群白名单，请填QQ群号，在白名单的QQ群消息将会推送
# 两个群号之间用英文逗号隔开
# 最外层用英文中括号括起来
WhiteList = [12345, 12345]

# TG相关设置
# 需要接收消息的TG用户ID
TG_UID = "00000000"
# Telegram群组消息绑定关系
# 格式为：{"群号": "TG群组ID", "群号": "TG群组ID"......}
# 群号和TG群组ID用英文双引号引起来，两者之间用英文冒号间隔，不同的绑定关系之间用英文逗号间隔
# 最外层用英文花括号括起来
TG_GroupLink = {"12345": "-00000", "123456": "-0000"}

# 推送接口设置
MiPush_API = "https://tdtt.top/send"
FCM_API = "https://wirepusher.com/send"
TG_API = "https://api.telegram.org"
