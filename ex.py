import KIS
import sys
import time
import talib
from PyQt5.QtWidgets import QWidget,QPushButton,QApplication,QListWidget,QGridLayout,QLabel
from PyQt5.QtCore import QTimer,QDateTime
from PyQt5.QtWidgets import *
import pandas as pd
from pandas import to_numeric
from PyQt5.QtCore import *
from collections import deque
import numpy as np
import datetime
import sqlite3
from pprint import pprint
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
# from ccxt.base.decimal_to_precision import TICK_SIZE
# from collections import deque
# # 5초에 한번씩 함수 실행
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
def stamp_to_int(stamp_time):
    dt = datetime.datetime.fromtimestamp(stamp_time)
    dt = dt.strftime('%Y%m%d%H%M')
    return int(dt)
def stamp_to_datetime(stamp_time):
    if len(str(int(stamp_time))) == 13:
        stamp_time = stamp_time / 1000 #밀리초단위일 경우
    int_time = stamp_to_int(stamp_time)
    return datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
def stamp_to_str(t):
    date_time = stamp_to_datetime(t)
    return datetime.datetime.strftime(date_time, "%Y-%m-%d %H:%M")
def fetch_open_orders(exchange, market,ticker,category,id):  # 미체결주문 조회
    if market == 'bybit':
        if category == 'spot':
            symbol = ticker+'/USDT'
        elif category == 'inverse':
            symbol = ticker+'USD'
        elif category == 'future':
            symbol = ticker+'USDT'
        params = {}
        res = exchange.fetch_open_orders(symbol=symbol, params=params)
    elif market == 'binance':
        if category == 'spot':
            symbol = ticker+'/USDT'
        elif category == 'inverse':
            symbol = ticker+'/USD'
        elif category == 'future':
            symbol = ticker
        params = {}
        res = exchange.fetch_open_orders(symbol=symbol, params=params)
    for order in res:
        if order['id'] == id:
            return order
def fetch_closed_orders(exchange,market, id, ticker, category):  # 체결주문 조회
    params = {}
    if market == 'bybit':
        if category == 'spot':
            symbol = ticker+'/USDT'
        elif category == 'inverse':
            symbol = ticker+'USD'
        elif category == 'future':
            symbol = ticker+'USDT'
        # order = self.ex_bybit.fetch_closed_orders(self.ticker, params=params)
        res = exchange.fetch_closed_orders(symbol=symbol, params=params)
    if market == 'binance':
        if category == 'spot':
            symbol = ticker+'/USDT'
        elif category == 'inverse':
            symbol = ticker+'/USD'
        elif category == 'future':
            symbol = ticker
        res = exchange.fetch_closed_orders(symbol=ticker, params=params)
    for order in res:
        if order['id'] == id:
            return order
def fetch_order(exchange,market, ticker, id, category, qty):
    주문수량 = qty
    ord_open = fetch_open_orders(exchange,market, ticker, category, id)
    if ord_open == None:  # 체결일 경우
        ord_closed = fetch_closed_orders(exchange,market, id, ticker, category)  # open 주문과 close 주문 2중으로 확인
        pprint(ord_closed)
        print('==================')
        if ord_closed == None:
            return {'체결': '주문취소'}
        else:
            진입가 = float(ord_closed['average'])
            체결수량 = float(ord_closed['filled'])
            if not ord_closed['fee'] == None:
                진입수수료 = float(ord_closed['fee']['cost'])
            else:
                진입수수료 = ord_closed['fee']
            총체결금액 = float(ord_closed['cost'])
            체결시간 = stamp_to_str(ord_closed['timestamp'])
            if 주문수량 >= 체결수량:
                print(f"체결완료 - {ticker= }  {category= }  {체결수량=} ")
            return {'체결': True, '체결가': 진입가, '체결수량': 체결수량, '수수료': 진입수수료, '체결시간': 체결시간}

    else:
        return {'체결': False}

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


def amount_to_precision(exchange, market, category, ticker, amount):
    if market == 'bybit':
        if category == 'spot':
            symbol = ticker + '/USDT'
        elif category == 'inverse':
            symbol = ticker + 'USD'
        return float(exchange.amount_to_precision(symbol=symbol, amount=amount))
    elif market == 'binance':
        if category == 'spot':
            symbol = ticker + '/USDT'
        elif category == 'inverse':
            symbol = ticker + 'USD'
        return float(exchange.amount_to_precision(symbol=symbol, amount=amount))

