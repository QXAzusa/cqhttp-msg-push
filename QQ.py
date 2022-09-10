# coding=utf-8

import json
import requests
import html
import re
import os
import time
import logging
import traceback
from requests.packages import urllib3
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
    userId = json.loads(requests.get("http://localhost:5700/get_login_info").text).get("data").get("user_id")
except:
    prt("无法从go-cqhttp获取信息,请检查go-cqhttp是否运行或端口配置是否正确")
    os._exit(0)

app = Flask(__name__)


def msgFormat(msg, groupid='0'):
    if '[CQ:image' in msg:
        img_cqcode = re.findall('\[(.*?)\]', msg)
        for cqcode in img_cqcode:
            imgcode = '[' + cqcode + ']'
            imgurl =  re.findall('(.*?),url=(.*?)\]', imgcode)[0][1]
            msg = msg.replace(imgcode, '[图片] ' + imgurl + '\n') if str(config.TG) == "True" else msg.replace(imgcode, '[图片]')
    if '[CQ:video' in msg:
        videourl = re.findall('(.*?)url=(.*?)\]', msg)[0][1]
        msg = '[视频] ' + videourl if str(config.TG) == "True" else "[视频]"
    if '[CQ:reply' in msg:
        replymsg_id = ''.join(re.findall('\[CQ:reply,id=(.*?)\]', msg))
        reply_format = replymsg(replymsg_id)
        msg = msg.replace('[CQ:reply,id=' + str(replymsg_id) + ']', reply_format)
    if '[CQ:at' in msg:
        if '[CQ:at,qq=all]' in msg:
            msg = msg.replace('[CQ:at,qq=all]', '@全体成员')
        else:
            at_id = re.findall('\[CQ:at,qq=(.*?)\]', msg)
            for uid in at_id:
                at_info_api = 'http://localhost:5700/get_group_member_info?group_id=' + str(groupid) + "&user_id=" + str(uid)
                at_info = json.loads(requests.get(at_info_api).content)
                if str(at_info.get("data")) != 'None':
                    at_name = "@" + str(at_info.get("data").get("nickname")) if at_info.get("data").get("card") == "" else "@" + str(at_info.get("data").get("card"))
                    at_cqcode = '[CQ:at,qq=' + str(uid) + ']'
                    msg = msg.replace(at_cqcode, at_name)
                else:
                    msg = 'None'
                    break
    if "[CQ:face" in msg:
        face_idgroup = re.findall('\[CQ:face,id=(.*?)\]', msg)
        for face_id in face_idgroup:
            emoji_name = getEmojiName(face_id)
            face_cqcode = '[CQ:face,id=' + face_id + ']'
            msg = msg.replace(face_cqcode, emoji_name)
    if "[CQ:json" in msg:
        data = json.loads(str(re.findall('(.*?)\[CQ:json,data=(.*?)\]', msg)[0][1]).replace('&#44;', ','))
        view = list(data.get('meta').keys())[0]
        if 'com.tencent.miniapp' in data.get('app'):
            mini_title = data.get('meta').get(view).get('title')
            mini_url = data.get('meta').get(view).get('url').replace('\\', '')
            msg = '[小程序]' + mini_title + '\n' + mini_url if str(config.TG) == "True" else '[小程序]' + mini_title
        elif 'com.tencent.structmsg' in data.get('app'):
            jumpurl = data.get('meta').get(view).get('jumpUrl')
            title = data.get('meta').get(view).get('title')
            msg = '[分享]' + title + '\n' + jumpurl if str(config.TG) == 'True' else '[分享]' + title
        else:
            msg = '[卡片消息]'
    if "[CQ:record" in msg:
        msg = "[语音]"
    if "[CQ:share" in msg:
        msg = "[链接]"
    if "[CQ:music" in msg:
        msg = "[音乐分享]"
    if "[CQ:redbag" in msg:
        msg = "[红包]"
    if "[CQ:forward" in msg:
        msg = "[合并转发]"
    if "[CQ:xml" in msg:
        msg = '[卡片消息]'
    if "&#91;戳一戳&#93;请使用最新版手机QQ体验新功能。" in msg:
        msg = "[戳一戳]"
    msg = html.unescape(msg)
    return msg


