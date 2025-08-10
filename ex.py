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
    # res = session.get_coins_balance(
    #     accountType=accountType, # CONTRACT: Inverse Derivatives Account, UNIFIED: Unified Trading Account
    #     coin=ticker, # BTCUSD, BTC
    # )
    # # return res['result']['balance'][0]['walletBalance']
    # # pprint(res)
    # if balance == '보유':
    #     return float(res['result']['balance'][0]['walletBalance'])
    # elif balance == '잔고':
    #     return float(res['result']['balance'][0]['transferBalance'])
    if market == 'bybit':
        pass
    elif market == 'binance':
        res_spot = exchange.fetch_balance()
        res = exchange.fetch_balance(params={"type": 'delivery'})
        # markets_binance = exchange.load_markets()
        # usdt_free = res_spot['USDT']['free']
        # usdt_total = res_spot['USDT']['total']
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

# 펀딩비율 재투자 시뮬레이션 클래스
class FundingRateSimulator:
    def __init__(self, initial_capital=1000, min_contract_size=100, reinvest_threshold=100):
        self.initial_capital = initial_capital
        self.min_contract_size = min_contract_size
        self.reinvest_threshold = reinvest_threshold

        # 시뮬레이션 상태 변수
        self.current_capital = initial_capital
        self.invested_amount = 0
        self.accumulated_interest = 0
        self.total_interest_earned = 0
        self.reinvest_count = 0

        # 결과 추적용 리스트
        self.history = []

    def calculate_funding_fee(self, invested_amount, funding_rate):
        """
        펀딩비율에 따른 이자 계산
        양수: 이자 받기, 음수: 이자 지불
        """
        return invested_amount * funding_rate

    def can_invest(self, amount):
        """투자 가능 여부 확인"""
        return amount >= self.min_contract_size

    def simulate_period(self, funding_rate, timestamp, btc_price):
        """한 기간(8시간) 시뮬레이션"""
        # 현재 투자 중인 금액에서 펀딩비율 적용
        if self.invested_amount > 0:
            funding_fee = self.calculate_funding_fee(self.invested_amount, funding_rate)
            self.accumulated_interest += funding_fee
            self.total_interest_earned += funding_fee

        # 재투자 조건 확인
        if self.accumulated_interest >= self.reinvest_threshold:
            # 재투자 실행
            new_capital = self.current_capital + self.accumulated_interest
            if self.can_invest(new_capital):
                self.current_capital = new_capital
                self.invested_amount = new_capital
                self.accumulated_interest = 0
                self.reinvest_count += 1
                reinvested = True
            else:
                reinvested = False
        else:
            reinvested = False

        # 첫 투자 (처음에만)
        if self.invested_amount == 0 and self.can_invest(self.current_capital):
            self.invested_amount = self.current_capital

        # 결과 기록
        self.history.append({
            'timestamp': timestamp,
            'funding_rate': funding_rate,
            'btc_price': btc_price,
            'invested_amount': self.invested_amount,
            'accumulated_interest': self.accumulated_interest,
            'total_capital': self.current_capital + self.accumulated_interest,
            'total_interest_earned': self.total_interest_earned,
            'reinvested': reinvested,
            'reinvest_count': self.reinvest_count
        })

    def run_simulation(self, funding_data):
        """전체 시뮬레이션 실행"""
        for idx, row in funding_data.iterrows():
            self.simulate_period(
                row['BTC'],
                row.index,
                # row['btc_price']
            )

    def get_results(self):
        """결과 데이터프레임 반환"""
        return pd.DataFrame(self.history)

    def get_summary(self):
        """요약 통계 반환"""
        final_capital = self.current_capital + self.accumulated_interest
        return {
            '초기 투자금': self.initial_capital,
            '최종 자본': final_capital,
            '총 수익': final_capital - self.initial_capital,
            '수익률': (final_capital / self.initial_capital - 1) * 100,
            '총 이자 수익': self.total_interest_earned,
            '재투자 횟수': self.reinvest_count,
            '평균 펀딩비율': np.mean([h['funding_rate'] for h in self.history]) * 100
            }
def calculate_short_pnl(entry_price, current_price, quantity):
    pnl_coin = (entry_price - current_price) * quantity
    pnl_usd = pnl_coin * current_price
    return pnl_coin, pnl_usd



