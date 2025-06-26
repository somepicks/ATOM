import datetime
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow,QGridLayout,QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QHBoxLayout,
                             QTableWidget,QSplitter,QApplication,QCheckBox,QTextEdit,QTableWidgetItem,QHeaderView,
                             QComboBox,QDialog)
from PyQt5.QtCore import Qt,QThread,pyqtSlot,QTimer,pyqtSignal,QWaitCondition
from PyQt5.QtTest import QTest
import time
import math
import subprocess
import os
import numpy as np
import talib
import KIS
import common_def
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
# pd.options.display.float_format = '{:.6f}'.format

class do_trade(QThread):
    qt_open = pyqtSignal(pd.DataFrame)
    qt_closed = pyqtSignal(pd.DataFrame)
    val_light = pyqtSignal(bool)
    shutdown_signal = pyqtSignal()
    def __init__(self,parent,exchange,df_set):
        super().__init__(parent)
        self.cond = QWaitCondition()
        self.bool_light = False
        self._status = True
        self.exchange = exchange
        self.df = pd.DataFrame()
        self.list_ticker = self.df.index.tolist()


    def run(self):
        self.bool_light = True
        self.val_light.emit(self.bool_light)
        finish_time = datetime.datetime.now().replace(hour=15,minute=20)
        account, df = self.exchange.fetch_balance()
        if df.empty:
            self.df = df
        else:
            self.df = df[df['청산가능수량'] > 0]
        현재시간 = datetime.datetime.now().replace(second=0, microsecond=0)
        now_day = 현재시간.date().strftime("%Y%m%d")
        now_time = 현재시간.strftime("%H%M") + "00"  # 마지막에 초는 00으로
        KOSPI200_ticker = '101W09'
        # 선물조회
        # print('선물지수 데이터 취합 중...',end='')
        # ohlcv_future = self.exchange.fetch_1m_ohlcv(symbol=KOSPI200_ticker, limit=5, ohlcv=[], now_day=now_day, now_time=now_time)
        # df_KOSPI200 = common_def.get_kis_ohlcv('국내선옵', ohlcv_future)
        # df_KOSPI200.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
        #                    '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
        # self.df_KOSPI200_5 = common_def.resample_df(df_KOSPI200, '5분봉', '5min', '5분봉', False)
        # self.df_KOSPI200_30 = common_def.resample_df(df_KOSPI200, '30분봉', '30min', '30분봉', False)
        # print('완료')
        # self.df_KOSPI200_day = common_def.resample_df(df_KOSPI200, '30분봉', '30min', '30분봉', False)

        if not self.df.empty:
            # 중복 인덱스 제거
            # self.df = self.df[~self.df.index.duplicated(keep='last')]
            self.df['수익률'] = round(self.df['평가손익'] / self.df['매입금액'] * 100, 1)
            self.df['최고수익률'] = self.df['수익률']
            self.df['최저수익률'] = self.df['수익률']
            # self.df_compare = self.df[['잔고수량','체결평균단가','청산가능수량','매입금액','종목코드']]
            self.list_ticker = self.df.index.tolist()
            for ticker in self.df.index.tolist():
                print(f'{ticker} 데이터 취합 중')
                globals()[ticker] = self.exchange.fetch_1m_ohlcv(symbol=ticker, limit=5, ohlcv=[], now_day=now_day, now_time=now_time)
        else:
            self.df = pd.DataFrame(columns=['잔고수량', '체결평균단가', '청산가능수량', '매입금액', '종목코드'])
            self.list_ticker = []
        self.df_compare = self.df[['잔고수량','체결평균단가','청산가능수량','매입금액','종목코드']]

        while True:
            account, df = self.exchange.fetch_balance()
            now_time = 현재시간.strftime("%H%M") + "00"  # 마지막에 초는 00으로
            #
            # ohlcv_future = self.exchange.fetch_1m_ohlcv(symbol=KOSPI200_ticker, limit=5, ohlcv=ohlcv_future, now_day=now_day,
            #                                             now_time=now_time)
            # df_KOSPI200 = common_def.get_kis_ohlcv('국내선옵', ohlcv_future)
            # df_KOSPI200.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
            #                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
            # self.df_future_5 = common_def.resample_df(df_KOSPI200, '5분봉', '5min', '5분봉', False)
            # self.df_future_30 = common_def.resample_df(df_KOSPI200, '30분봉', '30min', '30분봉', False)
            # _, self.df_KOSPI200 = common_def.detail_to_spread(df_KOSPI200, '5분봉', '1분봉', False)

            if not df.empty:
                df_compare = df[['잔고수량','체결평균단가','청산가능수량','매입금액','종목코드']]
            else:
                df_compare = pd.DataFrame(columns=['잔고수량','체결평균단가','청산가능수량','매입금액','종목코드'])

            if not self.df_compare.equals(df_compare):
                # 신규 편입/제거 종목 찾기
                list_ticker = df_compare.index.tolist()
                self.list_ticker = self.df_compare.index.tolist()  # 종목코드 대신 index 사용
                new_tickers = list(set(list_ticker) - set(self.list_ticker))
                del_tickers = list(set(self.list_ticker) - set(list_ticker))
                # 신규 편입 종목 처리
                if new_tickers:
                    print(f"신규 편입 종목: {new_tickers}")
                    df_open = df[df['청산가능수량'] > 0].copy()  # copy() 추가
                    df_open['수익률'] = round(df_open['평가손익'] / df_open['매입금액'] * 100, 1)

                    for ticker in new_tickers:
                        # print(f'{ticker} 종목편입')
                        # 신규 종목의 최고/최저 수익률을 현재 수익률로 초기화
                        current_return = df_open.loc[ticker, '수익률']
                        current_return_value = current_return.iloc[0] if hasattr(current_return, 'iloc') else float(
                            current_return)

                        df_open.loc[ticker, '최고수익률'] = current_return_value
                        df_open.loc[ticker, '최저수익률'] = current_return_value

                        # self.df에 추가 (중복 방지)
                        if ticker not in self.df.index:
                            df_new = df_open.loc[[ticker]].copy()
                            print(f'{ticker} 데이터 취합 중...', end='')
                            self.df = pd.concat([self.df, df_new])
                            globals()[ticker] = self.exchange.fetch_1m_ohlcv(symbol='101W09', limit=5,
                                                                             ohlcv=[], now_day=now_day,
                                                                             now_time=now_time)
                            print('완료')
                        else:
                            print(f"종목 {ticker}는 이미 존재합니다.")

                    # 중복 인덱스 제거
                    # self.df = self.df[~self.df.index.duplicated(keep='last')]
                # 제거된 종목 처리
                if del_tickers:
                    print(f"제거된 종목: {del_tickers}")
                    for ticker in del_tickers:
                        print(f'{ticker} 종목삭제')
                        if ticker in self.df.index:
                            # self.df.loc[ticker,'최고수익률'] = 0
                            # self.df.loc[ticker,'최저수익률'] = 0
                            self.df.drop(index=ticker, inplace=True)

                # self.list_ticker = df_compare.index.tolist()
                self.df_compare = df_compare

            if not df.empty:
                df_open = df[df['청산가능수량'] > 0].copy()  # copy() 추가
                df_close = df[df['청산가능수량'] == 0].copy()

                if not df_open.empty:
                    # 현재 수익률 계산
                    df_open['수익률'] = round(df_open['평가손익'] / df_open['매입금액'] * 100, 1)

                    # 현재 보유 종목 리스트
                    list_ticker = df_open.index.tolist()  # 종목코드 대신 index 사용

                    # 기존 종목들의 최고/최저 수익률 업데이트
                    for ticker in list_ticker:
                        if ticker in self.df.index:  # 안전성 체크
                            # try:
                            # 안전하게 스칼라 값 추출
                            현재수익률_값 = df_open.loc[ticker, '수익률']
                            현재수익률 = 현재수익률_값.iloc[0] if hasattr(현재수익률_값, 'iloc') else float(현재수익률_값)

                            기존최고수익률_값 = self.df.loc[ticker, '최고수익률']
                            기존최고수익률 = 기존최고수익률_값.iloc[0] if hasattr(기존최고수익률_값, 'iloc') else float(기존최고수익률_값)

                            기존최저수익률_값 = self.df.loc[ticker, '최저수익률']
                            기존최저수익률 = 기존최저수익률_값.iloc[0] if hasattr(기존최저수익률_값, 'iloc') else float(기존최저수익률_값)

                            # 최고수익률 업데이트
                            새로운최고수익률 = max(현재수익률, 기존최고수익률)
                            # 최저수익률 업데이트
                            새로운최저수익률 = min(현재수익률, 기존최저수익률)

                            # self.df 업데이트 (중복 인덱스 문제 방지)
                            self.df.loc[self.df.index == ticker, '수익률'] = 현재수익률
                            self.df.loc[self.df.index == ticker, '최고수익률'] = 새로운최고수익률
                            self.df.loc[self.df.index == ticker, '최저수익률'] = 새로운최저수익률

                            # df_open도 업데이트
                            df_open.loc[df_open.index == ticker, '최고수익률'] = 새로운최고수익률
                            df_open.loc[df_open.index == ticker, '최저수익률'] = 새로운최저수익률

                            globals()[ticker] = self.exchange.fetch_1m_ohlcv(symbol=ticker, limit=5,
                                                                        ohlcv=globals()[ticker], now_day=now_day,
                                                                        now_time=now_time)
                            df_ohlcv = common_def.get_kis_ohlcv('국내선옵', globals()[ticker])
                            df_ohlcv.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                                                        '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
                            df_ohlcv = common_def.resample_df(df_ohlcv, '5분봉', '5min', '5분봉', False)
                            self.get_sell_signal(df_open.loc[ticker],finish_time,df_ohlcv)

                            # except Exception as e:
                            #     print(f"종목 {ticker} 처리 중 오류: {e}")
                            #     print(f"현재수익률 타입: {type(df_open.loc[ticker, '수익률'])}")
                            #     print(f"기존최고수익률 타입: {type(self.df.loc[ticker, '최고수익률'])}")
                            #     continue

                    # 현재 보유 종목 리스트 업데이트
                    # self.list_ticker = list_ticker

                    # 결과 출력 (디버깅용)
                    # print("=== 현재 포트폴리오 상태 ===")
                    # print(self.df[['수익률', '최고수익률', '최저수익률']])
                    # print("========================")
                else:
                    # 보유 종목이 없는 경우
                    self.list_ticker = []
                    df_open = pd.DataFrame()
                    df_close = pd.DataFrame()

            else:
                # fetch_balance가 빈 DataFrame을 반환한 경우
                # print("잔고 조회 결과가 비어있습니다.")
                self.list_ticker = []
                df_open = pd.DataFrame()
                df_close = pd.DataFrame()

            # 종료 조건 체크
            if datetime.datetime.now() > finish_time+datetime.timedelta(minutes=1):
                print("거래 시간 종료")
                self.shutdown_signal.emit()
                break

            self.active_light(df_open,df_close)
            QTest.qWait(500)
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
            주문가 = self.common_define.price_to_precision(market=market,category='inverse',ticker=ticker,price=price)
            res = self.common_define.order_open(market=market, category='inverse', ticker=ticker, side='sell',
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
        현재가 = self.common_define.fetch_ticker(market=market,ticker=ticker + '/USDT')['close']
        주문가 = 현재가 + (현재가 * rate_spot / 100)
        주문가 = self.common_define.price_to_precision(market=market,category=category, ticker=ticker, price=주문가)
        fee = 0.1
        레버리지 = 1
        진입수량 = (100 - (fee * 레버리지)) / 100 * 배팅금액 / 주문가
        진입수량 = self.common_define.amount_to_precision(market=market, category=category,ticker=ticker, amount=진입수량)
        df = df_usdt.loc[df_usdt['market']==market]
        보유현금 = df['free(USDT)'].tolist()[0]
        필요분 = (진입수량*주문가)+(진입수량*주문가)*0.001 #수수료 포함
        if 보유현금 < 필요분:
            print(f"USDT 부족 - 보유한 USDT: {보유현금}, 필요한 USDT {필요분}")
            return 0
        res = self.common_define.order_open(market= market,category=category, ticker=ticker, side='buy', orderType="limit",
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
        #     현재가 = self.common_define.fetch_ticker(market=market,Account=category, ticker=ticker+'/USDT')['close']
        #     주문가 = 현재가 + (현재가 * rate_spot / 100)
        #     주문가 = self.common_define.price_to_precision(market=market,category=category, ticker=ticker + 'USDT', price=주문가)
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

    def get_sell_signal(self,series,finish_time,df):
        ticker = series['종목코드']
        수익률 = series['수익률']
        최고수익률 = series['최고수익률']
        최저수익률 = series['최저수익률']
        청산가능수량 = series['청산가능수량']
        청산가능수량 = series['청산가능수량']
        sell_signal = False
        매도조건 = 0
        if 수익률 > 10:
            최고수익률대비 = (최고수익률-(최고수익률-수익률))/최고수익률*100
            if 최고수익률대비 < 65:
                sell_signal = True
                매도조건 = 3
                print(f"{최고수익률대비= }")
        if 수익률 <-15:
            sell_signal = True
            매도조건 = 1
        if datetime.datetime.now() > finish_time:
            sell_signal = True
            매도조건 = 2


        if sell_signal == True:
            self.exchange.create_market_buy_order(symbol=ticker, quantity=int(청산가능수량), side='sell')
            print(f'매도 - {ticker= }  {매도조건= }  {수익률=}  {최고수익률=}  {최저수익률=}')

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

    def active_light(self,df_open,df_close):
        self.val_light.emit(self.bool_light)
        self.bool_light = not self.bool_light
        # self.val_wallet.emit(self.wallet)
        # self.val_time.emit(str(self.text_time))
        self.qt_open.emit(df_open)
        self.qt_closed.emit(df_close)
        # self.qt_closed.emit(self.df_closed)
        # self.qt_future.emit(self.df_future)

    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.bool_light = False
            self.cond.wakeAll()
        elif not self._status:
            self.bool_light = False
            self.val_light.emit(self.bool_light)


class Window(QMainWindow):
    buy_signal = pyqtSignal(str,str,int,float,pd.DataFrame)
    set_signal = pyqtSignal(pd.DataFrame)

    def __init__(self):
        super().__init__()
        self.init_file()
        self.set_UI()
        self.time_sync()
        time.sleep(1)

        self.funding_time_old = int(time.time())

        self.QPB_start.clicked.connect(self.onStartButtonClicked)
        self.QPB_stop.clicked.connect(self.onStopButtonClicked)
        self.QPB_api_save.clicked.connect(lambda :self.save_api())
        self.QL_rate_short.textChanged.connect(self.on_text_changed_rate_short)
        self.QL_rate_spot.textChanged.connect(self.on_text_changed_rate_spot)


    def set_UI(self):
        QW_main = QWidget()
        self.setWindowTitle(f'auto sell')

        self.QT_trade_open = QTableWidget()
        self.QT_trade_closed = QTableWidget()
        # self.QT_trade_history = QTableWidget()
        # self.QT_trade_open = QTableWidget()


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
        # self.QCB_off = QComboBox()
        # self.QCB_off.addItems(['자동꺼짐','1분후','5분후','10분후','30분후','1시간후','설정안함'])
        self.QLE_api = QLineEdit()
        self.QLE_account = QLineEdit()
        self.QLE_id = QLineEdit()
        self.QLE_secret = QLineEdit()
        self.QPB_api_save = QPushButton('API 저장')

        # self.QCB_off.setCurrentText(self.df_set.loc['auto_finish','val'])
        QW_grid = QWidget()
        StyleSheet_Qtextedit = "font: 10pt 나눔고딕; "
        QW_grid.setStyleSheet(StyleSheet_Qtextedit)
        QW_grid.setLayout(self.QGL_menu)
        QW_grid.setMaximumSize(1980,100)


        QHB_button = QHBoxLayout()
        QHB_button.addWidget(self.QPB_start)
        QHB_button.addWidget(self.QPB_stop)
        QHB_api = QHBoxLayout()
        QHB_api.addWidget(QLabel('API: '))
        QHB_api.addWidget(self.QLE_api)
        QHB_api.addWidget(QLabel('SECRET: '))
        QHB_api.addWidget(self.QLE_secret)

        # QHB_api.addWidget(QLabel('id: '))
        # QHB_api.addWidget(self.QLE_id)
        QHB_api.addWidget(QLabel('account: '))
        QHB_api.addWidget(self.QLE_account)

        QHB_api.addWidget(self.QPB_api_save)

        QVB_main = QVBoxLayout()

        StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 12pt 나눔고딕; "
        # self.QT_trade_history.setStyleSheet(StyleSheet_Qtable)
        # self.QT_trade_open.setStyleSheet(StyleSheet_Qtable)
        self.QT_trade_open.setStyleSheet(StyleSheet_Qtable)
        self.QT_trade_closed.setStyleSheet(StyleSheet_Qtable)
        # self.QPB_start.setStyleSheet("border-style: solid;border-width: 1px;border-color: #0080ff")
        self.QPB_start.setStyleSheet(" background-color: #cccccc;")
        self.QPB_stop.setStyleSheet("background-color: #cccccc;")
        # self.QL_hoga = QTextEdit()

        self.setCentralWidget(QW_main)

        QSV_main = QSplitter(Qt.Vertical)
        QSH_table_up = QSplitter(Qt.Vertical)
        QSH_table = QSplitter(Qt.Horizontal)
        QSH_history_table = QSplitter(Qt.Horizontal)

#         QSH_table.addWidget(self.QT_trade_open)
#         QSH_table.addWidget(self.QT_trade_history)
        QSH_table_up.addWidget(self.QT_trade_open)
        QSH_table_up.addWidget(self.QT_trade_closed)
        QSV_main.addWidget(QSH_table_up)
        QSV_main.addWidget(QSH_history_table)
        QSV_main.addWidget(QSH_table)
        QSV_main.addWidget(QW_grid)


        QVB_main.addWidget(QSV_main)
        QVB_main.addLayout(QHB_button)
        QVB_main.addLayout(QHB_api)

        QW_main.setLayout(QVB_main)
    def save_api(self):
        if not self.QLE_api.text() == '':
            self.df_set.loc[f'api','val']=self.QLE_api.text()
        if not self.QLE_secret.text() == '':
            self.df_set.loc[f'secret','val']=self.QLE_secret.text()
        if not self.QLE_id.text() == '':
            self.df_set.loc[f'id','val']=self.QLE_id.text()
        if not self.QLE_account.text() == '':
            self.df_set.loc[f'account','val']=self.QLE_account.text()
        self.QLE_api.clear()
        self.QLE_secret.clear()
        self.QLE_id.clear()
        self.QLE_account.clear()
        self.df_set.to_sql('set', self.conn, if_exists='replace')

    def init_file(self):
        db_file = 'DB/auto_sell.db'
        if not os.path.isfile(db_file):
            self.conn = sqlite3.connect(db_file)
            li = ['market','ticker', 'category', '주문가', '주문수량', '매수금액', '수수료', '수익률',
                  '주문시간', '체결시간', '체결가', '체결수량','id', '상태', '펀딩비', 'spot비율',
                  'short비율']
            self.df_open = pd.DataFrame(columns=li)
            self.df_closed = pd.DataFrame(columns=li)
            self.df_closed.to_sql('closed', self.conn, if_exists='replace')
            self.df_open.to_sql('open', self.conn, if_exists='replace')


            self.list_compare_col = ['market', 'ticker', 'free(qty)', 'free(USDT)', 'total(USDT)']
            self.df_inverse = pd.DataFrame(index=[], columns=self.list_compare_col)
            self.df_inverse.to_sql('inverse', self.conn, if_exists='replace')

            self.df_set = pd.DataFrame(index=['auto_start','auto_finish','start_time','rate_short','rate_spot','funding_time',
                                              'api_bybit','secret_bybit','api_binance','secret_binance'],
                                       columns=['val'])
            self.df_set.loc['api','val'] = None
            self.df_set.loc['secret','val'] = None
            self.df_set.loc['id','val'] = None
            self.df_set.loc['account','val'] = None
            self.df_set.to_sql('set', self.conn, if_exists='replace')

        else:
            self.conn = sqlite3.connect(db_file)
            self.df_open = pd.read_sql(f"SELECT * FROM 'open'", self.conn).set_index('index')
            self.df_closed = pd.read_sql(f"SELECT * FROM 'closed'", self.conn).set_index('index')
            self.df_inverse = pd.read_sql(f"SELECT * FROM 'inverse'", self.conn).set_index('index')
            # self.list_compare_col = self.df_inverse.columns.to_list()
            self.df_set = pd.read_sql(f"SELECT * FROM 'set'", self.conn).set_index('index')


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


    def onStartButtonClicked(self):
        self.exchange = self.make_exchange_kis()


        self.thread = do_trade(self,self.exchange,self.df_set)
        self.thread.start()

        self.thread.qt_open.connect(self.qtable_open)
        self.thread.qt_closed.connect(self.qtable_closed)
        # self.thread.qt_history.connect(self.qtable_history)
        # self.thread.qt_have.connect(self.qtable_have)
        self.thread.val_light.connect(self.effect_start)
        # self.thread.val_wallet.connect(self.QL_wallet.setText)
        # self.thread.val_time.connect(self.QL_time.setText)
        # self.thread.qt_set.connect(self.save_set)
        # self.thread.qt_future.connect(self.qtable_future)
        # self.thread.qt_inverse.connect(self.qtable_inverse)
        self.thread.shutdown_signal.connect(self.show_shutdown_dialog)

        # self.set_signal.connect(self.thread.change_set)
        # self.buy_signal.connect(self.thread.buy_manual)

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
            df['평가금액'] = df['평가금액'].apply(lambda int_num: "{:,}".format(int_num))
            df['매입금액'] = df['매입금액'].apply(lambda int_num: "{:,}".format(int_num))
            df['평가손익'] = df['평가손익'].apply(lambda int_num: "{:,}".format(int_num))
            df = df[['상품명','종목코드','평가손익','수익률','매입금액','청산가능수량','잔고수량','체결평균단가','평가금액','정산단가','지수종가',
                     '상품번호','상품유형코드','매도매수구분명','매매손익금액']]
            self.set_table_make(self.QT_trade_open, df)
            # self.df_qtable_have = df.copy()
    def qtable_inverse(self,df): #iverse 자산 변경 시 저장을 위해
        df.to_sql('inverse', self.conn, if_exists='replace')
    def qtable_future(self,df):
        if not df.empty:
            df = df[['market','ticker','보유수량', '매수금액', '현재가', '방향', '수익률', '손익',
                     '진입가', '청산가']]
            self.set_table_make(self.QT_trade_closed, df)
        else:
            self.set_table_make(self.QT_trade_closed, pd.DataFrame())
    def qtable_open(self,df):
        # df_active = df[['market','ticker', '주문시간', '주문수량', '매수금액', '주문가', '상태', 'category', 'spot비율','short비율','id']]
        # '잔고수량', '체결평균단가', '평가금액', '정산단가',
        # '지수종가', '청산가능수량',  '평가손익',
        # '상품번호', '상품명', '상품유형코드',
        # '매도매수구분명', '매매손익금액'
        # df_active = df[['종목코드','매입금액', '주문시간', '주문수량', '매수금액', '주문가', '상태', 'category', 'spot비율','short비율','id']]
        # if not df_active['매수금액'].isna().any():
        #     df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        # df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_open, df)

    def qtable_closed(self, df):
        # if not self.df_closed_old.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
        #     df.to_sql('closed', self.conn, if_exists='replace')
        #     self.df_closed_old = df.copy()
        # df_active = df[['market','ticker', '체결시간', '주문수량', 'id', '수수료', '매수금액', '주문가', '상태',
        #           'category', 'spot비율','short비율']]
        # df_active['매수금액'] = df_active['매수금액'].apply(lambda int_num: "{:,}".format(int_num))
        # df_active['주문가'] = df_active['주문가'].apply(lambda int_num: "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_closed, df)

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

    def make_exchange_kis(self):
        key = self.df_set.loc['api', 'val']
        secret = self.df_set.loc['secret', 'val']
        acc_no = self.df_set.loc['account', 'val']
        if key == '' or secret == '' or acc_no == '' :
            print('api 확인 필요')
            return 0
        elif key == None or secret == None or acc_no == None :
            print('api 확인 필요')
            return 0
        else:
            market = '선옵'
            mock = False
            exchange = KIS.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, market=market, mock=mock)
        return exchange

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

    def time_sync(self):
        print(datetime.datetime.now())
        subprocess.Popen('python timesync.py')

class common_define():
    def __init__(self,ex_bybit,session,ex_binance):
        pass
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





