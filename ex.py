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
import uuid
import sqlite3
from pprint import pprint
from PyQt5.QtTest import QTest
import asyncio
import KIS
from common_def import make_exchange_upbit, make_exchange_upbit_pro

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
import math
import ast
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
def fetch_inverse_detail(ex,market):
    if market == 'bybit':
        res = ex.fetch_balance()
        usdt_free = res['USDT']['free']
        usdt_total = res['USDT']['total']
        pprint(usdt_free)
        pprint(usdt_total)
        quit()
    elif market == 'binance':
        res_spot = ex.fetch_balance()
        res = ex.fetch_balance(params={"type": 'delivery'})
        markets_binance = ex.load_markets()
        usdt_free = res_spot['USDT']['free']
        usdt_total = res_spot['USDT']['total']
    # held_coins = {}
    balance = {}
    for ticker, data in res['total'].items():
        # if data > 0 and ticker in res and ticker != 'USDT':
        if data > 0 and ticker in res:
            if market == 'bybit':
                if ticker in list_bybit_inverse:  # 바이비트의 경우 인버스 종목이 한정적
                    balance[ticker] = res[ticker]
                    balance_bybit = common_define.fetch_account_info_bybit(Account='inverse',
                                                                                symbol=ticker + 'USD')
                    balance[ticker]['주문최소금액'] = float(
                        balance_bybit['lotSizeFilter']['minOrderQty'])  # inverse 최소주문USDT구하기

                    balance[ticker]['현재가'] = common_define.fetch_ticker(market, ticker + 'USD')['close']
                    # balance[ticker]['현재가(linear)']= self.common_define.fetch_ticker(market,ticker + 'USDT')['close']
                    # balance[ticker]['category'] = 'inverse/spot'
                elif ticker == 'USDT':
                    usdt_free = res[ticker]['free']
                    usdt_total = res[ticker]['total']
            if market == 'binance':
                balance[ticker] = res[ticker]
                balance[ticker]['주문최소금액'] = markets_binance[f"{ticker}/USD:{ticker}"]['contractSize']
                # ticker_info = markets_binance[f'{ticker}/USD:{ticker}']
                # if ticker == 'BTC':
                #     balance[ticker]['주문최소금액'] = 100
                # else:
                #     balance[ticker]['주문최소금액'] = 10

                balance[ticker]['현재가'] = self.common_define.fetch_ticker(market, ticker + 'USD_PERP')['close']
    #                     balance[currency]['category'] = 'inverse/spot'
    # balance[currency]['현재가(linear)'] = self.common_define.fetch_ticker(market, currency + '/USDT')['close']
    return balance, usdt_free, usdt_total

