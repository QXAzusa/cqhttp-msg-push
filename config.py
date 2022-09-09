# coding=utf-8

# 推送方式选择
MiPush = "True"
FCM = "False"
TG = "False"

# MIPush:应用“消息接收”中别名
# FCM：应用“WirePusher”中的ID
# TG:创建机器人时所提供的token
KEY = "000000"

# QQ群白名单，请填QQ群号，在白名单的QQ群消息会推送
WhiteList = ['12345', '12345']

# TG相关设置
TG_UID = "00000000"
TG_GroupLink = {"12345": "-00000", "123456": "-0000"}

# 推送接口设置
MiPush_API = "https://tdtt.top/send"
FCM_API = "https://wirepusher.com/send"
TG_API = "https://api.telegram.org"
