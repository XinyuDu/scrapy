import requests
import json

class pushplus():
    def __init__(self, body):
        self.body = body

    def send(self):
        print(self.body)
        token = self.body['token']  # 前边复制到那个token
        title = self.body['title']
        content = self.body['content']
        template = 'html'
        url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
        print(url)
        r = requests.get(url=url)
        print(r.text)

        return r.text