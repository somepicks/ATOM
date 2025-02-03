import KIS
import sys
import talib
# import pyupbit
from PyQt5.QtWidgets import QWidget,QPushButton,QApplication,QListWidget,QGridLayout,QLabel
from PyQt5.QtCore import QTimer,QDateTime
from PyQt5.QtWidgets import *
import pandas as pd
from pandas import to_numeric
from PyQt5.QtCore import *
from collections import deque
import numpy as np
import datetime
# from pymongo import MongoClient
# import ccxt
import sqlite3
from pprint import pprint
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
# from ccxt.base.decimal_to_precision import TICK_SIZE
# import talib as ta
# import pyupbit
# from collections import deque
# import schedule
# # 5초에 한번씩 함수 실행
# import schedule
# import time
# import mojito
# import pickle
# import requests
# import json
# import talib
import common_def
import ccxt

def stamp_to_int( stamp_time):
    dt = datetime.datetime.fromtimestamp(stamp_time)
    dt = dt.strftime('%Y%m%d%H%M')
    return int(dt)
def stamp_to_int(t):
    hours = str(t // 3600)
    remaining_seconds = t % 3600
    minutes = str(remaining_seconds // 60)
    seconds = str(remaining_seconds % 60)
    return f"{hours}:{minutes}:{seconds}"

def str_to_datetime( str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
def int_to_stamp( int_time):
    dt = datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
    return int(dt.timestamp())
def int_to_datetime( int_time):
    return datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
def stamp_to_datetime( stamp_time):
    int_time = stamp_to_int(stamp_time)
    return datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
def datetime_to_stamp(date_time):
    return int(time.mktime(date_time.timetuple()))


from pybit.unified_trading import HTTP, WebSocket
# Bybit API 키 설정
api_key = 'ZFEksBSBjIHk7drUou'
api_secret = 'MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI'

session = HTTP(
    testnet=False,
    api_key='ZFEksBSBjIHk7drUou',
    api_secret='MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI',
)
def fetch_balance(accountType,ticker,balance):
    res = session.get_coins_balance(
        accountType=accountType, # CONTRACT: Inverse Derivatives Account, UNIFIED: Unified Trading Account
        coin=ticker, # BTCUSD, BTC
    )
    # return res['result']['balance'][0]['walletBalance']
    # pprint(res)
    if balance == '보유':
        return float(res['result']['balance'][0]['walletBalance'])
    elif balance == '잔고':
        return float(res['result']['balance'][0]['transferBalance'])
def fetch_withdrawable(ticker):
    res = session.get_positions()
    pprint(res)
def pybit_open_order(category,ticker,side,orderType,price,qty):
    res = session.place_order(
        category=category, # spot, linear, inverse, option
        symbol=ticker,
        side=side, #Buy, Sell
        orderType=orderType, # Market, Limit
        qty=qty,
        price=price,
        timeInForce="PostOnly",
        # orderLinkId="spot-test-postonly",
        isLeverage=1, #0(default): false then spot trading, 1: true then margin trading
        orderFilter="Order",
    )
    return res
def pybit_open_order1():
    res = session.place_order(
        category="inverse",
        symbol="BTCUSD",
        side="Sell",
        orderType="Market",# Market, Limit
        qty="1",
    )
    return res
def fetch_closed_order(category,id):
    res = session.get_executions(
        category=category,  # spot, linear, inverse, option
        limit = 50
    )['result']['list']
    pprint(res)
    print(type(res))
    return res
def fetch_order(category,ticker,id):
    res = session.get_open_orders(
        category=category,
        symbol=ticker,
        openOnly=0,
        limit=10,
    )['result']['list']
    if res == []:
        execution = True
    else:
        for order in res:
            if not order['orderId'] == id:
                execution = True
            else:
                print('미체결')
                return {'체결':False}
    if execution == True:
        res = session.get_order_history(
            category=category,  # spot, linear, inverse, option
            limit = 10
        )['result']['list']
        for order in res:
            if order['orderId'] == id:
                pprint(order['orderStatus'])
                if order['orderStatus'] == 'Filled':
                    print('체결완료')
                    # pprint(order)
                    return {'체결':True, '체결가':order['avgPrice'], '체결수량':order['cumExecQty'],'수수료':order['cumExecFee']}
                elif order['orderStatus'] == 'Cancelled':
                    print('주문취소')
                    return {'체결':'주문취소'}
                elif order['orderStatus'] == 'PartiallyFilledCanceled':
                    print('부분체결')
    return {'체결':False}

def pnl():
    return session.get_executions(
        category="inverse",
        limit=1,
    )
def internal_transfer(ticker,qty,fromAccount,toAccount):
    return session.create_internal_transfer(
        transferId="42c0cfb0-6bca-c242-bc76-4e6df6cbcb16",
        coin=ticker, # BTC
        amount=qty,
        fromAccountType=fromAccount, # UNIFIED
        toAccountType=toAccount, # CONTRACT
    )
def ticker_info(Account,ticker):
    return session.get_instruments_info(
    category=Account, # spot, linear, inverse, option
    symbol=ticker,
    )['result']['list'][0]
def fetch_ticker(Account, ticker):
    return session.get_tickers(
        category=Account,
        symbol=ticker,
    )['result']['list'][0]
def fetch_account_info( Account, ticker):
    return session.get_instruments_info(
        category=Account,  # spot, linear, inverse, option
        symbol=ticker, # BTC, BTCUSDT, BTCUSD
    )['result']['list'][0]
def price_to_precision(category, ticker, price):
    if category == 'spot':
        res = fetch_account_info(Account=category, ticker=ticker)
        price_min = res['priceFilter']['tickSize'].index('1') - 1
        return round(price, price_min)
    elif category == 'inverse':
        res = fetch_account_info(Account=category, ticker=ticker)
        price_step = res['priceFilter']['tickSize']
        point = price_step.index('.')
        price = round(price, point)
        j = round(price % float(price_step), point)
        return price - j
def amount_to_precision(self,category, ticker, amount):
    if category == 'spot' or category == 'linear':
        ticker = ticker+'USDT'
    elif category == 'inverse':
        ticker = ticker+'USD'
    res = self.fetch_account_info(Account=category,ticker=ticker)
    qty_min = res['lotSizeFilter']['basePrecision'].index('1')-1
    qty = round(amount,qty_min)
    if qty < float(res['lotSizeFilter']['minOrderQty']):
        print(f"최소주문수량 미만 (최소주문수량: {res['lotSizeFilter']['minOrderQty']}, > 주문수량: {qty}")
        raise
    return qty

def order_open(ex_bybit, ticker, price, qty, side, type, leverage): #ccxt
    if side == 'buy':  # 지정가 open long
        params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
        res = ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty,price=price, params=params)
    elif side == 'sell':  # 지정가 open short
        params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
        res = ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty,
                                         price=price, params=params)
    else:
        print('에라 오픈')
        raise

    # print(f"{self.yellow(f'{type} open 주문')} [{res['id']}] [{side}] - 진입가:{price}, 수량:{qty}, 레버리지: {leverage}, 배팅금액: {round(price * qty, 4)}")
    return res['id']

import sqlite3, io

# nd.array to text  when Insert DB
def adapt_array(arr):
  """
  http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
  """
  out = io.BytesIO()
  np.save(out, arr)
  out.seek(0)
  return sqlite3.Binary(out.read())
# text to nd.array when Select DB
def convert_array( text):
  out = io.BytesIO(text)
  out.seek(0)
  return np.load(out)

import sqlite3
import json  # 리스트를 문자열로 변환하기 위해 필요

###
def distribute_by_ratio(number, ratios, decimal_places=0):
    # 비율 합계를 100으로 보정하여 계산할 비율을 구함
    total_ratio = sum(ratios)
    effective_number = number * (total_ratio / 100)

    # 각 비율에 따른 분배값 계산
    results = [(effective_number * (ratio / total_ratio)) for ratio in ratios]

    # 소숫점 자릿수에 맞게 반올림
    results = [round(result, decimal_places) for result in results]

    # 반올림 후 합이 달라졌을 수 있으므로 보정
    rounded_total = sum(results)
    difference = round(effective_number - rounded_total, decimal_places)

    # 보정이 필요한 경우 첫 번째 원소에 차이 추가
    if difference != 0:
        results[0] = round(results[0] + difference, decimal_places)

    return results

def bybit_set_tickers(fetch_tickers):
    for ticker in fetch_tickers.keys():
        fetch_tickers[ticker]['ask1Price'] = float(fetch_tickers[ticker]['info']['ask1Price'])
        # fetch_tickers[ticker]['ask1Size'] = int(fetch_tickers[ticker]['info']['ask1Size'])
        fetch_tickers[ticker]['bid1Price'] = float(fetch_tickers[ticker]['info']['bid1Price'])
        # fetch_tickers[ticker]['bid1Size'] = int(fetch_tickers[ticker]['info']['bid1Size'])
        fetch_tickers[ticker]['highPrice24h'] = float(fetch_tickers[ticker]['info']['highPrice24h'])
        fetch_tickers[ticker]['indexPrice'] = float(fetch_tickers[ticker]['info']['indexPrice'])
        fetch_tickers[ticker]['lastPrice'] = float(fetch_tickers[ticker]['info']['lastPrice'])
        fetch_tickers[ticker]['lowPrice24h'] = float(fetch_tickers[ticker]['info']['lowPrice24h'])
        fetch_tickers[ticker]['markPrice'] = float(fetch_tickers[ticker]['info']['markPrice'])
        # fetch_tickers[ticker]['openInterest'] = int(fetch_tickers[ticker]['info']['openInterest'])
        fetch_tickers[ticker]['openInterestValue'] = float(fetch_tickers[ticker]['info']['openInterestValue'])
        fetch_tickers[ticker]['prevPrice1h'] = float(fetch_tickers[ticker]['info']['prevPrice1h'])
        fetch_tickers[ticker]['prevPrice24h'] = float(fetch_tickers[ticker]['info']['prevPrice24h'])
        fetch_tickers[ticker]['price24hPcnt'] = float(fetch_tickers[ticker]['info']['price24hPcnt'])
        fetch_tickers[ticker]['turnover24h'] = float(fetch_tickers[ticker]['info']['turnover24h'])
        fetch_tickers[ticker]['volume24h'] = float(fetch_tickers[ticker]['info']['volume24h'])
        del fetch_tickers[ticker]['info']
    df = pd.DataFrame.from_dict(data=fetch_tickers, orient='index')  # 딕셔너리로 데이터프레임  만들기 키값으로 행이름을 사용
    return df

# Bybit API에 연결
bybit = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'position_mode': True
        # 'defaultType': 'inverse',  # spot 또는 future를 설정할 수 있음
    },
})
# tickers = bybit.fetch_tickers()
# df = bybit_set_tickers(tickers)
# print(df['quoteVolume'])
st = '1~2'
print(st[st.index('~')+1:])
print(st[:st.index('~')])
di = {'수급동향': False,'asdf': True}
if di:
    print('asdf')