def order_open(exchange,market, category, ticker, side, orderType, price, qty,leverage=1): #ccxt
    if market == 'bybit':
        if category == 'spot':
            params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + '/USDT'
            # leverage = 1
        elif category == 'inverse':
            params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + 'USD'
#             leverage = 1
        elif category == 'future':
            symbol = ticker + 'USDT'
            if side == 'buy':
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            elif side == 'sell':  # 지정가 open short
                params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            # leverage = 3
        try:
            exchange.set_leverage(leverage=leverage, symbol=symbol)
        except:
            pass
        res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                         price=price, params=params)
    elif market == 'binance':
        if category == 'spot':
            params = {}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + '/USDT'
            leverage = 1
        elif category == 'inverse':
            # params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            params = {}
            symbol = ticker + 'USD_PERP'
            leverage = 1
        elif category == 'future':
            symbol = ticker + 'USDT'
            if side == 'buy':
                pass
                # params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            elif side == 'sell':  # 지정가 open short
                pass
                # params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            # leverage = 3
        # print(f"{market= }   {symbol= }   {orderType= }   {side= }    {qty= }   {price= }")
        try:
            exchange.set_leverage(leverage=leverage, symbol=symbol)
        except:
            pass
        res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                           price=price, params=params)
    # print(f"{self.yellow(f'{type} open 주문')} [{res['id']}] [{side}] - 진입가:{price}, 수량:{qty}, 레버리지: {leverage}, 배팅금액: {round(price * qty, 4)}")
    return res

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



################################################################
import time
import asyncio
sample_array = np.arange(1,6)
sample_array
df = pd.DataFrame({
    'col1' : sample_array,
    'col2' : sample_array*2,
    'col3' : ["A","B","C","D","E"]
})
df1 = pd.DataFrame(index=[2,3,4,5,6],data={
    'col1' : sample_array,
    'col2' : sample_array*2,
    'col3' : ["A","B","C","D","E"]
})

api = 'PSCLO2WTCrnbFTVJLqZcRGZwYVAll8BHU34I'
secret = 'l/12Smyub2n5MSDGwxiLde3vK6FWsRWq6HcU8RPfKYgw31qnDiQLhyaj1y2cpyOromd9nZOkeIBIug7PWu+RQShovpzMGB5uf59xKFnOAIbkmTGFGdNhr9ULEWR4OiK2SDdUuZ9PST94RZfy5IDpewS2vUi0q6wcO2t1C/pJ1QZFxsPNvvk='
acc_no = '64422606-03'
market = '선옵'
mock = False
현재시간 = datetime.datetime.now().replace(second=0, microsecond=0)
now_day = 현재시간.date().strftime("%Y%m%d")
now_time = 현재시간.strftime("%H%M") + "00"  # 마지막에 초는 00으로
exchange = KIS.KoreaInvestment(api_key=api, api_secret=secret, acc_no=acc_no, market=market, mock=mock)
ohlcv = exchange.fetch_1m_ohlcv(symbol='101W09', limit=2, ohlcv=[], now_day=now_day, now_time=now_time)
df = common_def.get_kis_ohlcv('국내선옵',ohlcv)
df.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
df = common_def.resample_df(df, '일봉', 'D', '일봉',False)
print(df)
quit()
if sub:
    print('y')
    for idx in sub:
        new = df1.loc[[idx]]
        df = pd.concat([df,new])
if cha:
    print('y')
    for idx in cha:
        df.drop(index=idx,inplace=True)
print(df)
quit()

conn_holiday = sqlite3.connect('DB/DB_futopt.db')
df_holiday = pd.read_sql(f"SELECT * FROM 'holiday'", conn_holiday).set_index('날짜')
conn_holiday.close()
now_day = datetime.datetime.now().date().strftime("%Y%m%d")
print(df_holiday.loc[now_day,'개장일'])
quit()

async def delivery(name, mealtime):
    print(f"{name}에게 배달 완료")
    await asyncio.sleep(mealtime)
    print(f"{name} 식사 완료, {mealtime}초 소요...")
    print(f"{name} 그릇 수거 완료")


