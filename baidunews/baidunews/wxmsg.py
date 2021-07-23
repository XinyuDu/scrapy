# 发送消息到pushplus
import requests
import json

class wxmsg():
    def __init__(self, token, title, content):
        self.token = token
        self.title = title
        self.content = content

    def send(self):
        url = 'http://pushplus.hxtrip.com/send'
        data = {
            "token": self.token,
            "title": self.title,
            "content": self.content
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        requests.post(url, data=body, headers=headers)