print(type(datetime.datetime.now().date()))

conn = sqlite3.connect('DB/DB_futopt.db')
ticker_symbol = '콜옵션_355'
df_exist = pd.read_sql(f"SELECT * FROM '{ticker_symbol}'", conn).set_index('날짜')
print(df_exist.dtypes)
print(df_exist)
df_exist.index = pd.to_datetime(df_exist.index)
print(df_exist)
for i in range(10):
    if i ==5:
        continue
    print(i)
quit()
print('===================')
마디가 = [0.04,0.09,0.16,0.29,0.39,0.46,0.57,0.75,0.89,1.07,1.51,1.8,2.16,2.59,3.07,3.52,4.34,5.13]
# print(f"{마디가= }")
진입가 = 0.5
익절가 = [x for x in 마디가 if 진입가 < x ]
print(f"{익절가= }")
print(f"{익절가[2]= }")
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 현재 날짜 가져오기
today = datetime.today()

# 지난달의 첫째 날 계산
first_day_of_last_month = today.replace(day=1) - relativedelta(months=1)

# 지난달의 일수 구하기
days_in_last_month = (today.replace(day=1) - first_day_of_last_month).days

print(f"{first_day_of_last_month.year}년 {first_day_of_last_month.month}월의 일수: {days_in_last_month}일")
print()
# 손절가 = max([x for x in 마디가 if 진입가 * 0.9 > x ])
# print(f"{손절가= }")
# print(f"{익절가[1]= }")