def fetch_balance(exchange, market,ticker):
    if market == 'bybit':
        pass
    elif market == 'binance':
        res = exchange.fetch_balance(params={"type": 'delivery'})

    return res[ticker]
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
        elif category == 'linear':
            symbol = ticker+'USDT'
        params = {}
        res = exchange.fetch_open_orders(symbol=symbol, params=params)
    elif market == 'binance':
        if category == 'spot':
            symbol = ticker+'/USDT'
        elif category == 'inverse':
            symbol = ticker+'/USD'
        elif category == 'linear':
            symbol = ticker+'/USDT:USDT'
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
        elif category == 'linear':
            symbol = ticker+'USDT'
        # order = self.ex_bybit.fetch_closed_orders(self.ticker, params=params)
        res = exchange.fetch_closed_orders(symbol=symbol, params=params)
    if market == 'binance':
        if category == 'spot':
            symbol = ticker+'/USDT'
        elif category == 'inverse':
            symbol = ticker+'/USD'
        elif category == 'linear':
            symbol = ticker+'/USDT:USDT'
        res = exchange.fetch_closed_orders(symbol=symbol, params=params)
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
            if ord_closed['info'].get('status')=='FILLED' or ord_closed['info'].get('orderStatus')=='Filled':
                진입가 = float(ord_closed['average'])
                체결수량 = float(ord_closed['filled'])
                수수료 = ord_closed.get('fee', 0)
                if 수수료 == None: 수수료 = 0
                수수료 = float(수수료)
                체결금액 = float(ord_closed['cost'])
                체결시간 = stamp_to_str(ord_closed['timestamp'])
                time.sleep(1)

                if category == 'spot':
                    if market == 'binance':  # 바이낸스의 경우 현물 구매 시 구매 수량에서 수수료만큼 수량이 빠지는듯
                        res = exchange.fetch_balance(params={'type': 'spot'})
                        체결수량 = res[ticker]['free']

                dict_info = {'체결': True, '체결가': 진입가, '체결수량': 체결수량, '체결금액': 체결금액, '수수료': 수수료,
                             '체결시간': 체결시간, 'id': id, 'side': ord_closed.get('side', None)}
                return dict_info

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
def transfer_to(exchange, market, ticker, amount,departure, destination):
    if market == 'bybit':
        session = exchange
        while True:
            id = str(uuid.uuid1())
            print(id)
            res = session.create_internal_transfer(
                transferId=id,
                coin=ticker,  # BTC
                amount=amount,
                fromAccountType="UNIFIED",  # UNIFIED (spot 계좌)
                toAccountType="CONTRACT",  # CONTRACT (inverse 계좌)
            )

            if res['retMsg'] == 'success':
                print(f'{ticker}  {amount} 개  inverse로 계좌이동 완료')
                break
            print(f'{ticker} 계좌 이동중...')
            QTest.qWait(1000)
    elif market == 'binance':
        symbol = ticker
        try:
            exchange.transfer(symbol, amount, departure, destination)
        except Exception as e:
            print(f"자금 이동 중 오류 발생 [transfer_to]: {e} {ticker= } {amount= }")
            return False
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
        elif category == 'linear':
            symbol = ticker + 'USDT'
        return float(exchange.amount_to_precision(symbol=symbol, amount=amount))
    elif market == 'binance':
        if category == 'spot':
            symbol = ticker + '/USDT'
        elif category == 'inverse':
            symbol = ticker + 'USD'
        elif category == 'linear':
            symbol = ticker + 'USDT'
        return float(exchange.amount_to_precision(symbol=symbol, amount=amount))
def GetMinimumAmount(binance, ticker):
    limit_values = binance.load_markets()[ticker]['limits']

    min_amount = limit_values['amount']['min']
    min_cost = limit_values['cost']['min']
    min_price = limit_values['price']['min']

    coin_info = binance.fetch_ticker(ticker)
    coin_price = coin_info['last']

    print("min_cost: ",min_cost)
    print("min_amount: ",min_amount)
    print("min_price: ",min_price)
    print("coin_price: ",coin_price)

    # get mininum unit price to be able to order
    if min_price < coin_price:
        min_price = coin_price

    # order cost = price * amount
    min_order_cost = min_price * min_amount

    num_min_amount = 1

    if min_cost is not None and min_order_cost < min_cost:
        # if order cost is smaller than min cost
        # increase the order cost bigger than min cost
        # by the multiple number of minimum amount
        while min_order_cost < min_cost:
            num_min_amount = num_min_amount + 1
            min_order_cost = min_price * (num_min_amount * min_amount)

    return num_min_amount * min_amount
def order_open(exchange,market, category, ticker, side, orderType, price, qty, leverage=1): #ccxt
    if market == 'bybit':
        if category == 'spot':
            params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + '/USDT'
            # leverage = 1
        elif category == 'inverse':
            params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + 'USD'
