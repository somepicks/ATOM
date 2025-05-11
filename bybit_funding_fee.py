from pybit.unified_trading import HTTP
import datetime
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QMainWindow,QGridLayout,QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QHBoxLayout,QTableWidget,QSplitter,QApplication,QCheckBox,QTextEdit,QTableWidgetItem,QHeaderView,QComboBox,QDialog
from PyQt5.QtCore import Qt,QThread,pyqtSlot,QTimer,pyqtSignal,QWaitCondition,QMutex
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
# pd.options.display.float_format = '{:.6f}'.format

class do_trade(QThread):
    qt_have = pyqtSignal(pd.DataFrame)
    qt_inverse = pyqtSignal(pd.DataFrame)
    qt_open = pyqtSignal(pd.DataFrame)
    qt_closed = pyqtSignal(pd.DataFrame)
    qt_future = pyqtSignal(pd.DataFrame)
    qt_set = pyqtSignal(pd.DataFrame)
    val_light = pyqtSignal(bool)
    val_wallet = pyqtSignal(str)
    val_time = pyqtSignal(str)
    shutdown_signal = pyqtSignal()
    def __init__(self,parent,session,ex_bybit,ex_binance,df_open,df_closed,list_bybit_inverse,
                 df_inverse,df_set):
        super().__init__(parent)
        self.cond = QWaitCondition()
        self.bool_light = False
        self._status = True
        self.session = session
        self.ex_bybit = ex_bybit
        self.ex_binance = ex_binance
        self.wallet = '0'
        self.df_open = df_open
        self.df_closed = df_closed
        self.df_inverse_past = df_inverse
        # self.df_inverse = df_inverse
        self.list_compare_col = df_inverse.columns.to_list()

        self.df_set = df_set
        self.list_bybit_inverse = list_bybit_inverse
        # self.rate_short = float(rate_short)
        self.funding_time_old = int(time.time())
        # self.get_funding_time()
        self.common_def = common_def(self.ex_bybit,self.session,self.ex_binance)

    def run(self):
        start_time = self.df_set.loc['start_time', 'val']
        finish_time = self.df_set.loc['auto_finish', 'val']
        if str == type(start_time):
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

        dict_time = {'1분후': 1, '5분후': 5, '10분후': 10, '30분후': 30, '1시간후': 60, '설정안함':43200}
        finish_time = start_time + datetime.timedelta(minutes=dict_time[finish_time])
        while self._status:
            self.fetch_inverse()
            self.fetch_future()
            funding_time = pd.to_datetime(self.df_set.loc['funding_time','val'])
            current_t = datetime.datetime.now().replace(microsecond=0)
            self.text_time = funding_time - current_t
            # days를 제외한 시간, 분, 초만 계산
            hours, remainder = divmod(self.text_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.text_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            if not self.df_open.empty:
                for id in self.df_open.index.tolist():
                    if self.df_open.loc[id, '상태'] == '매수주문' or self.df_open.loc[id, '상태'] == '부분체결':
                        self.chegyeol_buy(id)
            for idx in self.df_inverse.index.tolist():
                self.buy_auto(idx)
                self.buy_future(idx)
            self.active_light()
            QTest.qWait(500)
            if datetime.datetime.now() > finish_time:
                # 윈도우 종료
                self.shutdown_signal.emit()
                break
                # os.system("shutdown /s /t 0")
            ####################################
            #선물 진입

        self._status = False

    def buy_auto(self,idx):
        market = self.df_inverse.loc[idx,'market']
        주문최소금액 = self.df_inverse.loc[idx,'주문최소금액(USD)']
        현재가 = self.df_inverse.loc[idx,'현재가']
        보유코인합계 = self.df_inverse.loc[idx,'보유코인합계(USD)']
        배팅가능합계 = self.df_inverse.loc[idx,'배팅가능합계(USD)']
        배팅가능 = self.df_inverse.loc[idx,'free(qty)']
        ticker = self.df_inverse.loc[idx,'ticker']
        # print(market)
        if self.df_set.loc['rate_short','val'] == None:
            rate_short = 0
        else:
            rate_short = float(self.df_set.loc['rate_short','val'])
        안전마진 = 5 # 잔고가 펀딩비로 받는 금액의 5배 이상 있을 경우에만 진행
        funding_rate = 0.01/100
        # 배팅가능수량 = self.df_inverse.loc[idx,'free(qty)'] #contract 여유 잔고수량 불러오기
        # 진입수량 = self.df_inverse.loc[idx,'used(qty)'] #contract 진입수량 불러오기
        price = 현재가 + (현재가 * (rate_short) / 100)
        여유돈 = 보유코인합계*funding_rate*안전마진
        배팅가능금액 = 배팅가능합계 - 여유돈
        진입수량 = math.trunc(배팅가능금액) #소수점 절사
        order = True if 진입수량 >= 주문최소금액 else False

        # print(f"{market= }  {ticker= }  {배팅가능금액= }  {배팅가능합계= }   {여유돈= }   {보유코인합계= }   {funding_rate= } {진입수량= }   ")
        # if 배팅가능수량 * 주문가 > 주문최소금액: #최소수량보다 잔고가 많을경우마다 주문하면 마이너스피 일 때는 갖고있는 잔고에서 매번 수수료가 나가기 때문
        if order : # 현재 잔고가 진입수량*펀딩비율*5배 보다 많아야 매수 조건 성립 (최소수량보다 잔고가 많을경우마다 주문하면 마이너스피 일 때는 갖고있는 잔고에서 매번 수수료가 나가기 때문)
            df_open = pd.DataFrame()

            진입수량 = 진입수량//주문최소금액
            주문가 = self.common_def.price_to_precision(market=market,category='inverse',ticker=ticker,price=price)
            res = self.common_def.order_open(market=market, category='inverse', ticker=ticker, side='sell',
                                             orderType="limit",
                                             price=주문가, qty=진입수량)
            id = res['id']
            df_open.loc[id, 'market'] = market
            df_open.loc[id, 'ticker'] = ticker
            df_open.loc[id, '주문시간'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            df_open.loc[id, '주문수량'] = 진입수량
            df_open.loc[id, 'short비율'] = rate_short
            df_open.loc[id, 'spot비율'] = np.nan
            df_open.loc[id, 'id'] = id
            df_open.loc[id, '매수금액'] = 진입수량*주문최소금액
            df_open.loc[id, '상태'] = '매수주문'
            df_open.loc[id, 'category'] = 'inverse'
            df_open.loc[id, '주문가'] = 주문가
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | 자동매수 {ticker}: {진입수량=}, {주문가=}, {진입수량 * 주문가}')
            if not self.df_open.empty:
                print("=============")
                print(self.df_open)
                print(df_open)
                self.df_open = pd.concat([self.df_open, df_open], axis=0).astype(self.df_open.dtypes)
                print("**************")
            else:
                self.df_open = df_open.copy()
            self.qt_open.emit(self.df_open)
    def buy_manual(self,market,ticker,배팅금액,rate_spot,df_usdt):
        print("현물 매수 요청 수신!")
        df_open = pd.DataFrame()
        # try:
        category = 'spot'
        현재가 = self.common_def.fetch_ticker(market=market,ticker=ticker + '/USDT')['close']
        주문가 = 현재가 + (현재가 * rate_spot / 100)
        주문가 = self.common_def.price_to_precision(market=market,category=category, ticker=ticker, price=주문가)
        fee = 0.1
        레버리지 = 1
        진입수량 = (100 - (fee * 레버리지)) / 100 * 배팅금액 / 주문가
        진입수량 = self.common_def.amount_to_precision(market=market, category=category,ticker=ticker, amount=진입수량)
        df = df_usdt.loc[df_usdt['market']==market]
        보유현금 = df['free(USDT)'].tolist()[0]
        필요분 = (진입수량*주문가)+(진입수량*주문가)*0.001 #수수료 포함
        if 보유현금 < 필요분:
            print(f"USDT 부족 - 보유한 USDT: {보유현금}, 필요한 USDT {필요분}")
            return 0
        res = self.common_def.order_open(market= market,category=category, ticker=ticker, side='buy', orderType="limit",
                              price=주문가, qty=진입수량)
        id = res['id']
        df_open.loc[id, 'market'] = market
        df_open.loc[id, 'ticker'] = ticker
        df_open.loc[id, '주문시간'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        df_open.loc[id, '주문수량'] = 진입수량
        df_open.loc[id, 'spot비율'] = rate_spot
        df_open.loc[id, 'short비율'] = np.nan
        df_open.loc[id, 'id'] = id
        df_open.loc[id, '매수금액'] = 배팅금액
        df_open.loc[id, '상태'] = '매수주문'
        df_open.loc[id, 'category'] = 'spot'
        df_open.loc[id, '주문가'] = 주문가
        # df_open.loc[id, 'spot비율'] = rate_spot

        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | 수동매수 {ticker}: {진입수량=}, {주문가=}, {진입수량 * 주문가}')
        # elif market == 'binance':
        #     현재가 = self.common_def.fetch_ticker(market=market,Account=category, ticker=ticker+'/USDT')['close']
        #     주문가 = 현재가 + (현재가 * rate_spot / 100)
        #     주문가 = self.common_def.price_to_precision(market=market,category=category, ticker=ticker + 'USDT', price=주문가)
        #
        #     print('바이낸스 매수')
        # except Exception as e:
        #     print(f"오류 발생: 주문 확인요망 API 확인 등.. {e}")
        if not self.df_open.empty:
            self.df_open = pd.concat([self.df_open, df_open], axis=0).astype(self.df_open.dtypes)
            print('self.df_open.empty')
            print(self.df_open)
            print('***********')
            print(df_open)
            print('===========')
        else:
            self.df_open = df_open.copy()
            print('df_open.empty')
        self.qt_open.emit(self.df_open)
    def change_set(self,df_set):
        self.df_set = df_set
    def chegyeol_buy(self, id):
        ticker = self.df_open.loc[id, 'ticker']
        category = self.df_open.loc[id, 'category']
        market = self.df_open.loc[id, 'market']

        주문시간 = self.df_open.loc[id,'주문시간']
        qty = self.df_open.loc[id,'주문수량']
        주문시간 = datetime.datetime.strptime(주문시간,'%Y-%m-%d %H:%M')
        dict_chegyeol = self.fetch_order(market=market, ticker=ticker, id=id , category=category,qty=qty)
        if dict_chegyeol['체결'] == True:
            print(f"{ticker}  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간{dict_chegyeol['체결시간']}")
            self.df_closed.loc[id] = self.df_open.loc[id].copy()
            self.df_open.drop(index=id, inplace=True)
            self.df_closed.loc[id, '체결가'] = dict_chegyeol['체결가']
            self.df_closed.loc[id, '체결시간'] = dict_chegyeol['체결시간']
            self.df_closed.loc[id, '수수료'] = dict_chegyeol['수수료']
            self.df_closed.loc[id, '체결수량'] = dict_chegyeol['체결수량']
            self.df_closed.loc[id, '상태'] = '체결완료'

            if market == 'byubit':
                pass
            elif market == 'binance':
                # res_spot = self.ex_binance.fetch_balance()
                # free = res_spot[ticker]['free']

                self.common_def.transfer_to_inverse_wallet(market, ticker, dict_chegyeol['체결수량'])

        elif dict_chegyeol['체결'] == '주문취소':
            print(f'주문취소 - {market= } | {ticker= } | {category } | {qty= } | {id= }')
            self.df_open.drop(index=id, inplace=True)

        elif 주문시간 + datetime.timedelta(hours=8) < datetime.datetime.now(): #주문시간에서 8시간 동안 체결안되면 취소
            print(f'주문취소 - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | {market= } | {ticker= } | {category= } | {qty= } | {id= }')
            배팅금액 = self.df_open.loc[id, '매수금액']
            self.common_def.order_cancel(market,category,ticker,id)
            self.df_open.drop(index=id,inplace=True)
            if category == 'spot':
                rate_spot = float(self.df_set.loc['rate_spot','val'])
                self.buy_manual(market=market,ticker=ticker,배팅금액=배팅금액,rate_spot=rate_spot,df_usdt=self.df_inverse)

        elif dict_chegyeol['체결'] == '부분체결':
            self.df_open.loc[id,'상태'] = '부분체결'

    def buy_future(self,idx):
        market = self.df_inverse.loc[idx,'market']
        ticker = self.df_inverse.loc[idx,'ticker']
        # min_inverse = self.df_inverse.loc[idx,'주문최소금액(USD)']
        min_cont = self.df_inverse.loc[idx,'주문최소금액(USD)']
        used_qty = self.df_inverse.loc[idx, 'used(qty)']
        df = self.get_df(market, ticker, '4시간봉',10) #10일 전부터의 데이터 불러오기
        buy_signal = self.get_buy_signal(df,market,ticker)
        # print(self.df_inverse)
        future_leverage = 2
        if buy_signal == True:
            print(f" 매수신호 - {datetime.datetime.now()}  {market=}  {ticker= }")
            if market == 'bybit':
                symbol = f'{ticker}/USDT:USDT'
                market_info = self.ex_bybit.load_markets()[symbol]  # future 최소주문금액 조회
            elif market == 'binance':
                symbol = f'{ticker}/USDT'
                market_info = self.ex_binance.load_markets()[symbol]

            min_qty = market_info['limits']['amount']['min']

            if used_qty < min_qty or used_qty < min_cont:
                return # 보유수량이 선물 최소주문수량보다 작거나 인버스 주문최소금액보다 작을 경우 pass

            bet = used_qty/20 # 1/n 만큼만 배팅
            if min_qty > bet*future_leverage: #최소주문수량보다 작으면 (레버리지 3일경우 future = 3.3으로 되어야 함
                bet = min_qty/future_leverage




            price = self.df_inverse.loc[idx,'현재가']
            bet = bet * price
            category = 'inverse'
            res = self.common_def.order_open(market=market,category=category,ticker=ticker,side='buy',
                                             orderType='market',price=price,qty=bet)
            id = res['id']
            while True:
                time.sleep(1)
                dict_chegyeol = self.fetch_order(market=market,ticker=ticker,id=id,category=category,qty=bet)
                if dict_chegyeol['체결'] == True:
                    print(f"{ticker=},  {category=},  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간: {dict_chegyeol['체결시간']}")
                    break
            category = 'spot'
            현재가 = self.common_def.fetch_ticker(market=market,ticker=ticker + '/USDT')['close']
            price = res['close']  # 현물가격조회
            qty = bet / 현재가
            # res = amount_to_precision(bybit, 'bybit', 'spot', ticker, qty)
            qty = self.common_def.amount_to_precision(market=market, category=category, ticker=ticker, amount=qty)
            self.common_def.order_open(market=market,category=category,ticker=ticker,side='sell',
                                       orderType='market',price=price,qty=qty)
            while True:
                time.sleep(1)
                dict_chegyeol = self.fetch_order(market=market, ticker=ticker, id=id, category=category, qty=qty)
                if dict_chegyeol['체결'] == True:
                    print(f"{ticker=},  {category=},  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간: {dict_chegyeol['체결시간']}")
                    break

            self.common_def.order_open(market=market,category='future',ticker=ticker,side='buy',
                                       orderType='market',price=price,qty=qty)


    def get_buy_signal(self,df,market,ticker):
        if (df.loc[df.index[-3],'RSI14'] > 30) and (df.loc[df.index[-2],'RSI14'] < 30):
            return True
        if (df.loc[df.index[-3],'RSI18'] > 30) and (df.loc[df.index[-2],'RSI18'] < 30):
            return True
        if (df.loc[df.index[-3],'RSI30'] > 30) and (df.loc[df.index[-2],'RSI30'] < 30):
            return True
        if df.loc[df.index[-3],'이평20'] < df.loc[df.index[-3],'이평60']:
            if df.loc[df.index[-2],'이평20'] > df.loc[df.index[-2],'이평60']:
                return True
        return False

    def active_light(self):
        self.val_light.emit(self.bool_light)
        self.bool_light = not self.bool_light
        self.val_wallet.emit(self.wallet)
        self.val_time.emit(str(self.text_time))
        self.qt_have.emit(self.df_inverse)
        self.qt_open.emit(self.df_open)
        self.qt_closed.emit(self.df_closed)
        self.qt_future.emit(self.df_future)

    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.bool_light = False
            self.cond.wakeAll()
        elif not self._status:
            self.bool_light = False
            self.val_light.emit(self.bool_light)

    def fetch_inverse(self):
        # li_col = ['market','ticker','used(qty)', 'free(qty)', 'total(qty)', '현재가', '현재가(linear)',
        #           '보유코인합계(USD)', '배팅가능합계(USD)','주문최소금액(USD)']
        # self.df_inverse = pd.DataFrame(columns=li_col)
        self.df_inverse = pd.DataFrame()
        self.df_inverse_fetch = pd.DataFrame()
        # try:
        # 잔고 조회
        for market in ['bybit','binance']:
            if market == 'bybit' and self.ex_bybit == None:
                continue #None일 경우 건너뛰기
            if market == 'binance' and self.ex_binance == None:
                continue
            balance, usdt_free, usdt_total = self.fetch_balance(market)
            # have_usdt = float(self.fetch_balance(accountType='UNIFIED', ticker='USDT', balance='잔고'))
            # all_usdt = float(self.fetch_balance(accountType='UNIFIED', ticker='USDT', balance='보유'))
            for ticker in balance:
                if not ticker == 'USDT':
                    # self.df_inverse.loc[f"{market}_{ticker}", 'category'] = balance[ticker]['category']
                    self.df_inverse.loc[f"{market}_{ticker}", 'free(qty)'] = balance[ticker]['free']
                    # self.df_inverse.loc[f"{market}_{ticker}", 'free(qty)'] = 0.0002
                    self.df_inverse.loc[f"{market}_{ticker}", 'used(qty)'] = balance[ticker]['used']
                    self.df_inverse.loc[f"{market}_{ticker}", 'total(qty)'] = balance[ticker]['total']
                    self.df_inverse.loc[f"{market}_{ticker}", '주문최소금액(USD)'] = round(balance[ticker]['주문최소금액'])
                    self.df_inverse.loc[f"{market}_{ticker}", 'ticker'] = ticker
                    self.df_inverse.loc[f"{market}_{ticker}", 'market'] = market
                    self.df_inverse.loc[f"{market}_{ticker}", '현재가'] = balance[ticker]['현재가']
                    # self.df_inverse.loc[f"{market}_{ticker}", '현재가(linear)'] = balance[ticker]['현재가(linear)']
                    self.df_inverse.loc[f"{market}_{ticker}", 'free(USDT)'] = usdt_free
                    self.df_inverse.loc[f"{market}_{ticker}", 'total(USDT)'] = usdt_total
                    self.df_inverse.loc[f"{market}_{ticker}", '배팅가능합계(USD)'] = round(balance[ticker]['free']*balance[ticker]['현재가'],1)
                    self.df_inverse.loc[f"{market}_{ticker}", '보유코인합계(USD)'] = round(balance[ticker]['total']*balance[ticker]['현재가'],1)
        if not self.df_inverse.empty:
            self.wallet = str(round(self.df_inverse['free(USDT)'].sum()))
            self.df_inverse = self.df_inverse[self.df_inverse['주문최소금액(USD)']<self.df_inverse['보유코인합계(USD)']]
            self.df_inverse = self.df_inverse.sort_index(ascending=False)
            self.df_inverse_fetch = self.df_inverse[self.list_compare_col]
    def fetch_future(self):
        self.df_future = pd.DataFrame()
        common_col = ['unrealizedPnl', 'contracts','liquidationPrice', 'side', 'markPrice', 'entryPrice','매수금액','market','symbol']
        for market in ['bybit','binance']:
            if market == 'bybit':
                if not self.ex_bybit == None:
                    res = self.ex_bybit.fetch_positions()
                    for data in res:
                        data['매수금액'] = data['collateral']
                        # del data['info']
                    df = pd.DataFrame(res)
                    if 'symbol' in df.columns.tolist():
                        df.index = 'bybit_' + df['symbol'].copy()
                        df['market'] = 'bybit'
                        # df['수익률'] = df['손익'] / df['매수금액'] * 100
                        # df = df[['symbol', '현재가', '레버리지', '방향', '수익률', '손익', '보유수량', '매수금액', '진입가', '청산가', 'marginMode']]
                        df = df[common_col]

                        self.df_future = pd.concat([self.df_future,df],axis=0)
                    # print(self.df_future)
            if market == 'binance':
                if not self.ex_binance == None:
                    res = self.ex_binance.fetch_positions()
                    for data in res:
                        data['매수금액'] = float(data['info']['isolatedWallet'])
                        # del data['info']
                    df = pd.DataFrame(res)
                    if 'symbol' in df.columns.tolist():
                        df.index = 'binance_' + df['symbol'].copy()
                        df['market'] = 'binance'
                        df = df[common_col]
                        # df.rename(columns={'unrealizedPnl': '손익', 'leverage': '레버리지', 'contracts': '보유수량',
                        #                    'liquidationPrice': '청산가',
                        #                    'side': '방향', 'markPrice': '현재가', 'entryPrice': '진입가'}, inplace=True)
                        self.df_future = pd.concat([self.df_future,df],axis=0, ignore_index=True)
        if not self.df_future.empty:
            self.df_future['symbol'] = self.df_future['symbol'].str.split('/').str[0] #/기준 왼쪽만 남겨서 BTC만 추출
            self.df_future.rename(columns={'unrealizedPnl': '손익', 'contracts': '보유수량',
                               'liquidationPrice': '청산가','symbol': 'ticker',
                               'side': '방향', 'markPrice': '현재가', 'entryPrice': '진입가'},
                                inplace=True)
            # print(self.df_future)
            self.df_future['수익률'] = self.df_future['손익'] / self.df_future['매수금액'] * 100

    def fetch_order(self, market, ticker, id, category, qty):
        # print(f"{market= }    {id=}    {ticker= }   {category= }")
        # 주문수량 = self.df_open.loc[id, '주문수량']
        주문수량 = qty
        ord_open = self.fetch_open_orders(market, ticker, category, id)
        if ord_open == None:  # 체결일 경우
            ord_closed = self.fetch_closed_orders(market, id, ticker, category)  # open 주문과 close 주문 2중으로 확인
            # pprint(ord_closed)
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
                체결시간 = self.common_def.stamp_to_str(ord_closed['timestamp'])
                if 주문수량 >= 체결수량:
                    print(f"체결완료 - {ticker= }  {category= } {체결수량=} ")
                return {'체결': True, '체결가': 진입가, '체결수량':체결수량, '수수료':진입수수료,'체결시간':체결시간}
        else:
            return {'체결': False}


    def fetch_open_orders(self,market,ticker,category,id):  # 미체결주문 조회
        # try:
        if market == 'bybit':
            if category == 'spot':
                ticker = ticker+'/USDT'
            else:
                ticker = ticker+'USD'
            params = {}
            res = self.ex_bybit.fetch_open_orders(symbol=ticker, params=params)
        elif market == 'binance':
            if category == 'spot':
                ticker = ticker+'/USDT'
            else:
                ticker = ticker+'/USD'
            params = {}
            res = self.ex_binance.fetch_open_orders(symbol=ticker, params=params)
        for order in res:
            if order['id'] == id:
                return order
        # except:
        #     order = {'체결':'조회할 수 없음'}
        #     return order
                # return res
            # except:
            #     print('open 조회 에러')
            #     order={'id':None,'info':{'orderStatus':None}}
            #     return order
    def fetch_closed_orders(self,market, id, ticker, category):  # 체결주문 조회
        params = {}
        # try:
        if market == 'bybit':
            if category == 'spot':
                ticker = ticker+'/USDT'
            else:
                ticker = ticker+'USD'
            # order = self.ex_bybit.fetch_closed_orders(self.ticker, params=params)
            res = self.ex_bybit.fetch_closed_orders(symbol=ticker, params=params)
        if market == 'binance':
            if category == 'spot':
                ticker = ticker+'/USDT'
            else:
                ticker = ticker+'/USD'
            res = self.ex_binance.fetch_closed_orders(symbol=ticker, params=params)
        for order in res:
            if order['id'] == id:
                return order
        # except:
        #     print('close 조회 에러')
        #     order={'id':None,'info':{'orderStatus':None}}
        #     # order = []
        #     return order
    def fetch_cancel_orders(self,market, id, ticker, category):  # 체결주문 조회
        params = {}
        # try:
        if market == 'bybit':
            if category == 'spot':
                ticker = ticker+'/USDT'
            else:
                ticker = ticker + 'USD'
            # order = self.ex_bybit.fetch_closed_orders(self.ticker, params=params)
            res = self.ex_bybit.fetch_canceled_orders(symbol=ticker, params=params)
        if market == 'binance':
            if category == 'spot':
                ticker = ticker+'/USDT'
            else:
                ticker = ticker + '/USD'
            res = self.ex_binance.fetch_canceled_orders(symbol=ticker, params=params)
        for order in res:
            if order['id'] == id:
                return order
        # except:
        #     print('close 조회 에러')
        #     order={'id':None,'info':{'orderStatus':None}}
        #     # order = []
        #     return order

    def get_df(self,market,ticker,bong,since_day):
        dict_bong_stamp = {'1분봉': 1 * 60, '3분봉': 3 * 60, '5분봉': 5 * 60, '15분봉': 15 * 60, '30분봉': 30 * 60,
                           '60분봉': 60 * 60, '4시간봉': 240 * 60, '일봉': 1440 * 60,
                           '주봉': 10080 * 60}
        dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉': '4h',
                     '일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
        present = datetime.datetime.now()
        date_old = present.date() - datetime.timedelta(days=int(since_day))
        stamp_date_old = self.common_def.datetime_to_stamp(date_old)
        i = 0
        ohlcv = []
        while True:
            try:
                if market == 'bybit':
                    list_ohlcv = self.ex_bybit.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong],
                                                   limit=10000, since=int(stamp_date_old * 1000))  # 밀리초로 전달
                if market == 'binance':
                    list_ohlcv = self.ex_binance.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong],
                                                   limit=10000, since=int(stamp_date_old * 1000))  # 밀리초로 전달
                ohlcv = ohlcv + list_ohlcv
                stamp_date_old = list_ohlcv[-1][0] / 1000 + dict_bong_stamp[bong]  # 다음봉 시간 계산
                if stamp_date_old > time.time():
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
        df = self.common_def.convert_df(df)

        # df.index = df.index - pd.Timedelta(hours=9)
        return df

    def fetch_balance(self,market):
        if market == 'bybit':
            res = self.ex_bybit.fetch_balance()


        elif market == 'binance':
            res_spot = self.ex_binance.fetch_balance()
            res = self.ex_binance.fetch_balance(params={"type": 'delivery'})
            markets_binance = self.ex_binance.load_markets()
            usdt_free = res_spot['USDT']['free']
            usdt_total = res_spot['USDT']['total']


        # held_coins = {}
        balance = {}

        for currency, data in res['total'].items():
            # if data > 0 and currency in res and currency != 'USDT':
            if data > 0 and currency in res:
                if market == 'bybit':
                    if currency in self.list_bybit_inverse: #바이비트의 경우 인버스 종목이 한정적
                        balance[currency] = res[currency]
                        balance_bybit = self.common_def.fetch_account_info_bybit(Account='inverse',
                                                                                 symbol=currency + 'USD')
                        balance[currency]['주문최소금액'] = float(balance_bybit['lotSizeFilter']['minOrderQty'])  # inverse 최소주문USDT구하기

                        balance[currency]['현재가']= self.common_def.fetch_ticker(market,currency + 'USD')['close']
                        # balance[currency]['현재가(linear)']= self.common_def.fetch_ticker(market,currency + 'USDT')['close']
                        # balance[currency]['category'] = 'inverse/spot'
                    elif currency == 'USDT':
                        usdt_free = res[currency]['free']
                        usdt_total = res[currency]['total']
                if market == 'binance':
                    balance[currency] = res[currency]
                    ticker_info = markets_binance[f'{currency}/USD:{currency}']
                    if currency == 'BTC':
                        balance[currency]['주문최소금액'] = 100
                    else:
                        balance[currency]['주문최소금액'] = 10

                    balance[currency]['현재가'] = self.common_def.fetch_ticker(market, currency + 'USD_PERP')['close']
