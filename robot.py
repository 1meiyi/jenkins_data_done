#!/usr/bin/env python3
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests, json


class Robot:
    def __init__(self, token, secret=None):
        self.token = token
        self.secret = secret
        self.headers = {'Content-Type': 'application/json'}

    def sign_secret(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        return [timestamp, sign]

    def gen_send_url(self):
        timestamp, sign = self.sign_secret()
        return f"https://oapi.dingtalk.com/robot/send?access_token={self.token}&timestamp={timestamp}&sign={sign}"

    def send_text(self, text, at_dingtalk_ids=[]):
        data = {
            "msgtype": "text",
            "text": {"content": text},
            "isAtAll": False}
        if len(at_dingtalk_ids) > 0:
            data["at"] = {"atDingtalkIds": at_dingtalk_ids}
        return requests.post(self.gen_send_url(), data=json.dumps(data), headers=self.headers)

    def send_link(self, link, text, title, at_dingtalk_ids=[]):
        data = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "messageUrl": link,
            },
        }
        if len(at_dingtalk_ids) > 0:
            data["at"] = {"atDingtalkIds": at_dingtalk_ids}
        return requests.post(self.gen_send_url(), data=json.dumps(data), headers=self.headers)

    def send_markdown(self, text, title, at_dingtalk_ids=[]):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "text": text,
                "title": title,
            },
        }
        if len(at_dingtalk_ids) > 0:
            data["at"] = {"atDingtalkIds": at_dingtalk_ids}
        return requests.post(self.gen_send_url(), data=json.dumps(data), headers=self.headers)

    def send_msg(self, text, type='text', title="", at_dingtalk_ids=[]):
        if type == 'text':
            rs = self.send_text(text, at_dingtalk_ids)
        elif type == 'markdown':
            rs = self.send_markdown(text, title, at_dingtalk_ids)
        else:
            raise Exception(f"not support msg type:{type}")
        return rs

    def get_group_member(self, open_conversation_id):
        url = f"https://oapi.dingtalk.com/topapi/im/chat/scenegroup/member/get?access_token={self.token}"
        data = {
            "cursor": "0",
            "size": 10,
            "open_conversation_id": "open_conversation_id"}
        return requests.post(url, data=json.dumps(data), headers=self.headers)


# https://open.dingtalk.com/document/group/custom-robot-access
if "__main__" == __name__:
    token = "a6610f68343a345c1b8b5d4cced57dbeb70a6783c9a18f96f85dad268fa05054"
    secret = "SEC44b85d6cfe5812423e4482d5b50c7c193631cd1aa0e29833c77e28e9ed97705d"
    o = Robot(token, secret)
    # rs = o.send_markdown("## haha \n 内容换行\n### 111", "test")
    # rs = o.send_text("test @jowl1l0,test", ['jowl1l0'])
    # print(rs.text)
    # rs = o.send_link("http://www.baidu.com","baidu", "baidu!")
    # print(rs.text)
    # rs = o.send_markdown("## haha \n 内容换行@jowl1l0,test","test", ['jowl1l0'])
    # rs = o.send_markdown("## haha \n 内容换行\n### 111","test")

