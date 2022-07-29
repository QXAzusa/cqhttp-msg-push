from email import message
from tokenize import group
from flask import Flask,request,jsonify
import json
import requests
import httpx
import urllib.parse
import re
import time

try:
    with open("config.json","r",encoding = 'UTF-8') as f:
        config = json.load(f)
    group_whitelist = config["WhiteList"]
    MiPush = config["MiPush"]
    FCM = config["FCM"]
    TG = config["TG"]
    KEY = config["KEY"]
    TG_UID = config["TG_UID"]
    TG_API = config["TG_API"]
    TG_GroupLink = config["TG_GroupLink"]
except:
    print("读取配置文件异常,请检查配置文件是否存在或语法是否有问题")
    assert()

try:
    groupInfo = json.loads(requests.get("http://localhost:5700/get_group_list").text)
    friendInfo = json.loads(requests.get("http://localhost:5700/get_friend_list").text)
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
                imageurl = re.findall('(?<=,url=).*?(?=\?term=)', code)
                imageurl = ' '.join(imageurl)
                renew = '[图片] ' + imageurl + '\n'
                msg = msg.replace(code, renew)
        else:
            cqcode = re.findall('\[CQ:image.*?]', msg)
            for code in cqcode:
                msg = msg.replace(code, '[图片]')
    if "CQ:video" in msg:
        if TG == "True":
            videourl = re.findall('(?<=.url=).*?(?=,])', msg)
            videourl = ' '.join(videourl)
            renew = '[视频] ' + videourl
            msg = msg.replace(msg, renew)
        else:
            msg = "[视频]"
    if "CQ:reply" in msg:
        cqcode = re.findall('\[CQ:reply.*?]', msg)
        cqcode = ' '.join(cqcode)
        replymsg_id = re.findall('(?<=.id=).*?(?=])', cqcode)
        replymsg_id = ' '.join(replymsg_id)
        reply_format = replymsg(replymsg_id)
        msg = msg.replace(cqcode, reply_format)
    if "CQ:at" in msg:
        if "all" in msg:
            regex1 = re.compile(r'\[CQ:at,qq=all]')
            cqcode = regex1.search(msg)
            cqcode = (cqcode.group())
            msg = msg.replace(cqcode, " @全体成员 ")
        else:
            atid = re.findall('(?<=qq=).*?(?=])', msg)
            for uid in atid:
                atimfurl = 'http://localhost:5700/get_group_member_info?group_id=' + str(groupId) + "&user_id=" + str(uid)
                imf = json.loads(requests.get(atimfurl).content)
                regex1 = re.compile(r'\[CQ:at,qq=' + uid + ']')
                cqcode = regex1.search(msg)
                cqcode = (cqcode.group())
                if imf["data"]["card"] != "":
                    at = " @" + imf["data"]["card"] + " "
                else:
                    at = " @" + imf["data"]["nickname"] + " "
                msg = msg.replace(cqcode, at)
    if 'com.tencent.miniapp' in msg:
        '''小程序跳转链接'''
        mini_jumpurl = re.findall('(?<="qqdocurl":").*?(?=")', msg)
        mini_jumpurl = ' '.join(mini_jumpurl)
        mini_jumpurl = mini_jumpurl.replace('\\', '')
        '''小程序标题'''
        mini_imf = re.findall('{"appType":.*?}', msg)
        mini_imf = ' '.join(mini_imf)
        mini_tittle = re.findall('(?<="desc":").*?(?=")', mini_imf)
        mini_tittle = ' '.join(mini_tittle)
        '''小程序归属'''
        mini_from = re.findall('(?<="title":").*?(?=")', msg)
        mini_from = ' '.join(mini_from)
        if TG == "True":
            msg = '[小程序] ' + mini_from + '\n' + mini_tittle + '\n' + mini_jumpurl
        else:
            msg = '[小程序] ' + mini_from + '\n' + mini_tittle
    if 'com.tencent.structmsg' in msg:
        jumpurl = re.findall('(?<="jumpUrl":").*?(?="&)',msg)
        jumpurl = ' '.join(jumpurl)
        jumpurl = jumpurl.replace('\\','')
        tittle = re.findall(r'(?<="title":").*?(?="&)',msg)
        tittle = ' '.join(tittle)
        if TG == 'True':
            msg = tittle + '\n' + jumpurl
        else:
            msg = tittle
    if "CQ:record" in msg:
        msg = "[语音]"
    if "CQ:share" in msg:
        msg = "[链接]"
    if "CQ:music" in msg:
        msg = "[音乐分享]"
    if "CQ:redbag" in msg:
        msg = "[红包]"
    if "CQ:forward" in msg:
        msg = "[合并转发]"
    if "CQ:json" in msg:
        msg = '[卡片消息]'
    if "CQ:xml" in msg:
        msg = '[卡片消息]'
    if "戳一戳" in msg:
        msg = "戳了你一下"
    return msg

