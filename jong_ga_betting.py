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
import math
import subprocess
import os
import numpy as np
import talib
from pprint import pprint
import json
import pickle
import asyncio
import requests
import websockets
from pprint import pprint
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None)


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
                self.df_linear.loc[index,'현재가'] = 현재가
                self.df_linear.loc[index,'수익률'] = round(수익률,2)
                self.df_linear.loc[index,'수익금'] = round(수익금,2)


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

class kiwoom_finance:
    def __init__(self, api_key: str, api_secret: str, market: str,
                 exchange: str = "서울", mock: bool = False):
        self.mock = mock
        self.market = market
        self.set_base_url(market, mock) # self.base_url 설정
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = exchange
        self.access_token = None
        self.fetch_access = True
        if self.check_access_token(): #기존에 생성한 토큰이 있는지 확인
            print('기존 토큰 로드')
            self.load_access_token()
        else:
            print('신규 토큰 발행')
            self.issue_access_token() #없을 경우 토큰 발행

    def set_base_url(self, market: str = '주식', mock: bool = True):
        if mock:
            self.base_url = "https://mockapi.kiwoom.com"
        else:
            self.base_url = "https://api.kiwoom.com"

    def issue_access_token(self):
        if self.api_key == 'test':
            pass
        else:
            endpoint = 'oauth2/token'
            url = f"{self.base_url}/{endpoint}"
            headers = {'Content-Type': 'application/json;charset=UTF-8'}
            params = {
                'grant_type': 'client_credentials',  # grant_type
                'appkey': self.api_key,  # 앱키
                'secretkey': self.api_secret,  # 시크릿키
            }
            response = requests.post(url, headers=headers, json=params)
            data = response.json()
            try:
                self.access_token = data["token"]
            except Exception as e:
                print(f"API 오류 발생: {e}")
                print(f"{data= }")
                quit()
            data['api'] = self.api_key
            if self.mock:
                file_name = "kiwoom_token_mock.dat"
            else:
                file_name = "kiwoom_token.dat"
            with open(file_name, "wb") as f:
                pickle.dump(data, f)

    def check_access_token(self):
        if self.mock:
            file_name = "kiwoom_token_mock.dat"
        else:
            file_name = "kiwoom_token.dat"
        try:
            f = open(file_name, "rb")
            data = pickle.load(f)
            f.close()
            expire_epoch = data['expires_dt']
            if datetime.datetime.strptime(expire_epoch,"%Y%m%d%H%M%S")-datetime.datetime.now() < datetime.timedelta(hours=12):
                status = False #기존 토큰 제거
            elif not data['api'] == self.api_key:
                status = False
            else:
                status = True
            return status
        except IOError:
            return False

    def load_access_token(self):
        if self.mock:
            file_name = "kiwoom_token_mock.dat"
        else:
            file_name = "kiwoom_token.dat"
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.access_token = data["token"]

    def fetch_asset(self) -> dict:
        endpoint = '/api/dostk/acnt'
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # 컨텐츠타입
            'authorization': f'Bearer {self.access_token}',  # 접근토큰
            'cont-yn': "N",  # 연속조회여부
            'next-key': "",  # 연속조회키
            'api-id': 'ka01690',  # TR명
        }
        params = {
            'qry_dt': datetime.datetime.now().strftime("%Y%m%d"),  # 조회일자
        }
        res = requests.post(url, headers=headers, json=params)
        data = res.json()

        dict_data = {}
        if data['return_msg'] == "정상적으로 처리되었습니다":
            dict_data['추정자산'] = int(data['day_stk_asst'])
            dict_data['예수금'] = int(data['dbst_bal'])
            dict_data['총 매입가'] = int(data['tot_buy_amt'])
            dict_data['총 평가금액'] = int(data['tot_evlt_amt'])
            dict_data['총 평가손익'] = int(data['tot_evltv_prft'])
            dict_data['수익률'] = float(data['tot_prft_rt'])
        return dict_data
    def order_open(self,ticker,qty,price,ord_type):
        endpoint = '/api/dostk/ordr'
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # 컨텐츠타입
            'authorization': f'Bearer {self.access_token}',  # 접근토큰
            'cont-yn': "N",  # 연속조회여부
            'next-key': "",  # 연속조회키
            'api-id': 'kt10000',  # TR명
        }
        if ord_type == '지정가':
            ord_type = '1'
        elif ord_type == '시장가':
            ord_type = '3'
        params = {
            'dmst_stex_tp': 'KRX',  # 국내거래소구분 KRX,NXT,SOR
            'stk_cd': ticker[1:],  # 종목코드
            'ord_qty': str(qty),  # 주문수량
            'ord_uv': str(price),  # 주문단가
            'trde_tp': ord_type,
            # 매매구분 0:보통 , 3:시장가 , 5:조건부지정가 , 81:장마감후시간외 , 61:장시작전시간외, 62:시간외단일가 , 6:최유리지정가 , 7:최우선지정가 , 10:보통(IOC) , 13:시장가(IOC) , 16:최유리(IOC) , 20:보통(FOK) , 23:시장가(FOK) , 26:최유리(FOK) , 28:스톱지정가,29:중간가,30:중간가(IOC),31:중간가(FOK)
            'cond_uv': '',  # 조건단가
        }
        res = requests.post(url, headers=headers, json=params)
        data = res.json()
        return data
    def order_close(self,ticker,qty,price,ord_type):
        endpoint = '/api/dostk/ordr'
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # 컨텐츠타입
            'authorization': f'Bearer {self.access_token}',  # 접근토큰
            'cont-yn': "N",  # 연속조회여부
            'next-key': "",  # 연속조회키
            'api-id': 'kt10001',  # TR명
        }
        if ord_type == '지정가':
            ord_type = '1'
        elif ord_type == '시장가':
            ord_type = '3'
        params = {
            'dmst_stex_tp': 'KRX',  # 국내거래소구분 KRX,NXT,SOR
            'stk_cd': ticker[1:],  # 종목코드
            'ord_qty': str(qty),  # 주문수량
            'ord_uv': str(price),  # 주문단가
            'trde_tp': ord_type,
            # 매매구분 0:보통 , 3:시장가 , 5:조건부지정가 , 81:장마감후시간외 , 61:장시작전시간외, 62:시간외단일가 , 6:최유리지정가 , 7:최우선지정가 , 10:보통(IOC) , 13:시장가(IOC) , 16:최유리(IOC) , 20:보통(FOK) , 23:시장가(FOK) , 26:최유리(FOK) , 28:스톱지정가,29:중간가,30:중간가(IOC),31:중간가(FOK)
            'cond_uv': '',  # 조건단가
        }
        res = requests.post(url, headers=headers, json=params)
        data = res.json()
        return data


