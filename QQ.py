# coding=utf-8

import json
import requests
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
    userId = json.loads(requests.get("http://localhost:5700/get_login_info").text).get("data").get("user_id")
except:
    prt("无法从go-cqhttp获取信息,请检查go-cqhttp是否运行或端口配置是否正确")
    os._exit(0)

app = Flask(__name__)


def msgFormat(msg, groupid='0'):
    if '[CQ:image' in msg:
        if str(config.TG) == "True":
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
        if str(config.TG) == "True":
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
        if str(reply_format) == 'None':
            msg == 'None'
        else:
            msg = msg.replace(reply_cqcode, reply_format)
    if '[CQ:at' in msg:
        if '[CQ:at,qq=all]' in msg:
            msg = msg.replace('[CQ:at,qq=all]', '@全体成员')
        else:
            at_id = re.findall('\[CQ:at,qq=.*?\]', str(msg))
            for uid in at_id:
                at_info_api = 'http://localhost:5700/get_group_member_info?group_id=' + str(groupid) + "&user_id=" + str(uid)
                at_info = json.loads(requests.get(at_info_api).content)
                if str(at_info.get("data")) != 'None':
                    if at_info.get("data").get("card") != "":
                        at_name = "@" + str(at_info.get("data").get("card"))
                    else:
                        at_name = "@" + str(at_info.get("data").get("nickname"))
                    at_cqcode = '[CQ:at,qq=' + str(uid) + ']'
                    msg = msg.replace(at_cqcode, at_name)
                else:
                    msg = 'None'
                    break
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
        if str(config.TG) == "True":
            msg = '[小程序] ' + mini_from + '\n' + mini_tittle + '\n' + mini_jumpurl
        else:
            msg = '[小程序] ' + mini_from + '\n' + mini_tittle
    if 'com.tencent.structmsg' in msg:
        jumpurl = re.findall('(?<="jumpUrl":").*?(?="&)',msg)
        jumpurl = ' '.join(jumpurl)
        jumpurl = jumpurl.replace('\\','')
        tittle = re.findall(r'(?<="title":").*?(?="&)',msg)
        tittle = ' '.join(tittle)
        if str(config.TG) == 'True':
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
    length = len(groupInfo.get("data"))
    for i in range(length):
        if groupId == groupInfo.get("data")[i].get("group_id"):
            return groupInfo.get("data")[i].get("group_name")


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
        if UID == friendInfo.get("data")[i].get("user_id"):
            if friendInfo.get("data")[i].get("remark") != '':
                name = friendInfo.get("data")[i].get("remark")
            else:
                name = friendInfo.get("data")[i].get("nickname")
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
        if str(config.TG) == "True":
            replymsg = "[回复：" + replymsg_sender + "(" + replymsg_styletime + "): " + replymsg + "]\n"
        else:
            replymsg = f"回复 {replymsg_sender}的消息: "
    else:
        replymsg = 'None'
    return replymsg


def getEmojiName(face_id):
    face_name = '表情'
    for i in range(0, len_face):
        if face_data.get("sysface")[i].get('QSid') == face_id:
            QDes = face_data.get('sysface')[i].get('QDes')
            face_name = QDes.replace('/','')
            break
    return face_name


@app.route("/",methods=['GET', 'POST'])
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
                if str(json_data.get("group_id")) in list(list(config.WhiteList)):
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
    errorlog_clean = open(str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/')) + '/error.log', 'w').close()
    prt('程序开始运行')
    app.run(host="127.0.0.1",port=5000)
