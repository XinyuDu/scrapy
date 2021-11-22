from baidunews.wxpusher import wxpusher

content = "this is content"
title = "this is title"
for i in range(1):
    body = {
      "appToken":"AT_a2fSMuBxfl5WEOkOkq13NixH7ZTKYJqG",
      "content":"Wxpusher祝你中秋节快乐!",
      "summary":"消息摘要",
      "contentType":1,
      "uids":["UID_RxY9fJ8MaWCFWdXzOfMCkCmYhdPY"],
      "url":"http://wxpusher.zjiecode.com"
    }
    msg = wxpusher(body)
    re = msg.send()
    print(re.text)
