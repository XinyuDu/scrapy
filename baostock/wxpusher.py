# 发送消息到WxPusher
import requests
import json

class wxpusher():
    def __init__(self, body):
        self.body = body

    def send(self):
        url = 'http://wxpusher.zjiecode.com/api/send/message'
        body = json.dumps(self.body).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        re = requests.post(url, data=body, headers=headers)
        return re