async def main():
    await asyncio.gather(   # 비동기함수 동시 실행
        delivery("A", 5),
        delivery("B", 3),
        delivery("C", 4)
    )


if __name__=="__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print("총 소요시간: {:.3f}초".format(end-start))
quit()

# 바이낸스 API 설정
# dt = datetime.datetime.strptime('2015-07-15','%Y-%m-%d')
# print(dt)
# print(type(dt))
#
# quit()
api_key = 'fYs2tykmSutKiF3ZQySbDz387rqzIDJa88VszteWjqpgDlMtbejg2REN0wdgLc9e'
api_secret = 'ddsuJMwqbMd5SQSnOkCzYF6BU5pWytmufN8p0tUM3qzlnS4HYZ1w5ZhlnFCuQos6'
binance_futures = ccxt.binance(config={
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
                # 'position_mode': True,  #롱 & 숏을 동시에 유지하면서 리스크 관리(헷징)할 때
                'defaultType': 'future'
                },
})

res_spot = binance_futures.fetch_balance()
# pprint(res_spot)
print('=====================')
res = binance_futures.fetch_balance(params={"type": 'delivery'})
pprint(res)



# # 시장 데이터 로드
# markets = binance_futures.load_markets()
#
# # 선물 BTCUSDT 심볼 정보 가져오기
# symbol = 'BTC/USDT'  # 바이낸스 선물에서는 이런 형식 사용
# market_info = markets[symbol]
#
# pprint(market_info)
# # 최소 주문 수량 확인
# min_amount = market_info['limits']['amount']['min']
# print(f"BTCUSDT 선물 최소 주문 수량: {min_amount}{type(min_amount)}")

# binance = ccxt.binance(config={
#     'apiKey': api_key,
#     'secret': api_secret,
#     'enableRateLimit': True,
#     'options': {'position_mode': True, },
#     })
# ticker = 'BTC'
# symbol = ticker +'/USDT'
# markets = binance.load_markets()
# market_info = markets[symbol]
#
# # 최소 주문 수량 확인
# min_amount = market_info['limits']['amount']['min']
# print(f"BTCUSDT 선물 최소 주문 수량: {min_amount}")




# # 시장 데이터 로드
# markets = binance_futures.load_markets()
# symbol = 'BTC/USDT'
# market_info = markets[symbol]
#
# # 최소 주문 수량 확인
# min_amount = market_info['limits']['amount']['min']
# print(f"BTCUSDT 선물 최소 주문 수량: {min_amount}")
# id = order_open(exchange=binance ,market='bybit' , category='inverse' , ticker= ticker, side='buy' ,
#                 orderType= 'market', price= 88000, qty=10 )
# pprint(id)

quit()
print('==============================================')
api_key = "k3l5BpTorsRTHvPmAj"
api_secret = "bdajEM0VJJLXCbKw0i9VfGemAlfRGga4C5jc"
bybit = ccxt.bybit(config={
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {'position_mode': True, },
})


ticker = 'SOL'
0.0419282
94436
leverage = 2
used = 8.67714
현재가 = 145.73
주문최소금액 = 1
# min_qty = 0.001
bet = used/20
market_info = bybit.load_markets()[f'{ticker}/USDT:USDT']
min_qty = market_info['limits']['amount']['min']
print(f"1- 보유금액: {used*현재가}   {min_qty= }")
if min_qty > bet*leverage:
    bet = min_qty/leverage
    print(f"{min_qty=} {bet= }")
print(f"{bet =}")
bet = bet * 현재가
print(f"{bet =}")
min_cont = 100
if min_cont > bet:
    print("min_cont > bet")
    bet = min_cont
print(f"{bet/min_cont= }")
# id = order_open(exchange=bybit ,market='bybit' , category='inverse' , ticker= 'BTC', side='buy' ,
#                 orderType= 'market', price= 88000, qty=10 )
# pprint(id)