#                     balance[currency]['category'] = 'inverse/spot'
                    # balance[currency]['현재가(linear)'] = self.common_def.fetch_ticker(market, currency + '/USDT')['close']
        return balance, usdt_free, usdt_total


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
    buy_signal = pyqtSignal(str,str,int,float,pd.DataFrame)
    set_signal = pyqtSignal(pd.DataFrame)

    def __init__(self):
        super().__init__()
        self.init_file()
        self.set_UI()
        # self.session = self.make_exchange_bybit()
        self.time_sync()
        time.sleep(2)
        self.ex_bybit,self.session = self.make_exchange_bybit_ccxt()
        self.ex_binance = self.make_exchange_binance()
        self.defines = common_def(self.ex_bybit,self.session,self.ex_binance)
        self.qtable_open(self.df_open)
        self.qtable_closed(self.df_closed)

        self.funding_time_old = int(time.time())
        # self.get_funding_time()

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
        self.QT_trade_history = QTableWidget()
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
        self.QL_repeat_per = QLineEdit()
        self.QL_rate_spot = QLineEdit()
        self.QL_rate_short = QLineEdit()
        self.QL_rate_spot.setText(str(self.df_set.loc['rate_spot', 'val']))
        self.QL_rate_short.setText(str(self.df_set.loc['rate_short', 'val']))
        self.QPB_manual_buy_binance = QPushButton('BINANCE 현물매수')
        self.QPB_chart_bybit = QPushButton('펀딩비율바이비트')
        self.QPB_chart_binance = QPushButton('펀딩비율바이낸스')
        self.QCB_auto = QCheckBox('오토스타트')
        if self.df_set.loc['auto_start', 'val'] == 'auto':
            self.QCB_auto.setChecked(True)
        else:
            self.QCB_auto.setChecked(False)
        self.QCB_off = QComboBox()
        self.QCB_off.addItems(['자동꺼짐','1분후','5분후','10분후','30분후','1시간후','설정안함'])
        self.QLE_api_bybit = QLineEdit()
        self.QLE_secret_bybit = QLineEdit()
        self.QPB_api_save_bybit = QPushButton('bybit API 저장')
        self.QLE_api_binance = QLineEdit()
        self.QLE_secret_binance = QLineEdit()
        self.QPB_api_save_binance = QPushButton('binance API 저장')
        dict_grid = {
            self.QPB_start: self.QPB_stop,
            self.QCB_auto: self.QCB_off,
            QLabel('합계(USD)'):self.QL_wallet,
            QLabel('누적수수료'):self.QL_fee_sum,
            QLabel('누적매수'):self.QL_buy_sum,
            QLabel('펀딩비시간'):self.QL_time,
            QLabel('재투자비율(%)'):self.QL_repeat_per,
            QLabel('현물주문(%)'):self.QL_rate_spot,
            QLabel('인버스주문(%)'):self.QL_rate_short,
            QLabel('ticker(현물)'):self.QL_manual_ticker,
            QLabel('매수금액'):self.QL_manual_price,
            self.QPB_manual_buy_binance:self.QPB_manual_buy_bybit,
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
        QW_grid.setMaximumSize(1980,100)


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
        self.QT_trade_history.setStyleSheet(StyleSheet_Qtable)
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
        QSH_table.addWidget(self.QT_trade_history)
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
        if market == 'binance':
            if not self.QLE_api_binance.text() == '':
                self.df_set.loc[f'api_{market}','val']=self.QLE_api_binance.text()
            if not self.QLE_secret_binance.text() == '':
                self.df_set.loc[f'secret_{market}','val']=self.QLE_secret_binance.text()
            self.QLE_api_binance.clear()
            self.QLE_secret_binance.clear()
        self.df_set.to_sql('set', self.conn, if_exists='replace')

    def init_file(self):
        db_file = 'DB/Funding_Strategy.db'
        if not os.path.isfile(db_file):
            self.conn = sqlite3.connect(db_file)
            li = ['market','ticker', 'category', '주문가', '주문수량', '매수금액', '수수료', '수익률',
                  '주문시간', '체결시간', '체결가', '체결수량','id', '상태', '펀딩비', 'spot비율',
                  'short비율']
            self.df_open = pd.DataFrame(columns=li)
            self.df_closed = pd.DataFrame(columns=li)
            self.df_closed.to_sql('closed', self.conn, if_exists='replace')
            self.df_open.to_sql('open', self.conn, if_exists='replace')

            # li_col = ['보유자산합계', '배팅가능합계']
            # self.df_history = pd.DataFrame(columns=li_col)
            # self.df_history.to_sql('history', self.conn, if_exists='replace')

            self.list_compare_col = ['market', 'ticker', 'free(qty)', 'free(USDT)', 'total(USDT)']
            self.df_inverse = pd.DataFrame(index=[], columns=self.list_compare_col)
            self.df_inverse.to_sql('inverse', self.conn, if_exists='replace')

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
            self.df_open = pd.read_sql(f"SELECT * FROM 'open'", self.conn).set_index('index')
            self.df_closed = pd.read_sql(f"SELECT * FROM 'closed'", self.conn).set_index('index')
            self.df_inverse = pd.read_sql(f"SELECT * FROM 'inverse'", self.conn).set_index('index')
            # self.list_compare_col = self.df_inverse.columns.to_list()
            self.df_set = pd.read_sql(f"SELECT * FROM 'set'", self.conn).set_index('index')
            funding_time = pd.to_datetime(self.df_set.loc['funding_time', 'val'])
            current_t = datetime.datetime.now().replace(microsecond=0)
            if funding_time < current_t:
                self.df_set.loc['funding_time', 'val'] = self.get_funding_time(datetime.datetime.now().replace(microsecond=0))
                self.df_set.to_sql('set', self.conn, if_exists='replace')

        self.df_open_old = self.df_open.copy()
        self.df_closed_old = self.df_closed.copy()

    def fetch_inverse_list_bybit(self):
        # 바이비트 inverse 종목 정리
        list_bybit_inverse = []
        if not self.ex_bybit == None:
            markets = self.ex_bybit.load_markets()
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
        return list(set(list_bybit_inverse))
    def fetch_inverse_list_binance(self):
        # 바이낸스 inverse 종목 정리
        if not self.ex_binance == None:
            res = self.ex_binance.fetch_balance(params={"type": 'delivery'})
            list_binance_inverse = res['total'].keys()
        else:
            list_binance_inverse = []
        return list(set(list_binance_inverse))
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

    def view_chart(self,market):
        plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우의 맑은 고딕
        def weighted_average(values):
            """최근 데이터에 더 높은 가중치를 주어 평균 계산"""
            weights = [i + 1 for i in range(len(values))]  # 가중치 (1, 2, 3, ... n)
            weighted_sum = sum(v * w for v, w in zip(values, weights))
            return weighted_sum / sum(weights)  # 가중 평균

        def simple_average(values):
            """단순 평균값 계산"""
            return sum(values) / len(values)
        def pad_list(lst,length):
            """길이가 10보다 작으면 앞쪽을 0으로 채워 10으로 맞춤"""
            return [0] * (length - len(lst)) + lst if len(lst) < length else lst

        def add_accumulated_value(data_list, initial_amount=1000):
            current_amount = initial_amount

            for item in data_list:
                # 현재 funding rate 값을 가져옵니다
                rate = item['fundingRate']

                # 현재 금액에 rate를 적용하여 변화량을 계산합니다
                change = initial_amount * rate

                # 현재 금액을 업데이트합니다
                current_amount += change

                # 누적합 키를 추가합니다
                item['accumulated'] = current_amount
                del item['info']
            return data_list
        if market == 'bybit':
            list_inverse = self.fetch_inverse_list_bybit()
        elif market == 'binance':
            res = self.ex_binance.fetch_balance(params={"type": 'delivery'})
            list_inverse = list(res['total'].keys())

        top_10_weighted = {}
        top_10_simple = {}
        dict_data = {}
        init_USD = 1000
        for ticker in list_inverse:
            # out_lately = self.ex_bybit.fetch_funding_rate_history(symbol=f'{ticker}USD')
            out_lately = self.defines.fetch_funding_rates(market=market,ticker=ticker,since=None)
            since = out_lately[0]['timestamp']
            origin = datetime.datetime.now() - datetime.timedelta(days=365)
            while self.defines.stamp_to_datetime(since) > origin:
                since = since - 8 * 3600 * 1000 * 201  # 8시간 , 한시간에 3600초, 밀리초 1000, 최대 200개 조회가능
                # out = self.ex_bybit.fetch_funding_rate_history(symbol=f'{ticker}USD', since=since)
                out = self.defines.fetch_funding_rates(market=market,ticker=ticker,since=since)
                out.extend(out_lately)
                out_lately = out

            data = [x['fundingRate'] for x in out_lately]
            timestamps = [x['timestamp'] for x in out_lately]
            # ADA, BTC, ETH의 funding rate 데이터 (예제)
            # 1️⃣ 각 리스트의 평균값 계산
            w_avg = weighted_average(data)  # 가중 평균 계산
            s_avg = simple_average(data)  # 단순 평균 계산

            out_lately = add_accumulated_value(out_lately, init_USD)
            # dict_data[ticker] = result
            # 가중 평균 상위 10개 선택
            dict_data[ticker] = out_lately


        # 1. 각 티커별 fundingRate의 단순평균값 계산
        simple_avg = {}
        for ticker, values in dict_data.items():
            rates = [item['fundingRate'] for item in values]
            simple_avg[ticker] = sum(rates) / len(rates)

        # 2. 각 티커별 fundingRate의 가중평균값 계산 (가중치는 시간 간격으로 계산)
        weighted_avg = {}
        for ticker, values in dict_data.items():
            if len(values) <= 1:
                weighted_avg[ticker] = simple_avg[ticker]
                continue

            rates = [item['fundingRate'] for item in values]
            timestamps = [item['timestamp'] for item in values]

            # 시간 간격 계산
            time_diffs = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
            time_diffs.append(time_diffs[-1])  # 마지막 간격은 이전 간격과 동일하게 처리

            # 가중평균 계산
            weighted_sum = sum(rates[i] * time_diffs[i] for i in range(len(rates)))
            total_time = sum(time_diffs)
            weighted_avg[ticker] = weighted_sum / total_time

        # 3. 마지막 accumulated 값 추출
        last_rates = {}
        for ticker, values in dict_data.items():
            # 타임스탬프 기준으로 정렬하여 마지막 항목의 fundingRate 가져오기
            sorted_values = sorted(values, key=lambda x: x['timestamp'])
            last_rates[ticker] = sorted_values[-1]['accumulated']

        # 4. 각 지표별 상위 10개 티커 선정
        simple_avg_top10 = dict(sorted(simple_avg.items(), key=lambda x: x[1], reverse=True)[:10])
        weighted_avg_top10 = dict(sorted(weighted_avg.items(), key=lambda x: x[1], reverse=True)[:10])
        last_rates_top10 = dict(sorted(last_rates.items(), key=lambda x: x[1], reverse=True)[:10])

        # 5. 단순평균과 가중평균 상위 10개의 교집합 계산
        intersection_tickers = set(simple_avg_top10.keys()) & set(weighted_avg_top10.keys())
        print(f"\n단순평균과 가중평균 상위 10개의 교집합: {intersection_tickers}")

        # 6. BTC 기준 날짜 생성
        btc_dates = [datetime.datetime.strptime(item['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ') for item in dict_data['BTC']]
        reference_dates = [d.strftime('%Y-%m-%d %H:%M') for d in btc_dates]

        # 7. 시각화
        plt.figure(figsize=(12, 14))

        # 7.1 마지막 fundingRate 상위 10개 티커 시각화
        plt.subplot(3, 1, 1)
        tickers = list(last_rates_top10.keys())
        rates = list(last_rates_top10.values())
        plt.bar(tickers, rates)
        plt.title('accumulated 상위 10개 암호화폐')
        plt.ylabel('accumulated')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 7.2 단순평균 상위 10개 시각화
        plt.subplot(3, 1, 2)
        plt.bar(simple_avg_top10.keys(), simple_avg_top10.values())
        plt.title('단순평균 fundingRate 상위 10개 암호화폐')
        plt.ylabel('fundingRate')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 7.3 가중평균 상위 10개 시각화
        plt.subplot(3, 1, 3)
        plt.bar(weighted_avg_top10.keys(), weighted_avg_top10.values())
        plt.title('가중평균 fundingRate 상위 10개 암호화폐')
        plt.ylabel('fundingRate')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig('top10_crypto_funding_analysis.png', dpi=300)
        plt.show()

        # 8. 누적 금액 그래프 - 마지막 fundingRate 상위 10개 티커에 대해서만
        plt.figure(figsize=(12, 6))
        for ticker in last_rates_top10.keys():
            if ticker in dict_data:
                # 해당 티커의 날짜와 누적 금액 추출
                ticker_dates = [datetime.datetime.strptime(item['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ') for item in dict_data[ticker]]
                ticker_accumulated = [item['accumulated'] for item in dict_data[ticker]]

                # BTC 기준 날짜에 맞추기
                mapped_dates = []
                mapped_values = []
                btc_datetime = [datetime.datetime.strptime(item['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ') for item in dict_data['BTC']]

                for btc_date in btc_datetime:
                    found = False
                    for i, ticker_date in enumerate(ticker_dates):
                        if ticker_date == btc_date:
                            mapped_dates.append(btc_date)
                            mapped_values.append(ticker_accumulated[i])
                            found = True
                            break
                    if not found:
                        mapped_dates.append(btc_date)
                        mapped_values.append(init_USD)  # 해당 날짜에 데이터가 없으면 init_USD 으로 표시

                plt.plot(mapped_dates, mapped_values, label=ticker)

        plt.title('BTC 기준 마지막 accumulated 상위 10개 암호화폐의 누적 금액 비교')
        plt.xlabel('날짜')
        plt.ylabel('누적 금액 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.7)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        # plt.savefig('top10_accumulated_comparison.png', dpi=300)
        plt.show()

        # 9. 단순평균과 가중평균 상위 10개의 교집합에 대한 데이터프레임 생성
        intersection_df = pd.DataFrame({
            'Ticker': list(intersection_tickers),
            'Last_Rate': [last_rates[ticker] for ticker in intersection_tickers],
            'Simple_Average': [simple_avg[ticker] for ticker in intersection_tickers],
            'Weighted_Average': [weighted_avg[ticker] for ticker in intersection_tickers]
        })

        # 단순평균 기준으로 내림차순 정렬
        intersection_df = intersection_df.sort_values('Simple_Average', ascending=False)

        print("\n단순평균과 가중평균 상위 10개의 교집합에 대한 데이터:")
        print(intersection_df)

    def setting(self):
        if self.QCB_auto.isChecked() == True:
            self.df_set.loc['auto_start','val'] = "auto"
        else:
            self.df_set.loc['auto_start','val'] = "manual"
        if not self.QCB_off.currentText() == '자동꺼짐':
            self.df_set.loc['auto_finish','val'] = self.QCB_off.currentText()
        self.df_set.to_sql('set', self.conn, if_exists='replace')

    def onStartButtonClicked(self):
        self.ex_bybit, self.session = self.make_exchange_bybit_ccxt()
        self.ex_binance = self.make_exchange_binance()
        self.defines = common_def(self.ex_bybit, self.session, self.ex_binance)
        # self.defines.time_sync()

        list_bybit_inverse = self.fetch_inverse_list_bybit()
        # list_binance_inverse = self.fetch_inverse_list_binance()
        start_time = datetime.datetime.now().replace(microsecond=0)
        self.df_set.loc['start_time', 'val'] = start_time

        self.thread = do_trade(self,self.session,self.ex_bybit,self.ex_binance,self.df_open,self.df_closed,
                               list_bybit_inverse,self.df_inverse,self.df_set)
        self.thread.start()

        self.thread.qt_open.connect(self.qtable_open)
        self.thread.qt_closed.connect(self.qtable_closed)
        # self.thread.qt_history.connect(self.qtable_history)
        self.thread.qt_have.connect(self.qtable_have)
        self.thread.val_light.connect(self.effect_start)
        self.thread.val_wallet.connect(self.QL_wallet.setText)
        self.thread.val_time.connect(self.QL_time.setText)
        self.thread.qt_set.connect(self.save_set)
        self.thread.qt_future.connect(self.qtable_future)
        self.thread.qt_inverse.connect(self.qtable_inverse)
        self.thread.shutdown_signal.connect(self.show_shutdown_dialog)

        self.set_signal.connect(self.thread.change_set)
        self.buy_signal.connect(self.thread.buy_manual)

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
        self.buy_signal.emit(market,ticker,배팅금액,rate_spot,self.df_qtable_have)

    def save_set(self,df):
        df.to_sql('set',self.conn,if_exists='replace')


    def qtable_have(self,df):
        if not df.empty:
            df['free(qty)'] = df['free(qty)'].apply(lambda int_num: "{:,}".format(int_num))
            df['현재가'] = df['현재가'].apply(lambda int_num: "{:,}".format(int_num))
            # df['현재가(linear)'] = df['현재가(linear)'].apply(lambda int_num: "{:,}".format(int_num))
            df['보유코인합계(USD)'] = df['보유코인합계(USD)'].apply(lambda int_num: "{:,}".format(int_num))
            df['배팅가능합계(USD)'] = df['배팅가능합계(USD)'].apply(lambda int_num: "{:,}".format(int_num))
            df = df[['market', 'ticker', 'free(qty)', 'used(qty)', 'total(qty)', '현재가', '배팅가능합계(USD)','보유코인합계(USD)', '주문최소금액(USD)', 'free(USDT)', 'total(USDT)']]
            self.set_table_make(self.QT_trade_inverse, df)
            self.df_qtable_have = df.copy()

    def qtable_inverse(self,df): #iverse 자산 변경 시 저장을 위해
        df.to_sql('inverse', self.conn, if_exists='replace')
    def qtable_future(self,df):
        if not df.empty:
            df = df[['market','ticker','보유수량', '매수금액', '현재가', '방향', '수익률', '손익',
                     '진입가', '청산가']]
            self.set_table_make(self.QT_trade_future, df)
        else:
            self.set_table_make(self.QT_trade_future, pd.DataFrame())
    def qtable_open(self,df):
        df_compare = df[['상태','id']]
        if not self.df_open_old.equals(df_compare):
            df.to_sql('open',self.conn,if_exists='replace')
            self.df_open_old = df_compare.copy()
        # print(df)
        df_active = df[['market','ticker', '주문시간', '주문수량', '매수금액', '주문가', '상태', 'category', 'spot비율','short비율','id']]
        if not df_active['매수금액'].isna().any():
            df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_open, df_active)

    def qtable_closed(self, df):
        if not self.df_closed_old.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
            df.to_sql('closed', self.conn, if_exists='replace')
            self.df_closed_old = df.copy()
        df_active = df[['market','ticker', '체결시간', '주문수량', 'id', '수수료', '매수금액', '주문가', '상태',
                  'category', 'spot비율','short비율']]
        df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_history, df_active)

    # def qtable_history(self, df):
    #     if not self.df_history.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
    #         df.to_sql('history', self.conn, if_exists='replace')
    #         self.df_history_old = df.copy()

    def set_table_make(self, table,df):
        table.setSortingEnabled(False)
        table.clear()
        table.setRowCount(len(df.index))
        table.setColumnCount(len(df.columns))
        header = table.horizontalHeader()# 컬럼내용에따라 길이 자동조절
        for i in range(len(df.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(df.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents) # 컬럼내용에따라 길이 자동조절
        # for i in range(len(df.index)):
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(df.index[i])[5:10]))
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
        # table.verticalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True) #소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가


    def make_exchange_bybit_ccxt(self):
        api = self.df_set.loc['api_bybit','val']
        secret = self.df_set.loc['secret_bybit','val']
        if api == None or secret == None:
                # or np.isnan(api) or np.isnan(secret)):
            print('bybit API 확인 필요')
            bybit = None
            session = None
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
                print(bybit)
            except:
                print("에러 - make_exchange_bybit_ccxt ")
                bybit = None
                session = None
        return bybit, session

    def make_exchange_binance(self):
        api = self.df_set.loc['api_binance', 'val']
        secret = self.df_set.loc['secret_binance', 'val']
        if api == None or secret == None:
            # or np.isnan(api) or np.isnan(secret):
            print('binance API 확인 필요')
            binance = None
        else:
            binance = ccxt.binance(config={
                'apiKey': api,
                'secret': secret,
                'enableRateLimit': True,
                'options': {'position_mode': True, },
            })
            print(binance)
            binance.load_markets()
        return binance
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

class common_def():
    def __init__(self,ex_bybit,session,ex_binance):
        self.ex_bybit = ex_bybit
        self.session = session
        self.ex_binance = ex_binance

    def fetch_ticker(self,market, ticker):
        if market == 'bybit':
            return self.ex_bybit.fetch_ticker(ticker)
            # return self.session.get_tickers(
            #     category=Account,
            #     symbol=ticker,
            # )['result']['list'][0]
        elif market == 'binance':
            return self.ex_binance.fetch_ticker(ticker)
    def fetch_account_info_bybit(self, Account, symbol):
        return self.session.get_instruments_info(
            category=Account,  # spot, linear, inverse, option
            symbol=symbol, # BTC, BTCUSDT, BTCUSD
        )['result']['list'][0]



    def order_open(self, market, category, ticker, side, orderType, price, qty):
        if market == 'bybit':
            if category == 'spot':
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'/USDT'
                leverage = 1
            elif category == 'inverse':
                params = {'positionIdx': 0}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                symbol = ticker +'USD'
                leverage = 1
            elif category == 'future':
                symbol = ticker + 'USDT'
                if side == 'buy':
                    params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                elif side == 'sell':  # 지정가 open short
                    params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            try:
                self.ex_bybit.set_leverage(leverage=leverage, symbol=symbol)
            except:
                pass
            # print(f"symbol={ticker}, type={orderType}, side={side}, amount={qty},price= {price}, params= {params}")
            # print(f"{market= }   {symbol= }   {orderType= }   {side= }    {qty= }   {price= }")
            res = self.ex_bybit.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
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
            elif category == 'future':
                symbol = ticker + 'USDT'
                if side == 'buy':
                    pass
                    # params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                elif side == 'sell':  # 지정가 open short
                    pass
            try:
                self.ex_binance.set_leverage(leverage=leverage, symbol=symbol)
            except:
                pass
            res = self.ex_binance.create_order(symbol=symbol, type=orderType, side=side, amount=qty,
                                             price=price, params=params)
        QTest.qWait(1000)
        #     if category == 'spot':
        #         rate = 0
        #     elif category == 'inverse':
        #         rate = 1
        #     else:
        #         raise
        #     res = self.session.place_order(
        #         category=category,  # spot, linear, inverse, option
        #         symbol=ticker,
        #         side=side,  # Buy, Sell
        #         orderType=orderType,  # Market, Limit
        #         qty=qty,
        #         price=price,
        #         timeInForce="PostOnly",
        #         # orderLinkId="spot-test-postonly",
        #         isLeverage=rate,  # 0(default): false then spot trading, 1: true then margin trading
        #         orderFilter="Order",
        #     )
        # else:
        #     pass
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
            self.ex_binance.cancel_order(id=order_id,symbol=symbol,params={})
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
            return float(self.ex_bybit.amount_to_precision(symbol=symbol,amount=amount))
        elif market == 'binance':
            if category == 'spot':
                symbol = ticker + '/USDT'
            elif category == 'inverse':
                symbol = ticker + 'USD'
            return float(self.ex_binance.amount_to_precision(symbol=symbol, amount=amount))
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
            return float(self.ex_bybit.price_to_precision(symbol=symbol, price=price))
        elif market == 'binance':
            if category == 'spot':
                symbol = ticker+'/USDT'
            elif category == 'inverse':
                symbol = ticker+'/USD'
            return float(self.ex_binance.price_to_precision(symbol=symbol,price=price))
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
    def transfer_to_inverse_wallet(self,market, currency, amount):
        if market == 'bybit':
            while True:
                id = str(uuid.uuid1())
                print(id)
                res = self.session.create_internal_transfer(
                    transferId=id,
                    coin=currency,  # BTC
                    amount=amount,
                    fromAccountType="UNIFIED",  # UNIFIED (spot 계좌)
                    toAccountType="CONTRACT",  # CONTRACT (inverse 계좌)
                )

                if res['retMsg'] == 'success':
                    print(f'{currency}  {amount} 개  inverse로 계좌이동 완료')
                    break
                print(f'{currency} 계좌 이동중...')
                QTest.qWait(1000)
        elif market == 'binance':
            try:
                self.ex_binance.transfer(currency, amount, 'spot', 'inverse')
            except Exception as e:
                print(f"자금 이동 중 오류 발생 [transfer_to_inverse_wallet]: {e} {currency= } {amount= }")
                #     return False
    def transfer_to_linear_wallet(self,market, currency, amount):
        if market == 'bybit':
            while True:
                id = str(uuid.uuid1())
                print(id)
                res = self.session.create_internal_transfer(
                    transferId=id,
                    coin=currency,  # BTC
                    amount=amount,
                    fromAccountType="UNIFIED",  # UNIFIED (spot 계좌)
                    toAccountType="CONTRACT",  # CONTRACT (inverse 계좌)
                )

                if res['retMsg'] == 'success':
                    print(f'{currency}  {amount} 개  inverse로 계좌이동 완료')
                    break
                print(f'{currency} 계좌 이동중...')
                QTest.qWait(1000)
        elif market == 'binance':
            try:
                # BUSD를 Coin-M Futures 지갑으로 이동
                params = {
                    'asset': 'USDT',  # 전송할 자산
                    'amount': amount,  # 전송할 금액
                    'type': 1  # 1: 현물 → USDT-M 선물 계정, 2: USDT-M 선물 → 현물 계정
                }
                transfer = self.ex_binance.sapi_post_futures_transfer(params)
                print(f"✅ {amount} USDT를 선물 계정으로 전송 완료!", transfer)
                time.sleep(2)  # 이동 완료를 위한 대기
                return True
            except Exception as e:
                print(f"자금 이동 중 오류 발생[transfer_to_linear_wallet]: {e} {currency= } {amount= } ")
                return False
    def fetch_funding_rates(self,market,ticker,since):
        if market == 'bybit':
            symbol = ticker + 'USD'
            out = self.ex_bybit.fetch_funding_rate_history(symbol=symbol,since=since)
        elif market == 'binance':
            symbol = ticker + 'USD_PERP'
            out = self.ex_bybit.fetch_funding_rate_history(symbol=symbol,since=since)

        return out

    def convert_df(self, df):
        # print(convert_df)
        df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
        df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
        df['이평5'] = talib.MA(df['종가'], 5)
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

class ShutdownDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.seconds_left = 30
        self.shutdown_timer = QTimer()
        self.shutdown_timer.timeout.connect(self.update_timer)

        self.init_ui()
        self.start_timer()

    def init_ui(self):
        self.setWindowTitle('윈도우 종료 알림')
        self.setFixedSize(300, 150)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 레이아웃 설정
        main_layout = QVBoxLayout()

        # 안내 메시지
        self.message_label = QLabel('시스템이 30초 후에 종료됩니다.')
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