class Window(QMainWindow):
    manual_buy_signal = pyqtSignal(str,str,int,float,pd.DataFrame)
    set_signal = pyqtSignal(pd.DataFrame)
    def __init__(self):
        super().__init__()
        self.init_file()
        self.set_UI()
        # self.time_sync() #현재시간 동기화
        QTest.qWait(500)
        self.funding_time_old = int(time.time())
        self.QPB_start.clicked.connect(self.onStartButtonClicked)
        self.QPB_stop.clicked.connect(self.onStopButtonClicked)
        self.QCB_auto.clicked.connect(self.setting)
        self.QPB_api_save.clicked.connect(lambda :self.save_api('bybit'))
        self.QCB_off.currentIndexChanged.connect(self.setting)
        if self.QCB_auto.isChecked() == True:
            self.onStartButtonClicked()
            # 메인 윈도우의 시그널을 스레드의 슬롯에 연결

    def set_UI(self):
        QW_main = QWidget()
        self.setWindowTitle(f'jong_be')
        self.QT_trade_inverse = QTableWidget()

        self.QGL_menu = QGridLayout()
        self.QPB_start = QPushButton('START')
        self.QPB_stop = QPushButton('STOP')

        self.QL_wallet = QLabel()

        self.QCB_auto = QCheckBox('오토스타트')
        if self.df_set.loc['auto_start', 'val'] == 'auto':
            self.QCB_auto.setChecked(True)
        else:
            self.QCB_auto.setChecked(False)
        self.QCB_off = QComboBox()
        self.QCB_off.addItems(['자동꺼짐','loop','1분후','5분후','10분후','30분후','1시간후','설정안함'])
        self.QLE_api = QLineEdit()
        self.QLE_secret = QLineEdit()
        self.QPB_api_save = QPushButton('API 저장')


        self.QCB_off.setCurrentText(self.df_set.loc['auto_finish','val'])
        QW_grid = QWidget()
        StyleSheet_Qtextedit = "font: 10pt 나눔고딕; "
        QW_grid.setStyleSheet(StyleSheet_Qtextedit)
        QW_grid.setLayout(self.QGL_menu)
        # QW_grid.setMaximumSize(1980,100)


        QHB_api = QHBoxLayout()
        QHB_api.addWidget(self.QPB_start)
        QHB_api.addWidget(self.QPB_stop)
        QHB_api.addWidget(self.QCB_auto)
        QHB_api.addWidget(self.QL_wallet)


        QHB_api.addWidget(QLabel('API: '))
        QHB_api.addWidget(self.QLE_api)
        QHB_api.addWidget(QLabel('SECRET: '))
        QHB_api.addWidget(self.QLE_secret)
        QHB_api.addWidget(self.QPB_api_save)

        QVB_main = QVBoxLayout()

        StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 12pt 나눔고딕; "
        self.QT_trade_inverse.setStyleSheet(StyleSheet_Qtable)
        self.QPB_start.setStyleSheet(" background-color: #cccccc;")
        self.QPB_stop.setStyleSheet("background-color: #cccccc;")

        self.setCentralWidget(QW_main)

        QSV_main = QSplitter(Qt.Vertical)
        QSH_table_up = QSplitter(Qt.Horizontal)
        QSH_table = QSplitter(Qt.Horizontal)
        QSH_history_table = QSplitter(Qt.Horizontal)

        QSH_table_up.addWidget(self.QT_trade_inverse)
        QSV_main.addWidget(QSH_table_up)
        QSV_main.addWidget(QSH_history_table)
        QSV_main.addWidget(QSH_table)
        QSV_main.addWidget(QW_grid)
        QVB_main.addWidget(QSV_main)
        QVB_main.addLayout(QHB_api)
        QW_main.setLayout(QVB_main)

    def save_api(self,market):
        if not self.QLE_api_binance.text() == '':
            self.df_set.loc[f'api_{market}','val']=self.QLE_api_binance.text()
        if not self.QLE_secret_binance.text() == '':
            self.df_set.loc[f'secret_{market}','val']=self.QLE_secret_binance.text()
        self.QLE_api_binance.clear()
        self.QLE_secret_binance.clear()
        self.dict_binance = self.make_exchange_binance()
        self.df_set.to_sql('set', self.conn, if_exists='replace')

    def init_file(self):
        db_file = 'DB/jong_be.db'
        if not os.path.isfile(db_file): #파일이 없으면
            self.conn = sqlite3.connect(db_file)
            self.df_closed = pd.DataFrame(columns=['market','ticker', 'category', '주문가','체결가', '주문수량',
                                                   '체결수량', '매수금액','수수료', '주문시간', '체결시간',
                                                   'id', '상태'])
            self.df_closed.to_sql('closed', self.conn, if_exists='replace')
            self.df_linear = pd.DataFrame(columns=['market','ticker', 'category', '주문가','체결가','평단가', '주문수량',
                                                   '보유수량', '매수금액', '수수료', '체결시간', '매수횟수','레버리지','방향'],
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
            self.df_set.loc['api_bybit','val'] = None
            self.df_set.loc['secret_bybit','val'] = None
            self.df_set.loc['api_binance','val'] = None
            self.df_set.loc['secret_binance','val'] = None
            self.df_set.to_sql('set', self.conn, if_exists='replace')

        else:
            self.conn = sqlite3.connect(db_file)
            self.df_open = pd.read_sql(f"SELECT * FROM 'open'", self.conn).set_index('index')
            self.df_closed = pd.read_sql(f"SELECT * FROM 'closed'", self.conn).set_index('index')
            self.df_linear = pd.read_sql(f"SELECT * FROM 'linear'", self.conn).set_index('index')
            self.df_wallet = pd.DataFrame(columns=['binance_USDT','bybit_USDT','total'])
            self.df_wallet.to_sql('wallet', self.conn, if_exists='replace')
            self.df_wallet = pd.read_sql(f"SELECT * FROM 'wallet'", self.conn).set_index('index')
            self.df_set = pd.read_sql(f"SELECT * FROM 'set'", self.conn).set_index('index')
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


    # def time_sync(self):
    #     print(datetime.datetime.now())
    #     subprocess.Popen('python timesync.py')
    def convert_column_types(self,df): #데이터프레임 중 숫자로 바꿀 수 있는데이터는 숫자로 변환
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='raise')
            except ValueError:
                pass
        return df