# id = 'b64e1da7-220a-4a38-aa70-27242a496b1b'
ticker = 'BTC'
bet = 10
quit()
# while True:
#     time.sleep(1)
#     res = fetch_order(bybit,'bybit',ticker,id,'inverse',10)
#     if res['체결'] == True:
#         print(f"{ticker}  {res['체결수량']} 개  체결 완료 - 체결시간{res['체결시간']}")
#         break
# pprint(res)
# res = bybit.fetch_ticker(symbol=ticker+'/USDT',params={})
# price = res['close']#현물가격조회
# qty = amount_to_precision(bybit,'bybit','spot',ticker,10 / price)
# # res = order_open(exchange=bybit ,market='bybit' , category='spot' , ticker= 'BTC', side='sell' ,
# #                 orderType= 'market', price= price, qty=qty)
#
# id = '1934383654126317056'
# while True:
#     time.sleep(1)
#     dict_chegyeol = fetch_order(bybit,'bybit',ticker,id,'spot',10)
#     if dict_chegyeol['체결'] == True:
#         print(f"{ticker}  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간{dict_chegyeol['체결시간']}")
#         break
category = 'future'
res = bybit.fetch_ticker(symbol=ticker+'USDT',params={})
# 마켓 정보 로드
markets = bybit.load_markets()

# BTC/USDT 마켓 정보
symbol = 'BTC/USDT'
# Bybit USDT 선물 객체

# 마켓 정보 불러오기

# 선물 심볼은 'BTC/USDT' (spot처럼 보이지만 bybitusdm 객체에서는 선물)
market_info = bybit.load_markets()[f'{ticker}/USDT:USDT']

# 선물 BTCUSDT 심볼 정보 가져오기
# symbol = 'BTC/USDT:USDT'  # 선물 계약 심볼 형식
# market_info = markets[symbol]

# 최소 주문 수량 확인
pprint(market_info)
min_amount = market_info['limits']['amount']['min']
print(f"BTCUSDT 선물 최소 주문 수량: {min_amount}")
price = res['close']#선물가격조회
print(price)
qty = amount_to_precision(bybit,'bybit','spot',ticker,bet / price)
leverage = 3
print(qty)
if min_amount > qty:
    print(f'min: {min_amount}')
res = order_open(exchange=bybit ,market='bybit' , category=category , ticker= 'BTC', side='buy' ,
                orderType= 'market', price= price, qty=qty, leverage=leverage)
pprint(res)
id = res['id']
print(f"{id= }")
while True:
    time.sleep(1)
    dict_chegyeol = fetch_order(bybit,'bybit',ticker,id,category,10)
    if dict_chegyeol['체결'] == True:
        print(f"{ticker}  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간{dict_chegyeol['체결시간']}")
        break
print('===========')
quit()


dict_bong_stamp = {'1분봉': 1 * 60, '3분봉': 3 * 60, '5분봉': 5 * 60, '15분봉': 15 * 60, '30분봉': 30 * 60,
                   '60분봉': 60 * 60, '4시간봉': 240 * 60, '일봉': 1440 * 60,
                   '주봉': 10080 * 60}
dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉': '4h',
             '일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
ohlcv = []
i=0
ticker = 'BTC'
bong = '4시간봉'

bong_since = 10 #10일 전 데이터부터 추출
present = datetime.datetime.now()
date_old = present.date() - datetime.timedelta(days=int(bong_since))
stamp_date_old = common_def.datetime_to_stamp(date_old)

list_ohlcv = binance.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong],
                                          limit=10000, since=int(stamp_date_old * 1000))  # 밀리초로 전달
while True:
    try:
        list_ohlcv = binance.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong],
                                          limit=10000, since=int(stamp_date_old * 1000))  # 밀리초로 전달
        # pprint(list_ohlcv)
        ohlcv = ohlcv + list_ohlcv
        stamp_date_old = list_ohlcv[-1][0] / 1000 + dict_bong_stamp[bong]  # 다음봉 시간 계산

        if stamp_date_old > time.time():
            print('asdf')
            break
    except:
        time.sleep(1)
        i += 1
        if i > 9:
            print(f' {ticker=}, {bong=}, {i}회 이상 fetch_ohlcv 조회 에러')
            break
df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
df['날짜'] = df['날짜'].dt.tz_localize(None)
df.set_index('날짜', inplace=True)
df = common_def.convert_df(df)
# df.index = df.index - pd.Timedelta(hours=9)
print(df)
print(df.loc[df.index[-1],'RSI14'])
print(df.loc[df.index[-2],'RSI14'])
quit()

