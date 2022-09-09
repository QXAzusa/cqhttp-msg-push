import json
import requests
import httpx
import html
import re
import os
import time
import logging
import traceback
from flask import Flask,request
from datetime import datetime

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def prt(mes):
    print(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + str(mes))

try:
    import config
except:
    prt("读取配置文件异常,请检查配置文件是否存在或语法是否有问题")
    os._exit(0)

try:
    with open(str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/')) + '/face_config.json', 'r', encoding='utf-8') as f:
        face_data = json.load(f)
    len_face = len(face_data.get("sysface"))
except:
    prt("读取表情包配置文件异常,请检查配置文件是否存在或语法是否有问题")
    os._exit(0)

try:
    groupInfo = json.loads(requests.get("http://localhost:5700/get_group_list").text)
    friendInfo = json.loads(requests.get("http://localhost:5700/get_friend_list").text)
    userId = json.loads(requests.get("http://localhost:5700/get_login_info").text)["data"]["user_id"]
except:
    prt("无法从go-cqhttp获取信息,请检查go-cqhttp是否运行或端口配置是否正确")
    os._exit(0)

app = Flask(__name__)


def msgFormat(msg, groupid='0'):
    if '[CQ:image' in msg:
        if config.TG == "True":
            img_cqcode = re.findall('\[CQ:image.*?]', msg)
            for cqcode in img_cqcode:
                imageurl = re.findall('(?<=,url=).*?(?=\?term=)', cqcode)
                imageurl = ' '.join(imageurl)
                renew = '[图片] ' + imageurl + '\n'
                msg = msg.replace(cqcode, renew)
        else:
            img_cqcode = re.findall('\[CQ:image.*?]', msg)
            for cqcode in img_cqcode:
                msg = msg.replace(cqcode, '[图片]')
    if '[CQ:video' in msg:
        if config.TG == "True":
            videourl = re.findall('(?<=.url=).*?(?=,])', msg)
            videourl = ' '.join(videourl)
            renew = '[视频] ' + videourl
            msg = msg.replace(msg, renew)
        else:
            msg = "[视频]"
    if '[CQ:reply' in msg:
        reply_cqcode = re.findall('\[CQ:reply.*?]', msg)
        reply_cqcode = ' '.join(reply_cqcode)
        replymsg_id = re.findall('(?<=.id=).*?(?=])', reply_cqcode)
        replymsg_id = ' '.join(replymsg_id)
        reply_format = replymsg(replymsg_id)
        msg = msg.replace(reply_cqcode, reply_format)
    if '[CQ:at' in msg:
        if '[CQ:at,qq=all]' in msg:
            msg = msg.replace('[CQ:at,qq=all]', '@全体成员')
        else:
            at_id = re.findall('\[CQ:at,qq=.*?\]', str(msg))
            for uid in at_id:
                at_info_api = 'http://localhost:5700/get_group_member_info?group_id=' + str(groupid) + "&user_id=" + str(uid)
                at_info = json.loads(requests.get(at_info_api).content)
                if at_info["data"]["card"] != "":
                    at_name = " @" + at_info["data"]["card"] + " "
                else:
                    at_name = " @" + at_info["data"]["nickname"] + " "
                at_cqcode = '[CQ:at,qq=' + str(uid) + ']'
                msg = msg.replace(at_cqcode, at_name)
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
        if config.TG == "True":
            msg = '[小程序] ' + mini_from + '\n' + mini_tittle + '\n' + mini_jumpurl
        else:
            msg = '[小程序] ' + mini_from + '\n' + mini_tittle
    if 'com.tencent.structmsg' in msg:
        jumpurl = re.findall('(?<="jumpUrl":").*?(?="&)',msg)
        jumpurl = ' '.join(jumpurl)
        jumpurl = jumpurl.replace('\\','')
        tittle = re.findall(r'(?<="title":").*?(?="&)',msg)
        tittle = ' '.join(tittle)
        if config.TG == 'True':
            msg = tittle + '\n' + jumpurl
        else:
            msg = tittle
    if "CQ:face" in msg:
        face_idgroup = re.findall('(?<=CQ:face,id=).*?(?=\])', msg)
        for face_id in face_idgroup:
            emoji_name = getEmojiName(face_id)
            emoji_name = f'[{emoji_name}]'
            regex = '\[CQ:face,id=' + face_id + ']'
            face_cqcode = re.findall(regex, msg)
            for cqcode in face_cqcode:
                msg = msg.replace(cqcode, emoji_name)
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
    msg = html.unescape(msg)
    return msg


def getGroupName(groupId):
    length = len(groupInfo["data"])
    for i in range(length):
        if groupId == groupInfo["data"][i]["group_id"]:
            return groupInfo["data"][i]["group_name"]


def getnickname(id):
    url = 'http://localhost:5700/get_stranger_info?user_id=' + str(id)
    userInfo = json.loads(requests.get(url).text)
    return userInfo["data"]["nickname"]


def styletime(now):
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def getfriendmark(UID):
    name = 'None'
    length = len(friendInfo.get("data"))
    for i in range(length):
        if UID == friendInfo["data"][i]["user_id"]:
            if friendInfo["data"][i]["remark"] != '':
                name = friendInfo["data"][i]["remark"]
            else:
                name = friendInfo["data"][i]["nickname"]
            break
    if name == 'None':
        name = getnickname(UID) or "未知"
    return name


def replymsg(msgid):
    replymsg_api= f'http://localhost:5700/get_msg?message_id={msgid}'
    replymsg_json = json.loads(requests.get(replymsg_api).text)
    replymsg = replymsg_json["data"]["message"]
    replymsg_sender = replymsg_json["data"]["sender"]["nickname"]
    replymsg_timestamp = replymsg_json["data"]["time"]
    replymsg_styletime = styletime(replymsg_timestamp)
    if config.TG == "True":
        replymsg = "[回复：" + replymsg_sender + "(" + replymsg_styletime + "): " + replymsg + "]\n"
    else:
        replymsg = f"回复 {replymsg_sender}的消息: "
    return replymsg


def getEmojiName(face_id):
    face_name = '表情'
    for i in range(0, len_face):
        if face_data["sysface"][i]['QSid'] == face_id:
            QDes = face_data['sysface'][i]['QDes']
            face_name = QDes.replace('/','')
            break
    return face_name


@app.route("/",methods=['POST'])
async def recvMsg():
    global TG_ID, groupId
    groupId = ''
    TG_ID = ''
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    try:
        if json_data["post_type"] == "meta_event":
            if json_data["meta_event_type"] == "heartbeat":
                prt("接收心跳信号成功")
        elif json_data["post_type"] == "request":
            if json_data["request_type"] == "friend":
                friendId = json_data["user_id"]
                prt("新的好友添加请求：%s" % friendId)
                if config.MiPush == "True":
                    await httpx.AsyncClient().post(config.MiPush_API, data={'title': "新的好友添加请求", 'content': '%s想要添加您为好友' % friendId,'alias': config.KEY})
                elif config.FCM == "True":
                    await httpx.AsyncClient().post(config.FCM, data={'id': config.KEY, 'title': "新的好友添加请求",'message': '%s想要添加您为好友' % friendId,'type': 'FriendAdd'})
                elif config.TG == "True":
                    msg = friendId + ' 请求添加您为好友'
                    senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
                    url = f"{config.TG_API}/bot{config.KEY}/sendMessage"
                    await httpx.AsyncClient().post(url=url, data=senddata)
        elif json_data["post_type"] == "notice":
            if json_data["notice_type"] == "group_upload":
                if json_data["group_id"] in config.WhiteList:
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
                    if config.MiPush == "True":
                        await httpx.AsyncClient().post(config.MiPush_API, data={'title': "QQ通知", 'content': '%s' % (msg), 'alias': config.KEY})
                    if config.FCM == "True":
                        await httpx.AsyncClient().post(config.FCM, data={'id': config.KEY, 'title': "QQ通知", 'message': msg,'type': 'privateMsg'})
                    if config.TG == "True":
                        if str(groupId) in config.TG_GroupLink:
                            TG_ID = config.TG_GroupLink[str(groupId)]
                        senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
                        url = f"{config.TG_API}/bot{config.KEY}/sendMessage"
                        await httpx.AsyncClient().post(url=url, data=senddata)
        elif json_data["message_type"] == "private":
            msg = msgFormat(json_data["message"])
            uid = json_data["sender"]["user_id"]
            nickname = getfriendmark(uid)
            prt("来自%s的私聊消息:%s" % (nickname, msg))
            if config.MiPush == "True":
                await httpx.AsyncClient().post(config.MiPush_API, data={'title': nickname, 'content': msg, 'alias': config.KEY})
            elif config.FCM == "True":
                await httpx.AsyncClient().post(config.FCM, data={'id': config.KEY, 'title': nickname, 'message': msg,'type': 'privateMsg'})
            elif config.TG == "True":
                if str(uid) in config.TG_GroupLink:
                    TG_ID = config.TG_GroupLink[str(uid)]
                else:
                    TG_ID = config.TG_UID
                msg = nickname + ":\n" + msg
                senddata = {"chat_id": TG_ID, "text": msg, "disable_web_page_preview": "true"}
                url = f"{config.TG_API}/bot{config.KEY}/sendMessage"
                await httpx.AsyncClient().post(url=url, data=senddata)
        elif json_data["message_type"] == "group":
            groupId = json_data["group_id"]
            groupName = getGroupName(groupId)
            nickName = json_data["sender"]["nickname"]
            card = json_data["sender"]["card"]
            msg = msgFormat(json_data["message"], groupId)
            if groupId in config.WhiteList:
                prt("群聊%s的消息:%s:%s" % (groupName, nickName, msg))
                if config.MiPush == "True":
                    if card != "":
                        await httpx.AsyncClient().post(config.MiPush_API, data={'title': '%s' % groupName,'content': '%s:%s' % (card, msg), 'alias': config.KEY})
                    else:
                        await httpx.AsyncClient().post(config.MiPush_API, data={'title': '%s' % groupName, 'content': '%s:%s' % (nickName, msg), 'alias': config.KEY})
                if config.FCM == "True":
                    await httpx.AsyncClient().post(config.FCM, data={'id': '%s' % config.KEY, 'title': groupName,'message': '%s:%s' % (nickName, msg), 'type': 'groupMsg'})
                if config.TG == "True":
                    if str(groupId) in config.TG_GroupLink:
                        TG_ID = config.TG_GroupLink[str(groupId)]
                    else:
                        TG_ID = config.TG_UID
                    if card != "":
                        text = card + "[" + groupName + "]" + ":\n" + msg
                    else:
                        text = nickName + "[" + groupName + "]" + ":\n" + msg
                    senddata = {"chat_id": TG_ID, "text": text, "disable_web_page_preview": "true"}
                    url = f"{config.TG_API}/bot{config.KEY}/sendMessage"
                    await httpx.AsyncClient().post(url=url, data=senddata)
    except:
        with open(str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/')) + '/error.log', 'a', encoding='utf-8') as f:
            f.write(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + str(traceback.format_exc()) + '\n')
        prt('发生错误，错误信息已保存到error.log')
    return "200 OK"


if __name__ == '__main__':
    errorlog_clean = open(str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/')) + '/error.log', 'w').close()
    prt('程序开始运行')
    app.run(host="127.0.0.1",port=5000)