class WebSocketClient:
    def __init__(self, ACCESS_TOKEN):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.websocket = None
        self.connected = False
        self.keep_running = True
        self.search_chennel = None
        self.signal_buy = False
        self.df = pd.DataFrame()
    # WebSocket 서버에 연결합니다.
    async def connect(self):
        try:
            url = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # 접속 URL
            self.websocket = await websockets.connect(url, ping_interval=None)
            self.connected = True
            print("서버와 연결을 시도 중입니다.")

            # 로그인 패킷
            param = {
                'trnm': 'LOGIN',
                'token': self.ACCESS_TOKEN
            }

            print('실시간 시세 서버로 로그인 패킷을 전송합니다.')
            # 웹소켓 연결 시 로그인 정보 전달
            await self.send_message(message=param)

        except Exception as e:
            print(f'Connection error: {e}')
            self.connected = False

    # 서버에 메시지를 보냅니다. 연결이 없다면 자동으로 연결합니다.
    async def send_message(self, message):
        if not self.connected:
            await self.connect()  # 연결이 끊어졌다면 재연결
        if self.connected:
            # message가 문자열이 아니면 JSON으로 직렬화
            if not isinstance(message, str):
                message = json.dumps(message)
        await self.websocket.send(message)
        print(f'async def send_message: {message}')

    # 서버에서 오는 메시지를 수신하여 출력합니다.
    async def receive_messages(self):
        while self.keep_running:
            try:
                # 서버로부터 수신한 메시지를 JSON 형식으로 파싱
                response = json.loads(await self.websocket.recv())
                # 메시지 유형이 LOGIN일 경우 로그인 시도 결과 체크
                if response.get('trnm') == 'LOGIN':
                    if response.get('return_code') != 0:
                        print('로그인 실패하였습니다. : ', response.get('return_msg'))
                        await self.disconnect()
                    else:
                        print('로그인 성공하였습니다.')
                        print('조건검색 목록조회 패킷을 전송합니다.')
                        # 로그인 패킷
                        param = {
                            'trnm': 'CNSRLST'
                        }
                        await self.send_message(message=param)
                # 메시지 유형이 PING일 경우 수신값 그대로 송신
                elif response.get('trnm') == 'PING':
                    await self.send_message(response)
                elif response.get('trnm') == 'CNSRLST': #전체 조건 검색 식 불러오기
                    for i, li in enumerate(response['data']):
                            if title in li:
                                num_str = li[0]
                                print(f"{num_str= }")
                                self.search_chennel = num_str
                elif response.get('trnm') == 'CNSRREQ': # 종목들 불러오기
                    self.df = pd.DataFrame(response['data'])
                    self.df.rename(
                        columns={'9001': '종목코드', '302': '종목명', '10': '현재가', '25': '전일대비기호',
                                 '11': '전일대비', '12': '등락율', '13': '누적거래량', '16': '시가', '17': '고가', '18': '저가'}, inplace=True)
                    for col in self.df.columns:
                        try:
                            self.df[col] = pd.to_numeric(self.df[col], errors='raise')

                            break

                        except ValueError:
                            pass
                    break
                if response.get('trnm') != 'PING':
                    print(f'실시간 시세 서버 응답 수신: {response}')

            except websockets.ConnectionClosed:
                print('Connection closed by the server')
                self.connected = False
                await self.websocket.close()

    # WebSocket 실행
    async def run(self):
        print('async def run(self):')
        # await self.connect()
        await self.receive_messages()

    # WebSocket 연결 종료
    async def disconnect(self):
        self.keep_running = False
        if self.connected and self.websocket:
            await self.websocket.close()
            self.connected = False
            print('Disconnected from WebSocket server')

