from pybit.unified_trading import HTTP
from datetime import datetime,timedelta
import sqlite3
import pandas as pd
from pprint import pprint
from PyQt5.QtWidgets import QMainWindow,QGridLayout,QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QHBoxLayout,QTableWidget,QSplitter,QApplication,QCheckBox,QTextEdit,QTableWidgetItem,QHeaderView,QComboBox
from PyQt5.QtCore import Qt,QThread,pyqtSlot,QTimer,pyqtSignal,QWaitCondition,QMutex
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics,QFont
import time
import uuid
import math
import subprocess
import ccxt
import numpy as np
import os
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
pd.options.display.float_format = '{:.5f}'.format

class do_trade(QThread):
    qt_have = pyqtSignal(pd.DataFrame)
    qt_open = pyqtSignal(pd.DataFrame)
    qt_closed = pyqtSignal(pd.DataFrame)
    qt_history = pyqtSignal(pd.DataFrame)
    val_light = pyqtSignal(bool)
    val_wallet = pyqtSignal(str)
    val_time = pyqtSignal(str)
    def __init__(self,parent,session,exchange,df_open,df_closed,df_history,rate_short,list_bybit_inverse):
        super().__init__(parent)
        self.cond = QWaitCondition()
        self.bool_light = False
        self._status = True
        self.session = session
        self.exchange = exchange
        self.wallet = '0'
        self.df_open = df_open
        self.df_closed = df_closed
        self.df_history = df_history
        self.list_bybit_inverse = list_bybit_inverse
        self.rate_short = float(rate_short)
        self.funding_time_old = int(time.time())
        self.get_funding_time()

    def run(self):
        while self._status:
            self.fetch_have_ticker()
            t = self.funding_time - int(time.time())
            self.text_time = (self.count_down(t))
            if t > 0:
                for id in self.df_open.index.tolist():
                    ticker = self.df_open.loc[id,'ticker']
                    category = self.df_open.loc[id,'구분']
                    if not self.df_open.empty:
                        if self.df_open.loc[id, '상태'] == '매수주문' or self.df_open.loc[id, '상태'] == '부분체결':
                            self.chegyeol_buy(ticker, id, category)
                    # QTest.qWait(500)
                list_tickers = self.df_inverse['ticker'].tolist()
                list_tickers = [x for x in list_tickers if x!='USDT']
                for ticker in list_tickers:
                    self.auto_buy(ticker)


            elif t < 0:
                self.time_sync()
                self.get_funding_time()
                for id in self.df_open.index.tolist():

                    category = self.df_open.loc[id, '구분']
                    id = self.df_open.loc[id, 'id']
                    ticker = self.df_open.loc[id, 'ticker']


                    if category == 'inverse':
                        symbol = ticker + 'USD'
                        # side = 'Sell'
                    elif category == 'spot':
                        symbol = ticker + 'USDT'
                        # side = 'Buy'

                    self.session.cancel_order(category=category, symbol=symbol, orderId=id)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | 기존주문 취소 {ticker}: {category}")

                    if category == 'spot': # inverse일 경우는 알아서 주문이 나가기 때문에
                        배팅금액 = self.df_open.loc[id, '매수금액']
                        현재가 = float(self.fetch_ticker(Account=category, ticker=symbol)['lastPrice'])
                        rate_spot = self.df_open.loc[id, 'spot비율']
                        주문가 = 현재가 + (현재가 * rate_spot / 100)
                        주문가 = self.price_to_precision(category=category, ticker=symbol, price=주문가)

                        fee = 0.1
                        레버리지 = 1
                        주문수량 = (100 - (fee * 레버리지)) / 100 * 배팅금액 / 주문가
                        주문수량 = self.amount_to_precision(category, symbol, 주문수량)

                        res = self.order_open(category=category, ticker=symbol, side='Buy', orderType="Limit", price=주문가,qty=주문수량)
                        id = res['result']['orderId']
                        self.df_open.loc[id, 'ticker'] = ticker
                        self.df_open.loc[id, '주문시간'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        self.df_open.loc[id, '주문수량'] = 주문수량
                        self.df_open.loc[id, 'id'] = id
                        self.df_open.loc[id, '매수금액'] = 주문가 * 주문수량
                        self.df_open.loc[id, '주문가'] = 주문가
                        self.df_open.loc[id, '상태'] = '매수주문'
                        self.df_open.loc[id, '구분'] = category
                        self.df_open.loc[id, 'short비율'] = self.rate_short
                        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} | 자동재매수 {ticker}: {주문수량=}, {주문가=}, {주문수량 * 주문가}')
                    QTest.qWait(500)

                self.df_history.loc[time.time(),'보유자산합계'] = self.df_inverse['보유자산합계(USD)'].sum()
                self.df_history.loc[time.time(),'배팅가능합계'] = self.df_inverse['배팅가능합계(USD)'].sum()
                self.qt_history.emit(self.df_history)

            self.active_light()
            QTest.qWait(1000)
        self._status = False

    def auto_buy(self,ticker):
        주문최소금액 = self.df_inverse.loc[ticker,'주문최소금액(USD)']
        # 배팅가능수량 = self.df_inverse.loc[ticker,'배팅가능'] #contract 여유 잔고수량 불러오기
        # 보유수량 = self.df_inverse.loc[ticker,'보유수량'] #contract 보유수량 불러오기
        현재가 = self.df_inverse.loc[ticker,'현재가(inverse)']
        보유자산합계 = self.df_inverse.loc[ticker,'보유자산합계(USD)']
        배팅가능합계 = self.df_inverse.loc[ticker,'배팅가능합계(USD)']
        안전마진 = 5 # 잔고가 펀딩비로 받는 금액의 5배 이상 있을 경우에만 진행
        주문가 = self.price_to_precision(category='inverse', ticker=ticker + 'USD', price=현재가 + (현재가 * (self.rate_short) / 100))
        funding_rate = 0.01/100

        여유돈 = 보유자산합계*funding_rate*안전마진
        배팅가능금액 = 배팅가능합계 - 여유돈


        # if 배팅가능수량 * 주문가 > 주문최소금액: #최소수량보다 잔고가 많을경우마다 주문하면 마이너스피 일 때는 갖고있는 잔고에서 매번 수수료가 나가기 때문
        if 배팅가능금액 > 주문최소금액 : # 현재 잔고가 보유수량*펀딩비율*5배 보다 많아야 매수 조건 성립 (최소수량보다 잔고가 많을경우마다 주문하면 마이너스피 일 때는 갖고있는 잔고에서 매번 수수료가 나가기 때문)
            # print('=========================================================')
            # print(f"{ticker= }   {보유자산합계= }   {배팅가능합계= }   {여유돈= }  =  {배팅가능수량=} / ({보유수량=} * {배팅가능금액=})")
            # print(f"{배팅가능금액= }")
            # print(f"{배팅가능합계-배팅가능금액=}")
            진입금액 = math.trunc(배팅가능금액)
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} | 자동매수 {ticker}: {진입금액=}, {주문가=}, {진입금액 * 주문가}')
            res = self.order_open(category='inverse', ticker=ticker + 'USD', side='Sell', orderType="Limit", price=주문가,qty=진입금액)
            id = res['result']['orderId']
            self.df_open.loc[id, 'ticker'] = ticker
            self.df_open.loc[id, '주문시간'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.df_open.loc[id, '주문수량'] = 진입금액
            self.df_open.loc[id, 'id'] = id
            self.df_open.loc[id, '매수금액'] = 진입금액
            self.df_open.loc[id, '주문가'] = 주문가
            self.df_open.loc[id, '상태'] = '매수주문'
            self.df_open.loc[id, '구분'] = 'inverse'
            self.df_open.loc[id, 'short비율'] = self.rate_short
            QTest.qWait(5000)


    def chegyeol_buy(self,ticker, id, category):
        dict_chegyeol = self.fetch_order(ticker, id, category)

        if dict_chegyeol['체결'] == True:
            # 체결가 = dict_chegyeol['체결가']
            # 수수료 = dict_chegyeol['수수료']
            # 체결수량 = dict_chegyeol['체결수량']
            print(f"{ticker}  {dict_chegyeol['체결수량']} 개  체결 완료 - 체결시간{dict_chegyeol['체결시간']}")
            self.df_closed.loc[id] = self.df_open.loc[id].copy()
            self.df_open.drop(index=id, inplace=True)
                # self.df_closed.loc[id, '체결수량'] = 체결수량
                # self.df_closed.loc[id, '수수료'] = 수수료
                # self.df_closed.loc[id, '체결시간'] = self.stamp_to_str(dict_chegyeol['체결시간'])
            # elif category == 'inverse':
                # 수수료 = round(dict_chegyeol['수수료']*체결가, 4)
            self.df_closed.loc[id, '체결가'] = dict_chegyeol['체결가']
            self.df_closed.loc[id, '체결시간'] = self.stamp_to_str(dict_chegyeol['체결시간'])
            self.df_closed.loc[id, '수수료'] = dict_chegyeol['수수료']
            self.df_closed.loc[id, '체결수량'] = dict_chegyeol['체결수량']
            self.df_closed.loc[id, '상태'] = '체결완료'

            if category == 'spot': # inverse로 이동
                체결수량 = float(self.fetch_balance(accountType='UNIFIED', ticker=ticker, balance='잔고'))
                id,response = self.internal_transfer(ticker=ticker,qty=str(체결수량),fromAccount='UNIFIED',toAccount='CONTRACT') #계좌 이동
                while True:
                    if response['retMsg'] == 'success':
                        print(f'{ticker}  {체결수량} 개  inverse로 계좌이동 완료')
                        break
                    print(f'{ticker} 계좌 이동중...')
                    QTest.qWait(1000)

        elif dict_chegyeol['체결'] == '주문취소':
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} | 주문취소')
            self.df_open.drop(index=id,inplace=True)

        elif dict_chegyeol['체결'] == '부분체결':
            self.df_open.loc[id,'상태'] = '부분체결'


    def active_light(self):
        self.val_light.emit(self.bool_light)
        self.bool_light = not self.bool_light
        self.val_wallet.emit(self.wallet)
        self.val_time.emit(self.text_time)
        self.qt_have.emit(self.df_inverse)
        self.qt_open.emit(self.df_open)
        self.qt_closed.emit(self.df_closed)


    def fetch_ticker(self, Account, ticker):
        return self.session.get_tickers(
            category=Account,
            symbol=ticker,
        )['result']['list'][0]
    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.bool_light = False
            self.cond.wakeAll()
        elif not self._status:
            self.bool_light = False
            self.val_light.emit(self.bool_light)
    def fetch_have_ticker(self):
        li_col = ['market','ticker','보유수량', '배팅가능', '수량합계', '현재가(inverse)', '현재가(linear)',
                  '보유자산합계(USD)', '배팅가능합계(USD)','주문최소금액(USD)']
        self.df_inverse = pd.DataFrame(columns=li_col)
        # try:
        # 잔고 조회
        res = self.exchange.fetch_balance(params={'type': 'inverse'})
        # pprint(res)
        # print('=================')
        have_usdt = float(self.fetch_balance(accountType='UNIFIED', ticker='USDT', balance='잔고'))
        all_usdt = float(self.fetch_balance(accountType='UNIFIED', ticker='USDT', balance='보유'))
        if res['info']['result']:
            output = res['info']['result']['list'][0]['coin']
            # 잔고가 있는 코인들만 출력
            # dict_data['ticker']
            # list_ticker = list(res['total'].keys())
            # self.df_inverse = pd.DataFrame(index=list_ticker)
            print(pd.DataFrame(output))
            pprint(output)
            print(have_usdt)
            quit()
            for have_ticker in output:
                # pprint(have_ticker)
                ticker = have_ticker['coin']
                if have_ticker['availableToWithdraw'] == '':
                    self.df_inverse.loc[ticker, '배팅가능'] = 0
                else:
                    self.df_inverse.loc[ticker, '배팅가능'] = float(have_ticker['availableToWithdraw'])
                # self.df_inverse.loc[ticker, '보유수량'] = float(have_ticker['equity'])
                self.df_inverse.loc[ticker, '보유수량'] = float(have_ticker['totalPositionIM'])
                self.df_inverse.loc[ticker, '수량합계'] = float(have_ticker['walletBalance'])

                if ticker in self.list_bybit_inverse:
                    self.df_inverse.loc[ticker, '현재가(inverse)'] = self.exchange.fetch_ticker(ticker + 'USD')['close']
                    self.df_inverse.loc[ticker, '현재가(linear)'] = self.exchange.fetch_ticker(ticker + 'USDT')['close']
                    if np.isnan(self.df_inverse.loc[ticker, '주문최소금액(USD)']) and self.df_inverse.loc[ticker, '보유수량'] != 0:
                        res = self.fetch_account_info(Account='inverse', ticker=ticker + 'USD')
                        self.df_inverse.loc[ticker, '주문최소금액(USD)'] = float(res['lotSizeFilter']['minOrderQty']) # inverse 최소주문USDT구하기

            self.df_inverse['보유자산합계(USD)'] = self.df_inverse['보유수량'] * self.df_inverse['현재가(inverse)']
            self.df_inverse['배팅가능합계(USD)'] = self.df_inverse['배팅가능'] * self.df_inverse['현재가(inverse)']
            self.df_inverse['보유자산합계(USD)'].round(2)
            self.df_inverse['배팅가능합계(USD)'].round(2)
            self.df_inverse['ticker'] = self.df_inverse.index
            self.df_inverse['market'] = "bybit"
            self.df_inverse = self.df_inverse[self.df_inverse['보유수량']!=0]
            self.wallet = str(round(self.df_inverse['보유자산합계(USD)'].sum()+self.df_inverse['배팅가능합계(USD)'].sum()))
        # except Exception as e:
        #     print(f"오류 발생: API 확인 {e}")

    def fetch_order(self,ticker, id, category):
        if category == 'spot':
            ticker = ticker+'USDT'
        elif category == 'inverse':
            ticker = ticker+'USD'

        res = self.session.get_open_orders(
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
                    return {'체결': False}
        if execution == True:
            res = self.session.get_order_history(
                category=category,  # spot, linear, inverse, option
                limit=10
            )['result']['list']
            # pprint(res)
            for order in res:
                if order['orderId'] == id:
                    if order['orderStatus'] == 'Filled':
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {ticker} - 체결완료")

                        return {'체결': True, '체결가': float(order['avgPrice']), '체결수량': float(order['cumExecQty']),
                                '수수료': float(order['cumExecFee']), '체결시간': int(int(order['updatedTime'])/1000)}
                    elif order['orderStatus'] == 'Cancelled':
                        return {'체결':'주문취소'}
                    elif order['orderStatus'] == 'PartiallyFilledCanceled':
                        return {'체결':'부분체결'}
        return {'체결': False}
    def order_open(self, category, ticker, side, orderType, price, qty):
        if category == 'spot':
            rate = 0
        elif category == 'inverse':
            rate = 1
        else:
            raise
        res = self.session.place_order(
            category=category,  # spot, linear, inverse, option
            symbol=ticker,
            side=side,  # Buy, Sell
            orderType=orderType,  # Market, Limit
            qty=qty,
            price=price,
            timeInForce="PostOnly",
            # orderLinkId="spot-test-postonly",
            isLeverage=rate,  # 0(default): false then spot trading, 1: true then margin trading
            orderFilter="Order",
        )
        return res
    def fetch_account_info(self, Account, ticker):
        return self.session.get_instruments_info(
            category=Account,  # spot, linear, inverse, option
            symbol=ticker, # BTC, BTCUSDT, BTCUSD
        )['result']['list'][0]
    def internal_transfer(self, ticker, qty, fromAccount, toAccount):
        id = str(uuid.uuid1())
        print(id)
        res = self.session.create_internal_transfer(
            transferId=id,
            coin=ticker,  # BTC
            amount=qty,
            fromAccountType=fromAccount,  # UNIFIED (spot 계좌)
            toAccountType=toAccount,  # CONTRACT (inverse 계좌)
        )
        return id, res
    def fetch_balance(self, accountType, ticker, balance):
        res = self.session.get_coins_balance(
            accountType=accountType,  # CONTRACT: Inverse Derivatives Account, UNIFIED: Unified Trading Account
            coin=ticker, # BTC
        )
        if balance == '보유':
            return res['result']['balance'][0]['walletBalance']
        elif balance == '잔고':
            return res['result']['balance'][0]['transferBalance']
    def get_funding_time(self):
        while True:
            self.funding_time = int(int((self.session.get_funding_rate_history(
                category="inverse",
                symbol="BTCUSD",
                limit=1,
            )['result']['list'][0]['fundingRateTimestamp']))/1000)+3600*8
            time.sleep(1)
            if self.funding_time_old != self.funding_time:
                self.funding_time_old = self.funding_time
                break
    def price_to_precision(self,category, ticker, price):
        if category == 'spot':
            res = self.fetch_account_info(Account=category,ticker=ticker)
            price_min = res['priceFilter']['tickSize'].index('1')-1
            return round(price,price_min)
        elif category == 'inverse':
            res = self.fetch_account_info(Account=category,ticker=ticker)
            price_step = res['priceFilter']['tickSize']
            point = price_step.index('.')
            price = round(price, point)
            j = round(price % float(price_step), point)
            return price-j
    def count_down(self,t):
        hours = str(t // 3600)
        remaining_seconds = t % 3600
        minutes = str(remaining_seconds // 60)
        seconds = str(remaining_seconds % 60)
        return f"{hours}:{minutes}:{seconds}"
    def stamp_to_str(self,t):
        date_time = self.stamp_to_datetime(t)
        return datetime.strftime(date_time, "%Y-%m-%d %H:%M")

    def stamp_to_int(self,stamp_time):
        dt = datetime.fromtimestamp(stamp_time)
        dt = dt.strftime('%Y%m%d%H%M')
        return int(dt)

    def stamp_to_datetime(self,stamp_time):
        int_time = self.stamp_to_int(stamp_time)
        return datetime.strptime(str(int_time), '%Y%m%d%H%M')

    def amount_to_precision(self,category, ticker, amount):
        res = self.fetch_account_info(Account=category,ticker=ticker)
        qty_min = res['lotSizeFilter']['basePrecision'].index('1')-1
        qty = round(amount,qty_min)
        if qty < float(res['lotSizeFilter']['minOrderQty']):
            print(f"최소주문수량 미만 (최소주문수량: {res['lotSizeFilter']['minOrderQty']}, > 주문수량: {qty}")
            raise
        return qty
    def time_sync(self):
        subprocess.Popen('python timesync.py')

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_UI()
        self.init_file()
        self.session = self.make_exchange_bybit()
        self.exchange = self.make_exchange_bybit_ccxt()

        self.qtable_open(self.df_open)
        self.qtable_closed(self.df_closed)

        self.time_sync()
        self.funding_time_old = int(time.time())
        # self.get_funding_time()

        self.QPB_start.clicked.connect(self.onStartButtonClicked)
        self.QPB_stop.clicked.connect(self.onStopButtonClicked)
        self.QPB_api_save_bybit.clicked.connect(self.save_api)
        self.QPB_manual_buy_bybit.clicked.connect(lambda :self.manual_buy('bybit'))
        self.QPB_manual_buy_binance.clicked.connect(lambda :self.manual_buy('binance'))
        self.onStartButtonClicked()

    def set_UI(self):
        QW_main = QWidget()
        self.setWindowTitle(f'Funding Bybit')

        self.QT_trade_have = QTableWidget()
        self.QT_trade_history = QTableWidget()
        self.QT_trade_open = QTableWidget()


        self.QGL_menu = QGridLayout()

        self.QPB_start = QPushButton('START')
        self.QPB_stop = QPushButton('STOP')
        self.QPB_manual_buy_bybit = QPushButton('BYBIT 수동매수')
        self.QL_manual_ticker = QLineEdit('BTC')
        self.QL_manual_price = QLineEdit('100')
        self.QL_wallet = QLabel()
        self.QL_fee_sum = QLabel()
        self.QL_buy_sum = QLabel()
        self.QL_time = QLabel()
        self.QL_repeat_per = QLineEdit()
        self.QL_rate_spot = QLineEdit('-1')
        self.QL_rate_short = QLineEdit('1')
        self.QPB_manual_buy_binance = QPushButton('BINANCE 수동매수')
        self.QPB_chart = QPushButton('차트보기')
        self.QLE_api_bybit = QLineEdit()
        self.QLE_secret_bybit = QLineEdit()
        self.QPB_api_save_bybit = QPushButton('bybit API 저장')
        self.QLE_api_binance = QLineEdit()
        self.QLE_secret_binance = QLineEdit()
        self.QPB_api_save_binance = QPushButton('binance API 저장')
        dict_grid = {
            self.QPB_start: self.QPB_stop,
            QLabel('합계(USD)'):self.QL_wallet,
            QLabel('누적수수료'):self.QL_fee_sum,
            QLabel('누적매수'):self.QL_buy_sum,
            QLabel('남은시간'):self.QL_time,
            QLabel('재투자비율(%)'):self.QL_repeat_per,
            QLabel('spot주문(%)'):self.QL_rate_spot,
            QLabel('short주문(%)'):self.QL_rate_short,
            QLabel('ticker(spot)'):self.QL_manual_ticker,
            QLabel('매수금액'):self.QL_manual_price,
            self.QPB_manual_buy_binance:self.QPB_manual_buy_bybit,
        }
        for i, key in enumerate(dict_grid):
            self.QGL_menu.addWidget(key, 0, i)
            self.QGL_menu.addWidget(dict_grid[key], 1, i)



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
        self.QT_trade_have.setStyleSheet(StyleSheet_Qtable)
        # self.QPB_start.setStyleSheet("border-style: solid;border-width: 1px;border-color: #0080ff")
        self.QPB_start.setStyleSheet(" background-color: #cccccc;")
        self.QPB_stop.setStyleSheet("background-color: #cccccc;")
        # self.QL_hoga = QTextEdit()

        self.setCentralWidget(QW_main)

        QSV_main = QSplitter(Qt.Vertical)
        QSH_table = QSplitter(Qt.Horizontal)
        QSH_history_table = QSplitter(Qt.Horizontal)

        QSH_table.addWidget(self.QT_trade_open)
        QSH_table.addWidget(self.QT_trade_history)
        QSV_main.addWidget(self.QT_trade_have)
        QSV_main.addWidget(QSH_history_table)
        QSV_main.addWidget(QSH_table)
        QSV_main.addWidget(QW_grid)


        QVB_main.addWidget(QSV_main)
        QVB_main.addLayout(QHB_api)

        QW_main.setLayout(QVB_main)
    def save_api(self):
        QLE_api_bybit=self.QLE_api_bybit.text()
        QLE_secret_bybit=self.QLE_secret_bybit.text()
        self.df_api.loc['api','value']=QLE_api_bybit
        self.df_api.loc['secret','value']=QLE_secret_bybit
        self.df_api.to_sql('api', self.conn, if_exists='replace')
        self.QLE_api_bybit.clear()
        self.QLE_secret_bybit.clear()

    def time_sync(self):
        subprocess.Popen('python timesync.py')

    def init_file(self):
        db_file = 'DB/stg_funding_bybit.db'
        if not os.path.isfile(db_file):
            self.conn = sqlite3.connect(db_file)
            li = ['market','ticker', '구분', '주문가', '주문수량', '매수금액', '수수료', '수익률',
                  '주문시간', '체결시간', '체결가', '체결수량',
                  'id', '상태', '펀딩비', 'spot비율', 'short비율']
            self.df_open = pd.DataFrame(columns=li)
            self.df_closed = pd.DataFrame(columns=li)
            self.df_closed.to_sql('closed', self.conn, if_exists='replace')
            self.df_open.to_sql('open', self.conn, if_exists='replace')

            li_col = ['보유자산합계', '배팅가능합계']
            self.df_history = pd.DataFrame(columns=li_col)
            self.df_history.to_sql('history', self.conn, if_exists='replace')
            # dic = {'api':'','secret':''}
            self.df_api = pd.DataFrame(index=['api','secret'], columns=['value'])
            self.df_api.to_sql('api', self.conn, if_exists='replace')
        else:
            self.conn = sqlite3.connect(db_file)
            self.df_open = pd.read_sql(f"SELECT * FROM 'open'", self.conn).set_index('index')
            self.df_closed = pd.read_sql(f"SELECT * FROM 'closed'", self.conn).set_index('index')
            self.df_history = pd.read_sql(f"SELECT * FROM 'history'", self.conn).set_index('index')
            self.df_api = pd.read_sql(f"SELECT * FROM 'api'", self.conn).set_index('index')
        self.df_open_old = self.df_open.copy()
        self.df_closed_old = self.df_closed.copy()

    def onStartButtonClicked(self):

        # 바이비트 inverse 종목 정리
        list_bybit_inverse = []
        markets = self.exchange.load_markets()
        # inverse 종목만 필터링
        inverse_markets = {}
        for symbol, market in markets.items():
            if market.get('inverse') == True:
                inverse_markets[symbol] = market
        # inverse 종목 목록 출력
        for symbol in inverse_markets:
            list_bybit_inverse.append(symbol[:symbol.index('/')])


        out = self.exchange.fetch_funding_rate_history('BTCUSD')
        print(pd.DataFrame(out))
        quit()


        self.thread = do_trade(self,self.session,self.exchange,self.df_open,self.df_closed,
                               self.df_history,self.QL_rate_short.text(),list_bybit_inverse)
        self.thread.start()

        self.thread.qt_open.connect(self.qtable_open)
        self.thread.qt_closed.connect(self.qtable_closed)
        self.thread.qt_history.connect(self.qtable_history)
        self.thread.qt_have.connect(self.qtable_have)
        self.thread.val_light.connect(self.effect_start)
        self.thread.val_wallet.connect(self.QL_wallet.setText)
        self.thread.val_time.connect(self.QL_time.setText)

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

    def manual_buy(self,market):
        try:
            ticker = self.QL_manual_ticker.text()
            배팅금액 = int(self.QL_manual_price.text())
            category = 'spot'

            현재가 = float(self.fetch_ticker(Account=category,ticker=ticker+'USDT')['lastPrice'])
            rate_spot = float(self.QL_rate_spot.text())
            주문가 = 현재가+(현재가*rate_spot/100)
            주문가 = self.price_to_precision(category=category,ticker=ticker+'USDT',price=주문가)

            fee = 0.1
            레버리지 = 1
            진입수량 = (100 - (fee * 레버리지)) / 100 * 배팅금액 / 주문가
            진입수량 = self.amount_to_precision(category,ticker+'USDT',진입수량)

            res = self.open_order(category=category, ticker=ticker + 'USDT', side='Buy', orderType="Limit", price=주문가, qty=진입수량)
            id = res['result']['orderId']
            self.df_open.loc[id,'ticker'] = ticker
            self.df_open.loc[id,'주문시간'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.df_open.loc[id,'주문수량'] = 진입수량
            self.df_open.loc[id,'id'] = id
            self.df_open.loc[id,'매수금액'] = 주문가*진입수량
            self.df_open.loc[id,'상태'] = '매수주문'
            self.df_open.loc[id,'구분'] = 'spot'
            self.df_open.loc[id,'주문가'] = 주문가
            self.df_open.loc[id,'spot비율'] = float(self.QL_rate_spot.text())

            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M")} | 수동매수 {ticker}: {진입수량=}, {주문가=}, {진입수량 * 주문가}')
            self.df_open.to_sql('open',self.conn,if_exists='replace')
        except Exception as e:
            print(f"오류 발생: 주문 확인요망 API 확인 등.. {e}")
        self.qtable_open(self.df_open)

    def open_order(self, category, ticker, side, orderType, price, qty):
        if category == 'spot':
            rate = 0
        elif category == 'inverse':
            rate = 1
        else:
            raise
        res = self.session.place_order(
            category=category,  # spot, linear, inverse, option
            symbol=ticker,
            side=side,  # Buy, Sell
            orderType=orderType,  # Market, Limit
            qty=qty,
            price=price,
            timeInForce="PostOnly",
            # orderLinkId="spot-test-postonly",
            isLeverage=rate,  # 0(default): false then spot trading, 1: true then margin trading
            orderFilter="Order",
        )
        return res

    # def pybit_open_order1(self, ):
    #     res = self.session.place_order(
    #         category="inverse",
    #         symbol="BTCUSD",
    #         side="Sell",
    #         orderType="Market",
    #         qty="1",
    #     )
    #     return res


    def qtable_have(self,df):
        df['배팅가능'] = df['배팅가능'].apply(lambda int_num: "{:,}".format(int_num))
        df['현재가(inverse)'] = df['현재가(inverse)'].apply(lambda int_num: "{:,}".format(int_num))
        df['현재가(linear)'] = df['현재가(linear)'].apply(lambda int_num: "{:,}".format(int_num))
        # df['보유자산합계(USD)'] = df['보유자산합계(USD)'].apply(lambda int_num: "{:,}".format(int_num))
        # df['배팅가능합계(USD)'] = df['배팅가능합계(USD)'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_have, df)

    def qtable_open(self,df):
        df_compare = df[['상태','id']]
        if not self.df_open_old.equals(df_compare):
            df.to_sql('open',self.conn,if_exists='replace')
            self.df_open_old = df_compare.copy()
        df_active = df[['ticker', '주문시간', '주문수량', '매수금액', '주문가', '상태', '구분', 'spot비율','short비율','id']]
        df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_open, df_active)

    def qtable_closed(self, df):
        if not self.df_closed_old.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
            df.to_sql('closed', self.conn, if_exists='replace')
            self.df_closed_old = df.copy()
        df_active = df[['ticker', '체결시간', '주문수량', 'id', '수수료', '매수금액', '주문가', '상태',
                  '구분', 'spot비율','short비율']]
        df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_history, df_active)

    def qtable_history(self, df):
        if not self.df_history.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
            df.to_sql('history', self.conn, if_exists='replace')
            self.df_history_old = df.copy()

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


    def fetch_ticker(self, Account, ticker):
        return self.session.get_tickers(
            category=Account,
            symbol=ticker,
        )['result']['list'][0]

    def make_exchange_bybit(self):
        api = self.df_api.loc['api','value']
        secret = self.df_api.loc['secret','value']
        exchange = HTTP(
            testnet=False,
            api_key=api,
            api_secret=secret,
        )
        return exchange

    def make_exchange_bybit_ccxt(self):
        api = self.df_api.loc['api','value']
        secret = self.df_api.loc['secret','value']
        exchange_ccxt = ccxt.bybit(config={
            'apiKey': api,
            'secret': secret,
            'enableRateLimit': True,
            'options': {'position_mode': True, },
        })
        return exchange_ccxt

    def fetch_account_info(self, Account, ticker):
        return self.session.get_instruments_info(
            category=Account,  # spot, linear, inverse, option
            symbol=ticker, # BTC, BTCUSDT, BTCUSD
        )['result']['list'][0]

    def price_to_precision(self,category, ticker, price):
        if category == 'spot':
            res = self.fetch_account_info(Account=category,ticker=ticker)
            price_min = res['priceFilter']['tickSize'].index('1')-1
            return round(price,price_min)
        elif category == 'inverse':
            res = self.fetch_account_info(Account=category,ticker=ticker)
            price_step = res['priceFilter']['tickSize']
            point = price_step.index('.')
            price = round(price, point)
            j = round(price % float(price_step), point)
            return price-j

    def amount_to_precision(self,category, ticker, amount):
        res = self.fetch_account_info(Account=category,ticker=ticker)
        qty_min = res['lotSizeFilter']['basePrecision'].index('1')-1
        qty = round(amount,qty_min)
        if qty < float(res['lotSizeFilter']['minOrderQty']):
            print(f"최소주문수량 미만 (최소주문수량: {res['lotSizeFilter']['minOrderQty']}, > 주문수량: {qty}")
            raise
        return qty

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
    os.system('pause')

    # main()