print('============================')
res = bybit.fetch_positions()
pprint(res)

for data in res:
    del data['info']

quit()
df.index = df['symbol'].copy()
df.rename(columns={'unrealizedPnl': '손익','leverage':'레버리지','contracts':'보유수량','liquidationPrice':'청산가',
                   'collateral':'매수금액','side':'방향','markPrice':'현재가','entryPrice':'진입가'}, inplace=True)
df['수익률'] = df['손익']/df['매수금액']*100
df = df[['symbol','현재가','레버리지','방향','수익률','손익','보유수량','매수금액','진입가','청산가','marginMode']]
print(df)
# df = pd.DataFrame(position)
# print(df)

quit()
# res = bybit.fetch_closed_orders(symbol='BTCUSD',params={})

ticker = "XRP/USDT"
# print("============================")
res = bybit.fetch_balance()
pprint(res)
print('asdf')
df_set = pd.DataFrame(index=['auto_start', 'rate_short', 'rate_spot', 'funding_time', 'api_bybit', 'secret_bybit',
                                  'api_binance', 'secret_binance'],
                           columns=['check', 'val', 'key'])
df_set.loc['auto_start', 'check'] = False
a = df_set.loc['api_bybit','key']
if a== None:
    print(1)
quit()
# print('=======')
# res = binance.fapiprivate_post_leverage({"symbol":ticker,"leverage":3})
# pprint(res)
# print('=======')
# try:
#     res = binance.fapiprivate_post_margintype({"symbol":ticker,"marginType":"ISOLATED"})
# except:
#     pass
# pprint(res)
# print('=======')
# res = binance.create_order(symbol=ticker,amount=5,side="buy",type="limit",price=2.22,params={})

# res = binance.create_order(symbol='XRP/USDT',type='limit',side='buy',amount=5,price=2.22,params={})
# pprint(res)
quit()



# spot
balanceSpot = binance.fetch_balance()['total']
spot = pd.DataFrame(list(balanceSpot.items()), columns=['name', 'balance'])
spot = spot[spot['balance'] > 0]
print(spot)
print('============')

# coin-m
balanceCoinm = binance.fetch_balance(params={"type": 'delivery'})['total']
Coinm = pd.DataFrame(list(balanceCoinm.items()), columns=['name', 'balance'])
Coinm = Coinm[Coinm['balance'] > 0]
print(Coinm)
print('============')



# spot and coin-m
total = pd.concat([spot, Coinm])
total = total[total['balance'] > 0]
pprint(total)
print('============')
quit()
############################################################
# 중복데이터 정리
dfBn = total.drop_duplicates("name", keep=False)

df1 = total[total.duplicated('name', keep = 'first')]
df2 = total[total.duplicated('name', keep = 'last')]


# 분리된 데이터 더하기
nameBn = []
amountBn = []
for coin in df1['name']:
    nameBn.append(coin)
    am = df1[df1['name'] == coin]['balance'].values[0] + df2[df2['name'] == coin]['balance'].values[0]
    amountBn.append(am)

dfz = []
dfz.append(nameBn)
dfz.append(amountBn)
dfz = pd.DataFrame(dfz)
dfz =dfz.transpose()
dfz.columns = ['name', 'balance']
# dfBn: 중복 제거, dfz: 중복된 것들
dfBn = pd.concat([dfz, dfBn])
pprint(dfBn)
print('============')

############################################################
# 비상장/소액 제거하기
nameBn = []
usdBn = []
amountBn = []
priceBn = []

# 페어 및 가격 가져오기
markets = binance.fetch_tickers()
keys = markets.keys()

for coin in dfBn['name']:
    amount = dfBn[dfBn['name'] == coin]['balance'].values[0]
    coin2 = coin + "/USDT"
    for pair in keys:
        if pair == coin2: # usdt 페어 있는 경우만
            price = markets[pair]['last']
            usd = price * amount
            if usd > 10: # 10$ 이상만
                nameBn.append(coin)
                usdBn.append(usd)
                amountBn.append(amount)
                priceBn.append(price)