my_list = [1, 2, 3, 4, 5]

for i,item in enumerate(reversed(my_list)):
    print(i,item)

quit()
values = [['2', 2, 3], ['4', 5, 6], ['1', 8, 9]]
index = ['one', 'two', 'three']
columns = ['시가_ETH_외인', '고가_ETH_기관', '저가_ETH_개인']
import json
df = pd.DataFrame(index=index,columns=columns,data=values)

li_col = df.columns.to_list()

if '외인' in df.columns.to_list():
    print(1)

values = [[1, 2, 3], [4, 5, 6], [1, 8, 9]]
index = ['1', '2', '3']
columns = ['시가_ETH_5분봉', '고가_ETH_5분봉', '저가_ETH_5분봉']
df1 = pd.DataFrame(index=index,columns=columns,data=values)
# print(df1)
# print(df1.iloc[1:2])
conn = sqlite3.connect('DB/stg_futopt.db')
df_closed = pd.read_sql(f"SELECT * FROM 'history'", conn).set_index('index')
df_stg = pd.read_sql(f"SELECT * FROM 'stg'", conn).set_index('index')
today = datetime.datetime(2025,1,7)
# print(datetime.datetime.now())
df_closed['청산시간'] = pd.to_datetime(df_closed['청산시간'], utc=True)
df_closed = df_closed[df_closed['청산시간'].dt.date == today.date()]
# print(df_closed)
# print(df_stg)
# df = pd.concat([df_closed,df_stg],axis=1,ignore_index=False)
# print(df)
# sum_closed = df_closed['매입금액'].sum()
win = len(df_closed.loc[df_closed['수익금'] > 0])


