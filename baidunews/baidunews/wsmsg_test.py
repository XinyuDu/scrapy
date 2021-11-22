from baidunews.wxmsg import wxmsg

content = "this is content"
title = "this is title"
for i in range(10):
    msg = wxmsg(token='95ffa823a2bd41a5b9119fe491d5c0f8', title=title, content=content)
    msg.send()
