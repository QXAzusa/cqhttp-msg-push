from email import message
from tokenize import group
from flask import Flask,request,jsonify
import json
import requests
import httpx
import urllib.parse
import re

try:
    with open("config.json","r",encoding = 'UTF-8') as f:
        config = json.load(f)
    group_whitelist = config["WhiteList"]
    MiPush = config["MiPush"]
    FCM = config["FCM"]
    TG = config["TG"]
    KEY = config["KEY"]
    TG_ID = config["TG_UID"]
    TG_API = config["TG_API"]
    TG_GroupLink = config["TG_GroupLink"]
except:
    print("读取配置文件异常,请检查配置文件是否存在或语法是否有问题")
    assert()

try:
    groupInfo = json.loads(requests.get("http://localhost:5700/get_group_list").text)
    userId = json.loads(requests.get("http://localhost:5700/get_login_info").text)["data"]["user_id"]
except:
    print("无法从go-cqhttp获取信息,请检查go-cqhttp是否运行或端口配置是否正确")
    assert()

app = Flask(__name__)

def msgFormat(msg):
    if "CQ:image" in msg:
        if TG == "True":
            cqcode = re.findall('\[CQ:image.*?]', msg)
            for code in cqcode:
                imageurl = re.findall('(?<=.image,url=).*?(?=,subType=)', code)
                imageurl = ' '.join(imageurl)
                renew = '[图片 ' + imageurl + ']'
                msg = msg.replace(code, renew)
        else:
            cqcode = re.findall('\[CQ:image.*?]', msg)
            for code in cqcode:
                msg = msg.replace(code, '[图片]')
        msg = msg
    elif "CQ:record" in msg:
        msg = "[语音]"
    elif "CQ:share" in msg:
        msg = "[链接]"
    elif "CQ:music" in msg:
        msg = "[音乐分享]"
    elif "CQ:redbag" in msg:
        msg = "[红包]"
    elif "CQ:forward" in msg:
        msg = "[合并转发]"
    elif "戳一戳" in msg:
        msg = "戳了你一下"
    elif "CQ:at" in msg:
        if json_data["message_type"] == "group":
            atid = re.findall('(?<=qq=).*?(?=])', msg)
            for uid in atid:
                atimfurl = 'http://localhost:5700/get_group_member_info?group_id' + str(groupId) + "?user_id=" + str(uid)
                imf = json.loads(requests.get(atimfurl).content)
                regex1 = re.compile(r'\[CQ:at,qq=' + uid + ']')
                cqcode = regex1.search(msg)
                cqcode = (cqcode.group())
                if imf["data"]["card"] != "":
                    at = "@" + imf["data"]["card"] + " "
                else:
                    at = "@" + imf["data"]["nickname"] + " "
                msg = msg.replace(cqcode, at)
        else:
            msg = msg
    elif "com.tencent.miniapp" in msg:
        minijson = json.loads(re.findall('(?<=\[CQ:json,data=).*?(?=])', msg))
        mini_title = minijson["prompt"]
        if "detail_1" in msg:
            mini_url = urllib.parse.quote(minijson["meta"]["detail_1"]["qqdocurl"])
            mini_desc = minijson["meta"]["detail_1"]["desc"]
        else:
            mini_url = ""
            mini_desc = ""
        if TG == "True":
            msg = mini_title + "%0A" + mini_desc + "%0A" + mini_url
        else:
            msg = mini_title + "%0A" + mini_desc
    elif "com.tencent.structmsg" in msg:
        structjson = json.loads(re.findall('(?<=\[CQ:json,data=).*?(?=])', msg))
        structtitle = structjson["prompt"]
        msg = structtitle
    else:
        msg = msg
    return msg

def getGroupName(groupId):
    length = len(groupInfo["data"])
    for i in range(length):
        if groupId == groupInfo["data"][i]["group_id"]:
            return groupInfo["data"][i]["group_name"]

def getnickname(id):
    url = 'http://localhost:5700/get_stranger_info?user_id=' + str(id)
    jsonnickname = json.loads(requests.get(url).content)
    nickname = jsonnickname["data"]["nickname"]
    return nickname