quit()
print(df['청산시간'])
df['청산시간'] = pd.to_datetime(df['청산시간'], utc=True)
# print(df)
# print(df['청산시간'])
print('=================')
today_rows = df[df['청산시간'].dt.date == today.date()]
print(today_rows)

quit()
# ex_bybit.fetch_closed_orders(symbol=ticker,since=)
# params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
# res = ex_bybit.create_order(symbol=ticker, type='limit', side='buy', amount=10,
#                                  price=0.5109, params=params)



stg_file = 'DB/stg_futopt.db'
conn_stg = sqlite3.connect(stg_file)
df_history = pd.read_sql(f"SELECT * FROM 'history'", conn_stg).set_index('index')
stg = '횡보풋'
df_stg = df_history.loc[df_history['전략명'] == stg]
list_col = df_stg.columns.tolist()
print(list_col)
dict_buy = {}
dict_sell = {}
for i, idx in enumerate(df_stg.index):
    buy_time = json.loads(df_stg.iloc[i, list_col.index('분할진입시간')])
    buy_price = json.loads(df_stg.iloc[i, list_col.index('분할진입가')])
    if buy_time: #분할일 경우
        for j,time in enumerate(buy_time):
            if time != '':
                time = time[:-2]+'00'
                time = common_def.str_to_datetime(time)
                dict_buy[time] = buy_price[j]
    else:
        buy_time = df_stg.iloc[i, list_col.index('진입시간')]
        buy_price = df_stg.iloc[i, list_col.index('진입가')]
        if buy_price != 0:
            buy_time = buy_time[:-2] + '00'
            buy_time = common_def.str_to_datetime(buy_time)
            dict_buy[buy_time] = buy_price
    sell_time = json.loads(df_stg.iloc[i, list_col.index('분할청산시간')])
    sell_price = json.loads(df_stg.iloc[i, list_col.index('분할청산가')])
    if sell_time:
        for j,time in enumerate(sell_time):
            if time != '':
                time = time[:-2]+'00'
                time = common_def.str_to_datetime(time)
                dict_sell[time] = sell_price[j]
    else:
        sell_time = df_stg.iloc[i, list_col.index('청산시간')]
        sell_price = df_stg.iloc[i, list_col.index('청산가')]
        if sell_price != 0:
            sell_time = sell_time[:-2] + '00'
            sell_time = common_def.str_to_datetime(sell_time)
            dict_sell[sell_time] = sell_price
print(dict_buy)
print(dict_sell)
import ccxt
# Bybit API 키와 비밀 키 설정
api_key = "ZFEksBSBjIHk7drUou"
api_secret = "MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI"



# print('==============================================')
# pprint(bybit.fetch_balance(params={'type':'linear'}))
# print('==============================================')
# # pprint(bybit.fetch_balance(params={'type':'spot'}))
# print('==============================================')
# pprint(fetch_balance(accountType='UNIFIED',ticker='USDT',balance='잔고'))
# print('==============================================')
# li = ['ticker', '주문시간', '체결시간', '주문수량',
#       'uuid', '수수료', '매수금액', '주문가', '상태', '구분', '펀딩비',
#       'spot비율', 'short비율']
# df = pd.DataFrame(columns=li)
# li = []
#
# df.loc['1','ticker'] = json.dumps(li)
# print(df)
# li = json.loads(df.loc['1', 'ticker'])
# print(f"{li= }    {type(li)= }")
# print('=====================================')
# li.append('123')
# print(f"{li= }    {type(li)= }")
# df.loc['1','ticker'] = json.dumps(li)
def decimal_places(number):
    # 정수인지 확인하여 0을 반환합니다.
    if isinstance(number, int) or number.is_integer():
        return 0

    # 소수점 이하 자리수를 계산합니다.
    decimal_str = str(number).split('.')[1]
    return len(decimal_str)
