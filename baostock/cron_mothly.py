import pandas as pd
from sqlalchemy import create_engine, types
from datetime import datetime
from utils import get_all_data, get_daily_data

engine = create_engine('mysql+pymysql://root:123qwe@localhost:3306/stocks')

# get all stock list and put it into db
stock_list = get_all_data()
stock_list.to_sql('stock_list', engine, index=True, if_exists='replace')

# get every stock daily date and put it into db in loop
today = datetime.now().strftime("%Y-%m-%d")
behave = 'replace'
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

for index, row in stock_list.iterrows():
    stock_code = row['code']
    ipo_date = '1990-12-19'  # get_ipo_date(stock_code)
    daily_result = get_daily_data(stock_code, ipo_date, today)
    daily_result.replace('', 0, inplace=True)
    daily_result.to_sql('daily_history', engine, index=False, if_exists=behave, dtype=sql_types)
    if behave == 'replace':
        with engine.connect() as con:
            con.execute('ALTER TABLE `daily_history` ADD INDEX `code_index` USING BTREE (`code`) VISIBLE;')
        behave = 'append'