#             leverage = 1
        elif category == 'linear':
            symbol = ticker + 'USDT'
            if side == 'buy':
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            elif side == 'sell':  # 지정가 open short
                params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            # leverage = 3
        try:
            exchange.set_leverage(leverage=leverage, symbol=symbol)
        except Exception as e:
            print(f"주문 중 오류 발생 [order_open]: {e} ")
        res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                         price=price, params=params)
    elif market == 'binance':
        if category == 'spot':
            params = {}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + '/USDT'
            leverage = 1
        elif category == 'inverse':
            params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + 'USD_PERP'
            leverage = 1
        elif category == 'linear':
            symbol = ticker + 'USDT'
            params = {'positionSide': 'LONG'}
            if side == 'buy':
                pass
            elif side == 'sell':  # 지정가 open short
                pass
        try:
            if category == 'spot' or category == 'inverse':
                exchange.set_leverage(leverage=leverage, symbol=f'{ticker}/USDT')
            elif category == 'linear':
                exchange.set_leverage(leverage=leverage, symbol=f'{ticker}/USDT')
        except Exception as e:
            print(f"레버리지 set 오류 발생 [order_open]: {e} ")
        try:
            if category == 'spot' or category == 'inverse':
                exchange.set_margin_mode('isolated',f'{ticker}/USDT')
            elif category == 'linear':
                exchange.set_margin_mode('isolated',f'{ticker}/USDT')
        except Exception as e:
            print(f"주문 중 오류 발생 [order_open]: {e} ")
        if category == 'spot' or category == 'inverse':
            print(f"{market=}  {category=}  {symbol=}  {orderType=}  {side=}  {qty=}  {price=}  {params=}  ")
            res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty, price=price, params=params)
        elif category == 'linear':
            res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty, price=price, params=params)
    # print(f"{self.yellow(f'{type} open 주문')} [{res['id']}] [{side}] - 진입가:{price}, 수량:{qty}, 레버리지: {leverage}, 배팅금액: {round(price * qty, 4)}")
    return res
def order_close(exchange, market, category, ticker, side, orderType, price, qty): #ccxt
    if market == 'bybit':
        if category == 'spot':
            params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + '/USDT'
        elif category == 'inverse':
            params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + 'USD'
        elif category == 'linear':
            symbol = ticker + 'USDT'
            if side == 'buy':
                params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            elif side == 'sell':  # 지정가 open short
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
        res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                         price=price, params=params)
    elif market == 'binance':
        if category == 'spot':
            params = {}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + '/USDT'
            leverage = 1
        elif category == 'inverse':
            params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            symbol = ticker + 'USD_PERP'
            leverage = 1
        elif category == 'linear':
            symbol = ticker + 'USDT'
            params = {'positionSide': 'LONG'}
            if side == 'buy':
                pass
            elif side == 'sell':  # 지정가 open short
                pass
        try:
            if category == 'spot' or category == 'inverse':
                exchange.set_leverage(leverage=leverage, symbol=f'{ticker}/USDT')
            elif category == 'linear':
                exchange.set_leverage(leverage=leverage, symbol=f'{ticker}/USDT')
        except Exception as e:
            print(f"레버리지 set 오류 발생 [order_open]: {e} ")
        try:
            if category == 'spot' or category == 'inverse':
                exchange.set_margin_mode('isolated',f'{ticker}/USDT')
            elif category == 'linear':
                exchange.set_margin_mode('isolated',f'{ticker}/USDT')
        except Exception as e:
            print(f"주문 중 오류 발생 [order_open]: {e} ")
        if category == 'spot' or category == 'inverse':
            print(f"{market=}  {category=}  {symbol=}  {orderType=}  {side=}  {qty=}  {price=}  {params=}  ")
            res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty, price=price, params=params)
        elif category == 'linear':
            res = exchange.create_order(symbol=symbol, type=orderType, side=side, amount=qty, price=price, params=params)
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

import math