def distribute_by_ratio(number, ratios, decimal_places=0):  # distribute_by_ratio(10, [30,30,30], 0)  # [3,3,3]
    # 비율 합계를 100으로 보정하여 계산할 비율을 구함
    total_ratio = sum(ratios)
    effective_number = number * (total_ratio / 100)

    # 각 비율에 따른 분배값 계산
    results = [(effective_number * (ratio / total_ratio)) for ratio in ratios]

    # 소숫점 자릿수에 맞게 반올림
    results = [round(result, decimal_places) for result in results]

    # 반올림 후 합이 달라졌을 수 있으므로 보정
    rounded_total = sum(results)
    difference = round(effective_number - rounded_total, decimal_places)

    # 보정이 필요한 경우 첫 번째 원소에 차이 추가
    if difference != 0:
        results[0] = round(results[0] + difference, decimal_places)

    return results
print(distribute_by_ratio(2,[30,30,30],0))
print(decimal_places(2.5))

print(sys.maxsize)
if 9223372036854775807 < 9223372036854775806:
    print('asdf')

import pandas as pd

# 예제 데이터프레임
data = {
    'col1': [1, 1, 1, 1],
    'col2': [2, 3, 2, 2],
    'col3': [5, 5, 5, 5]
}
df = pd.DataFrame(data)

# 특정 열이 모두 특정 숫자로 되어 있는지 확인
column_name = 'col1'  # 확인할 열 이름
specific_number = 1   # 특정 숫자

is_all_specific = (df['col1'] == specific_number).all()
if (df['col1'] == df.loc[df.index[0],'col1']).all():
    print(f"{column_name} 열이 모두 {specific_number}인가요? {is_all_specific}")

from dateutil.relativedelta import relativedelta
def nth_weekday(the_date, nth_week, week_day):
    temp = the_date.replace(day=1)
    adj = (week_day - temp.weekday()) % 7
    temp += datetime.timedelta(days=adj)
    temp += datetime.timedelta(weeks=nth_week-1)
    return temp
def get_recent_due(mydate:datetime)->datetime:
    # get 2nd thursday of the same month
    thismonth_duedate = nth_weekday(mydate, 2, 3)
    # in case today already passed the duedate (10/15) -> get nextmonth_duedate
    if mydate <= thismonth_duedate:
        return thismonth_duedate
    elif mydate > thismonth_duedate :
        nextmonth_duedate = nth_weekday(mydate+relativedelta(months=1),2, 3)
        return nextmonth_duedate


# x = [x for x in 마디값 if 중심가 * 1.1 > x ]
콜옵션_월간 = '콜옵션_월간'

today = datetime.datetime(2024,11,14)
today = datetime.datetime.today()
# from datetime import datetime, timedelta

# from datetime import datetime
# from dateutil.relativedelta import relativedelta

# datetime.datetime(2021,12,1).isocalendar()
# datetime.datetime(2021,12,1).isocalendar()[1]
# print(datetime.datetime(2022,3,1).isocalendar()[1])

# n = datetime.datetime.now()
# n.isocalendar()
# print(n.isocalendar()[1])


# from datetime import datetime.date

def get_week_of_month(input_date):
    # 이번 달 1일의 요일 계산
    first_day_of_month = input_date.replace(day=1)
    first_day_weekday = first_day_of_month.isoweekday()  # 0 = 월요일, 6 = 일요일, 월요일 기준으로 하고싶으면 isoweekday() 대신에 weekday()로 변경

    # 이번 달 시작 주를 보정하여 몇 주차인지 계산
    adjusted_day = input_date.day + first_day_weekday
    return (adjusted_day - 1) // 7

# 오늘 날짜 가져오기
# today = datetime.today()
today = datetime.datetime(2024,12,21)
week_of_month = get_week_of_month(today)
dt=datetime.datetime.now().replace(second=0, microsecond=0)
print(dt)
print(type(dt))