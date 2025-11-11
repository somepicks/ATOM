from pybit.unified_trading import HTTP
import datetime
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
                             QHBoxLayout,
                             QTableWidget, QSplitter, QApplication, QCheckBox, QTableWidgetItem, QHeaderView,
                             QComboBox, QDialog, QMessageBox)
from PyQt5.QtCore import Qt,QThread,pyqtSlot,QTimer,pyqtSignal,QWaitCondition
from PyQt5.QtTest import QTest
import time
import uuid
import math
import subprocess
import ccxt
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import talib
from pprint import pprint


pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다

class do_trade(QThread):
    qt_inverse = pyqtSignal(pd.DataFrame)
    qt_open = pyqtSignal(pd.DataFrame)
    qt_future = pyqtSignal(pd.DataFrame)
    qt_linear = pyqtSignal(pd.DataFrame)
    save_inverse = pyqtSignal(pd.DataFrame)
    save_df = pyqtSignal(pd.DataFrame,str)
    save_set = pyqtSignal(pd.DataFrame)
    val_light = pyqtSignal(bool)
    val_wallet = pyqtSignal(int,int)
    val_time = pyqtSignal(str)
    shutdown_signal = pyqtSignal()
    def __init__(self, parent, dict_bybit, dict_binance,df_open,df_closed,df_set,df_linear,dict_option):
        super().__init__(parent)
        self.cond = QWaitCondition()
        self.bool_light = False
        self._status = True
        self.dict_bybit = dict_bybit

        self.dict_binance = dict_binance

        self.df_open = df_open
        self.df_closed = df_closed

        self.df_set = df_set
        self.df_linear = df_linear
        self.dict_option = dict_option

        self.funding_time_old = dict_option['start_time']

        self.common = common_define(dict_bybit,dict_binance)

        if self.dict_bybit['active'] == True:
            self.list_inverse_bybit = self.common.fetch_inverse_list('bybit')
        if self.dict_binance['active'] == True:
            self.list_inverse_binance = self.common.fetch_inverse_list('binance')
    def run(self):
        # 현재 시간의 분, 초, 마이크로초를 0으로 만들고 1시간 추가 (다음으로 올 정시 구하기)
        next_hour = self.dict_option['start_time'].replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        self.fetch_balance()

        # df_linear을 수동으로 청산할 경우가 있기 때문에 교집합으로 종목이 있는지 확인
        list_cross = list(set(self.df_linear.index.tolist()) & set(self.df_future.index.tolist()))
        self.df_linear = self.df_linear.loc[list_cross] #리스트에있는 행만 추출
        self.df_linear = self.df_linear.sort_values('market')
        for idx,row in self.df_future.iterrows():
            if row['진입수량'] < self.df_linear.loc[idx,'보유수량']:
                self.df_linear.loc[idx, '보유수량'] = row['진입수량']
                # self.df_linear.loc[idx, '매수금액'] = self.df_linear.loc[idx, '보유수량']+self.df_linear.loc[idx, '평단가']
                self.df_linear.loc[idx, '매수금액'] = self.df_linear.loc[idx, '보유수량']+row['진입가']
                self.df_linear.loc[idx, '평단가'] = row['진입가']
                self.df_linear.loc[idx, '매수횟수'] = 1
                # quit()
        self.save_df.emit(self.df_linear,'linear')
        start_time = self.df_set.loc['start_time', 'val']
        finish_time = self.df_set.loc['auto_finish', 'val']
        if str == type(start_time):
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

        dict_time = {'loop': 0,'1분후': 1, '5분후': 5, '10분후': 10, '30분후': 30, '1시간후': 60, '설정안함':43200}
        finish_time = start_time + datetime.timedelta(minutes=dict_time[finish_time])

        while self._status:
            now_time = datetime.datetime.now()
            if self.dict_bybit['active'] == True:
                self.tickers_bybit = self.common.fetch_tickers('bybit') #현재가 조회용
            if self.dict_binance['active'] == True:
                self.tickers_binance = self.common.fetch_tickers('binance')#현재가 조회용
            funding_time = pd.to_datetime(self.df_set.loc['funding_time','val'])
            current_t = now_time.replace(microsecond=0)
            self.text_time = funding_time - current_t
            # days를 제외한 시간, 분, 초만 계산
            hours, remainder = divmod(self.text_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.text_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.change_price()
            if now_time > next_hour:# 매 정시마다 잔고 조회
                # print('잔고조회')
                self.fetch_balance()
                next_hour = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            if not self.df_open.empty:
                dict_txt_chegyeol = {}
                for id in self.df_open.index.tolist():
                    if self.df_open.loc[id, '상태'] == '매수주문' or self.df_open.loc[id, '상태'] == '부분체결':
                        dict_txt_chegyeol = self.chegyeol_buy(id, dict_txt_chegyeol)
                df_txt_chegyeol = pd.DataFrame(dict_txt_chegyeol).T #id가 행으로 오게해서 체결을 데이터프레임으로 보여주기
                if '체결' in df_txt_chegyeol['체결'].tolist() or '주문취소' in df_txt_chegyeol['체결'].tolist() or '주문 자동취소' in df_txt_chegyeol['체결'].tolist() or '부분체결' in df_txt_chegyeol['체결'].tolist():
                    print('- 체결 -')
                    print(df_txt_chegyeol) #체결이 있을 경우에만 프린트
                    df_txt_chegyeol.reset_index(inplace=True)
                    self.fetch_balance()

            dict_txt_linear = {}
            dict_txt_inverse = {}
            for idx in self.df_inverse.index.tolist():
                market = self.df_inverse.loc[idx,'market']
                ticker = self.df_inverse.loc[idx,'ticker']
                if ticker == 'USDT':
                    continue # USDT 제외
                elif market == 'bybit' and not ticker in self.list_inverse_bybit: # 인버스 항목에 없으면 제외
                    continue
                elif market == 'binance' and not ticker in self.list_inverse_binance:
                    continue
                df = self.common.get_df(market, ticker, '4시간봉', 10)  # 10일 전부터의 데이터 불러오기
                dict_txt_inverse = self.buy_auto(idx,market,ticker,dict_txt_inverse)

                dict_division = {'BTC':25, 'ETH':30, 'XRP':25, 'SOL':28}
                dict_leverage = {'BTC':3, 'ETH':3, 'XRP':3, 'SOL':3}
                # dict_txt_linear = self.buy_linear(df=df,idx=idx,division=dict_division.get(ticker,40),
                #                            future_leverage=dict_leverage.get(ticker,2),dict_txt=dict_txt_linear)
                if idx in self.df_linear.index.tolist():
                    self.sell_future(df=df,idx=idx)
            if dict_txt_linear:
                print('- linear 진입 -')
                df_linear = pd.DataFrame(dict_txt_linear).T
                df_linear.reset_index(inplace=True)
                print(df_linear)
                self.fetch_balance()
            if dict_txt_inverse:
                print('- iverse 진입 -')
                df_inverse = pd.DataFrame(dict_txt_inverse).T
                df_inverse.reset_index(inplace=True)
                print(df_inverse)
                self.fetch_balance() # 주문이 나가면 기존의 free 잔고가 변경되기 때문에 주문시 마다 조회를 해줘야됨

            self.active_light()
            QTest.qWait(500)
            if datetime.datetime.now() > finish_time:
                # 윈도우 종료
                self.shutdown_signal.emit()
                break
        self._status = False

    def change_price(self):
        if not self.df_inverse.empty:
            for index, row in self.df_inverse.iterrows():
                ticker = self.df_inverse.loc[index,'ticker']
                if ticker == 'USDT':
                    continue
                elif row['market'] == 'bybit':
                    self.df_inverse.loc[index,'현재가'] = self.tickers_bybit[f"{ticker}/USDT:USDT"]['close']
                elif row['market'] == 'binance':
                    self.df_inverse.loc[index,'현재가'] = self.tickers_binance[f"{ticker}/USDT"]['close']
        if not self.df_future.empty:
            for index, row in self.df_future.iterrows():
                ticker = self.df_future.loc[index,'ticker']
                if row['market'] == 'bybit':
                    현재가 = self.tickers_bybit[f"{ticker}/USDT:USDT"]['close']
                elif row['market'] == 'binance':
                    현재가 = self.tickers_binance[f"{ticker}/USDT"]['close']
                if row['방향'] == 'long':
                    수익률 = (현재가-row['진입가'])/row['진입가']*row['레버리지']*100
                    수익금 = (현재가-row['진입가'])*row['진입수량']
                elif row['방향'] == 'short':
                    수익률 = (row['진입가']-현재가)/row['진입가']*row['레버리지']*100
                    수익금 = (row['진입가']-현재가)*row['진입수량']
                self.df_future.loc[index,'현재가'] = 현재가
                self.df_future.loc[index,'수익률'] = 수익률
                self.df_future.loc[index,'수익금'] = 수익금
        if not self.df_linear.empty:
            for index, row in self.df_linear.iterrows():
                ticker = self.df_linear.loc[index,'ticker']
                if row['market'] == 'bybit':
                    현재가 = self.tickers_bybit[f"{ticker}/USDT:USDT"]['close']
                elif row['market'] == 'binance':
                    현재가 = self.tickers_binance[f"{ticker}/USDT"]['close']
                if row['방향'] == 'long':
                    수익률 = (현재가-row['평단가'])/row['평단가']*row['레버리지']*100
                    수익금 = (현재가-row['평단가'])*row['보유수량']
                elif row['방향'] == 'short':
                    수익률 = (row['평단가']-현재가)/row['평단가']*row['레버리지']*100
                    수익금 = (row['평단가']-현재가)*row['보유수량']
                try:
                    self.df_linear.loc[index,'현재가'] = 현재가
                    self.df_linear.loc[index,'수익률'] = round(수익률,2)
                    self.df_linear.loc[index,'수익금'] = round(수익금,2)
                except:
                    print(f"change_price 에러 - {row['market']}   {ticker}   {현재가= }  {self.tickers_binance[{ticker}]}")


    def buy_auto(self, idx, market, ticker,dict_txt):
        주문최소금액 = self.df_inverse.loc[idx,'주문최소금액(USD)']
        현재가 = self.df_inverse.loc[idx,'현재가']
        보유코인합계 = self.df_inverse.loc[idx,'합계(USD)']
        배팅가능합계 = self.df_inverse.loc[idx,'배팅가능합계(USD)']
        # 배팅가능 = self.df_inverse.loc[idx,'free(qty)']
        if self.df_set.loc['rate_short','val'] == None:
            rate_short = 0
        else:
            # rate_short = float(self.df_set.loc['rate_short','val'])
            rate_short = self.dict_option['인버스호가']
        안전마진 = 5 # 잔고가 펀딩비로 받는 금액의 5배 이상 있을 경우에만 진행
        funding_rate = 0.01/100
        # 배팅가능수량 = self.df_inverse.loc[idx,'free(qty)'] #contract 여유 잔고수량 불러오기
        # 진입수량 = self.df_inverse.loc[idx,'used(qty)'] #contract 진입수량 불러오기
        price = 현재가 + (현재가 * (rate_short) / 100)
        여유돈 = 보유코인합계*funding_rate*안전마진
        배팅가능금액 = 배팅가능합계 - 여유돈

        진입수량 = math.trunc(배팅가능금액) #소수점 절사

        order = True if 진입수량 >= 주문최소금액 else False
        # if 배팅가능수량 * 주문가 > 주문최소금액: #최소수량보다 잔고가 많을경우마다 주문하면 마이너스피 일 때는 갖고있는 잔고에서 매번 수수료가 나가기 때문
        if order : # 현재 잔고가 진입수량*펀딩비율*5배 보다 많아야 매수 조건 성립 (최소수량보다 잔고가 많을경우마다 주문하면 마이너스피 일 때는 갖고있는 잔고에서 매번 수수료가 나가기 때문)
            df = self.common.get_df(market, ticker, '일봉', 60)  # 일봉의 이평이 데드크로스일 때만 신규 진입
            if df.loc[df.index[-1],'이평9'] < df.loc[df.index[-1],'이평20']:
                df_open = pd.DataFrame()

                진입수량 = 진입수량//주문최소금액
                주문가 = self.common.price_to_precision(market=market,category='inverse',ticker=ticker,price=price)
                res = self.common.order_open(market=market, category='inverse', ticker=ticker, side='sell',
                                                 orderType="limit", price=주문가, qty=진입수량)
                id = res['id']
                df_open.loc[id, 'market'] = market
                df_open.loc[id, 'ticker'] = ticker
                df_open.loc[id, '주문시간'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                df_open.loc[id, '주문수량'] = 진입수량
                # df_open.loc[id, 'short비율'] = rate_short
                # df_open.loc[id, 'spot비율'] = np.nan
                df_open.loc[id, 'id'] = id
                df_open.loc[id, '매수금액'] = 진입수량*주문최소금액
                df_open.loc[id, '상태'] = '매수주문'
                df_open.loc[id, 'category'] = 'inverse'
                df_open.loc[id, '주문가'] = 주문가
                # print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | 자동매수 {ticker}: {진입수량=}, {주문가=}, {진입수량 * 주문가}')
                if not self.df_open.empty:
                    self.df_open = pd.concat([self.df_open, df_open], axis=0).astype(self.df_open.dtypes)
                else:
                    self.df_open = df_open.copy()
                dict_txt[id] = {}
                dict_txt[id]['market'] = market
                dict_txt[id]['ticker'] = ticker
                dict_txt[id]['category'] = 'inverse'
                dict_txt[id]['주문수량'] = 진입수량
                dict_txt[id]['매수금액'] = 진입수량*주문최소금액
                dict_txt[id]['주문가'] = 주문가

                self.qt_open.emit(self.df_open)
        else:
            pass
        return dict_txt

    def buy_manual(self,market,ticker,배팅금액,rate_spot,df_inverse):
        print("현물 매수 요청 수신!")
        df_open = pd.DataFrame()
        category = 'spot'
        현재가 = self.common.fetch_ticker(market=market,ticker=ticker + '/USDT')['close']
        주문가 = 현재가 + (현재가 * rate_spot / 100)
        주문가 = self.common.price_to_precision(market=market,category=category, ticker=ticker, price=주문가)
        fee = 0.1
        레버리지 = 1
        진입수량 = (100 - (fee * 레버리지)) / 100 * 배팅금액 / 주문가
        진입수량 = self.common.amount_to_precision(market=market, category=category,ticker=ticker, amount=진입수량)
        df = df_inverse.loc[df_inverse['market']==market]
        보유현금 = df[df['ticker']=='USDT']['free(qty)'].values[0] # ticker가 USDT인 행의 free(qty)컬럼 첫번째 값
        매수금액 = (진입수량*주문가)+(진입수량*주문가)*0.001 #수수료 포함
        if 보유현금 < 매수금액:
            print(f"USDT 부족 - 보유한 USDT: {보유현금}, 필요한 USDT: {매수금액}  |  {market= }  {ticker= }   {배팅금액= }  {rate_spot= }")
            return 0
        else:
            res = self.common.fetch_load_market(market)
            if market == 'binance':
                min_usd = res[ticker + '/USDT']['limits']['cost']['min']
                if 매수금액 < min_usd:
                    print(f'{market= } {ticker= } {매수금액= } 매수금액이 더 필요합니다.')
                    return 0
            elif market == 'bybit':
                min_usd = res[ticker + '/USDT']['limits']['cost']['min']
                if 매수금액 < min_usd:
                    print(f'{market= } {ticker= } {매수금액= } 매수금액이 더 필요합니다.')
                    return 0
        res = self.common.order_open(market= market,category=category, ticker=ticker, side='buy', orderType="limit",
                              price=주문가, qty=진입수량)
        id = res['id']
        df_open.loc[id, 'market'] = market
        df_open.loc[id, 'ticker'] = ticker
        df_open.loc[id, '주문시간'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        df_open.loc[id, '주문수량'] = 진입수량
        # df_open.loc[id, 'spot비율'] = rate_spot
        # df_open.loc[id, 'short비율'] = np.nan
        df_open.loc[id, 'id'] = id
        df_open.loc[id, '매수금액'] = 배팅금액
        df_open.loc[id, '상태'] = '매수주문'
        df_open.loc[id, 'category'] = 'spot'
        df_open.loc[id, '주문가'] = 주문가
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | 수동매수 {ticker}: {진입수량=}, {주문가=}, 매수금액: {진입수량 * 주문가}')

        if not self.df_open.empty:
            self.df_open = pd.concat([self.df_open, df_open], axis=0).astype(self.df_open.dtypes)
        else:
            self.df_open = df_open.copy()
        self.qt_open.emit(self.df_open)
        self.fetch_balance()
    def change_set(self,df_set):
        self.df_set = df_set
    def chegyeol_buy(self, id, dict_txt):
        market = self.df_open.loc[id, 'market']
        ticker = self.df_open.loc[id, 'ticker']
        category = self.df_open.loc[id, 'category']
        주문시간 = self.df_open.loc[id,'주문시간']
        qty = self.df_open.loc[id,'주문수량']
        주문시간 = datetime.datetime.strptime(주문시간,'%Y-%m-%d %H:%M')
        dict_chegyeol = self.fetch_order(market=market, ticker=ticker, id=id , category=category,qty=qty)
        dict_txt[id] = {}
        dict_txt[id]['market'] = market
        dict_txt[id]['ticker'] = ticker
        dict_txt[id]['category'] = category

        if dict_chegyeol['체결'] == True:
            # print('=============================')
            # print(f"{ticker}  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간{dict_chegyeol['체결시간']} id:{id}")
            self.df_closed.loc[id] = self.df_open.loc[id].copy()
            self.df_open.drop(index=id, inplace=True)
            self.df_closed.loc[id, '체결가'] = dict_chegyeol['체결가']
            self.df_closed.loc[id, '체결시간'] = dict_chegyeol['체결시간']
            self.df_closed.loc[id, '수수료'] = dict_chegyeol['수수료']
            self.df_closed.loc[id, '체결수량'] = dict_chegyeol['체결수량']
            self.df_closed.loc[id, '상태'] = '체결완료'
            self.save_df.emit(self.df_closed,'closed')
            if market == 'bybit':
                pass
            elif market == 'binance' and category == 'spot':
                self.common.transfer_to(market, ticker, dict_chegyeol['체결수량'],'spot','inverse')
            dict_txt[id]['체결'] = '체결'
            dict_txt[id]['체결수량'] = dict_chegyeol['체결수량']
        elif dict_chegyeol['체결'] == '주문취소':
#             print(f'주문취소 - {market= } | {ticker= } | {category } | {qty= } | {id= }')
            self.df_open.drop(index=id, inplace=True)
            dict_txt[id]['체결'] = '주문취소'
            dict_txt[id]['체결수량'] = 0
        elif self.get_funding_time(주문시간) < datetime.datetime.now(): # 펀딩비시간까지 체결안되면 취소
#             print(f'주문취소 - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | {market= } | {ticker= } | {category= } | {qty= } | {id= }')
            배팅금액 = self.df_open.loc[id, '매수금액']
            self.common.order_cancel(market,category,ticker,id)
            self.df_open.drop(index=id,inplace=True)
            if category == 'spot':
                rate_spot = self.dict_option['현물호가']
                self.buy_manual(market=market,ticker=ticker,배팅금액=배팅금액,rate_spot=rate_spot,df_usdt=self.df_inverse)
            dict_txt[id]['체결'] = '주문 자동취소'
            dict_txt[id]['체결수량'] = 0
        elif dict_chegyeol['체결'] == '부분체결':
            self.df_open.loc[id,'상태'] = '부분체결'
            dict_txt[id]['체결'] = '부분체결'
            dict_txt[id]['체결수량'] = dict_chegyeol['체결수량']
        else:
            dict_txt[id]['체결'] = False
            dict_txt[id]['체결수량'] = 0

        return dict_txt


    def buy_linear(self,df,idx,division,future_leverage,dict_txt):
        market = self.df_inverse.loc[idx,'market']
        ticker = self.df_inverse.loc[idx,'ticker']
        min_cont = self.df_inverse.loc[idx,'주문최소금액(USD)']
        used_usdt = self.df_inverse.loc[idx, '합계(USD)']
        # df = self.get_df(market, ticker, '4시간봉',10) #10일 전부터의 데이터 불러오기

        buy_signal_future,side = self.get_buy_signal(df,market,ticker)
        # if market == 'binance' and ticker == 'MANA':
        #     buy_signal_future = True
        # else:
        #     buy_signal_future = False
        # buy_signal_future = True
        # market = 'bybit'
        # ticker = 'BTC'
        # min_cont = 100
        # used_usdt = 10
        if buy_signal_future == True:
            # print('*******************************************************************************************************')
            # print(f"buy_linear 매수신호 : {idx} - {datetime.datetime.now()}  {market=}  {ticker= }  {future_leverage=}")
            price = self.df_inverse.loc[idx,'현재가']
            # price = self.df_inverse.loc[f'{market}_{ticker}','현재가']
            res = self.common.fetch_load_market(market)
            if market == 'bybit':
                symbol = f'{ticker}/USDT:USDT'
                min_amount_future = res[symbol]['limits']['amount']['min']  #선물 최소 주문수량 (금액으로 조회 안됨)
                min_amount_future = min_amount_future*price
            elif market == 'binance':
                symbol = f'{ticker}/USDT:USDT'
                min_amount_future = res[symbol]['limits']['cost']['min'] #선물 최소 주문금액 (수량이 맞지않음)
#
            if used_usdt * future_leverage < min_amount_future:
                print(f"최소주문 미달 [used_usdt*future_leverage < min_amount_future] {used_usdt= }  |  {future_leverage= }  |  {min_amount_future= }")
                return      # 보유수량이 선물 최소주문수량보다 작거나 인버스 주문최소금액보다 작을 경우 pass
            elif used_usdt < min_cont:
                print(f"최소주문 미달 [used_usdt * price < min_cont] {used_usdt= }  |  {min_cont= }")
                return

            # for i in reversed(range(21)): # 1/N 만큼만 배팅 금액이 부족하면 1/(N-1) 로 하향
            bet_usdt = used_usdt/division
            bet_usdt = math.ceil(bet_usdt) # 소수점일경우 올림해서 정수로 변환
            if min_amount_future > min_cont:
                if min_amount_future > bet_usdt*future_leverage: #최소주문수량보다 작으면 (레버리지 3일경우 future = 3.3으로 되어야 함
                    bet_usdt = min_amount_future/future_leverage
                bet = bet_usdt
            else:
                if min_cont > bet_usdt:
                    bet = min_cont
                else:
                    bet = bet_usdt

            bet = bet/min_cont
            bet = math.ceil(bet) # 소수점일경우 올림해서 정수로 변환

            category = 'inverse'
            # _, usdt_free_before, __ = self.fetch_inverse_detail(market)
            res = self.common.order_open(market=market,category=category,ticker=ticker,side='buy',
                                             orderType='market',price=price,qty=bet,df=self.df_inverse)
            id = res['id']
            QTest.qWait(1000)
            i = 0

            while True:
                dict_chegyeol = self.fetch_order(market=market,ticker=ticker,id=id,category=category,qty=bet)
                if dict_chegyeol['체결'] == True:
                    # print(f"{idx} -  {category=},  체결수량:{dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간: {dict_chegyeol['체결시간']}")
                    # _, usdt_free, __ = self.fetch_inverse_detail(market) #잔고 증가했는지 확인
                    # if usdt_free>usdt_free_before:
                    break
                QTest.qWait(1000)
                i = i +1
                if i >10:
                    print(f'{market} buy_linear 에러 1  ')
                    quit()

            if market == 'binance':
                res = self.common.dict_binance['spot'].fetch_balance(params={"type": 'delivery'})
                free_qty = res[ticker]['free'] * 0.9  # 전부 옮기려니 안됨
                self.common.transfer_to(market=market, ticker=ticker, amount=free_qty, departure='inverse', destination='spot')
                for i in range(20):
                    QTest.qWait(1000)
                    res = self.common.dict_binance['spot'].fetch_balance()
                    print(f"market == 'binance': {free_qty}  <=  {res[ticker]['free']= }")
                    if free_qty <= res[ticker]['free']:
                        break
            elif market == 'bybit':
                res = self.common.dict_bybit['exchange'].fetch_balance()
                free_qty = res[ticker]['free'] * 0.9
                QTest.qWait(1000)

            category = 'spot'
            free_qty = self.common.amount_to_precision(market,category,ticker,free_qty)
            res = self.common.order_open(market=market, category=category, ticker=ticker, side='sell',
                             orderType='market', price=price, qty=free_qty)
            id = res['id']
            while True:
                dict_chegyeol = self.fetch_order(market=market, ticker=ticker, id=id, category=category, qty=free_qty)
                if dict_chegyeol['체결'] == True:
                    # print(f"{idx} -  'spot',  체결수량:{dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간: {dict_chegyeol['체결시간']}")
                    break

                QTest.qWait(1000)
                if i >10:
                    print(f'{market}  buy_linear 에러 2')
                    quit()

            usdt = dict_chegyeol['체결금액']
            if market == 'binance':
                self.common.transfer_to(market=market,ticker='USDT',amount=usdt,departure='spot',destination='linear')

            qty = (usdt * future_leverage) / price
            category = 'linear'
            qty = self.common.amount_to_precision(market, category, ticker, qty)
            res = self.common.order_open( market=market, category=category, ticker=ticker, side=side,
                             orderType='market', price=price, qty=qty, leverage=future_leverage)
            id = res['id']
            idx = idx+'_'+side #long일경우 'bybit_BTC_long'
            while True:
                # print(f'while {idx}   {qty= }  {id= }')
                dict_chegyeol = self.fetch_order( market=market, ticker=ticker, id=id, category=category, qty=qty)
                if dict_chegyeol['체결'] == True:
                    self.df_closed.loc[id,'ticker'] = ticker
                    self.df_closed.loc[id,'체결시간'] = dict_chegyeol['체결시간']
                    self.df_closed.loc[id,'market'] = market
                    self.df_closed.loc[id,'체결가'] = dict_chegyeol['체결가']
                    self.df_closed.loc[id,'주문가'] = price
                    self.df_closed.loc[id,'수수료'] = dict_chegyeol['수수료']
                    self.df_closed.loc[id,'체결수량'] = dict_chegyeol['체결수량']
                    self.df_closed.loc[id,'상태'] = '체결완료'
                    self.df_closed.loc[id,'category'] = 'linear'
                    self.df_closed.loc[id,'주문수량'] = qty
                    self.df_closed.loc[id,'매수금액'] = round((dict_chegyeol['체결가']*dict_chegyeol['체결수량'])/future_leverage)
                    self.save_df.emit(self.df_closed,'closed')
                    if not idx in self.df_linear.index.tolist(): #기존에 보유수량이 없으면
                        self.df_linear.loc[idx,'market'] = market
                        self.df_linear.loc[idx,'ticker'] = ticker
                        self.df_linear.loc[idx,'category'] = 'linear'
                        self.df_linear.loc[idx,'주문가'] = price
                        self.df_linear.loc[idx,'체결가'] = dict_chegyeol['체결가']
                        self.df_linear.loc[idx,'평단가'] = dict_chegyeol['체결가']
                        self.df_linear.loc[idx,'주문수량'] = qty
                        self.df_linear.loc[idx,'보유수량'] = dict_chegyeol['체결수량']
                        self.df_linear.loc[idx,'매수금액'] = round((dict_chegyeol['체결가']*dict_chegyeol['체결수량'])/future_leverage)
                        self.df_linear.loc[idx,'수수료'] = dict_chegyeol['수수료']
                        self.df_linear.loc[idx,'체결시간'] = dict_chegyeol['체결시간']
                        self.df_linear.loc[idx,'매수횟수'] = 1
                        self.df_linear.loc[idx,'레버리지'] = future_leverage
                        self.df_linear.loc[idx,'방향'] = side
                    else:
                        기존보유수량 = float(self.df_linear.loc[idx,'보유수량'])
                        기존매수금액 = float(self.df_linear.loc[idx,'매수금액'])
                        기존수수료 = float(self.df_linear.loc[idx,'수수료'])
                        기존매수횟수 = float(self.df_linear.loc[idx,'매수횟수'])
                        if 기존보유수량 == None :
                            기존보유수량 = 0
                        if 기존매수금액 == None:
                            기존매수금액 = 0
                        if 기존수수료 == None:
                            기존수수료 = 0
                        if 기존매수횟수 == None:
                            기존매수횟수 = 0
                        self.df_linear.loc[idx,'주문가'] = price
                        self.df_linear.loc[idx,'주문수량'] = qty
                        self.df_linear.loc[idx,'체결가'] = dict_chegyeol['체결가']
                        self.df_linear.loc[idx,'보유수량'] = 기존보유수량+dict_chegyeol['체결수량']
                        self.df_linear.loc[idx,'매수금액'] = round(기존매수금액+(dict_chegyeol['체결가']*dict_chegyeol['체결수량'])/future_leverage)
                        평단가 = self.df_linear.loc[idx,'매수금액']/self.df_linear.loc[idx,'보유수량']
                        평단가 = self.common.price_to_precision(market,'linear',ticker,평단가)
                        self.df_linear.loc[idx,'평단가'] = 평단가
                        self.df_linear.loc[idx,'수수료'] = 기존수수료+dict_chegyeol['수수료']
                        self.df_linear.loc[idx,'체결시간'] = dict_chegyeol['체결시간']
                        self.df_linear.loc[idx,'매수횟수'] = 기존매수횟수+1
                        self.df_linear.loc[idx,'레버리지'] = future_leverage

                    # self.fetch_balance()
                    self.save_df.emit(self.df_linear,'linear')
                    self.qt_linear.emit(self.df_linear)
                    break
                if i >10:
                    print(f'{market}buy_linear 에러 3')
                    quit()
                QTest.qWait(1000)
            dict_txt[id] = {}
            dict_txt[id]['market'] = market
            dict_txt[id]['ticker'] = ticker
            dict_txt[id]['category'] = 'linear'
            dict_txt[id]['체결수량'] = dict_chegyeol['체결수량']
            dict_txt[id]['매수금액'] = self.df_linear.loc[idx,'매수금액']
        else:
            pass
        return dict_txt
    def get_buy_signal(self,df,market,ticker):
        signal = False
        if (df.loc[df.index[-3],'RSI14'] > 30) and (df.loc[df.index[-2],'RSI14'] < 30):
            signal = True
        if (df.loc[df.index[-3],'RSI18'] > 30) and (df.loc[df.index[-2],'RSI18'] < 30):
            signal = True
        if (df.loc[df.index[-3],'RSI30'] > 30) and (df.loc[df.index[-2],'RSI30'] < 30):
            signal = True
        if (df.loc[df.index[-3],'이평9'] < df.loc[df.index[-3],'이평20']) and (df.loc[df.index[-2],'이평9'] > df.loc[df.index[-2],'이평20']):
            signal = True
        if (df.loc[df.index[-2], 'MACD_SIGNAL'] < df.loc[df.index[-2], 'MACD']) and (df.loc[df.index[-3], 'MACD_SIGNAL'] > df.loc[df.index[-3], 'MACD']):
            signal = True
        if (df.loc[df.index[-3],'종가']-df.loc[df.index[-3],'시가'])/df.loc[df.index[-3],'종가']*100 < -3.5:
            if (df.loc[df.index[-2],'종가']-df.loc[df.index[-2],'시가'])/df.loc[df.index[-2],'종가']*100 > -0.8:
                if (df.loc[df.index[-4],'종가']-df.loc[df.index[-4],'시가'])/df.loc[df.index[-4],'종가']*100 < 2.5:
                    signal = True
        if signal == True:
            df_close = self.df_linear[(self.df_linear['market'] == market) & (self.df_linear['ticker'] == ticker) & (
                        self.df_linear['category'] == 'linear')]
            if not df_close.empty:
                df_close['체결시간'] = pd.to_datetime(df_close['체결시간'])
                datetime_list = df_close['체결시간'].tolist()
                latest_datetime = max(datetime_list)
                if latest_datetime+datetime.timedelta(days=1) < datetime.datetime.now():
                    signal = True
                    print('이평신호 ',market,ticker ,df.loc[df.index[-3],'이평9'],df.loc[df.index[-3],'이평20'],df.loc[df.index[-2],'이평9'],df.loc[df.index[-2],'이평20'])
                else:
                    signal = False
            else:
                signal = True
        side = 'long'
        return signal, side

    def sell_future(self,df,idx):
        market = self.df_linear.loc[idx,'market']
        ticker = self.df_linear.loc[idx,'ticker']
        평단가 = self.df_linear.loc[idx,'평단가']
        레버리지 = self.df_linear.loc[idx,'레버리지']

        현재가 = df.loc[df.index[-1],'종가']


        ror = (현재가-평단가)/평단가*레버리지*100

        sell_signal_future, qty, 매수횟수 = self.get_sell_signal(df,idx,ror)
        # sell_signal_future = True
        # market = 'binance'
        # ticker = 'XRP'
        # idx = f"{market}_{ticker}"
        # qty = 5
        # 매수횟수 = 0
        if sell_signal_future == True and qty != 0:
            print('***************************************************************************************************')
            category = 'linear'
            qty = self.common.amount_to_precision(market, category, ticker, qty)
            if qty > self.df_future.loc[idx,'보유수량']:
                qty = self.df_future.loc[idx,'보유수량']
            print(f"sell_future 매도신호 {sell_signal_future} : {idx}, {qty=}, {category=}, {현재가= }   현재시간: {datetime.datetime.now()}  ")

            res = self.common.order_close(market=market, category=category, ticker=ticker, side='sell',
                                                orderType='market', price=현재가, qty=qty)
            id = res['id']
            QTest.qWait(1000)
            i = 0

            while True:
                dict_chegyeol = self.fetch_order(market=market, ticker=ticker, id=id, category=category, qty=qty)

                if dict_chegyeol['체결'] == True:
                    print(f"({market}) {ticker} -  {category=},  체결수량:{dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간: {dict_chegyeol['체결시간']} {dict_chegyeol}")

                    self.df_closed.loc[id, 'ticker'] = ticker
                    self.df_closed.loc[id, '체결시간'] = dict_chegyeol['체결시간']
                    self.df_closed.loc[id, 'market'] = market
                    self.df_closed.loc[id, '체결가'] = dict_chegyeol['체결가']
                    self.df_closed.loc[id, '주문가'] = 현재가
                    self.df_closed.loc[id, '수수료'] = dict_chegyeol['수수료']
                    self.df_closed.loc[id, '체결수량'] = dict_chegyeol['체결수량']
                    self.df_closed.loc[id, '상태'] = '매도완료'
                    self.df_closed.loc[id, 'category'] = 'linear'
                    self.df_closed.loc[id, '주문수량'] = qty
                    self.df_closed.loc[id, 'id'] = id
                    # self.df_closed.loc[id, '매수금액'] = round(
                    #     (dict_chegyeol['체결가'] * dict_chegyeol['체결수량']) / future_leverage)
                    self.save_df.emit(self.df_closed,'closed')

                    기존보유수량 = float(self.df_linear.loc[idx,'보유수량'])
                    기존매수금액 = float(self.df_linear.loc[idx,'매수금액'])
                    기존수수료 = float(self.df_linear.loc[idx,'수수료'])
                    self.df_linear.loc[idx,'매수횟수'] = 매수횟수
                    if self.df_linear.loc[idx,'매수횟수'] == 0:
                        self.df_linear.drop(index=idx,inplace=True)
                    else:
                        self.df_linear.loc[idx,'주문가'] = 현재가
                        self.df_linear.loc[idx,'주문수량'] = qty
                        self.df_linear.loc[idx,'체결가'] = dict_chegyeol['체결가']
                        self.df_linear.loc[idx,'보유수량'] = 기존보유수량 - dict_chegyeol['보유수량']
                        self.df_linear.loc[idx,'매수금액'] = round(기존매수금액 - (dict_chegyeol['체결금액'] / 레버리지))
                        평단가 = self.df_linear.loc[idx,'매수금액'] / self.df_linear.loc[idx,'보유수량']
                        평단가 = self.common.price_to_precision(market, 'linear', ticker, 평단가)
                        self.df_linear.loc[idx,'평단가'] = 평단가
                        self.df_linear.loc[idx,'수수료'] = 기존수수료 + dict_chegyeol['수수료']
                        self.df_linear.loc[idx,'체결시간'] = dict_chegyeol['체결시간']
                    self.qt_linear.emit(self.df_linear)
                    break
                elif i > 10:
                    print(f'{market}sell_future 에러 1')
                    quit()
                QTest.qWait(1000)
                i = i + 1

            usdt = round(dict_chegyeol['체결금액']/ 레버리지)
            rate_spot = float(self.df_set.loc['rate_spot', 'val'])
            if market == 'binance':
                self.common.transfer_to(market=market,ticker='USDT',amount=usdt,departure='linear',destination='spot')

            self.buy_manual(market=market,ticker=ticker,배팅금액=usdt,rate_spot=rate_spot,df_usdt=self.df_inverse)
        else:
            pass
    def get_sell_signal(self,df, idx,ror):
        수익률 = ror
        signal = False
        qty = 0
        매수금액 = self.df_linear.loc[idx,'매수금액']
        매수횟수 = self.df_linear.loc[idx,'매수횟수']

        # 보유수량 = self.df_linear.loc[idx,'보유수량']
        보유수량 = self.df_linear.loc[idx,'보유수량']
        qty = 보유수량
        if 수익률 > 10:
            if (df.loc[df.index[-2], 'MACD_SIGNAL'] > df.loc[df.index[-2], 'MACD']) and (df.loc[df.index[-3], 'MACD_SIGNAL'] < df.loc[df.index[-3], 'MACD']):
                매수횟수 = 0
                signal = 1
        elif 수익률 > 5 and 매수횟수 == 1:
            signal = 2
            qty = qty
            매수횟수 = 0
        elif 수익률 > 5 and 매수횟수 > 5 and df.loc[df.index[-1], 'RSI'] < 30 :
            signal = 3
            qty = qty/2
            매수횟수 = 2
        else:
            qty = 0
            signal = False
        # print(f"{market}_{ticker} | {매수금액= } | {매수횟수= } | {체결수량= } | {signal= }")
        return signal, qty, 매수횟수

    def active_light(self):
        self.val_light.emit(self.bool_light)
        self.bool_light = not self.bool_light
        # self.val_wallet.emit(self.wallet)
        self.val_time.emit(str(self.text_time))
        self.qt_inverse.emit(self.df_inverse)
        self.qt_open.emit(self.df_open)
        self.qt_linear.emit(self.df_linear)
        self.qt_future.emit(self.df_future)


    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.bool_light = False
            self.cond.wakeAll()
        elif not self._status:
            self.bool_light = False
            self.val_light.emit(self.bool_light)


    def fetch_order(self, market, ticker, id, category, qty):
        ord_open = self.common.fetch_open_orders(market, ticker, category, id)
        if ord_open == None:  # 체결일 경우
            ord_closed = self.common.fetch_closed_orders(market, id, ticker, category)  # open 주문과 close 주문 2중으로 확인

            if ord_closed == None:
                return {'체결': '주문취소'}
            else:
                if ord_closed['info'].get('status')=='FILLED' or ord_closed['info'].get('orderStatus')=='Filled': #바이낸스 == 'status', 바이비트 == 'orderStatus'
                    진입가 = float(ord_closed['average'])
                    체결수량 = float(ord_closed['filled'])
                    수수료 = ord_closed.get('fee', 0)
                    if 수수료 == None: #바이낸스
                        수수료 = 0
                    elif type(수수료) :
                        수수료 = 수수료['cost']#바이비트
                    수수료 = float(수수료)

                    # if not ord_closed['fee'] == None:
                    #     # 수수료 = float(ord_closed['fee']['cost'])
                    #     수수료 = float(ord_closed['fee'].get('cost',0))
                    # else:
                    #     수수료 = ord_closed.get('fee',0)
                    체결금액 = float(ord_closed['cost'])
                    체결시간 = self.common.stamp_to_str(ord_closed['timestamp'])
                    # QTest.qWait(1000) # 이거 넣으면 self.df_inverse의 일부 컬럼이 str로 변해서 사용안함
                    if category == 'spot':
                        if market == 'binance': #바이낸스의 경우 현물 구매 시 구매 수량에서 수수료만큼 수량이 빠지는듯
                            res = self.dict_binance['spot'].fetch_balance(params={'type': 'spot'})
                            체결수량 = res[ticker]['free']
                    dict_info = {'체결': True, '체결가': 진입가, '체결수량':체결수량,'체결금액':체결금액, '수수료':수수료,
                                 '체결시간':체결시간, 'id':id,'side':ord_closed.get('side',None)}
                    # print(f"fetch_order_체결완료({market}) : {category= } - {ticker= } | {dict_info} ")
                    # self.fetch_balance()
                    return dict_info
                else:
                    print(f'fetch_order 상태확인 필요  {market= }, {ticker= }, {id= }, {category= }, {qty= }')
                    pprint(ord_closed)
        else:
            return {'체결': False}

    def fetch_balance(self):
        self.df_inverse, self.df_future, assets_binance, assets_bybit = self.common.get_all_assets()


        self.val_wallet.emit(assets_binance, assets_bybit)
        self.qt_inverse.emit(self.df_inverse)
        self.qt_future.emit(self.df_future)


    def get_funding_time(self,now: datetime):
        funding_hours = [1, 9, 17]  # 펀딩비 시간
        today = now.replace(minute=0, second=0, microsecond=0)
        # 현재 시간 이후의 가장 가까운 펀딩비 시간을 찾음
        for hour in funding_hours:
            funding_time = today.replace(hour=hour)
            if funding_time > now:
                return funding_time
        # 오늘 모든 펀딩비 시간이 지났다면 다음 날 첫 번째 펀딩비 시간 반환
        funding_time = today + datetime.timedelta(days=1, hours=funding_hours[0] - today.hour)
        return funding_time



class Window(QMainWindow):
    manual_buy_signal = pyqtSignal(str,str,int,float,pd.DataFrame)
    set_signal = pyqtSignal(pd.DataFrame)

    def __init__(self):
        super().__init__()
        self.init_file()
        self.set_UI()
        self.time_sync()
        QTest.qWait(500)
        self.dict_bybit = self.make_exchange_bybit_ccxt()
        self.dict_binance = self.make_exchange_binance()
        self.qtable_open(self.df_open)
        self.qtable_linear(self.df_linear)
        self.funding_time_old = int(time.time())
        self.QPB_start.clicked.connect(self.onStartButtonClicked)
        self.QPB_stop.clicked.connect(self.onStopButtonClicked)
        self.QPB_chart_bybit.clicked.connect(lambda :self.view_chart('bybit'))
        self.QPB_chart_binance.clicked.connect(lambda :self.view_chart('binance'))
        self.QCB_auto.clicked.connect(self.setting)
        self.QPB_api_save_bybit.clicked.connect(lambda :self.save_api('bybit'))
        self.QPB_api_save_binance.clicked.connect(lambda :self.save_api('binance'))
        self.QPB_manual_buy_bybit.clicked.connect(lambda :self.request_buy('bybit'))
        self.QPB_manual_buy_binance.clicked.connect(lambda :self.request_buy('binance'))
        self.QL_rate_short.textChanged.connect(self.on_text_changed_rate_short)
        self.QL_rate_spot.textChanged.connect(self.on_text_changed_rate_spot)
        self.QCB_off.currentIndexChanged.connect(self.setting)
        if self.QCB_auto.isChecked() == True:
            self.onStartButtonClicked()
            # 메인 윈도우의 시그널을 스레드의 슬롯에 연결

    def set_UI(self):
        QW_main = QWidget()
        self.setWindowTitle(f'Funding Bybit')

        self.QT_trade_inverse = QTableWidget()
        self.QT_trade_future = QTableWidget()
        self.QT_trade_linear = QTableWidget()
        self.QT_trade_open = QTableWidget()
        self.QGL_menu = QGridLayout()
        self.QPB_start = QPushButton('START')
        self.QPB_stop = QPushButton('STOP')
        self.QPB_manual_buy_bybit = QPushButton('BYBIT 현물매수')
        self.QL_manual_ticker = QLineEdit('BTC')
        self.QL_manual_price = QLineEdit('100')
        self.QL_wallet = QLabel()
        self.QL_fee_sum = QLabel()
        self.QL_buy_sum = QLabel()
        self.QL_time = QLabel()
        # self.QL_repeat_per = QLineEdit()
        self.QL_rate_spot = QLineEdit()
        self.QL_rate_short = QLineEdit()
        self.QL_rate_spot.setText(str(self.df_set.loc['rate_spot', 'val']))
        self.QL_rate_short.setText(str(self.df_set.loc['rate_short', 'val']))
        self.QPB_manual_buy_binance = QPushButton('BINANCE 현물매수')
        self.QPB_chart_bybit = QPushButton('펀딩비_바이비트')
        self.QPB_chart_binance = QPushButton('펀딩비_바이낸스')
        self.QCB_auto = QCheckBox('오토스타트')
        if self.df_set.loc['auto_start', 'val'] == 'auto':
            self.QCB_auto.setChecked(True)
        else:
            self.QCB_auto.setChecked(False)
        self.QCB_off = QComboBox()
        self.QCB_off.addItems(['자동꺼짐','loop','1분후','5분후','10분후','30분후','1시간후','설정안함'])
        self.QLE_api_bybit = QLineEdit()
        self.QLE_secret_bybit = QLineEdit()
        self.QPB_api_save_bybit = QPushButton('bybit API 저장')
        self.QLE_api_binance = QLineEdit()
        self.QLE_secret_binance = QLineEdit()
        self.QPB_api_save_binance = QPushButton('binance API 저장')
        self.QCB_chart_duration = QComboBox()
        self.QCB_chart_duration.addItems(['1개월','3개월','6개월','1년','2년','3년'])
        dict_grid = {
            self.QPB_start: self.QPB_stop,
            self.QCB_auto: self.QCB_off,
            QLabel('합계(USD)'):self.QL_wallet,
            QLabel('누적수수료'):self.QL_fee_sum,
            QLabel('누적매수'):self.QL_buy_sum,
            QLabel('펀딩비시간'):self.QL_time,
            # QLabel('재투자비율(%)'):self.QL_repeat_per,
            QLabel('현물주문(%)'):self.QL_rate_spot,
            QLabel('인버스주문(%)'):self.QL_rate_short,
            QLabel('ticker(현물)'):self.QL_manual_ticker,
            QLabel('매수금액'):self.QL_manual_price,
            self.QPB_manual_buy_binance:self.QPB_manual_buy_bybit,
            QLabel('|'):QLabel('|'),
            QLabel('펀딩비율 확인'):self.QCB_chart_duration,
            self.QPB_chart_binance: self.QPB_chart_bybit
        }
        for i, key in enumerate(dict_grid):
            self.QGL_menu.addWidget(key, 0, i)
            self.QGL_menu.addWidget(dict_grid[key], 1, i)

        self.QCB_off.setCurrentText(self.df_set.loc['auto_finish','val'])
        QW_grid = QWidget()
        StyleSheet_Qtextedit = "font: 10pt 나눔고딕; "
        QW_grid.setStyleSheet(StyleSheet_Qtextedit)
        QW_grid.setLayout(self.QGL_menu)
        # QW_grid.setMaximumSize(1980,100)


        QHB_api = QHBoxLayout()
        QHB_api.addWidget(QLabel('[BYBIT] API: '))
        QHB_api.addWidget(self.QLE_api_bybit)
        QHB_api.addWidget(QLabel('SECRET: '))
        QHB_api.addWidget(self.QLE_secret_bybit)
        QHB_api.addWidget(self.QPB_api_save_bybit)
        QHB_api.addWidget(QLabel('[BINANCE] API: '))
        QHB_api.addWidget(self.QLE_api_binance)
        QHB_api.addWidget(QLabel('SECRET: '))
        QHB_api.addWidget(self.QLE_secret_binance)
        QHB_api.addWidget(self.QPB_api_save_binance)

        QVB_main = QVBoxLayout()

        StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 12pt 나눔고딕; "
        self.QT_trade_linear.setStyleSheet(StyleSheet_Qtable)
        self.QT_trade_open.setStyleSheet(StyleSheet_Qtable)
        self.QT_trade_inverse.setStyleSheet(StyleSheet_Qtable)
        self.QT_trade_future.setStyleSheet(StyleSheet_Qtable)
        # self.QPB_start.setStyleSheet("border-style: solid;border-width: 1px;border-color: #0080ff")
        self.QPB_start.setStyleSheet(" background-color: #cccccc;")
        self.QPB_stop.setStyleSheet("background-color: #cccccc;")
        # self.QL_hoga = QTextEdit()

        self.setCentralWidget(QW_main)

        QSV_main = QSplitter(Qt.Vertical)
        QSH_table_up = QSplitter(Qt.Horizontal)
        QSH_table = QSplitter(Qt.Horizontal)
        QSH_history_table = QSplitter(Qt.Horizontal)

        QSH_table.addWidget(self.QT_trade_open)
        QSH_table.addWidget(self.QT_trade_linear)
        QSH_table_up.addWidget(self.QT_trade_inverse)
        QSH_table_up.addWidget(self.QT_trade_future)
        QSV_main.addWidget(QSH_table_up)
        QSV_main.addWidget(QSH_history_table)
        QSV_main.addWidget(QSH_table)
        QSV_main.addWidget(QW_grid)
        QVB_main.addWidget(QSV_main)
        QVB_main.addLayout(QHB_api)
        QW_main.setLayout(QVB_main)
    def save_api(self,market):
        if market == 'bybit':
            if not self.QLE_api_bybit.text() == '':
                self.df_set.loc[f'api_{market}','val']=self.QLE_api_bybit.text()
            if not self.QLE_secret_bybit.text() == '':
                self.df_set.loc[f'secret_{market}','val']=self.QLE_secret_bybit.text()
            self.QLE_api_bybit.clear()
            self.QLE_secret_bybit.clear()
            self.dict_bybit = self.make_exchange_bybit_ccxt()

        if market == 'binance':
            if not self.QLE_api_binance.text() == '':
                self.df_set.loc[f'api_{market}','val']=self.QLE_api_binance.text()
            if not self.QLE_secret_binance.text() == '':
                self.df_set.loc[f'secret_{market}','val']=self.QLE_secret_binance.text()
            self.QLE_api_binance.clear()
            self.QLE_secret_binance.clear()
            self.dict_binance = self.make_exchange_binance()

        self.df_set.to_sql('set', self.conn, if_exists='replace')

    def init_file(self):
        db_file = 'DB/Funding_Strategy.db'
        if not os.path.isfile(db_file): #파일이 없으면
            self.conn = sqlite3.connect(db_file)
            self.df_closed = pd.DataFrame(columns=['market','ticker', 'category', '주문가','체결가', '주문수량',
                                                   '체결수량', '매수금액','수수료', '주문시간', '체결시간',
                                                   'id', '상태'])
            self.df_closed.to_sql('closed', self.conn, if_exists='replace')
            self.df_linear = pd.DataFrame(columns=['market','ticker', 'category', '주문가','체결가','평단가', '주문수량',
                                                   '보유수량', '매수금액', '수수료', '체결시간', '매수횟수','레버리지','방향'],
                                            # dtype={'market':'str','ticker':'str', 'category':'str', '주문가':'float',
                                            #        '체결가':'float','평단가':'float', '주문수량':'float',
                                            #        '보유수량':'float', '매수금액':'float', '수수료':'float', '체결시간':'str',
                                            #        '매수횟수':'float','레버리지':'int'}
                                            )
            self.df_linear.to_sql('linear', self.conn, if_exists='replace')
            self.df_open = pd.DataFrame(columns=['market','ticker', 'category', '주문가', '주문수량', '매수금액',
                                                 '주문시간','id','상태'])
            self.df_open.to_sql('open', self.conn, if_exists='replace')

            self.df_wallet = pd.DataFrame(columns=['binance_USDT','bybit_USDT','total'])
            self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')

            self.df_set = pd.DataFrame(index=['auto_start','auto_finish','start_time','rate_short','rate_spot','funding_time',
                                              'api_bybit','secret_bybit','api_binance','secret_binance'],
                                       columns=['val'])
            self.df_set.loc['auto_start','val'] = 'manual'
            self.df_set.loc['auto_finish','val'] = '설정안함'
            self.df_set.loc['start_time','val'] = ''
            self.df_set.loc['funding_time','val'] = self.get_funding_time(datetime.datetime.now().replace(microsecond=0))
            self.df_set.loc['api_bybit','val'] = None
            self.df_set.loc['secret_bybit','val'] = None
            self.df_set.loc['api_binance','val'] = None
            self.df_set.loc['secret_binance','val'] = None
            self.df_set.to_sql('set', self.conn, if_exists='replace')

        else:
            self.conn = sqlite3.connect(db_file)
            # cursor = self.conn.cursor()
            # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            # list_table = np.concatenate(cursor.fetchall()).tolist()
            self.df_open = pd.read_sql(f"SELECT * FROM 'open'", self.conn).set_index('index')
            self.df_closed = pd.read_sql(f"SELECT * FROM 'closed'", self.conn).set_index('index')
            self.df_linear = pd.read_sql(f"SELECT * FROM 'linear'", self.conn).set_index('index')
            self.df_wallet = pd.DataFrame(columns=['binance_USDT','bybit_USDT','total'])
            self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
            self.df_wallet = pd.read_sql(f"SELECT * FROM 'wallet'", self.conn).set_index('index')


            # self.df_linear['평단가'] = np.nan
            # self.df_linear.to_sql('linear', self.conn, if_exists='replace')
            # self.list_compare_col = self.df_inverse.columns.to_list()
            self.df_set = pd.read_sql(f"SELECT * FROM 'set'", self.conn).set_index('index')
            funding_time = pd.to_datetime(self.df_set.loc['funding_time', 'val'])
            current_t = datetime.datetime.now().replace(microsecond=0)
            if funding_time < current_t:
                self.df_set.loc['funding_time', 'val'] = self.get_funding_time(datetime.datetime.now().replace(microsecond=0))
                self.df_set.to_sql('set', self.conn, if_exists='replace')
        self.df_open_old = self.df_open.copy()
        self.df_linear_old = self.df_linear.copy()


    def on_text_changed_rate_short(self, text):
        if not text == '-':
            if text == '':
                self.df_set.loc['rate_short', 'val'] = text
            else:
                self.df_set.loc['rate_short','val'] = float(text)
            self.df_set.to_sql('set',self.conn,if_exists='replace')
            self.set_signal.emit(self.df_set)

    def on_text_changed_rate_spot(self, text):
        if not text == '-':
            if text == '':
                self.df_set.loc['rate_spot', 'val'] = text
            else:
                self.df_set.loc['rate_spot','val'] = float(text)
            self.df_set.to_sql('set',self.conn,if_exists='replace')
            self.set_signal.emit(self.df_set)

    def setting(self):
        if self.QCB_auto.isChecked() == True:
            self.df_set.loc['auto_start','val'] = "auto"
        else:
            self.df_set.loc['auto_start','val'] = "manual"
        if not self.QCB_off.currentText() == '자동꺼짐':
            self.df_set.loc['auto_finish','val'] = self.QCB_off.currentText()
        self.df_set.to_sql('set', self.conn, if_exists='replace')

    def onStartButtonClicked(self):
        # self.ex_bybit, self.session = self.make_exchange_bybit_ccxt()
        # self.ex_binance,self.ex_binance_future = self.make_exchange_binance()
        # self.defines = common_define(self.ex_bybit, self.session, self.ex_binance)
        # self.defines.time_sync()

        # list_bybit_inverse = self.fetch_inverse_list('bybit')
        # list_binance_inverse = self.fetch_inverse_list_binance()
        if self.dict_bybit['active'] == False and self.dict_binance['active'] == False:
            self.text_message('에러','가능한 API가 없습니다.')
            return
        if self.QL_rate_spot.text() == '' or self.QL_rate_spot.text() == 'None':
            rate_spot = 0
        else:
            rate_spot = float(self.QL_rate_spot.text())
        if self.QL_rate_short.text() == '' or self.QL_rate_short.text() == 'None':
            rate_short = 0
        else:
            rate_short = float(self.QL_rate_short.text())
        start_time = datetime.datetime.now().replace(microsecond=0)
        self.df_set.loc['start_time', 'val'] = start_time
        dict_option = {'현물호가':rate_spot,'인버스호가':rate_short,'start_time':start_time}
        self.thread = do_trade(self,self.dict_bybit,self.dict_binance,self.df_open,self.df_closed,self.df_set,self.df_linear,dict_option)
        self.thread.start()

        self.thread.qt_open.connect(self.qtable_open)
        self.thread.qt_inverse.connect(self.qtable_have)
        self.thread.qt_linear.connect(self.qtable_linear)
        self.thread.qt_future.connect(self.qtable_future)
        # self.thread.save_inverse.connect(self.qtable_inverse)

        self.thread.save_df.connect(self.save_to_sql)
        self.thread.save_set.connect(self.save_set)
        self.thread.val_light.connect(self.effect_start)
        self.thread.val_wallet.connect(self.wallet)
        self.thread.val_time.connect(self.QL_time.setText)
        self.thread.shutdown_signal.connect(self.show_shutdown_dialog)

        self.set_signal.connect(self.thread.change_set)
        self.manual_buy_signal.connect(self.thread.buy_manual)

    @pyqtSlot()
    def onStopButtonClicked(self):
        self.thread.toggle_status()
        # self.pb.setText({True: "Pause", False: "Resume"}[self.th.status])
        self.QPB_start.setStyleSheet("background-color: #cccccc;")
        # self.timer.stop()

    def effect_start(self, light):
        if light == True:
            self.QPB_start.setStyleSheet("background-color: #fa3232;")
        if light == False:
            self.QPB_start.setStyleSheet("background-color: #cccccc;")

    def request_buy(self,market):
        # 스레드로 buy 신호 발생
        ticker = self.QL_manual_ticker.text()
        배팅금액 = int(self.QL_manual_price.text())
        rate_spot = float(self.QL_rate_spot.text())
        self.manual_buy_signal.emit(market,ticker,배팅금액,rate_spot,self.df_qtable_have)

    def save_set(self,df):
        df.to_sql('set',self.conn,if_exists='replace')

    def qtable_have(self,df):
        if not df.empty:
            # df['free(qty)'] = df['free(qty)'].apply(lambda int_num: "{:,}".format(int_num))
            # df['현재가'] = df['현재가'].apply(lambda int_num: "{:,}".format(int_num))
            # df['합계(USD)'] = df['합계(USD)'].apply(lambda int_num: "{:,}".format(int_num))
            # df['배팅가능합계(USD)'] = df['배팅가능합계(USD)'].apply(lambda int_num: "{:,}".format(int_num))
            df = df[['market', 'ticker','합계(USD)', 'free(qty)', 'used(qty)', 'total(qty)', '현재가', '배팅가능합계(USD)', '주문최소금액(USD)']]
            self.set_table_make(self.QT_trade_inverse, df)
            self.df_qtable_have = df.copy()

    def qtable_future(self,df):
        if not df.empty:
            df = df[['market','ticker','매수금액','진입수량','수익률','수익금', '진입가','현재가', '방향','레버리지','청산가']]
            self.set_table_make(self.QT_trade_future, df)
        else:
            self.set_table_make(self.QT_trade_future, pd.DataFrame())

    def qtable_open(self,df):
        df_compare = df[['상태','id']]
        if not self.df_open_old.equals(df_compare):
            df.to_sql('open',self.conn,if_exists='replace')
            self.df_open_old = df_compare.copy()
        df_active = df[['market','ticker', '주문시간', '주문수량', '매수금액', '주문가', '상태', 'category', 'id']]
        if not df_active['매수금액'].isna().any():
            df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_open, df_active)

    def qtable_linear(self,df):
        # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를
        # 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위아래로 붙임
        if not df.empty:
            df = df[['market', 'ticker', '수익률','수익금','매수금액','현재가','평단가','매수횟수','보유수량','방향','category', '주문가', '체결가',  '주문수량',   '수수료', '체결시간',  '레버리지',    ]]
            self.set_table_make(self.QT_trade_linear, df)
        else:
            self.set_table_make(self.QT_trade_linear, pd.DataFrame())

    def save_to_sql(self, df, table):
        df.to_sql(table, self.conn, if_exists='replace')
    def wallet(self,asset_binance,asset_bybit):
        total = asset_binance+asset_bybit
        self.QL_wallet.setText(f"binance: {asset_binance} / bybit: {asset_bybit} / total: {total}")
        now = datetime.datetime.now().replace(second=0,microsecond=0)
        data = {'binance_USDT':asset_binance,
                'bybit_USDT': asset_bybit,
                'total':total}
        df = pd.DataFrame(data,index=[now])
        if not self.df_wallet.empty:
            self.df_wallet = pd.concat([self.df_wallet,df],axis=0)
        self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
    def set_table_make(self, table,df):
        table.setSortingEnabled(False)
        table.clear()
        table.setRowCount(len(df.index))
        table.setColumnCount(len(df.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절
        for i in range(len(df.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(df.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        table.verticalHeader().setVisible(False) #인덱스 삭제
        for row in range(len(df.index)):
            for column in range(len(df.columns)):
                val = df.iloc[row, column]
                if type(val) != str and type(val) != float and type(val) != int and val != None:
                    val = val.item()  # numpy.float 을 float으로 변환
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        table.horizontalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가
    def text_message(self,title,message):
        QMessageBox.about(self,title,message)

    def view_chart(self,market):
        dict_duration = {'1주일':7,'1개월': 30, '2개월': 60,'3개월': 90, '6개월': 180, '1년': 365, '2년': 365 * 2, '3년': 365 * 3}
        self.defi = common_define(self.dict_bybit,self.dict_binance)
        list_inverse = self.defi.fetch_inverse_list(market)
        df_funding = pd.DataFrame()
        since = datetime.datetime.now() - datetime.timedelta(days=dict_duration[self.QCB_chart_duration.currentText()])
        since = self.defi.datetime_to_stamp(since) * 1000  # 밀리초 곱하기
        df = self.defi.fetch_funding_rates(market=market, ticker='BTC', since=False)
        df.index = df.index // 1000
        btc_date_end = df.index[-1] #최근 일
        list_out = []
        for i, ticker in enumerate(list_inverse):
            df = self.defi.fetch_funding_rates(market=market, ticker=ticker, since=since)
            df.index = df.index // 1000
            print(df)  # print를 안하면 데이터에 Nan 이 섞여서 출력됨
            # 중복 인덱스가 있는지 확인
            print(f"{ticker}: df_funding 중복 인덱스:", df_funding.index.duplicated().any())
            print(f"df 중복 인덱스:", df.index.duplicated().any())

            # 중복 제거 후 결합
            df_funding = df_funding[~df_funding.index.duplicated(keep='first')]
            df = df[~df.index.duplicated(keep='first')]
            if df.index[-1] == btc_date_end:
                if not df_funding.empty:
                    if df_funding.index[0] < df.index[0]:
                        df_funding = pd.concat([df_funding, df], axis=1)
                    else:
                        df_funding = pd.concat([df, df_funding], axis=1)
                else:
                    df_funding = df
            # else:
            #     list_out.append(ticker)
        df_funding = df_funding.sort_index() # 시간순 정렬
        df_funding = df_funding.fillna(0) # nan 값 0으로 변환
        df_funding = df_funding[df_funding.index >= (since//1000)] #데이터프레임은 밀리초가 아니기때문에 /1000
        df_funding['날짜'] = pd.to_datetime(df_funding.index, utc=True, unit='s')
        df_funding['날짜'] = df_funding['날짜'].dt.tz_convert("Asia/Seoul")
        df_funding['날짜'] = df_funding['날짜'].dt.tz_localize(None)
        df_funding.set_index('날짜', inplace=True)
        has_duplicates = df.index.duplicated().any()
        if has_duplicates:
            print(f"중복 인덱스 존재 여부: {has_duplicates}")
            duplicate_indices = df.index[df.index.duplicated()].unique()
            print("중복된 인덱스들:")
            print(duplicate_indices)
        else:
            df_funding.to_sql('funding_rate', self.conn, if_exists='replace')
            df_ma = pd.DataFrame()
            df_ma['단순평균'] = df_funding.mean()
            df_ma = df_ma.sort_values('단순평균', ascending=False)
            print(df_ma)
            # print(f"{list_out= }")
            ema_values = {}
            for col in df_funding.columns.tolist():
                ema_values[col] = df_funding[col].ewm(span=(len(df_funding)/2), adjust=False).mean().iloc[-1]
            # 비숫자 열에 대해서는 '지수이동평균' 라벨 추가
            for col in df_funding.columns:
                if col not in df_funding.columns.tolist():
                    ema_values[col] = '지수이동평균'
            # 한 줄로 EMA 행 추가
            # df_funding.loc['지수이동평균'] = ema_values
            df_ema = pd.DataFrame(ema_values, index=['지수이동평균'])
            df_ema = df_ema.transpose()
            df_ema = df_ema.sort_values('지수이동평균', ascending=False)
            print(df_ema)
            df = pd.concat([df_ma,df_ema],axis=1)
            df['result']=(df['단순평균']+df['지수이동평균'])/2
            df = df.sort_values('result', ascending=False)
            print(df)
            list_ema10 = df_ema.head(10).index.tolist()
            list_ma10 = df_ma.head(10).index.tolist()
            list_cross = list(set(list_ema10) & set(list_ma10)) # ema 와 ma의 상위 10개 ticker의 교집합
            print(f"ema 와 ma의 상위 10개 ticker의 교집합 = {list_cross}")
            coin_lists = [list_ema10, list_ma10, list_cross]
            titles = ['지수이동평균', '단순평균', '지수이동평균&단순평균_교차']
            self.plot_funding_rates(df_funding,coin_lists,titles)

    def make_exchange_bybit_ccxt(self):
        api = self.df_set.loc['api_bybit','val']
        secret = self.df_set.loc['secret_bybit','val']
        if api == None or secret == None:
                # or np.isnan(api) or np.isnan(secret)):
            print('bybit API 확인 필요')
            bybit = None
            session = None
            active = False
        else:
            try:
                bybit = ccxt.bybit(config={
                    'apiKey': api,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'position_mode': True, },
                })
                bybit.load_markets()

                session = HTTP(
                    testnet=False,
                    api_key=api,
                    api_secret=secret,
                )
                active = True
            except:
                bybit = None
                session = None
                active = False
                print("바이비트 API 연결 에러")
                self.text_message('에러', "바이비트 API 연결에 문제가 있습니다. \n api가 유효한지 ip주소가 등록되어있는지 \n"
                                        "현재 시간이 동기화 되었는지 확인해주세요")

        return {'active':active,'exchange':bybit, 'session':session}

    def make_exchange_binance(self):
        api = self.df_set.loc['api_binance', 'val']
        secret = self.df_set.loc['secret_binance', 'val']
        if api == None or secret == None:
            # or np.isnan(api) or np.isnan(secret):
            print('binance API 확인 필요')
            spot = None
            linear = None
            coinm = None
            active = False
        else:
            spot = ccxt.binance(config={
                'apiKey': api,
                'secret': secret,
                'enableRateLimit': True,
                'options': {'position_mode': True, },})
            linear = ccxt.binance(config={
                'apiKey': api,
                'secret': secret,
                'enableRateLimit': True,
                'options': {
                    # 'position_mode': True,  #롱 & 숏을 동시에 유지하면서 리스크 관리(헷징)할 때
                    'defaultType': 'future'},})
            coinm = ccxt.binance({
                'apiKey': api,
                'secret': secret,
                #                 'sandbox': sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'delivery'  # COIN-M Futures
                }})
            active = True
            try:
                spot.load_markets()
            # except ccxt.base.errors.AuthenticationError as e:
            except:
                print("바이낸스 API 연결 에러",
                      '''binance {"code":-2015,"msg":"Invalid API-key, IP, or permissions for action."}''')
                self.text_message('에러',"바이낸스 API 연결에 문제가 있습니다. \n"
                                       "api가 유효한지 ip주소가 등록되어있는지 \n"
                                        "현재 시간이 동기화 되었는지 확인해주세요")

        return {'active':active, 'spot':spot, 'linear':linear,'coinm':coinm}

    def get_funding_time(self,now: datetime):
        funding_hours = [1, 9, 17]  # 펀딩비 시간
        today = now.replace(minute=0, second=0, microsecond=0)
        # 현재 시간 이후의 가장 가까운 펀딩비 시간을 찾음
        for hour in funding_hours:
            funding_time = today.replace(hour=hour)
            if funding_time > now:
                return funding_time
        # 오늘 모든 펀딩비 시간이 지났다면 다음 날 첫 번째 펀딩비 시간 반환
        funding_time = today + datetime.timedelta(days=1, hours=funding_hours[0] - today.hour)
        return funding_time

    def show_shutdown_dialog(self):
        self.onStopButtonClicked()
        print('프로그램 종료')
        self.close() #프로그램 종료
        # 종료 알람 다이얼로그 표시
        self.shutdown_dialog = ShutdownDialog()
        self.shutdown_dialog.exec_()

        # 다이얼로그가 닫힌 후 버튼 상태 복원
        # self.start_button.setEnabled(True)
        # self.start_button.setText('시작')


    def time_sync(self):
        print(datetime.datetime.now())
        subprocess.Popen('python timesync.py')
    def convert_column_types(self,df): #데이터프레임 중 숫자로 바꿀 수 있는데이터는 숫자로 변환
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='raise')
            except ValueError:
                pass
        return df

    def plot_funding_rates(self, df, coin_lists, titles):
        # 한글 폰트 설정 - 맑은고딕
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

        # 3개 서브플롯 생성 (1행 3열)
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle('암호화폐 펀딩비 분석', fontsize=16,)

        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

        for i, (coin_list, title) in enumerate(zip(coin_lists, titles)):
            ax = axes[i]

            # 해당 리스트의 티커들이 데이터프레임에 있는지 확인하고 필터링
            available_coins = [coin for coin in coin_list if coin in df.columns]

            if not available_coins:
                ax.text(0.5, 0.5, f'데이터 없음\n({title})',
                        ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(title)
                continue

            # 데이터 추출 및 플롯
            subset_df = df[available_coins].dropna(how='all')

            for j, coin in enumerate(available_coins):
                if coin in subset_df.columns:
                    # NaN이 아닌 데이터만 플롯
                    valid_data = subset_df[coin].dropna()
                    if not valid_data.empty:
                        ax.plot(valid_data.index, valid_data.values,
                                label=coin, color=colors[j % len(colors)],
                                linewidth=1.5, alpha=0.8)

            # 그래프 설정
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('날짜', fontsize=12)
            ax.set_ylabel('펀딩비 (%)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            # x축 날짜 포맷 설정
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            # y축에 0선 강조
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)

        plt.tight_layout()
        plt.show()

class common_define():
    def __init__(self,dict_bybit, dict_binance):
        self.dict_bybit = dict_bybit
        self.dict_binance = dict_binance
        self.ex_bybit = dict_bybit['exchange']
        self.session = dict_bybit['session']
        self.ex_binance = dict_binance['spot']
        self.ex_binance_future = dict_binance['linear']
        self.ex_binance_coinm = dict_binance['coinm']
    def fetch_load_market(self,market):
        if market == 'bybit':
            return self.dict_bybit['exchange'].load_markets()
        elif market == 'binance':
            return self.dict_binance['spot'].load_markets()
    def fetch_tickers(self,market):
        if market == 'bybit':
            return self.dict_bybit['exchange'].fetch_tickers()
        elif market == 'binance':
            return self.dict_binance['spot'].fetch_tickers()
    def fetch_ticker(self,market, ticker):
        if market == 'bybit':
            return self.dict_bybit['exchange'].fetch_ticker(ticker)
            # return self.session.get_tickers(
            #     category=Account,
            #     symbol=ticker,
            # )['result']['list'][0]
        elif market == 'binance':
            return self.dict_binance['spot'].fetch_ticker(ticker)
    def fetch_account_info_bybit(self, Account, symbol):
        return self.session.get_instruments_info(
            category=Account,  # spot, linear, inverse, option
            symbol=symbol, # BTC, BTCUSDT, BTCUSD
        )['result']['list'][0]

    def order_open(self, market, category, ticker, side, orderType, price, qty, leverage=1,df=pd.DataFrame()):
        #마지막에 데이터프레임은 오류났을 때 확인용
        if market == 'bybit':
            if category == 'spot':
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'/USDT'
                leverage = 1
            elif category == 'inverse':
                params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'USD'
                leverage = 1
            elif category == 'linear':
                symbol = ticker + 'USDT'
                if side == 'long':
                    side = 'buy'
                    params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                elif side == 'short':  # 지정가 open short
                    side = 'sell'
                    params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            try:
                self.dict_bybit['exchange'].set_leverage(leverage=leverage, symbol=symbol)
            except:
                pass
            # except Exception as e:
            #     print(f"주문 중 오류 발생 [order_open]: {e} ")
            #     print(f"{market=}, {category=}, {ticker=}, {side=}, {orderType=}, {price=}, {qty=}, {leverage=}")
            try:
                res = self.dict_bybit['exchange'].create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                                 price=price, params=params)
            except Exception as e:
                print(f"**에러** [order_open]: {e} \n {ticker= } {symbol= }  {orderType= }  {side= }  {qty= }  {price= }  {params= }")
                print('=====================')
                print(df)
                print('=====================')
                res = self.dict_bybit['exchange'].create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                                 price=price, params=params)
                raise
        elif market == 'binance':
            if category == 'spot':
                params = {}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'/USDT'
                leverage = 1
            elif category == 'inverse':
                params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'USD_PERP'
                leverage = 1
            elif category == 'linear':
                symbol = ticker + 'USDT'
                if side == 'long':
                    side ='buy'
                    params = {'positionSide': 'LONG'}
                    pass
                elif side == 'short':  # 지정가 open short
                    params = {'positionSide': 'SHORT'}
                    side = 'sell'
                    pass
            try:
                if category == 'spot' or category == 'inverse':
                    self.ex_binance.set_leverage(leverage=leverage, symbol=symbol)
                elif category == 'linear':
                    self.ex_binance_future.set_leverage(leverage=leverage, symbol=f'{ticker}/USDT')
            except:
                pass
            try:
                if category == 'spot' or category == 'inverse':
                    self.ex_binance.set_margin_mode('isolated', f'{ticker}/USDT')
                elif category == 'linear':
                    self.ex_binance_future.set_margin_mode('isolated', f'{ticker}/USDT')
            except:
                pass
            try:
                if category == 'spot' or category == 'inverse':
                    res = self.ex_binance.create_order(symbol=symbol, type=orderType, side=side, amount=qty, price=price, params=params)
                elif category == 'linear':
                    res = self.ex_binance_future.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                             price=price, params=params)
            except ccxt.base.errors.InsufficientFunds as e:
                print(f"[order_open] 에러 {e} {market=}  {category=}  {symbol=}  {orderType=}  {side=}  {qty=}  {price=}  {params=}  ")
                res = self.ex_binance.fetch_balance()
                print(f"{res[ticker]['free']= }")

            except:
                print(f"[order_open] 에러 {market=}  {category=}  {symbol=}  {orderType=}  {side=}  {qty=}  {price=}  {params=}  ")

                if category == 'spot' or category == 'inverse':
                    res = self.ex_binance.create_order(symbol=symbol, type=orderType, side=side, amount=qty, price=price, params=params)
                elif category == 'linear':
                    res = self.ex_binance_future.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                             price=price, params=params)
                pass

        QTest.qWait(1000)
        # print(f"주문[order_open] - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} {market=}, {category=}, "
        #       f"{ticker=}, {side=}, {orderType=}, {price=}, {qty=}, {leverage=}, id={res['id']}")
        return res
    def order_close(self, market, category, ticker, side, orderType, price, qty):
        if market == 'bybit':
            if category == 'spot':
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'/USDT'
                leverage = 1
            elif category == 'inverse':
                params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'USD'
                leverage = 1
            elif category == 'linear':
                symbol = ticker + 'USDT'
                if side == 'short':  # 지정가 close short
                    side = 'buy'
                    params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                elif side == 'long':  # 지정가 close long
                    side = 'sell'
                    params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            res = self.dict_bybit['exchange'].create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                             price=price, params=params)
        elif market == 'binance':
            if category == 'spot':
                params = {}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'/USDT'
                leverage = 1
            elif category == 'inverse':
                params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'USD_PERP'
                leverage = 1
            elif category == 'linear':
                symbol = ticker + 'USDT'
                if side == 'long':
                    params = {'positionSide': 'LONG'}
                    pass
                elif side == 'short':  # 지정가 open short
                    params = {'positionSide': 'SHORT'}
                    pass
            try:
                if category == 'spot' or category == 'inverse':
                    self.ex_binance.set_leverage(leverage=leverage, symbol=symbol)
                elif category == 'linear':
                    self.ex_binance_future.set_leverage(leverage=leverage, symbol=f'{ticker}/USDT')
            except:
                pass
            try:
                if category == 'spot' or category == 'inverse':
                    self.ex_binance.set_margin_mode('isolated', f'{ticker}/USDT')
                elif category == 'linear':
                    self.ex_binance_future.set_margin_mode('isolated', f'{ticker}/USDT')

            except:
                pass
            if category == 'spot' or category == 'inverse':
                res = self.ex_binance.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                             price=price, params=params)
            elif category == 'linear':
                res = self.ex_binance_future.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                             price=price, params=params)

        QTest.qWait(1000)
        print('=======================================================================================================')
        print(f"주문[order_close] - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} {market=}, {category=}, "
              f"{ticker=}, {side=}, {orderType=}, {price=}, {qty=}, id={res['id']}")
        return res
    def order_cancel(self, market, category, ticker, order_id):
        if market == 'bybit':
            if category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'spot':
                symbol = ticker + 'USDT'
            self.session.cancel_order(category=category, symbol=symbol, orderId=order_id)
            QTest.qWait(1000)
        elif market == 'binance':
            if category == 'inverse':
                symbol = ticker + 'USD_PERP'
            elif category == 'spot':
                symbol = ticker + '/USDT'
            self.dict_binance['spot'].cancel_order(id=order_id,symbol=symbol,params={})
    def fetch_open_orders(self,market,ticker,category,id):  # 미체결주문 조회
        # try:
        params = {}
        if market == 'bybit':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'linear':
                symbol = ticker + 'USDT'
            params = {}
            res = self.dict_bybit['exchange'].fetch_open_orders(symbol=symbol, params=params)
        elif market == 'binance':
            if category == 'spot':
                symbol = ticker + '/USDT'
                res = self.dict_binance['spot'].fetch_open_orders(symbol=symbol, params=params)
            elif category == 'inverse':
                symbol = ticker + '/USD'
                res = self.dict_binance['coinm'].fetch_open_orders(symbol=symbol, params=params)
            elif category == 'linear':
                symbol = ticker+'/USDT:USDT'
                res = self.dict_binance['linear'].fetch_open_orders(symbol=symbol, params=params)
        for order in res:
            if order['id'] == id:
                return order

    def fetch_closed_orders(self,market, id, ticker, category):  # 체결주문 조회
        params = {}
        if market == 'bybit':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'linear':
                symbol = ticker + 'USDT'
            res = self.dict_bybit['exchange'].fetch_closed_orders(symbol=symbol, params=params)
        if market == 'binance':
            if category == 'spot':
                symbol = ticker + '/USDT'
                res = self.dict_binance['spot'].fetch_closed_orders(symbol=symbol, params=params)
            elif category == 'inverse':
                symbol = ticker + '/USD'
                res = self.dict_binance['coinm'].fetch_closed_orders(symbol=symbol, params=params)
            elif category == 'linear':
                symbol = ticker+'/USDT:USDT'
                res = self.dict_binance['linear'].fetch_closed_orders(symbol=symbol, params=params)
        for order in res:
            if order['id'] == id:
                return order

    def fetch_cancel_orders(self,market, id, ticker, category):  # 체결주문 조회
        params = {}
        if market == 'bybit':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'linear':
                symbol = ticker + 'USDT'
            # order = self.dict_bybit['exchange'].fetch_closed_orders(self.ticker, params=params)
            res = self.dict_bybit['exchange'].fetch_canceled_orders(symbol=symbol, params=params)
        if market == 'binance':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + '/USD'
            elif category == 'linear':
                symbol = ticker
            res = self.dict_binance['spot'].fetch_canceled_orders(symbol=symbol, params=params)
        for order in res:
            if order['id'] == id:
                return order
    def stamp_to_datetime(self,stamp_time):
        if len(str(int(stamp_time))) == 13:
            stamp_time = stamp_time / 1000 #밀리초단위일 경우
        int_time = self.stamp_to_int(stamp_time)
        return datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')

    def stamp_to_int(self,stamp_time):
        dt = datetime.datetime.fromtimestamp(stamp_time)
        dt = dt.strftime('%Y%m%d%H%M')
        return int(dt)

    def stamp_to_str(self,t):
        date_time = self.stamp_to_datetime(t)
        return datetime.datetime.strftime(date_time, "%Y-%m-%d %H:%M")
    def datetime_to_stamp(self, date_time):
        return int(time.mktime(date_time.timetuple()))
    def amount_to_precision(self,market, category, ticker, amount):
        if market == 'bybit':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'linear':
                symbol = ticker + 'USDT'
            return float(self.dict_bybit['exchange'].amount_to_precision(symbol=symbol,amount=amount))
        elif market == 'binance':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'linear':
                symbol = ticker + 'USDT'
            return float(self.dict_binance['spot'].amount_to_precision(symbol=symbol, amount=amount))
        # res = self.fetch_account_info_bybit(Account=category,symbol=ticker)
        # qty_min = res['lotSizeFilter']['basePrecision'].index('1')-1
        # qty = round(amount,qty_min)
        # if qty < float(res['lotSizeFilter']['minOrderQty']):
        #     print(f"최소주문수량 미만 (최소주문수량: {res['lotSizeFilter']['minOrderQty']}, > 주문수량: {qty}")
        #     raise
        # return qty
    def price_to_precision(self, market, category, ticker, price):
        if market == 'bybit':
            if category == 'spot':
                symbol = ticker + 'USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            elif category == 'linear':
                symbol = ticker + 'USDT'
            try:
                return float(self.dict_bybit['exchange'].price_to_precision(symbol=symbol, price=price))
            except:
                print(f"[price_to_precision] {market= }, {category= }, {ticker= }, {price= }, {symbol= }  {price= }")
                return float(self.dict_bybit['exchange'].price_to_precision(symbol=symbol, price=price))
        elif market == 'binance':
            if category == 'spot':
                symbol = ticker+'/USDT'
                return float(self.dict_binance['spot'].price_to_precision(symbol=symbol,price=price))
            elif category == 'inverse':
                symbol = ticker+'/USD'
                return float(self.dict_binance['coinm'].price_to_precision(symbol=symbol,price=price))
            elif category == 'linear':
                symbol = ticker + 'USDT'
                return float(self.dict_binance['linear'].price_to_precision(symbol=symbol,price=price))
        else:
            print('[price_to_precision] market 확인 필요')
            return 0
        # if category == 'spot':
        #     res = self.fetch_account_info_bybit(Account=category,symbol=ticker)
        #     price_min = res['priceFilter']['tickSize'].index('1')-1
        #     return round(price,price_min)
        # elif category == 'inverse':
        #     res = self.fetch_account_info_bybit(Account=category,symbol=ticker)
        #     price_step = res['priceFilter']['tickSize']
        #     point = price_step.index('.')
        #     price = round(price, point)
        #     j = round(price % float(price_step), point)
        #     return price-j
    def transfer_to(self,market, ticker, amount ,departure , destination):
        if market == 'bybit':
            while True:
                id = str(uuid.uuid1())
                print(f"{id= }")
                res = self.session.create_internal_transfer(
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
            try:
                self.dict_binance['spot'].transfer(ticker, amount, departure, destination)
            except Exception as e:
                print(f"자금 이동 중 오류 발생 [transfer_to]: {e} {ticker= } {amount= }, 출: {departure}, 착: {destination}")
                #     return False
    def transfer_to_linear_wallet(self,market, currency, amount):
        if market == 'bybit':
            return False
            # while True:
                # id = str(uuid.uuid1())
                # print(id)
                # res = self.session.create_internal_transfer(
                #     transferId=id,
                #     coin=currency,  # BTC
                #     amount=amount,
                #     fromAccountType="UNIFIED",  # UNIFIED (spot 계좌)
                #     toAccountType="CONTRACT",  # CONTRACT (inverse 계좌)
                # )
                #
                # if res['retMsg'] == 'success':
                #     print(f'{currency}  {amount} 개  inverse로 계좌이동 완료')
                #     break
                # print(f'{currency} 계좌 이동중...')
                # QTest.qWait(1000)
                # return
        elif market == 'binance':
            try:
                # BUSD를 Coin-M Futures 지갑으로 이동
                params = {
                    'asset': 'USDT',  # 전송할 자산
                    'amount': amount,  # 전송할 금액
                    'type': 1  # 1: 현물 → USDT-M 선물 계정, 2: USDT-M 선물 → 현물 계정
                }
                transfer = self.dict_binance['spot'].sapi_post_futures_transfer(params)
                print(f"✅ {amount} USDT를 선물 계정으로 전송 완료!", transfer)
                time.sleep(2)  # 이동 완료를 위한 대기
                return True
            except Exception as e:
                print(f"자금 이동 중 오류 발생[transfer_to_linear_wallet]: {e} {currency= } {amount= } ")
                return False
        else:
            return False
    def fetch_funding_rates(self,market,ticker,since):
        if market == 'bybit':
            symbol = ticker + 'USD'
            out_lately = self.dict_bybit['exchange'].fetch_funding_rate_history(symbol=symbol, since=None)
            from_time = (out_lately[0]['timestamp'] // 1000) * 1000
            while from_time > since:
                from_time = from_time - (8 * 3600 * 1000 * 201 ) # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
                out = self.dict_bybit['exchange'].fetch_funding_rate_history(symbol=symbol, since=from_time)
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
            df.set_index('날짜', inplace=True)

        elif market == 'binance':
            symbol = ticker + 'USD_PERP'
            out_lately = self.dict_binance['spot'].fetch_funding_rate_history(symbol=symbol, since=None, params={'type':'delivery'})
            from_time = (out_lately[0]['timestamp'] // 1000) * 1000
            start_time = (out_lately[0]['timestamp'] // 1000) * 1000
            while start_time > since:
                out = self.dict_binance['spot'].fetch_funding_rate_history(symbol=symbol, since=from_time, params={'type':'delivery'})
                if not out:
                    break
                elif from_time < (out[0]['timestamp'] // 1000) * 1000:
                    lately_time = (out_lately[0]['timestamp'] // 1000) * 1000
                    out = [x for x in out if x['timestamp'] < lately_time]
                    out.extend(out_lately)
                    out_lately = out
                    break
                else:
                    start_time = (out[0]['timestamp'] // 1000) * 1000
                    from_time = start_time - ( 8 * 3600 * 1000 * (len(out_lately)))  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
                    out.extend(out_lately)
                    out_lately = out
            data = [x['fundingRate'] for x in out_lately]
            timestamps = [x['timestamp'] for x in out_lately]
            df = pd.DataFrame({
                f'{ticker}': data,
                '날짜': timestamps
            })
            df.set_index('날짜', inplace=True)
        return df

    def convert_df(self,ticker, df):
        df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
        df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
        df['이평9'] = talib.MA(df['종가'], 9)
        df['이평20'] = talib.MA(df['종가'], 20)
        df['이평60'] = talib.MA(df['종가'], 60)
        df['이평120'] = talib.MA(df['종가'], 120)
        df['이평240'] = talib.MA(df['종가'], 200)
        df['거래량이평3'] = talib.MA(df['거래량'], 3)
        df['거래량이평20'] = talib.MA(df['거래량'], 20)
        df['거래량이평60'] = talib.MA(df['거래량'], 60)
        df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(df['종가'], fastperiod=12, slowperiod=26,
                                                                    signalperiod=9)
        df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
        df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
        df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
        df['ATR'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
        df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
        df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
        df['이격도60이평'] = df['종가'].shift(1) / df['이평60'].shift(1) * 100
        df['밴드상'], df['밴드중'], df['밴드하'] = talib.BBANDS(df['종가'].shift(1), 20, 2)
        df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
        df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
        return df
    def get_df(self,market,ticker,bong,since_day):
        dict_bong_stamp = {'1분봉': 1 * 60, '3분봉': 3 * 60, '5분봉': 5 * 60, '15분봉': 15 * 60, '30분봉': 30 * 60,
                           '60분봉': 60 * 60, '4시간봉': 240 * 60, '일봉': 1440 * 60,
                           '주봉': 10080 * 60}
        present = datetime.datetime.now()
        date_old = present.date() - datetime.timedelta(days=int(since_day))
        stamp_date_old = self.datetime_to_stamp(date_old)
        i = 0
        ohlcv = []
        while True:
            try:
                if market == 'bybit':
                    dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉': '4h',
                                 '일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
                    list_ohlcv = self.dict_bybit['exchange'].fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong],
                                                   limit=10000, since=int(stamp_date_old * 1000))  # 밀리초로 전달
                if market == 'binance':
                    dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉': '4h',
                                 '일봉': '1d', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
                    list_ohlcv = self.dict_binance['linear'].fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong],
                                                   limit=10000, since=int(stamp_date_old * 1000))  # 밀리초로 전달
                ohlcv = ohlcv + list_ohlcv
                stamp_date_old = list_ohlcv[-1][0] / 1000 + dict_bong_stamp[bong]  # 다음봉 시간 계산
                if stamp_date_old > time.time():
                    break
            except:
                time.sleep(1)
                i += 1
                if i > 9:
                    print(f'{market} {ticker=}, {bong=}, {i}회 이상 fetch_ohlcv 조회 에러')
                    break
        df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
        df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
        df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
        df['날짜'] = df['날짜'].dt.tz_localize(None)
        df.set_index('날짜', inplace=True)
        df = self.convert_df(ticker,df)
        # df.index = df.index - pd.Timedelta(hours=9)
        return df
    def fetch_inverse_list(self,market):
        if market == 'bybit':
            # 바이비트 inverse 종목 정리
            list_bybit_inverse = []
            if not self.dict_bybit['active'] == None:
                markets = self.dict_bybit['exchange'].load_markets()
                # inverse 종목만 필터링
                inverse_markets = {}
                for symbol, market in markets.items():
                    if market.get('inverse') == True:
                        inverse_markets[symbol] = market
                # inverse 종목 목록 출력
                for symbol in inverse_markets:
                    list_bybit_inverse.append(symbol[:symbol.index('/')])
            else:
                list_bybit_inverse = []
            list_inverse = list(set(list_bybit_inverse))
        elif market == 'binance':
            # res = self.ex_binance.fetch_balance(params={"type": 'delivery'})
            markets = self.dict_binance['spot'].load_markets()
            # Coin-M Perpetual 종목만 필터링
            perpetual_symbols = []
            for symbol, identity in markets.items():
                if identity['type'] == 'swap' and identity['settle'] != 'USDT' and identity['quote'] == 'USD':
                    perpetual_symbols.append({
                        'symbol': symbol,
                        'base': identity['base'],
                        'quote': identity['quote'],
                        'settle': identity['settle'],
                        'contract_size': identity['contractSize'],
                        'active': identity['active']
                    })
            df_inverse = pd.DataFrame(perpetual_symbols)
            list_inverse = df_inverse['base'].tolist()
        return list_inverse
    def get_all_assets(self):
        """모든 자산 정보 조회 및 출력"""
        assets_binance = 0
        assets_bybit = 0
        df = pd.DataFrame()
        df_future = pd.DataFrame()
        for market in ['binance','bybit']:
            print(f"{market} 자산 조회 중...")
            if market == 'binance':
                if self.dict_binance['active'] == True:
                    # 스팟 잔고 조회
                    # spot의 개별티커 종목은 전부 수량*현재가 USDT로-used, USDT 종목은-free
                    # 매수 후 자동으로 계좌를 coin-m으로 옮기기 때문에 free 수량을 따로 잡지 않는다
                    df_spot, USDT_free, USDT_used = self.get_spot_balance()

                    # COIN-M Futures 잔고 조회
                    df_coinm, USDT_COIN = self.get_coinm_futures_balance()

                    # linear Futures 잔고 조회
                    df_future_binance,USDT_USD = self.get_usdm_futures_balance(market)
                    df_binance = df_coinm.copy()
                    # usdt 행 추가
                    # free, used, total, price, USDT, 주문최소금액
                    df_binance.loc['USDT'] = [USDT_free, USDT_used+USDT_USD, USDT_free+USDT_used+USDT_USD,1,1]  # 각 열에 맞는 값 입력
                    df_binance['합계(USD)'] = df_binance['total']*df_binance['price']
                    df_binance['배팅가능합계(USD)'] = df_binance['free']*df_binance['price']
                    df_binance.rename(columns={'free': 'free(qty)', 'used': 'used(qty)','total': 'total(qty)','price':'현재가'}, inplace=True)
                    df_binance['market'] = 'binance'
                    df_binance['ticker'] = df_binance.index
                    df_binance.index = 'binance_'+df_binance['ticker']
                    assets_binance = round(df_binance['합계(USD)'].sum())
                    df = pd.concat([df,df_binance], axis=0)
                    df_future = pd.concat([df_future,df_future_binance], axis=0)

            else:
                if self.dict_bybit['active'] == True:
                    assets_bybit, df_bybit = self.get_unified_balance()
                    df_future_bybit,USDT_linear = self.get_usdm_futures_balance(market)
                    df = pd.concat([df,df_bybit], axis=0)
                    df_future = pd.concat([df_future,df_future_bybit], axis=0)
        return df, df_future, assets_binance, assets_bybit

    def get_spot_balance(self):
        """스팟 잔고 조회"""

        balance = self.dict_binance['spot'].fetch_balance()
        tickers = self.dict_binance['spot'].fetch_tickers()
        # 0이 아닌 잔고만 필터링
        dict_balance = {}
        USDT_used = 0
        USDT_free = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total','timestamp','datetime']:
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    if not currency == 'USDT':
                        dict_balance[currency]['price'] = tickers[currency+'/USDT']['close']
                    else:
                        dict_balance[currency]['price'] = 1
                    dict_balance[currency]['USDT'] = dict_balance[currency]['price']*dict_balance[currency]['total']
                    if dict_balance[currency]['USDT'] < 1:
                        dict_balance.pop(currency)
                    else:
                        dict_balance[currency]['ticker'] = currency
                        if currency == 'USDT':
                            USDT_free = dict_balance[currency]['free']
                            USDT_used += dict_balance[currency]['USDT']-dict_balance[currency]['free']
                        else:
                            USDT_used += dict_balance[currency]['USDT']
        df = pd.DataFrame.from_dict(dict_balance, orient='index')
        df['market']='binance'
        df.index = df['market']+'_'+df['ticker']
        return df, USDT_free, USDT_used

    def get_coinm_futures_balance(self):
        """COIN-M Futures 잔고 조회"""
        # try:
        balance = self.dict_binance['coinm'].fetch_balance()
        tickers = self.dict_binance['coinm'].fetch_tickers()
        markets_binance = self.dict_binance['coinm'].load_markets()
        # 0이 아닌 잔고만 필터링
        dict_balance = {}
        USDT = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime']:
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    dict_balance[currency]['price'] = tickers[f"{currency}/USD:{currency}"]['close']
                    # dict_balance[currency]['USDT'] = dict_balance[currency]['price'] * dict_balance[currency]['total']
                    currency_USDT = dict_balance[currency]['price'] * dict_balance[currency]['total']
                    dict_balance[currency]['주문최소금액(USD)'] = markets_binance[f"{currency}/USD:{currency}"]['contractSize']
                    if currency_USDT < 1:
                        dict_balance.pop(currency)
                    else:
                        USDT += currency_USDT
        df = pd.DataFrame.from_dict(dict_balance, orient='index')
        return df, USDT


    def get_usdm_futures_balance(self,market):
        """USD-M Futures 잔고 조회"""
        if market == 'binance':
            balance = self.dict_binance['linear'].fetch_balance()
            tickers = self.dict_binance['linear'].fetch_tickers()
            # 0이 아닌 잔고만 필터링
            dict_balance = {}
            USDT = 0
            #전체
            for currency, amounts in balance.items():
                if currency not in ['info', 'free', 'used', 'total','timestamp','datetime','debt']:
                    if amounts['total'] > 0:
                        dict_balance[currency] = amounts
                        if not currency == 'USDT':
                            dict_balance[currency]['price'] = tickers[currency+'/USDT:USDT']['close']
                        else:
                            dict_balance[currency]['price'] = 1
                        dict_balance[currency]['USDT'] = dict_balance[currency]['price']*dict_balance[currency]['total']
                        if not dict_balance[currency]['USDT'] < 1:
                            USDT += dict_balance[currency]['USDT']


            res = self.dict_binance['linear'].fetch_positions()
            dict_linear = {}
            for data in res:
                ticker = 'binance_'+data['symbol'][:-10]+'_'+data['side']
                dict_linear[ticker] = {}
                dict_linear[ticker]['market'] = 'binance'
                dict_linear[ticker]['ticker'] = data['symbol'][:-10]
                dict_linear[ticker]['매수금액'] = float(data['info']['isolatedWallet'])
                dict_linear[ticker]['진입수량'] = data['contracts']
                dict_linear[ticker]['진입가'] = data['entryPrice']
                dict_linear[ticker]['레버리지'] = data['entryPrice']
                dict_linear[ticker]['현재가'] = data['markPrice']
                dict_linear[ticker]['방향'] = data['side']
                dict_linear[ticker]['청산가'] = float(data['info']['liquidationPrice'])
                dict_linear[ticker]['레버리지'] = round(data['notional'] / data['initialMargin'])

                if data['side'] == 'long':
                    dict_linear[ticker]['수익률'] = ((data['markPrice'] - data['entryPrice']) / data['markPrice']) * dict_linear[ticker]['레버리지'] * 100
                    dict_linear[ticker]['수익금'] = (data['markPrice'] - data['entryPrice']) * data['contracts']
                elif data['side'] == 'short':
                    dict_linear[ticker]['수익률'] = ((data['entryPrice'] - data['markPrice']) / data['entryPrice']) * dict_linear[ticker]['레버리지'] * 100
                    dict_linear[ticker]['수익금'] = (data['entryPrice'] - data['markPrice']) * data['contracts']

            df_linear = pd.DataFrame.from_dict(dict_linear, orient='index')
            # df_linear.index = 'binance_' + df_linear['ticker']
        elif market == 'bybit':
            list_linear = self.dict_bybit['exchange'].fetch_positions()
            dict_linear = {}
            if list_linear:
                for data in list_linear:
                    ticker = 'bybit_'+data['symbol'][:-10]+'_'+data['side']
                    dict_linear[ticker] = {}
                    dict_linear[ticker]['market'] = 'bybit'
                    dict_linear[ticker]['ticker'] = data['symbol'][:-10]
                    dict_linear[ticker]['매수금액'] = data['collateral']
                    dict_linear[ticker]['진입수량'] = data['contracts']
                    dict_linear[ticker]['진입가'] = data['entryPrice']
                    dict_linear[ticker]['레버리지'] = data['leverage']
                    dict_linear[ticker]['현재가'] = data['markPrice']
                    dict_linear[ticker]['청산가'] = data['liquidationPrice']
                    dict_linear[ticker]['방향'] = data['side']
                    if data['side'] == 'long':
                        dict_linear[ticker]['수익률'] = ((data['markPrice'] - data['entryPrice']) / data['entryPrice']) * data[
                            'leverage'] * 100
                        dict_linear[ticker]['수익금'] = (data['markPrice'] - data['entryPrice']) * data['contracts']
                    elif data['side'] == 'short':
                        dict_linear[ticker]['수익률'] = ((data['entryPrice'] - data['markPrice']) / data['entryPrice']) * data[
                            'leverage'] * 100
                        dict_linear[ticker]['수익금'] = (data['entryPrice'] - data['markPrice']) * data['contracts']
                df_linear = pd.DataFrame.from_dict(dict_linear, orient='index')
                # df_linear.index = 'bybit_' + df_linear['ticker']
                USDT = df_linear['매수금액'].sum()
            else:
                df_linear = pd.DataFrame()
                USDT = 0

        return df_linear, USDT

    def get_unified_balance(self):
        balance = self.dict_bybit['exchange'].fetch_balance()
        # pprint(balance)
        if balance['info']['result']['list'][0]['accountType'] == 'UNIFIED':
            # usdm_balance,USDT=self.get_usdm_futures_balance()
            tickers = self.dict_bybit['exchange'].fetch_tickers()
            # 0이 아닌 잔고만 필터링
            dict_balance = {}
            for currency, amounts in balance.items():
                if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime',
                                    'debt']:  # 바이비트에는 'debt'가있음
                    if amounts['total'] > 0:
                        dict_balance[currency] = amounts
                        if not currency == 'USDT':
                            dict_balance[currency]['현재가'] = tickers[currency + '/USDT:USDT']['close']
                        else:
                            dict_balance[currency]['현재가'] = 1

            list_coins = balance['info']['result']['list'][0]['coin']
            hold_tickers = dict_balance.keys()
            for data in list_coins:
                if data['coin'] in hold_tickers:
                    dict_balance[data['coin']]['market'] = 'bybit'
                    dict_balance[data['coin']]['ticker'] = data['coin']
                    # dict_balance[data['coin']]['cumRealisedPnl'] =  float(data['cumRealisedPnl'])
                    # dict_balance[data['coin']]['unrealisedPnl'] =  float(data['unrealisedPnl'])
                    # dict_balance[data['coin']]['total'] =  dict_balance[data['coin']]['total']+float(dict_balance[data['coin']]['unrealisedPnl'])
                    # dict_balance[data['coin']]['total'] =  float(data['equity'])
                    # dict_balance[data['coin']]['equity'] =  data['equity']
                    # dict_balance[data['coin']]['USDT'] =  dict_balance[data['coin']]['total']*float(dict_balance[data['coin']]['price'])
                    dict_balance[data['coin']]['합계(USD)'] = float(data['usdValue'])
                    if dict_balance[data['coin']]['합계(USD)'] < 1:
                        dict_balance.pop(data['coin'])
            df = pd.DataFrame.from_dict(dict_balance, orient='index')
            df.drop(labels='debt', axis=1, inplace=True)
            df.rename(columns={'free': 'free(qty)', 'used': 'used(qty)','total': 'total(qty)'}, inplace=True)
            df['배팅가능합계(USD)'] = df['free(qty)'] * df['현재가']
            df['주문최소금액(USD)'] = 1
            df.index = 'bybit_' + df['ticker']
            all_assets = round(df['합계(USD)'].sum())
        return all_assets,df
class ShutdownDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.seconds_left = 30
        self.shutdown_timer = QTimer()
        self.shutdown_timer.timeout.connect(self.update_timer)

        self.init_ui()
        self.start_timer()

    def init_ui(self):
        self.setWindowTitle('윈도우 절전 알림')
        self.setFixedSize(300, 150)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 레이아웃 설정
        main_layout = QVBoxLayout()

        # 안내 메시지
        self.message_label = QLabel('시스템이 30초 후에 절전모드로 전환 됩니다.')
        self.message_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.message_label)

        # 타이머 표시
        self.timer_label = QLabel(f'남은 시간: {self.seconds_left}초')
        self.timer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.timer_label)

        # 버튼 컨테이너
        button_layout = QHBoxLayout()

        # 종료 버튼
        self.shutdown_button = QPushButton('윈도우절전모드')
        self.shutdown_button.clicked.connect(self.shutdown_now)
        button_layout.addWidget(self.shutdown_button)

        # 취소 버튼
        self.cancel_button = QPushButton('취소')
        self.cancel_button.clicked.connect(self.cancel_shutdown)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def start_timer(self):
        self.shutdown_timer.start(1000)  # 1초마다 타이머 업데이트

    def update_timer(self):
        self.seconds_left -= 1
        self.timer_label.setText(f'남은 시간: {self.seconds_left}초')

        if self.seconds_left <= 0:
            self.shutdown_timer.stop()
            self.shutdown_now()

    def shutdown_now(self):
        self.shutdown_timer.stop()
        # 윈도우 종료 명령 실행
        # print('윈도우 종료')
        # os.system("shutdown /s /t 0") #죵료
        print('윈도우 절전모드')
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0") #절전모드
        self.close()

    def cancel_shutdown(self):
        self.shutdown_timer.stop()
        print('윈도우 종료 취소')
        self.close()
if __name__ == "__main__":
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    app = QApplication([])
    main_table = Window()
    main_table.setMinimumSize(600, 400)
    main_table.show()
    app.exec()
    # os.system('pause')

    # main()
















    # def fetch_inverse(self):
    #     # li_col = ['market','ticker','used(qty)', 'free(qty)', 'total(qty)', '현재가', '현재가(linear)',
    #     #           'USDT', '배팅가능합계(USD)','주문최소금액(USD)']
    #     # self.df_inverse = pd.DataFrame(columns=li_col)
    #     self.df_inverse = pd.DataFrame()
    #     self.df_inverse_fetch = pd.DataFrame()
    #     # try:
    #     # 잔고 조회
    #     for market in ['bybit','binance']:
    #         if market == 'bybit' and self.ex_bybit == None:
    #             continue #None일 경우 건너뛰기
    #         if market == 'binance' and self.ex_binance == None:
    #             continue
    #         try:
    #             balance, usdt_free, usdt_total = self.fetch_inverse_detail(market)
    #             # have_usdt = float(self.fetch_balance(accountType='UNIFIED', ticker='USDT', balance='잔고'))
    #             # all_usdt = float(self.fetch_balance(accountType='UNIFIED', ticker='USDT', balance='보유'))
    #             for ticker in balance:
    #                 if not ticker == 'USDT':
    #                     # self.df_inverse.loc[f"{market}_{ticker}", 'category'] = balance[ticker]['category']
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'free(qty)'] = balance[ticker]['free']
    #                     # self.df_inverse.loc[f"{market}_{ticker}", 'free(qty)'] = 0.0002
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'used(qty)'] = balance[ticker]['used']
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'total(qty)'] = balance[ticker]['total']
    #                     self.df_inverse.loc[f"{market}_{ticker}", '주문최소금액(USD)'] = round(balance[ticker]['주문최소금액'])
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'ticker'] = ticker
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'market'] = market
    #                     self.df_inverse.loc[f"{market}_{ticker}", '현재가'] = balance[ticker]['현재가']
    #                     # self.df_inverse.loc[f"{market}_{ticker}", '현재가(linear)'] = balance[ticker]['현재가(linear)']
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'free(USDT)'] = usdt_free
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'total(USDT)'] = usdt_total
    #                     self.df_inverse.loc[f"{market}_{ticker}", '배팅가능합계(USD)'] = round(balance[ticker]['free']*balance[ticker]['현재가'],1)
    #                     self.df_inverse.loc[f"{market}_{ticker}", 'USDT'] = round(balance[ticker]['total']*balance[ticker]['현재가'],1)
    #         except Exception as e:
    #             print('======== fetch_inverse 에러 발생 ========')
    #             print(e)
    #     if not self.df_inverse.empty:
    #         self.df_inverse = self.df_inverse[self.df_inverse['주문최소금액(USD)']<self.df_inverse['USDT']]
    #         self.df_inverse = self.df_inverse.sort_index(ascending=False)
    # def fetch_future(self):
    #     self.df_future = pd.DataFrame()
    #     common_col = ['unrealizedPnl', 'contracts','liquidationPrice', 'side', 'markPrice', 'entryPrice','매수금액',
    #                   'market','symbol','leverage']
    #     for market in ['bybit','binance']:
    #         if market == 'bybit':
    #             if not self.ex_bybit == None:
    #                 res = self.ex_bybit.fetch_positions()
    #                 for data in res:
    #                     data['매수금액'] = data['collateral']
    #                     data['수익률'] = data['percentage']
    #                     # del data['info']
    #                 df = pd.DataFrame(res)
    #                 if 'symbol' in df.columns.tolist():
    #                     df.index = 'bybit_' + df['symbol'].copy()
    #                     df['market'] = 'bybit'
    #                     # df['수익률'] = df['손익'] / df['매수금액'] * 100
    #                     # df = df[['symbol', '현재가', '레버리지', '방향', '수익률', '손익', '보유수량', '매수금액', '진입가', '청산가', 'marginMode']]
    #                     df = df[common_col]
    #
    #                     self.df_future = pd.concat([self.df_future,df],axis=0)
    #
    #         if market == 'binance':
    #             if not self.ex_binance == None:
    #                 res = self.ex_binance.fetch_positions()
    #                 for data in res:
    #                     data['leverage'] = math.trunc(1/data['initialMarginPercentage'])
    #                     data['매수금액'] = data['collateral']/data['leverage']
    #                     data['수익률'] = data['percentage']
    #
    #                     if data['liquidationPrice'] == None:
    #                         data['liquidationPrice'] = data['entryPrice']/data['leverage']
    #
    #                 df = pd.DataFrame(res)
    #                 if 'symbol' in df.columns.tolist():
    #                     df.index = 'binance_' + df['symbol'].copy()
    #                     df['market'] = 'binance'
    #                     df = df[common_col]
    #                     # df['liquidationPrice'] = 0 # 바이낸스의 경우 청산가 조회 안됨
    #                     # df.rename(columns={'unrealizedPnl': '손익', 'leverage': '레버리지', 'contracts': '보유수량',
    #                     #                    'liquidationPrice': '청산가',
    #                     #                    'side': '방향', 'markPrice': '현재가', 'entryPrice': '진입가'}, inplace=True)
    #                     self.df_future = pd.concat([self.df_future,df],axis=0, ignore_index=True)
    #     if not self.df_future.empty:
    #         self.df_future['symbol'] = self.df_future['symbol'].str.split('/').str[0] #/기준 왼쪽만 남겨서 BTC만 추출
    #         self.df_future.rename(columns={'unrealizedPnl': '손익', 'contracts': '보유수량',
    #                            'liquidationPrice': '청산가','symbol': 'ticker',
    #                            'side': '방향', 'markPrice': '현재가', 'entryPrice': '진입가', 'leverage': '레버리지'}, inplace=True)
    #         # self.df_future['수익률'] = self.df_future['손익'] / self.df_future['매수금액'] * 100
    #         self.df_future.index = self.df_future['market']+"_"+self.df_future['ticker']








    # def fetch_all_balance(self):
    #     if self.dict_binance['active'] == True:
    #         # 스팟 잔고 조회
    #         # spot의 개별티커 종목은 전부 수량*현재가 USDT로-used, USDT 종목은-free
    #         # 매수 후 자동으로 계좌를 coin-m으로 옮기기 때문에 free 수량을 따로 잡지 않는다
    #         df_spot, USDT_free, USDT_used = self.get_spot_balance()
    #         # COIN-M Futures 잔고 조회
    #         df_coinm, USDT_COIN = self.get_coinm_futures_balance()
    #         # linear Futures 잔고 조회
    #         df_linear,USDT_USD = self.get_usdm_futures_balance()
    #         df = df_coinm.copy()
    #         # usdt 행 추가
    #         df.loc['USDT'] = [USDT_free, USDT_used+USDT_USD, USDT_free+USDT_used+USDT_USD,1,USDT_free+USDT_used+USDT_USD]  # 각 열에 맞는 값 입력
    #         df['합계(USD)'] = df['total']*df['price']
    #         df['배팅가능합계(USD)'] = df['free']*df['price']
    #         df.rename(columns={'free': 'free(qty)', 'used': 'used(qty)','total': 'total(qty)','price':'현재가'}, inplace=True)
    #         all_assets = df['합계(USD)'].sum()
    #     elif self.dict_bybit['active'] == True:
    #         all_assets, df = self.get_unified_balance()
    #         USDT_linear, df_linear = self.get_usdm_futures_balance()
    #     return all_assets, df, df_linear

    #     def fetch_inverse_detail(self,market):
    #         if market == 'bybit':
    #             res = self.ex_bybit.fetch_balance()
    #
    #         elif market == 'binance':
    #             res_spot = self.ex_binance.fetch_balance()
    #             res = self.ex_binance.fetch_balance(params={"type": 'delivery'})
    #             markets_binance = self.ex_binance.load_markets()
    #             usdt_free = res_spot['USDT']['free']
    #             usdt_total = res_spot['USDT']['total']
    #
    #         # held_coins = {}
    #         balance = {}
    #
    #         for ticker, data in res['total'].items():
    #             # if data > 0 and ticker in res and ticker != 'USDT':
    #             if data > 0 and ticker in res:
    #                 if market == 'bybit':
    #                     if ticker in self.list_bybit_inverse: #인버스 종목이 한정적
    #                         balance[ticker] = res[ticker]
    #                         balance_bybit = self.common.fetch_account_info_bybit(Account='inverse',symbol=ticker + 'USD')
    #                         balance[ticker]['주문최소금액'] = float(balance_bybit['lotSizeFilter']['minOrderQty'])  # inverse 최소주문USDT구하기
    #
    #                         balance[ticker]['현재가']= self.common.fetch_ticker(market,ticker + 'USD')['close']
    #                         # balance[ticker]['현재가(linear)']= self.common.fetch_ticker(market,ticker + 'USDT')['close']
    #                         # balance[ticker]['category'] = 'inverse/spot'
    #                     elif ticker == 'USDT':
    #                         usdt_free = res[ticker]['free']
    #                         usdt_total = res[ticker]['total']
    #                 if market == 'binance':
    #                     balance[ticker] = res[ticker]
    #                     balance[ticker]['주문최소금액'] = markets_binance[f"{ticker}/USD:{ticker}"]['contractSize']
    #                     # ticker_info = markets_binance[f'{ticker}/USD:{ticker}']
    #                     # if ticker == 'BTC':
    #                     #     balance[ticker]['주문최소금액'] = 100
    #                     # else:
    #                     #     balance[ticker]['주문최소금액'] = 10
    #
    #                     balance[ticker]['현재가'] = self.common.fetch_ticker(market, ticker + 'USD_PERP')['close']
    # #                     balance[currency]['category'] = 'inverse/spot'
    #                     # balance[currency]['현재가(linear)'] = self.common.fetch_ticker(market, currency + '/USDT')['close']
    #         return balance, usdt_free, usdt_total