dfBn = [nameBn, usdBn, amountBn, priceBn]
dfBn = pd.DataFrame(dfBn)
dfBn = dfBn.transpose()
dfBn.columns = ['Name', 'Amount', 'Price', 'USD']
pprint(dfBn)
print('============')
############################################################
# spot usdt + futures usds
spot_usdt = balanceSpot['USDT']

balanceUsds = binance.fetch_balance(params={"type": "future"})
future_usd = balanceUsds['total']['USDT'] + balanceUsds['total']['BUSD']

total_usd = spot_usdt + future_usd
dfBn.loc[len(dfBn)+1] = ['USD', total_usd, 1, total_usd]

binance_usd = dfBn.sum(axis=0)['USD']

print(dfBn)
print("Total USD: {0:,.2f} USD".format(binance_usd))
quit()


# res = ex_binance.fetch_ticker('BTC/USDT')['close']
# balance = binance.fetch_balance()
# balance_binance = {}
# for currency, data in balance['total'].items():
#     if data > 0 and currency in balance:
#         balance_binance[currency] = balance[currency]
# pprint(binance)
# pprint(balance_binance)
# res = binance.fetch_ticker('BTC/USDT')
# pprint(res)
# res = binance.create_order(symbol='BTC/USD', type='limit', side='sell', amount=1,
#                                              price=85000, params={})
# response = exchange.sapi_post_futures_transfer({
#             "asset": 'XRP',
#             "amount": 100,
#             "type": 3  # 3: Spot -> COIN-M Futures
# 1	Spot → USDT-M Futures
# 2	USDT-M Futures → Spot
# 3	Spot → COIN-M Futures
# 4	COIN-M Futures → Spot
#         })
# print(response)



# 예제 데이터프레임 생성
li_col = ['날짜', '요일', '금융기관업무일', '입출금가능일', '개장일', '지불일']
df = pd.DataFrame(columns=li_col)
df.index = df['날짜']

# 데이터프레임 합치기
df1 = pd.DataFrame({'A': [1, 2, 3]}, index=[0, 1, 2])
df2 = pd.DataFrame({'A': [4, 5, 6]}, index=[1, 2, 3])
df = pd.concat([df1, df2])

# 인덱스 중복 제거 (위쪽 행 삭제, 마지막 행 유지)
df = df[~df.index.duplicated(keep='last')]
d = datetime.datetime.now().date()
i = 1
i -= 1
def pad_list(lst):
    """길이가 10보다 작으면 앞쪽을 0으로 채워 10으로 맞춤"""
    return [0] * (10 - len(lst)) + lst if len(lst) < 10 else lst

# 테스트 예제
data1 = [1, 2, 3, 4]  # 길이 4 → 앞쪽에 6개 0 추가
data2 = [5, 6, 7, 8, 9, 10, 11]  # 길이 7 → 앞쪽에 3개 0 추가
data3 = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]  # 길이 10 → 그대로 유지

# 적용
print(pad_list(data1))  # [0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
print(pad_list(data2))  # [0, 0, 0, 5, 6, 7, 8, 9, 10, 11]
print(pad_list(data3))  # [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
quit()
test_dates = [
    "2025-01-01",  # 3월 만기일이 가장 가까움
    "2025-03-15",  # 3월 만기일 이후, 6월 만기일이 가장 가까움
    "2025-06-15",  # 6월 만기일 이후, 9월 만기일이 가장 가까움
    "2025-09-15",  # 9월 만기일 이후, 12월 만기일이 가장 가까움
    "2025-12-15",  # 12월 만기일 이후, 다음 해 3월 만기일이 가장 가까움
]

for date in test_dates:
    nearest, date_str, days = get_nearest_futures_expiry(date)
    print(f"입력 날짜: {date}")
    print(f"다음 선물 만기일: {nearest.strftime('%Y-%m-%d')} ({date_str})")
    print(f"만기일까지 남은 일수: {days}일")
    print("-" * 30)


