# from utils import get_all_data, get_daily_data, get_ipo_date
#
# # print(get_ipo_date('sh.600031'))
# #
# # print(get_all_data())
# today = '2022-03-01'
# print(get_daily_data('sh.600031', today, today))
from pushplus import pushplus

body = {
    "token": "2cfba23c342a4deeba50a6d922ec2ea4",
    "content": 'test pushplus class',
    "title": "Baostock cron daily finished",
}

msg = pushplus(body)
msg.send()