@app.route("/",methods=['POST'])
async def recvMsg():
    global TG_API,TG_ID
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    if json_data["post_type"] == "meta_event":
        if json_data["meta_event_type"] == "heartbeat":
            print("接收心跳信号成功")
    elif json_data["post_type"] == "notice":
        if json_data["notice_type"] == "group_decrease":
            if json_data["group_id"] in group_whitelist:
                groupName = getGroupName(json_data["group_id"])
                nickname = getnickname(json_data["user_id"])
                msg = nickname + "(" + userId + ")" + " 离开了 " + groupName
                if MiPush == "True":
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':"QQ通知",'content':'%s'%(msg),'alias':KEY})
                if FCM == "True":
                    await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':"QQ通知",'message':msg,'type':'privateMsg'})
                if TG == "True":
                    if TG_API == "":
                        TG_API = "api.telegram.org"
                    if str(groupId) in TG_GroupLink:
                        TG_ID = TG_GroupLink[str(groupId)]
                    msg = urllib.parse.quote(msg)
                    url = 'https://' + TG_API + '/bot' + KEY + '/sendMessage?chat_id=' + TG_ID + '&text=' + msg
                    await httpx.AsyncClient().post(url)
        if json_data["notice_type"] == "group_increase":
            if json_data["group_id"] in group_whitelist:
                groupName = getGroupName(json_data["group_id"])
                nickname = getnickname(json_data["user_id"])
                msg = nickname + "(" + userId + ")" + " 加入了 " + groupName
                if MiPush == "True":
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':"QQ通知",'content':'%s'%(msg),'alias':KEY})
                if FCM == "True":
                    await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':"QQ通知",'message':msg,'type':'privateMsg'})
                if TG == "True":
                    if TG_API == "":
                        TG_API = "api.telegram.org"
                    if str(groupId) in TG_GroupLink:
                        TG_ID = TG_GroupLink[str(groupId)]
                    msg = urllib.parse.quote(msg)
                    url = 'https://' + TG_API + '/bot' + KEY + '/sendMessage?chat_id=' + TG_ID + '&text=' + msg
                    await httpx.AsyncClient().post(url)
        if json_data["notice_type"] == "group_upload":
            if json_data["group_id"] in group_whitelist:
                groupId = json_data["group_id"]
                groupName = getGroupName(groupId)
                filename = json_data["file"]["name"]
                userid = json_data["user_id"]
                cardurl = 'http://localhost:5700/get_group_member_info?group_id' + str(groupId) + "?user_id=" + str(user_id)
                cardjson = json.loads(requests.get(cardurl).content)
                if cardjson["data"]["card"] == "":
                    name = cardjson["data"]["nickname"]
                else:
                    name = cardjson["data"]["card"]
                msg = name + '上传了 ' + filename + ' 到 ' + groupName
                if MiPush == "True":
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':"QQ通知",'content':'%s'%(msg),'alias':KEY})
                if FCM == "True":
                    await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':"QQ通知",'message':msg,'type':'privateMsg'})
                if TG == "True":
                    if TG_API == "":
                        TG_API = "api.telegram.org"
                    if str(groupId) in TG_GroupLink:
                        TG_ID = TG_GroupLink[str(groupId)]
                    msg = urllib.parse.quote(msg)
                    url = 'https://' + TG_API + '/bot' + KEY + '/sendMessage?chat_id=' + TG_ID + '&text=' + msg
                    await httpx.AsyncClient().post(url)
    elif json_data["message_type"] == "private":
        nickName = json_data["sender"]["nickname"]
        msg = msgFormat(json_data["message"])
        uid = json_data["sender"]["user_id"]
        print("来自%s的私聊消息:%s"%(nickName,msg))
        if MiPush == "True":
            await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':nickName,'content':'%s'%(msg),'alias':KEY})
        elif FCM == "True":
            await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':nickName,'message':msg,'type':'privateMsg'})
        elif TG == "True":
            if TG_API == "":
                TG_API = "api.telegram.org"
            if str(uid) in TG_GroupLink:
                TG_ID = TG_GroupLink[str(uid)]
            msg = urllib.parse.quote(msg)
            url = 'https://' + TG_API + '/bot' + KEY + '/sendMessage?chat_id=' + TG_ID + '&text=' + msg
            await httpx.AsyncClient().post(url)
    elif json_data["message_type"] == "group":
        groupId = json_data["group_id"]
        groupName = getGroupName(groupId)
        nickName = json_data["sender"]["nickname"]
        card = json_data["sender"]["card"]
        msg = msgFormat(json_data["message"])
        if groupId in group_whitelist:
            print("群聊%s的消息:%s:%s"%(groupName,nickName,msg))
            if MiPush == "True":
                if card != "":
                    await httpx.AsyncClient().post("https://tdtt.top/send", data={'title': '%s' % groupName,'content': '%s:%s' % (card, msg),'alias': KEY})
                else:
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':'%s'%groupName,'content':'%s:%s'%(nickName,msg),'alias':KEY})
            if FCM == "True":
                await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':'%s'%KEY,'title':groupName,'message':'%s:%s'%(nickName,msg),'type':'groupMsg'})
            if TG == "True":
                if TG_API == "":
                    TG_API = "api.telegram.org"
                if str(groupId) in TG_GroupLink:
                    TG_ID = TG_GroupLink[str(groupId)]
                if card != "":
                    msg = urllib.parse.quote(msg)
                    text = card + "[" + groupName + "]" + ":%0A" + msg
                else:
                    msg = urllib.parse.quote(msg)
                    text = nickName + "[" + groupName + "]" + ":%0A" + msg
                url = 'https://' + TG_API + '/bot' + KEY + '/sendMessage?chat_id=' + TG_ID + '&text=' + text
                await httpx.AsyncClient().post(url)
        elif "[CQ:at,qq=%s]"%userId in msg:
            msg = msg.replace("[CQ:at,qq=%s]"%userId,"[有人@我]")
            print("群聊%s有人@我:%s:%s"%(groupName,nickName,msg))
            if MiPush == "True":
                if card != "":
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':'%s'%groupName,'content':'%s:%s'%(card,msg),'alias':KEY})
                else:
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title': '%s' % groupName, 'content': '%s:%s' % (nickName, msg),'alias': KEY})
            if FCM == "True":
                if card != "":
                    await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id': '%s' % KEY, 'title': groupName,'message': '%s:%s' % (card, msg), 'type': 'groupMsg'})
                else:
                    await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':'%s'%KEY,'title':groupName,'message':'%s:%s'%(nickName,msg),'type':'groupMsg'})
            if TG == "True":
                if TG_API == "":
                    TG_API = "api.telegram.org"
                if str(groupId) in TG_GroupLink:
                    TG_ID = TG_GroupLink[str(groupId)]
                if card != "":
                    msg = urllib.parse.quote(msg)
                    msg = card + "[" + groupName + "]" + ":%0A" + msg
                else:
                    msg = urllib.parse.quote(msg)
                    msg = nickName + "[" + groupName + "]" + ":%0A" + msg
                url = 'https://' + TG_API + '/bot' + KEY + '/sendMessage?chat_id=' + TG_ID + '&text=' + msg
                await httpx.AsyncClient().post(url)
    return "200 OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