def get_nearest_options_expiry(input_date):
    """
    주어진 날짜로부터 가장 가까운 미래의 옵션 만기일(매월 두 번째 목요일)을 찾습니다.

    Args:
        input_date: datetime 객체 또는 'YYYY-MM-DD' 형식의 문자열

    Returns:
        tuple: (만기일 datetime 객체, 만기일 문자열 'YY-MM-DD', 경과일 수)
    """
    # 문자열 형식의 날짜를 datetime 객체로 변환
    if isinstance(input_date, str):
        try:
            input_date = datetime.datetime.strptime(input_date, '%Y-%m-%d').date()
        except ValueError:
            try:
                input_date = datetime.datetime.strptime(input_date, '%Y%m%d').date()
            except ValueError:
                raise ValueError("날짜 형식은 'YYYY-MM-DD' 또는 'YYYYMMDD'이어야 합니다.")
    elif isinstance(input_date, datetime.datetime):
        input_date = input_date.date()

    # 현재 연도와 월
    current_year = input_date.year
    current_month = input_date.month

    # 현재 월의 옵션 만기일 계산
    current_month_expiry = get_options_expiry_date(current_year, current_month)

    # 현재 날짜가 현재 월의 옵션 만기일 이후라면 다음 달 만기일 찾기
    if input_date > current_month_expiry:
        # 다음 달 계산
        if current_month == 12:
            next_month_year = current_year + 1
            next_month = 1
        else:
            next_month_year = current_year
            next_month = current_month + 1

        next_expiry = get_options_expiry_date(next_month_year, next_month)
    else:
        # 현재 월의 만기일이 아직 지나지 않았으면 해당 월의 만기일 사용
        next_expiry = current_month_expiry

    # 만기일까지 남은 일수 계산
    days_until_expiry = (next_expiry - input_date).days

    return next_expiry, next_expiry.strftime('%y-%m-%d'), days_until_expiry


def get_options_expiry_date(year, month):
    """
    특정 연도와 월의 옵션 만기일(두 번째 목요일)을 계산합니다.

    Args:
        year: 연도 (정수)
        month: 월 (정수, 1-12)

    Returns:
        datetime.date: 해당 월의 옵션 만기일
    """
    # 해당 월의 첫 번째 날짜
    first_day = datetime.date(year, month, 1)

    # 첫 번째 날짜의 요일 (0: 월요일, 1: 화요일, ..., 6: 일요일)
    first_weekday = first_day.weekday()

    # 첫 번째 목요일까지의 일수 계산 (목요일은 weekday가 3)
    days_to_first_thursday = (3 - first_weekday) % 7
    first_thursday = first_day + datetime.timedelta(days=days_to_first_thursday)

    # 두 번째 목요일은 첫 번째 목요일로부터 7일 후
    second_thursday = first_thursday + datetime.timedelta(days=7)

    return second_thursday
today = datetime.date.today()
nearest_expiry, expiry_str, days_left = get_nearest_options_expiry(today)
print(f"오늘 날짜: {today.strftime('%Y-%m-%d')}")
print(f"다음 옵션 만기일: {nearest_expiry.strftime('%Y-%m-%d')} ({expiry_str})")
print(f"만기일까지 남은 일수: {days_left}일")
print("-" * 30)

# 테스트 날짜로 확인
test_dates = [
    "2025-01-01",  # 1월 만기일 전
    "2025-01-10",  # 1월 만기일 후, 2월 만기일 전
    "2025-02-20",  # 2월 만기일 후, 3월 만기일 전
]

for date in test_dates:
    nearest, date_str, days = get_nearest_options_expiry(date)
    print(f"입력 날짜: {date}")
    print(f"다음 옵션 만기일: {nearest.strftime('%Y-%m-%d')} ({date_str})")
    print(f"만기일까지 남은 일수: {days}일")
    print("-" * 30)


quit()
# globals()[f"{stg}"] =
# today = "20250301"
# expiry_day = "20250304"
# df_holiday = df_holiday[today:expiry_day]
# print((df_holiday['개장일']=="N").all())
수익률 = 11
최고수익률 = 17.78
print((최고수익률-(최고수익률-수익률))/최고수익률*100)
quit()
conn = sqlite3.connect('DB/DB_futopt.db')
ticker_symbol = '콜옵션_355'
df_exist = pd.read_sql(f"SELECT * FROM '{ticker_symbol}'", conn).set_index('날짜')
print(df_exist.dtypes)
print(df_exist)
df_exist.index = pd.to_datetime(df_exist.index)
quit()
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