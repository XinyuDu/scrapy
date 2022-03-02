import time
from sqlalchemy import create_engine, types
import pandas as pd
from datetime import datetime
from utils import get_all_data, get_daily_data
from wxpusher import wxpusher

engine = create_engine('mysql+pymysql://root:123qwe@localhost:3306/stocks')

start_line_num = pd.read_sql_query('select count(*) from daily_history', engine)
start_line_num = start_line_num.loc[0]['count(*)']


# last date
last_date = pd.read_sql_query('select max(date) from daily_history', engine)
last_date = last_date.loc[0]['max(date)']

# get all stock list and put it into db
stock_list = get_all_data(last_date)
if len(stock_list) > 0:
    stock_list.to_sql('stock_list', engine, index=True, if_exists='replace')

# del all data where date=today
today = datetime.now().strftime("%Y-%m-%d")
with engine.connect() as con:
    con.execute('DELETE FROM daily_history WHERE date=\'%s\'' % today)

# get every stock today date and put it into db in loop
behave = 'append'
sql_types = {'date': types.Date,
             'code': types.VARCHAR(50),
             'open': types.Float,
             'high': types.Float,
             'low': types.Float,
             'close': types.Float,
             'preclose': types.Float,
             'volume': types.BigInteger,
             'amount': types.Float,
             'adjustflag': types.SmallInteger,
             'tradestatus': types.SmallInteger,
             'pctChg': types.Float,
             'peTTM': types.Float,
             'pbMRQ': types.Float,
             'psTTM': types.Float,
             'pcfNcfTTM': types.Float,
             'isST': types.Float}

start_time = time.time()
for index, row in stock_list.iterrows():
    stock_code = row['code']
    daily_result = get_daily_data(stock_code, today, today)
    if len(daily_result) == 0:
        continue
    daily_result.replace('', 0, inplace=True)
    daily_result.to_sql('daily_history', engine, index=False, if_exists=behave, dtype=sql_types)

end_line_num = pd.read_sql_query('select count(*) from daily_history', engine)
end_line_num = end_line_num.loc[0]['count(*)']

end_time = time.time()
print('Total time cost:', end_time-start_time)

# push wx message
content = "The baostock daily cron task finished add record num: %d. Total time cost:%d seconds" % \
          (end_line_num-start_line_num, end_time-start_time)
body = {
                "appToken": "AT_a2fSMuBxfl5WEOkOkq13NixH7ZTKYJqG",
                "content": content,
                "summary": "Baostock cron daily finished",
                "contentType": 2,
                "uids": ["UID_RxY9fJ8MaWCFWdXzOfMCkCmYhdPY"],
                "url": "url"
            }
msg = wxpusher(body)
re = msg.send()
print(re.text)

