from utils import get_all_data, get_daily_data, get_ipo_date

print(get_ipo_date('sh.600031'))

print(get_all_data())

print(get_daily_data('sh.600031', '2020-01-01', '2020-02-24'))