async def main(ex):
    await websocket_client.connect()
    # await trade_stocks(access_token)

    receive_task = asyncio.create_task(websocket_client.run())

    await asyncio.sleep(1)
    if not websocket_client.search_chennel == None: #search_chennel 이 None이 아니면 메세지 전송
        await websocket_client.send_message({
            'trnm': 'CNSRREQ',  # 서비스명
            'seq': websocket_client.search_chennel,  # 조건검색식 일련번호
            'search_type': '0',  # 조회타입
            'stex_tp': 'K',  # 거래소구분
            'cont_yn': 'N',  # 연속조회여부
            'next_key': '',  # 연속조회키
        })

    await receive_task

    print('asdf')
    print(websocket_client.df)
    df = websocket_client.df.copy()
    print(f"필요금액: {df['현재가'].sum()}")
    for i,ticker in enumerate(df['종목코드'].tolist()):
        res = ex.order_open(ticker,1,df.loc[df.index[i],'현재가'],'시장가')
        pprint(res)
    quit()


if __name__ == "__main__":
    # mock = False
    # if mock:
    #     api_key = "zSQr2jdgor8SPPF5DigW5Vq64xKRQcbNQY_2O4muS2o"
    #     secret_key = "TusEUmZ3pL6QtDIjHy3owfdsxfw8gVjJVwt1I4IeomQ"
    #     SOCKET_domain = 'wss://mockapi.kiwoom.com:10000'  # 모의투자 접속 URL
    #     SOCKET_URL = "/api/dostk/websocket"
    # else:
    #     api_key = "P0FfJ6jrHYYv5rOroape_sHsMatIGQhdACJfA3K2TkM"
    #     secret_key = "TusEUmZ3pL6QtDIjHy3owfdsxfw8gVjJVwt1I4IeomQ"
    #     api_key = "yldEAW1zfmbEnyK0X0M_v91AqSk-b3LO5dvALqSLfRo"
    #     secret_key = "9BEshcgN9Rp9afF0KDmh3e8RRGxswjSkro0Df6O8cv8"
    # title = '종가'
    # ex = kiwoom_finance(api_key=api_key,api_secret=secret_key,market='주식',mock=mock)
    # dict_res = ex.fetch_asset()
    #
    # websocket_client = WebSocketClient(ex.access_token)
    #
    # db_file = 'jong_ga.db'
    # if not os.path.isfile(db_file):  # stg_file.db 파일이 없으면
    #     conn = sqlite3.connect(db_file)
    #     df_jong_ga = pd.DataFrame()
    #     df_jong_ga.to_sql('in_stock', conn, if_exists='replace')
    # else:
    #     conn = sqlite3.connect(db_file)
    #     df_jong_ga = pd.read_sql(f"SELECT * FROM 'in_stock'", conn).set_index('index')
    # while True:
    #     now = datetime.datetime.now()
    #
    #     if now.hour == 9 and now.minute >= 0:
    #         if not df_jong_ga.empty:
    #             for i,ticker in enumerate(df_jong_ga['종목코드'].tolist()):
    #                 res = ex.order_close(ticker,1,df_jong_ga.loc[df_jong_ga.index[i],'현재가'],'시장가')
    #                 pprint(res)
    #                 df_jong_ga = pd.DataFrame()
    #     # 오후 3시 30분 체크 (15:29)
    #     elif now.hour == 15 and now.minute >= 29:
    #         # asyncio로 프로그램을 실행합니다.
    #         asyncio.run(main(ex))
    #         break

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