market = 'binance'
ticker = 'BTC'
if market == 'binance':
    binance_key = 'fYs2tykmSutKiF3ZQySbDz387rqzIDJa88VszteWjqpgDlMtbejg2REN0wdgLc9e'
    binance_secret = 'ddsuJMwqbMd5SQSnOkCzYF6BU5pWytmufN8p0tUM3qzlnS4HYZ1w5ZhlnFCuQos6'

    binance_futures = ccxt.binance(config={
        'apiKey': binance_key,
        'secret': binance_secret,
        'enableRateLimit': True,
        'options': {
            # 'position_mode': True,  #롱 & 숏을 동시에 유지하면서 리스크 관리(헷징)할 때
            'defaultType': 'future'
        },
    })
    binance = ccxt.binance(config={
        'apiKey': binance_key,
        'secret': binance_secret,
        'enableRateLimit': True,
        'options': {'position_mode': True, },
    })
    print(binance.parse8601(f'2020-01-01T00:00:00Z'))
    quit()
    dict_duration = {'1주일': 7, '1개월': 30, '2개월': 60, '3개월': 90, '6개월': 180, '1년': 365, '2년': 365 * 2, '3년': 365 * 3}
    since = datetime.datetime.now() - datetime.timedelta(days=dict_duration['1년'])
    since = datetime_to_stamp(since) * 1000  # 밀리초 곱하기
    symbol = ticker+'USD_PERP'
    # out = binance.fetch_funding_rate_history(symbol=symbol,since=None,limit=None,params={'type':'delivery'})
    out_lately = binance.fetch_funding_rate_history(symbol=symbol, since=None,params={'type':'delivery'})
    df = pd.DataFrame(out_lately)
    print(df)
    df['timestamp'] = df['timestamp']//1000*1000
    print('=======================================================================')
    print((df.loc[df.index[-1], 'timestamp'] - df.loc[df.index[0], 'timestamp'])/(8 * 3600 * 1000))
    from_time = (out_lately[0]['timestamp'] // 1000) * 1000
    start_time = (out_lately[0]['timestamp'] // 1000) * 1000
    from_time = from_time - (8 * 3600 * 1000 * (len(out_lately)))  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
    print(f"{from_time= }    {stamp_to_str(from_time)}")
    while start_time > since:
        # from_time = from_time - 5731200000  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
        print(f"{from_time= }    {stamp_to_str(from_time)}")
        # from_time = from_time - 5731200000+(8 * 3600*1000)  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
        out = binance.fetch_funding_rate_history(symbol=symbol, since=from_time)
        #         pprint(out)
        df = pd.DataFrame(out)
        print(df)
        # from_time = (out[0]['timestamp'] // 1000) * 1000
        print('========================================')
        if not out:
            break
        else:
            if since == False:
                break
            elif from_time < (out[0]['timestamp'] // 1000) * 1000:
                lately_time = (out_lately[0]['timestamp']//1000)*1000
                print(f"{lately_time = }")
                out=[x for x in out if x['timestamp'] < lately_time]
                pprint(out)
                out.extend(out_lately)
                out_lately = out
                break
            else:
                start_time = (out[0]['timestamp'] // 1000) * 1000
                from_time = start_time - (8 * 3600 * 1000 * (len(out_lately)))  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
                out.extend(out_lately)
                out_lately = out

elif market == 'bybit':
    api_key = "k3l5BpTorsRTHvPmAj"
    api_secret = "bdajEM0VJJLXCbKw0i9VfGemAlfRGga4C5jc"
    bybit = ccxt.bybit(config={
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'position_mode': True, },
    })
    dict_duration = {'1주일': 7, '1개월': 30, '2개월': 60, '3개월': 90, '6개월': 180, '1년': 365, '2년': 365 * 2, '3년': 365 * 3}
    since = datetime.datetime.now() - datetime.timedelta(days=dict_duration['1년'])
    since = datetime_to_stamp(since) * 1000  # 밀리초 곱하기
    ticker = 'BTC'
    symbol = ticker+'USD'
    out_lately = bybit.fetch_funding_rate_history(symbol=symbol,since=None)
    # pprint(out_lately)
    from_time = (out_lately[0]['timestamp'] // 1000) * 1000
    df = pd.DataFrame(out_lately)
    print(df)
    print('=======================================================================')
    print(df.loc[df.index[-1],'timestamp']-df.loc[df.index[0],'timestamp'])
    print(5731200000/(8 * 3600*1000))

    while from_time > since:
        # from_time = from_time - 5731200000  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
        from_time = from_time - (8 * 3600*1000*201)  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
        # from_time = from_time - 5731200000+(8 * 3600*1000)  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
        out = bybit.fetch_funding_rate_history(symbol=symbol,since=from_time)
#         pprint(out)
        df = pd.DataFrame(out)
        print(df)
        # from_time = (out[0]['timestamp'] // 1000) * 1000
        print('========================================')
        if not out:
            break
        else:
            from_time = (out[0]['timestamp'] // 1000) * 1000
            out.extend(out_lately)
            out_lately = out
            if since == False:
                break
data = [x['fundingRate'] for x in out_lately]
timestamps = [x['timestamp'] for x in out_lately]
df = pd.DataFrame({
    f'{ticker}': data,
    '날짜': timestamps
})

print(df)
df['날짜'] = df['날짜']//1000*1000
df = df[df['날짜'] >= since]
df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
df['날짜'] = df['날짜'].dt.tz_localize(None)
df.set_index('날짜', inplace=True)
print(df)
has_duplicates = df.index.duplicated().any()
print(f"중복 인덱스 존재 여부: {has_duplicates}")
duplicate_indices = df.index[df.index.duplicated()].unique()
print("중복된 인덱스들:")
print(duplicate_indices)
df.to_sql('test',con=sqlite3.connect('bt.db'),if_exists='replace')
print(df)
quit()
import pandas as pd
dict_duration = {'1주일':7,'1개월': 30, '2개월': 60,'3개월': 90, '6개월': 180, '1년': 365, '2년': 365 * 2, '3년': 365 * 3}
df_funding = pd.DataFrame()
since = datetime.datetime.now()-datetime.timedelta(days=dict_duration['3개월'])
since = datetime_to_stamp(since)*1000 #밀리초 곱하기

df = fetch_funding_rates('binance',binance,'BTC',False)
df.index=df.index//1000
# btc_date_start = df.index[0]
btc_date_end = df.index[-1]
list_out = []
for i,ticker in enumerate(list_inverse):
    df = fetch_funding_rates(market,binance,ticker,since)

    df.index=df.index//1000
    print(df) #print를 안하면 데이터에 Nan 이 섞여서 출력됨
    if df.index[-1] == btc_date_end:
        df_funding = pd.concat([df_funding, df], axis=1)
    else:
        list_out.append(ticker)

# df_funding.index = df_funding['날짜']
print(df_funding)
df_funding = df_funding[df_funding.index>since//1000]
print(df_funding)

df_funding['날짜'] = pd.to_datetime(df_funding.index, utc=True, unit='s')
df_funding['날짜'] = df_funding['날짜'].dt.tz_convert("Asia/Seoul")
df_funding['날짜'] = df_funding['날짜'].dt.tz_localize(None)
df_funding.set_index('날짜', inplace=True)

df_ma = pd.DataFrame()
df_funding.loc['단순평균'] = df_funding.mean()
# print(df_ma.sort_values('단순평균',ascending=False))
# print(f"{list_out= }")

ema_values = {}
for col in df_funding.columns.tolist():
    ema_values[col] = df_funding[col].ewm(span=20, adjust=False).mean().iloc[-1]

# 비숫자 열에 대해서는 '지수이동평균' 라벨 추가
for col in df_funding.columns:
    if col not in df_funding.columns.tolist():
        ema_values[col] = '지수이동평균'

# 한 줄로 EMA 행 추가
df_funding.loc['지수이동평균'] = ema_values
# df_ema = pd.DataFrame(ema_values,index=['지수이동평균'])
# df_ema = df_ema.transpose()
# print(df_ema.sort_values('지수이동평균',ascending=False))

print(df_funding)
df_funding.index = df_funding.index.astype(str)
df_funding.to_sql('funding',sqlite3.connect('DB/funding_check.db'),if_exists='replace')
quit()
print(df_funding.tail(20))
print(list_out)


# 결과 데이터프레임 생성
results_df = simulator.get_results()
print("시뮬레이션 결과 (처음 10개 기간):")
print(results_df.head(10).round(4))
print("\n" + "=" * 80 + "\n")

# 요약 통계
summary = simulator.get_summary()
print("시뮬레이션 요약:")
for key, value in summary.items():
    if isinstance(value, float):
        print(f"{key}: {value:.2f}{'%' if '비율' in key or '수익률' in key else ' USDT'}")
    else:
        print(f"{key}: {value}")

print("\n" + "=" * 80 + "\n")

# 재투자 시점 확인
reinvest_points = results_df[results_df['reinvested'] == True]
if not reinvest_points.empty:
    print("재투자 시점들:")
    print(reinvest_points[['timestamp', 'total_capital', 'reinvest_count']].round(2))
else:
    print("재투자 조건을 만족한 시점이 없습니다.")

print("\n" + "=" * 80 + "\n")


# 성능 분석 함수
def analyze_performance(results_df):
    """성능 분석 함수"""
    print("성능 분석:")

    # 시간별 수익률 분석
    final_capital = results_df['total_capital'].iloc[-1]
    initial_capital = 1000
    days = len(results_df) / 3  # 하루 3번 정산

    print(f"투자 기간: {days:.1f}일")
    print(f"일평균 수익률: {(final_capital / initial_capital) ** (1 / days) - 1:.4%}")
    print(f"연환산 수익률: {((final_capital / initial_capital) ** (365 / days) - 1) * 100:.2f}%")

    # 펀딩비율 통계
    positive_funding = results_df[results_df['funding_rate'] > 0]
    negative_funding = results_df[results_df['funding_rate'] < 0]

    print(f"\n펀딩비율 통계:")
    print(f"양수 펀딩비율 비율: {len(positive_funding) / len(results_df) * 100:.1f}%")
    print(f"음수 펀딩비율 비율: {len(negative_funding) / len(results_df) * 100:.1f}%")
    print(f"평균 펀딩비율: {results_df['funding_rate'].mean() * 100:.4f}%")
    print(f"최대 펀딩비율: {results_df['funding_rate'].max() * 100:.4f}%")
    print(f"최소 펀딩비율: {results_df['funding_rate'].min() * 100:.4f}%")


analyze_performance(results_df)
quit()
# res = fetch_order(bybit,'bybit','MNT','1978820750840524288','spot',5.2)
# res = fetch_order(binance,'binance','XRP','12367717649','inverse',98)

# bet_usdt = used_usdt / 20
# bet_usdt = math.ceil(bet_usdt)  # 소수점일경우 올림해서 정수로 변환
# print(f"{used_inverse=}  {price= }   {used_usdt= }  |  |  {bet_usdt= }")
# if min_amount_future > min_cont:
#     if min_amount_future > bet_usdt * future_leverage:  # 최소주문수량보다 작으면 (레버리지 3일경우 future = 3.3으로 되어야 함
#         bet_usdt = min_amount_future / future_leverage
#     bet = bet_usdt
# else:
#     if min_cont > bet_usdt:
#         bet = min_cont
#     else:
#         bet = bet_usdt
#
# bet = bet/min_cont
# bet = math.ceil(bet)  # 소수점일경우 올림해서 정수로 변환
# print(f"{bet= }")
# category = 'inverse'
# res = order_open(exchange=exchange, market=market, category=category, ticker=ticker, side='buy',
#                  orderType='market', price=price, qty=bet)
# id = res['id']
# bet = 6
# while True:
#     res = fetch_order(exchange=exchange,market='binance',ticker=ticker,id='12522097533',category='inverse',qty=bet)
#     if res['체결'] == True:
#         break
#     else:
#         time.sleep(1)
# # print(f"{res=}")
# if market == 'binance':
#     res = binance.fetch_balance(params={"type": 'delivery'})
#     free_qty = res[ticker]['free']*0.99 #전부 옮기려니 안됨
# elif market == 'bybit':
#     res = bybit.fetch_balance()
#     used_inverse = res['used'][ticker]
# # 'ADA': {'free': 98.59136072, 'total': 1595.02949928, 'used': 1496.43813856},
# transfer_to(exchange=exchange,market='binance',ticker=ticker,amount=free_qty,departure='inverse',
#             destination='spot')
# time.sleep(1)
# res = order_open(exchange=exchange,market=market,category='spot',ticker=ticker,side='sell',
#                  orderType='market',price=price,qty=free_qty)
# pprint(res)
# # id = res['id']
# while True:
#     res = fetch_order(exchange=exchange,market='binance',ticker=ticker,id='7158174004',category='spot',qty=free_qty)
#     if res['체결'] == True:
#         break
#     else:
#         time.sleep(1)
# usdt = res['체결금액']
# usdt = 136.04584
# price = 2429.36
# print(f"{usdt = }")
# qty = (usdt*future_leverage)/price
# qty = amount_to_precision(binance,'binance','linear',ticker,qty)
# # transfer_to(exchange=exchange,market='binance',ticker='USDT',amount=usdt,departure='spot',destination='linear')
# print(qty)
# quit()
# res = order_open(exchange=binance, market=market, category='linear', ticker=ticker, side='buy',
#                  orderType='market', price=price, qty=qty, leverage=3)
# id = res['id']
print(f"{id= }")
res = binance.fetch_closed_orders(symbol='ETH/USD')
pprint(res)
quit()
while True:
    res = fetch_order(exchange=binance_futures,market='binance',ticker=ticker,id='8389765910084028367',category='linear',qty=0.1161)
    if res['체결'] == True:
        break
    else:
        time.sleep(1)

quit()

from pybit.unified_trading import HTTP, WebSocket
# Bybit API 키 설정

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
stamp_date_old = datetime_to_stamp(date_old)

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