def getGroupName(groupId):
    length = len(groupInfo.get("data"))
    for i in range(length):
        if groupId == groupInfo["data"][i]["group_id"]:
            return groupInfo["data"][i]["group_name"]


def getnickname(id):
    url = 'http://localhost:5700/get_stranger_info?user_id=' + str(id)
    userInfo = json.loads(requests.get(url).text)
    return userInfo.get("data").get("nickname")


def styletime(now):
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def getfriendmark(UID):
    name = 'None'
    length = len(friendInfo.get("data"))
    for i in range(length):
        if UID == friendInfo["data"][i]["user_id"]:
            name = friendInfo["data"][i]["remark"] if friendInfo["data"][i]["remark"] != '' else friendInfo["data"][i]["nickname"]
            break
    if name == 'None':
        name = getnickname(UID) or "未知"
    return name


def data_send(url, **kwargs):
    for i in range(1, 5):
        try:
            response = requests.post(url, data=kwargs, timeout=5, verify=False)
            if response.status_code > 299:
                raise RuntimeError
        except:
            if str(i) == '4':
                print(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + '连续三次向接口发送数据超时/失败，可能是网络问题或接口失效，终止发送')
                break
            print(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + '向接口发送数据超时/失败，第' + str(i) + '次重试')
        else:
            print(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + '成功向接口发送数据↑')
            break


def replymsg(msgid):
    replymsg_api= f'http://localhost:5700/get_msg?message_id={msgid}'
    replymsg_json = json.loads(requests.get(replymsg_api).text)
    if str(replymsg_json.get("data")) != 'None':
        replymsg = replymsg_json.get("data").get("message")
        replymsg_sender = replymsg_json.get("data").get("sender").get("nickname")
        replymsg_timestamp = replymsg_json.get("data").get("time")
        replymsg_styletime = styletime(replymsg_timestamp)
        reply_msg = "[回复" + replymsg_sender + "(" + replymsg_styletime + "): " + replymsg + "]\n" if str(config.TG) == "True" else replymsg = f"[回复{replymsg_sender}的消息]"
    else:
        reply_msg = '[消息回复]'
    return reply_msg


def getEmojiName(face_id):
    face_name = '[表情]'
    for i in range(0, len_face):
        QSid = face_data.get('sysface')[i].get('QSid')
        QDes = face_data.get('sysface')[i].get('QDes')
        if QSid == face_id:            
            face_name = '[' + QDes.replace('/','') + ']'
            break
    return face_name