def getGroupName(groupId):
    length = len(groupInfo["data"])
    for i in range(length):
        if groupId == groupInfo["data"][i]["group_id"]:
            return groupInfo["data"][i]["group_name"]

def getnickname(id):
    url = 'http://localhost:5700/get_stranger_info?user_id=' + str(id)
    jsonnickname = json.loads(requests.get(url).text)
    return jsonnickname["data"]["nickname"]

def styletime(now):
    timeArray = time.localtime(now/1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

def getfriendmark(UID):
    length = len(friendInfo["data"])
    try:
        for i in range(length):
            if UID == friendInfo["data"][i]["user_id"]:
                if friendInfo["data"]["remark"] != "":
                    nickname = friendInfo["data"]["remark"]
                else:
                    nickname = friendInfo["data"]["nickname"]
    except:
        try:
            nickname = getnickname(UID)
        except:
            nickname = "未知"
    return nickname

def replymsg(msgid):
    replymsg_api= f'http://localhost:5700/get_msg?message_id={msgid}'
    replymsg_json = json.loads(requests.get(replymsg_api).text)
    replymsg = replymsg_json["data"]["message"]
    replymsg_sender = replymsg_json["data"]["sender"]["nickname"]
    replymsg_timestamp = replymsg_json["data"]["time"]
    replymsg_styletime = styletime(replymsg_timestamp)
    if TG == "True":
        replymsg = "__回复：" + replymsg_sender + "(" + replymsg_styletime + "): " + replymsg + "__\n"
    else:
        replymsg = f"回复 {replymsg_sender}的消息: "
    return replymsg

async def sendmsg(msg):
    if MiPush == "True":
        await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':"QQ消息",'content':msg,'alias':KEY})
    elif FCM == "True":
        await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':"QQ消息",'message':msg,'type':'privateMsg'})
    elif TG == "True":
        TG_ID = TG_UID
        senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
        if TG_API != "":
            url = f"https://{TG_API}/bot{KEY}/sendMessage"
        else:
            url = f"https://api.telegram.org/bot{KEY}/sendMessage"
        await httpx.AsyncClient().post(url=url, data=senddata)

@app.route("/",methods=['POST'])
async def recvMsg():
    global TG_API,TG_ID,groupId
    groupId = ''
    TG_ID = ''
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    if json_data["post_type"] == "meta_event":
        if json_data["meta_event_type"] == "heartbeat":
            print("接收心跳信号成功")
    elif json_data["post_type"] == "request":
        if json_data["request_type"] == "friend":
            friendId = json_data["user_id"]
            print("新的好友添加请求：%s" % friendId)
            if MiPush == "True":
                await httpx.AsyncClient().post("https://tdtt.top/send",data={'title': "新的好友添加请求", 'content': '%s想要添加您为好友' % friendId,'alias': KEY})
            elif FCM == "True":
                await httpx.AsyncClient().post("https://wirepusher.com/send", data={'id': KEY, 'title': "新的好友添加请求",'message': '%s想要添加您为好友' % friendId,'type': 'FriendAdd'})
            elif TG == "True":
                msg = friendId + ' 请求添加您为好友'
                senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
                if TG_API != "":
                    url = f"https://{TG_API}/bot{KEY}/sendMessage"
                else:
                    url = f"https://api.telegram.org/bot{KEY}/sendMessage"
                await httpx.AsyncClient().post(url=url, data=senddata)
    elif json_data["post_type"] == "notice":
        if json_data["notice_type"] == "group_upload":
            if json_data["group_id"] in group_whitelist:
                groupId = json_data["group_id"]
                groupName = getGroupName(groupId)
                filename = json_data["file"]["name"]
                userid = json_data["user_id"]
                cardurl = 'http://localhost:5700/get_group_member_info?group_id=' + str(groupId) + "&user_id=" + str(userid)
                card = json.loads(requests.get(cardurl).content)
                if card["data"]["card"] != "":
                    card = card["data"]["card"] + " "
                else:
                    card = card["data"]["nickname"] + " "
                msg = card + '上传了 ' + filename + ' 到 ' + groupName
                if MiPush == "True":
                    await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':"QQ通知",'content':'%s'%(msg),'alias':KEY})
                if FCM == "True":
                    await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':"QQ通知",'message':msg,'type':'privateMsg'})
                if TG == "True":
                    if str(groupId) in TG_GroupLink:
                        TG_ID = TG_GroupLink[str(groupId)]
                    senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
                    if TG_API != "":
                        url = f"https://{TG_API}/bot{KEY}/sendMessage"
                    else:
                        url = f"https://api.telegram.org/bot{KEY}/sendMessage"
                    await httpx.AsyncClient().post(url=url, data=senddata)
    elif json_data["message_type"] == "private":
        msg = msgFormat(json_data["message"])
        uid = json_data["sender"]["user_id"]
        nickname = getfriendmark(uid)
        print("来自%s的私聊消息:%s"%(nickname,msg))
        if MiPush == "True":
            await httpx.AsyncClient().post("https://tdtt.top/send",data={'title':nickname,'content':msg,'alias':KEY})
        elif FCM == "True":
            await httpx.AsyncClient().post("https://wirepusher.com/send",data={'id':KEY,'title':nickname,'message':msg,'type':'privateMsg'})
        elif TG == "True":
            if str(uid) in TG_GroupLink:
                TG_ID = TG_GroupLink[str(uid)]
            else:
                TG_ID = TG_UID
            msg = nickname + ":\n" + msg
            senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
            if TG_API != "":
                url = f"https://{TG_API}/bot{KEY}/sendMessage"
            else:
                url = f"https://api.telegram.org/bot{KEY}/sendMessage"
            await httpx.AsyncClient().post(url=url, data=senddata)
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
                if str(groupId) in TG_GroupLink:
                    TG_ID = TG_GroupLink[str(groupId)]
                else:
                    TG_ID = TG_UID
                if card != "":
                    text = card + "[" + groupName + "]" + ":\n" + msg
                else:
                    text = nickName + "[" + groupName + "]" + ":\n" + msg
                senddata = {"chat_id": TG_ID, "text": text, "disable_web_page_preview": "true"}
                if TG_API != "":
                   url = f"https://{TG_API}/bot{KEY}/sendMessage"
                else:
                   url = f"https://api.telegram.org/bot{KEY}/sendMessage"
                await httpx.AsyncClient().post(url=url, data=senddata)
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
                if str(groupId) in TG_GroupLink:
                    TG_ID = TG_GroupLink[str(groupId)]
                else:
                    TG_ID = TG_UID
                if card != "":
                    msg = card + "[" + groupName + "]" + ":\n" + msg
                else:
                    msg = nickName + "[" + groupName + "]" + ":\n" + msg
                senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
                if TG_API != "":
                    url = f"https://{TG_API}/bot{KEY}/sendMessage"
                else:
                    url = f"https://api.telegram.org/bot{KEY}/sendMessage"
                await httpx.AsyncClient().post(url=url, data=senddata)
    return "200 OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