def calculate_order(current_price, budget, rate, qty_decimal, price_unit=1000):
    """
    current_price: 현재가
    budget: 예산 (30000)
    rate: 주문 비율 (-0.05 = -5%)
    price_unit: 호가 단위 (업비트 BTC = 1000원)
    qty_decimal: 수량 소수점 자리수 (업비트 BTC = 7자리)
    """

    # 1. 목표 매수가 계산 (호가 단위로 내림)
    target_price = current_price * (1 + rate)
    target_price = math.floor(target_price / price_unit) * price_unit

    # 2. 수량 계산 (소수점 7자리 내림)
    qty = budget / target_price
    qty = math.floor(qty * 10 ** qty_decimal) / 10 ** qty_decimal

    # 3. 실제 주문금액
    order_amount = target_price * qty

    # 4. 주문금액이 1,000원 단위가 아니면 수량 조정
    if order_amount % price_unit != 0:
        # 방법 A: 수량을 올려서 1,000원 단위 맞추기
        adjusted_qty = math.ceil(order_amount / price_unit) * price_unit / target_price
        adjusted_qty = math.floor(adjusted_qty * 10 ** qty_decimal) / 10 ** qty_decimal
        order_amount_adjusted = target_price * adjusted_qty

        # 예산 초과 시 내림
        if order_amount_adjusted > budget:
            adjusted_qty = math.floor(order_amount / price_unit) * price_unit / target_price
            adjusted_qty = math.floor(adjusted_qty * 10 ** qty_decimal) / 10 ** qty_decimal
            order_amount_adjusted = target_price * adjusted_qty

        qty = adjusted_qty
        order_amount = order_amount_adjusted

    print(f"목표가(-5%): {target_price:,}원")
    print(f"수량: {qty}개")
    print(f"주문금액: {order_amount:,.0f}원")
    print(f"1,000원 단위 확인: {'✅' if order_amount % price_unit == 0 else '❌'}")
    print(f"예산 초과 여부: {'❌ 초과!' if order_amount > budget else '✅ 예산 내'}")

    return target_price, qty, order_amount
def decimal_places(n):
    s = str(n)
    if '.' in s:
        return len(s.split('.')[1])
    return 0



import ccxt.pro as ccxtpro
import asyncio


async def watch_ticker():
    exchange = ccxtpro.upbit()

    while True:
        try:
            ticker = await exchange.watch_ticker('BTC/KRW')
            print(f"BTC 현재가: {ticker['last']:,}원")
        except Exception as e:
            print(f"에러: {e}")
            break

    await exchange.close()






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


# 예제 데이터프레임
# data = {
#     'col1': [1, 1, 1, 1],
#     'col2': [2, 3, 2, 2],
#     'col3': [5, 5, 5, 5]
# }
# df = pd.DataFrame(data)
#
# # 특정 열이 모두 특정 숫자로 되어 있는지 확인
# column_name = 'col1'  # 확인할 열 이름
# specific_number = 1   # 특정 숫자
#
# is_all_specific = (df['col1'] == specific_number).all()
# if (df['col1'] == df.loc[df.index[0],'col1']).all():
#     print(f"{column_name} 열이 모두 {specific_number}인가요? {is_all_specific}")

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

def get_week_of_month(input_date):
    # 이번 달 1일의 요일 계산
    first_day_of_month = input_date.replace(day=1)
    first_day_weekday = first_day_of_month.isoweekday()  # 0 = 월요일, 6 = 일요일, 월요일 기준으로 하고싶으면 isoweekday() 대신에 weekday()로 변경

    # 이번 달 시작 주를 보정하여 몇 주차인지 계산
    adjusted_day = input_date.day + first_day_weekday
    return (adjusted_day - 1) // 7

# ticker = '야간선물'
# conn = sqlite3.connect('DB/DB_futopt_kis.db')
# df = pd.read_sql(f"SELECT * FROM {ticker}", conn).set_index('날짜')
# print(df)
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Worker(QObject):
    @pyqtSlot(int)
    def recv_number(self, value):
        print("받은 값:", value)

class MainWindow(QMainWindow):
    sig_send_number = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.worker = Worker()
        # Main → Worker 연결
        self.sig_send_number.connect(self.worker.recv_number)
        # 값 전달
        self.sig_send_number.emit(777)

di = {'A01606': '1164.49'}
li = list(di.keys())[0]

while True:
    t = datetime.datetime.now().replace(microsecond=0)
    tt= t.time().second
    if tt == 44:
        print(t)
# app = QApplication(sys.argv)
#
# window = MainWindow()
# window.show()
#
# app.exec_()