@app.route("/", methods=['GET', 'POST'])
async def recvMsg():
    global TG_ID, groupId
    groupId = ''
    TG_ID = ''
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    try:
        if json_data.get("post_type") == "request":
            if json_data.get("request_type") == "friend":
                friendId = json_data.get("user_id")
                nickname = getnickname(friendId)
                prt("新的好友添加请求：%s" % friendId)
                if str(config.MiPush) == "True":
                    data_send(config.MiPush_API, title="新的好友添加请求", content='%s想要添加您为好友' % friendId, alias=config.KEY)
                elif str(config.FCM) == "True":
                    data_send(config.FCM_API, id=config.KEY, title="新的好友添加请求", message='%s想要添加您为好友' % friendId, type='FriendAdd')
                elif str(config.TG) == "True":
                    msg = friendId + ' 请求添加您为好友'
                    url = f"{str(config.TG_API)}/bot{str(config.KEY)}/sendMessage"
                    data_send(str(url), chat_id=str(TG_ID), text=str(msg), disable_web_page_preview="true")
        elif json_data.get("post_type") == "notice":
            if json_data.get("notice_type") == "group_upload":
                if json_data.get("group_id") in list(config.WhiteList):
                    groupId = json_data.get("group_id")
                    groupName = getGroupName(groupId)
                    filename = json_data.get("file").get("name")
                    userid = json_data.get("user_id")
                    cardurl = 'http://localhost:5700/get_group_member_info?group_id=' + str(groupId) + "&user_id=" + str(userid)
                    card = json.loads(requests.get(cardurl).content)
                    if card.get("data").get("card") != "":
                        card = card.get("data").get("card") + " "
                    else:
                        card = card.get("data").get("nickname") + " "
                    msg = card + '上传了 ' + filename
                    prt(str(groupName) + ': ' + str(msg))
                    if str(config.MiPush) == "True":
                        data_send(config.MiPush_API, title="QQ通知", content='%s' % (msg), alias=config.KEY)
                    if str(config.FCM) == "True":
                        data_send(config.FCM_API, id=config.KEY, title="QQ通知", message=str(msg), type='privateMsg')
                    if str(config.TG) == "True":
                        if str(groupId) in dict(config.TG_GroupLink):
                            TG_ID = dict(config.TG_GroupLink).get(str(groupId))
                        url = f"{str(config.TG_API)}/bot{str(config.KEY)}/sendMessage"
                        data_send(str(url), chat_id=str(TG_ID), text=str(msg), disable_web_page_preview="true")
        elif json_data.get("message_type") == "private":
            msg = msgFormat(json_data.get("message"))
            uid = json_data.get("sender").get("user_id")
            nickname = getfriendmark(uid)
            prt("%s: %s" % (nickname, msg))
            if str(config.MiPush) == "True":
                data_send(config.MiPush_API, title=str(nickname), content=str(msg), alias=config.KEY)
            elif str(config.FCM) == "True":
                data_send(config.FCM_API, id=config.KEY, title=str(nickname), message=msg, type='privateMsg')
            elif str(config.TG) == "True":
                if str(uid) in dict(config.TG_GroupLink):
                    TG_ID = dict(config.TG_GroupLink).get(str(uid))
                else:
                    TG_ID = str(config.TG_UID)
                msg = nickname + ":\n" + msg
                url = f"{str(config.TG_API)}/bot{str(config.KEY)}/sendMessage"
                data_send(str(url), chat_id=str(TG_ID), text=str(msg), disable_web_page_preview="true")
        elif json_data.get("message_type") == "group":
            uid = json_data.get("sender").get("user_id")
            nickName = json_data.get("sender").get("nickname")
            card = json_data.get("sender").get("card")
            groupId = json_data.get("group_id")
            msg = msgFormat(json_data.get("message"), groupid=str(groupId))
            groupName = getGroupName(groupId)
            nickName = str(card) if str(card) != "" else str(nickName)
            if str(msg) != 'None' and groupId in list(config.WhiteList):
                prt("%s: %s: %s" % (groupName, nickName, msg))
                if str(config.MiPush) == "True":
                    data_send(config.MiPush_API, title='%s' % groupName, content='%s:%s' % (nickName, msg), alias=config.KEY)
                if str(config.FCM) == "True":
                    data_send(config.FCM_API, id='%s' % config.KEY, title=str(groupName), message='%s:%s' % (nickName, msg), type='groupMsg')
                if str(config.TG) == "True":
                    if str(groupId) in dict(config.TG_GroupLink):
                        TG_ID = dict(config.TG_GroupLink).get(str(groupId))
                    else:
                        TG_ID = str(config.TG_UID)
                    text = nickName + "[" + groupName + "]" + ":\n" + msg
                    url = f"{str(config.TG_API)}/bot{str(config.KEY)}/sendMessage"
                    data_send(str(url), chat_id=str(TG_ID), text=str(text), disable_web_page_preview="true")
    except:
        with open(str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/')) + '/error.log', 'a', encoding='utf-8') as f:
            f.write(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + str(traceback.format_exc()) + '\n')
        prt('发生错误，错误信息已保存到error.log')
    return "200 OK"


if __name__ == '__main__':
    urllib3.disable_warnings()
    errorlog_clean = open(str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/')) + '/error.log', 'w').close()
    prt('程序开始运行')
    app.run(host="127.0.0.1", port=5000)
