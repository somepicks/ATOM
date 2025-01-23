import sys

# import pyupbit
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject, Qt

import sqlite3
import pandas as pd
import numpy as np
import ATOM_stg_numpy
import requests
import json
# import ATOM_chart_numpy
# import ATOM_chart
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
import tab_chart_table
import time
from datetime import datetime, timedelta
import ccxt
# import talib
from PyQt5.QtTest import *
# import cal_krx
import ATOM_backtest_numpy
import ATOM_bt_thread_numpy
import KIS
from pprint import pprint
# import get_df
# import tab_trade
import CYBOS_DB
import common_def
import math

pd.set_option('display.max_columns', None)  # 모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1500)
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment', None)  # SettingWithCopyWarning 경고를 끈다


class make_data(QThread):
    # 작업이 끝났을 때 신호를 발생시킨다.
    # finished = pyqtSignal()
    val = pyqtSignal(pd.DataFrame, pd.DataFrame)

    # val_df_detail = pyqtSignal(pd.DataFrame)
    # val_save = pyqtSignal(bool)

    def __init__(self, parent, dict_info):
        super().__init__(parent)

        self.dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240,
                                '일봉': 1440, '주봉': 10080}
        self.dict_bong = dict_info['dict_bong']
        self.market = dict_info['market']
        self.ticker = dict_info['ticker']
        self.bong = dict_info['bong']
        self.bong_detail = dict_info['bong_detail']
        self.conn_DB = dict_info['connect']
        self.start_day = datetime.strptime(dict_info['start_day'], '%Y-%m-%d')
        self.end_day = datetime.strptime(dict_info['end_day'], '%Y-%m-%d')

    def run(self):
        # 첫 번째 작업
        # 첫 번째 작업이 끝난 후 두 번째 작업을 진행
        # ticker_detail = self.ticker + '_' + self.dict_bong[self.bong_detail]
        if self.market == '코인':
            file = 'DB/DB_bybit.db'
        elif self.market == '국내주식':
            file = 'DB/DB_stock.db'
        elif self.market == '국내선옵':
            file = 'DB/DB_futopt.db'

        self.conn_DB = sqlite3.connect(file, check_same_thread=False)

        df_detail = pd.read_sql(f"SELECT * FROM '{self.ticker}'", self.conn_DB).set_index('날짜')
        df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환

        df_detail = df_detail.loc[(df_detail.index >= self.start_day) & (df_detail.index <= self.end_day)]

        if self.market == '코인':
            df_detail.index = df_detail.index - pd.Timedelta(hours=9)
            df, df_detail = common_def.detail_to_spread(df_detail, self.bong, self.bong_detail, False)
            df_detail.index = df_detail.index + pd.Timedelta(hours=9)
            df.index = df.index + pd.Timedelta(hours=9)
            for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
                start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
                end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(
                    minutes=self.dict_bong_stamp[self.bong_detail])
                df_detail.loc[start_time:end_time, '장시작시간'] = start_time
                df_detail.loc[start_time:end_time, '장종료시간'] = end_time
        else:
            df_detail.index = df_detail.index - pd.Timedelta(minutes=self.dict_bong_stamp[self.bong_detail])
            # df_detail = df_detail[df_detail.index >= datetime.strptime("20200326","%Y%m%d")]
            df, df_detail = common_def.detail_to_spread(df_detail, self.bong, self.bong_detail, False)
            df_detail = self.make_start_stop(df_detail, self.dict_bong_stamp[self.bong_detail])

        df_detail['현재시간'] = df_detail.index
        if self.bong == '일봉':
            df_detail['종료시간'] = df_detail['장종료시간'].copy()
        elif self.bong != '일봉' and self.bong != '주봉' and self.bong != '월봉':
            # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
            df_detail_end_time = df_detail['현재시간'].resample(f'{self.dict_bong_stamp[self.bong]}min').last()
            df_detail_end_time = pd.Series(df_detail_end_time, name='종료시간')  # 추출한 시리즈의 이름을 종료시간으로 변경
            df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
            df_detail.ffill(inplace=True)

        # save = True
        df['매수가'] = np.nan
        df['매도가'] = np.nan
        df['수량'] = np.nan
        df['수익률'] = np.nan
        df['최고수익률'] = np.nan
        df['최저수익률'] = np.nan
        df['수익금'] = np.nan
        df['전략수익률'] = np.nan
        df['매수금액'] = np.nan
        df['매도금액'] = np.nan
        df['잔고'] = np.nan
        df['수수료'] = np.nan
        df['자산'] = np.nan
        # return df,df_detail,save
        print('데이터프레임 생성완료')

        self.val.emit(df, df_detail)  # 첫 번째 작업이 끝났음을 신호로 알림

    def make_start_stop(self, df_detail, detail_stamp):
        # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
        df_detail['장시작시간'] = np.nan
        serise_start_t = df_detail.groupby(df_detail.index.date).transform(
            lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
        df_detail['장시작시간'] = serise_start_t
        df_detail['장종료시간'] = np.nan
        serise_end_t = df_detail.groupby(df_detail.index.date).transform(
            lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
        df_detail['장종료시간'] = serise_end_t
        # 시작 시간과 종료 시간 확인
        start_time = df_detail.index.min()
        end_time = df_detail.index.max()
        # 전체 1분 단위의 시간 인덱스 생성
        full_time_index = pd.date_range(start=start_time, end=end_time, freq=f'{detail_stamp}min')
        # 기존 데이터프레임을 새로운 인덱스에 맞춰 재인덱싱
        df_detail = df_detail.reindex(full_time_index)
        # 누락된 데이터를 바로 위의 데이터로 채우기
        # df_detail = df_detail.fillna(method='ffill')
        df_detail.ffill(inplace=True)
        # '장시작시간', '장종료시간'열을 딕셔너리로 만들기
        df_time = df_detail[['장시작시간', '장종료시간']]
        df_time = df_time.drop_duplicates()
        result_dict = df_time.set_index('장시작시간')['장종료시간'].to_dict()
        # 빈 리스트를 생성하여 각 시간 범위에 해당하는 데이터프레임을 저장
        dfs = []
        # 시간 범위 딕셔너리를 순회하며 데이터프레임 슬라이싱
        for start_time, end_time in result_dict.items():
            start_time = pd.to_datetime(start_time)
            end_time = pd.to_datetime(end_time)
            sliced_df = df_detail[start_time:end_time]
            dfs.append(sliced_df)
        df_detail = pd.concat(dfs)
        ###
        return df_detail

class CalendarPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)  # 팝업 형태로 설정
        self.setGeometry(0, 0, 300, 250)  # 팝업 크기 설정

        # QCalendarWidget 생성
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.date_selected)  # 날짜 클릭 이벤트 연결

        # 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)
        self.selected_date = None

    def date_selected(self, date):
        """날짜가 선택되면 저장하고 팝업 닫기"""
        self.selected_date = date.toString("yyyy-MM-dd")
        self.accept()  # QDialog를 닫음

class Window(QWidget):
    def __init__(self, chart_table):
        super().__init__()
        self.chart_table = chart_table
        self.init_file()
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m',
                          '4시간봉': '4h', '일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
        self.dict_bong_reverse = dict(zip(self.dict_bong.values(), self.dict_bong.keys()))
        self.set_UI()
        self.QCB_market.activated[str].connect(lambda: self.select_market(self.QCB_market.currentText()))
        self.QPB_DB_save.clicked.connect(lambda: self.save_DB())

        # conn = sqlite3.connect('DB/bt.db')
        # df = pd.read_sql(f"SELECT * FROM 'bt'", conn).set_index('날짜')
        #
        # df.index = pd.to_datetime(df.index)
        # df.index.rename('index', inplace=True)  # 인덱스명 변경

        # self.QPB_DB_save.clicked.connect(lambda: self.test(df))

        self.QPB_stg_buy_save.clicked.connect(lambda: self.save_stg_buy())
        self.QCB_stg_buy.activated[str].connect(lambda: self.selectedCombo_stg_buy())
        # self.QPB_start.clicked.connect(lambda: self.backtest())
        self.QPB_start.clicked.connect(self.do_backtest)
        self.QPB_stop.clicked.connect(self.on_stop)
        self.QPB_save_bt.clicked.connect(lambda: self.save_bt())
        self.QPB_stg_sell_save.clicked.connect(lambda: self.save_stg_sell())
        self.QCB_stg_sell.activated[str].connect(lambda: self.selectedCombo_stg_sell())
        self.QCB_ticker.activated[str].connect(self.select_ticker)
        self.QPB_stg_buy_del.clicked.connect(self.del_stg_buy)
        self.QPB_stg_sell_del.clicked.connect(self.del_stg_sell)
        self.QCB_bong.activated[str].connect(self.select_bong)
        self.QLE_bet.textChanged.connect(self.select_bet)

        self.QLE_start.mousePressEvent = self.show_calendar_popup_start  # 클릭 시 팝업 호출
        self.QLE_end.mousePressEvent = self.show_calendar_popup_end  # 클릭 시 팝업 호출



        # self.QCB_krx.setChecked(True)

        #
        # self.QCB_market.setCurrentText('국내시장')
        # self.QCB_ticker.setCurrentText('122630')
        # self.QCB_bong.setCurrentText('일봉')
        # self.QCB_bong_detail.setCurrentText('5분봉')

        self.QPB_stop.setEnabled(False)
        self.db_name = ''

        # 테스트용
        # self.QCB_ticker.addItems(['BTC'])
        # self.QCB_market.setCurrentText('코인')
        # self.QCB_ticker.setCurrentText('BTC')
        # self.QCB_bong.setCurrentText('5분봉')
        # self.QCB_bong_detail.setCurrentText('1분봉')

    def set_UI(self):
        self.QTE_stg_buy = QTextEdit()
        self.QTE_stg_sell = QTextEdit()
        self.QPB_bar = QProgressBar(self)
        self.setWindowTitle(f'BACKTEST')
        QVB_stg = QVBoxLayout()
        QVB_stg.addWidget(self.QTE_stg_buy)
        QVB_stg.addWidget(self.QTE_stg_sell)
        QGL = QGridLayout()
        # self.QCB_krx = QCheckBox('국내시장')
        # self.QCB_bybit = QCheckBox('바이비트')
        self.QCB_market = QComboBox()
        self.QCB_market.addItems(['', '코인', '국내주식', '국내선옵'])
        # self.QCB_detail = QCheckBox('상세 백테')
        # self.QCB_detail.setChecked(True)
        self.QCB_chart = QCheckBox('차트보기')
        self.QCB_chart.setChecked(True)
        self.QCB_ticker = QComboBox()
        self.QCB_bong = QComboBox()
        li_bong = ['봉']
        li_bong_keys = list(self.dict_bong.keys())
        li_bong.extend(li_bong_keys)
        self.QCB_bong.addItems(li_bong)
        self.QCB_bong_detail = QComboBox()
        li_bong_detail = ['상세봉']
        li_bong_keys = list(self.dict_bong.keys())
        li_bong_detail.extend(li_bong_keys)
        self.QCB_bong_detail.addItems(li_bong_detail)
        self.QLE_DB_ticker = QLineEdit()
        self.QPB_DB_save = QPushButton('DB 저장')
        self.QCB_stg_buy = QComboBox()
        self.QLE_stg_buy = QLineEdit()
        self.QLE_division_buy = QLineEdit()
        self.QPB_stg_buy_save = QPushButton('매수전략 저장')
        self.QPB_stg_buy_del = QPushButton('매수전략 삭제')
        self.QPB_stg_sell_del = QPushButton('매도전략 삭제')
        QL_start = QLabel('              시작일')
        self.QLE_start = QLineEdit()
        QL_bet = QLabel('        배팅사이즈')
        self.QLE_bet = QLineEdit('100')
        QL_end = QLabel('              종료일')
        self.QLE_end = QLineEdit()
        self.QCB_stg_sell = QComboBox()
        self.QLE_stg_sell = QLineEdit()
        self.QLE_division_sell = QLineEdit()

        self.QPB_stg_sell_save = QPushButton('매도전략 저장')
        self.QPB_start = QPushButton('백테스트')
        self.QPB_stop = QPushButton('중지')
        self.QPB_save_bt = QPushButton('백테스트저장')
        self.QLE_start.setText('2010-01-01')
        self.QLE_end.setText(datetime.now().strftime('%Y-%m-%d'))
        self.QLE_start.setReadOnly(True)  # 직접 입력 방지
        self.QLE_end.setReadOnly(True)  # 직접 입력 방지
        self.QL_state = QLabel()
        self.QCB_history = QComboBox()
        QT_history = QTableWidget()
        QT_history_detail = QTableWidget()
        QTE_var_buy = QTextEdit()
        QTE_var_sell = QTextEdit()

        # self.QCB_krx.setFixedWidth(100)
        # self.QCB_bybit.setFixedWidth(100)
        self.QCB_market.setFixedWidth(100)
        # self.QCB_detail.setFixedWidth(100)
        self.QCB_ticker.setFixedWidth(100)
        self.QCB_bong.setFixedWidth(100)
        self.QCB_bong_detail.setFixedWidth(100)
        self.QCB_stg_buy.setFixedWidth(100)
        self.QLE_stg_buy.setFixedWidth(100)
        self.QPB_stg_buy_save.setFixedWidth(100)
        self.QPB_stg_buy_del.setFixedWidth(100)
        self.QLE_division_buy.setFixedWidth(100)
        QL_start.setFixedWidth(100)
        self.QLE_start.setFixedWidth(100)
        self.QLE_DB_ticker.setFixedWidth(100)
        self.QPB_DB_save.setFixedWidth(100)
        QL_end.setFixedWidth(100)
        self.QLE_end.setFixedWidth(100)
        self.QCB_stg_sell.setFixedWidth(100)
        self.QLE_stg_sell.setFixedWidth(100)
        self.QPB_stg_sell_save.setFixedWidth(100)
        self.QPB_stg_sell_del.setFixedWidth(100)
        self.QLE_division_sell.setFixedWidth(100)
        self.QPB_start.setFixedWidth(100)
        self.QPB_stop.setFixedWidth(100)
        QL_bet.setFixedWidth(100)
        self.QLE_bet.setFixedWidth(100)
        self.QL_state.setFixedWidth(100)
        QGL.setSpacing(10)

        # QGL.addWidget(self.QCB_krx,0,0)
        # QGL.addWidget(self.QCB_bybit,0,1)
        QGL.addWidget(self.QCB_market, 0, 0)
        QGL.addWidget(self.QCB_ticker, 0, 1)
        QGL.addWidget(self.QCB_bong, 1, 0)
        QGL.addWidget(self.QCB_bong_detail, 1, 1)
        QGL.addWidget(self.QLE_DB_ticker, 2, 0)
        QGL.addWidget(self.QPB_DB_save, 2, 1)
        QGL.addWidget(self.QCB_stg_buy, 3, 0)
        QGL.addWidget(self.QLE_stg_buy, 3, 1)
        # QGL.addWidget(self.QPB_stg_buy_save,4,0,1,2)
        QGL.addWidget(self.QPB_stg_buy_save, 4, 0)
        QGL.addWidget(self.QPB_stg_buy_del, 4, 1)
        QGL.addWidget(QL_start, 5, 0)
        QGL.addWidget(self.QLE_start, 5, 1)
        QGL.addWidget(QL_end, 6, 0)
        QGL.addWidget(self.QLE_end, 6, 1)
        QGL.addWidget(QL_bet, 7, 0)
        QGL.addWidget(self.QLE_bet, 7, 1)
        QGL.addWidget(self.QPB_start, 8, 0)
        QGL.addWidget(self.QPB_stop, 8, 1)
        QGL.addWidget(self.QPB_save_bt, 9, 0)
        QGL.addWidget(self.QCB_chart, 9, 1)
        QGL.addWidget(self.QCB_stg_sell, 10, 0)
        QGL.addWidget(self.QLE_stg_sell, 10, 1)
        QGL.addWidget(self.QPB_stg_sell_save, 11, 0)
        QGL.addWidget(self.QPB_stg_sell_del, 11, 1)
        QGL.addWidget(self.QPB_bar, 12, 0, 1, 2)
        # QGL.addWidget(QLabel('상태'), 13, 0)
        # QGL.addWidget(self.QL_state, 13, 1)

        # QHB_ varsQHBoxLayout()

        QVB_history = QVBoxLayout()
        QVB_history.addWidget(self.QCB_history)
        QVB_history.addWidget(QT_history)
        QVB_history.addWidget(QT_history_detail)

        QHB_main = QHBoxLayout()
        QHB_main.addLayout(QVB_stg)
        QHB_main.addLayout(QGL)
        QHB_main.addLayout(QVB_history)

        self.setLayout(QHB_main)
        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 12pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 12pt 나눔고딕; "
        self.QTE_stg_buy.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE_stg_sell.setStyleSheet(StyleSheet_Qtextedit)
        # StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                     "border-color: black; font: 12pt 나눔고딕; "
        QT_history.setStyleSheet(StyleSheet_Qtextedit)
        QT_history_detail.setStyleSheet(StyleSheet_Qtextedit)
        font = QFont('나눔고딕')
        self.QTE_stg_buy.setTabStopWidth(QFontMetrics(font).width(' ' * 4))
        self.QTE_stg_sell.setTabStopWidth(QFontMetrics(font).width(' ' * 4))
        self.highlighter_buy = common_def.PythonHighlighter(self.QTE_stg_buy.document())
        self.highlighter_sell = common_def.PythonHighlighter(self.QTE_stg_sell.document())

        # self.setFixedSize(1200,800)
        # self.QCB_bong_detail.setCurrentText('5분봉')
        # self.QCB_bong_detail.setEnabled(False)
    def save_DB(self):
        # import pandas_datareader.data as web
        from pandas import to_numeric
        self.BTN_efect(self.QPB_DB_save)
        # dict_bong = {'1분봉':'1m','3분봉': '3m', '5분봉': '5m', '30분봉': '30m', '4시간봉': '4h', '일봉': 'd', '주봉':'W'}

        market = self.QCB_market.currentText()
        ticker = self.QLE_DB_ticker.text()
        if market == '코인':
            if ticker == '':  # 티커가 명시되어 있을 경우
                raise Exception('ticker 확인 필요')
            # ticker_bong = self.QLE_DB_ticker.text()+'_'+dict_bong[self.QCB_bong.currentText()]
            # self.exchange = self.make_exchange_bybit()
            db_file = 'DB/DB_bybit.db'
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_list = cursor.fetchall()
            # print(f"{table_list=}")
            # print(f"{self.dict_bong.values()=}")
            # if not
            if table_list:
                table_list = np.concatenate(table_list).tolist()
            # bong = self.QCB_bong_detail.currentText()
            bong = '1분봉'
            # raise
            # for bong in self.dict_bong.values():
            #     print(self.QLE_DB_ticker.text() + '_' + bong)
            #     ticker_bong = ticker + '_' + bong
            #     print(f"{ticker_bong= }")
            if ticker in table_list:
                df_old = pd.read_sql(f"SELECT * FROM '{ticker}'", conn).set_index('날짜')
                if df_old.empty:
                    start_time = self.exchange.parse8601(f'2020-01-01T00:00:00Z')
                    df_new = self.get_db_bybit(ticker, bong, start_time)
                    df_new.to_sql(ticker, conn, if_exists='replace')
                else:
                    df_old.index = pd.to_datetime(df_old.index)  # datime형태로 변환
                    last = df_old.index[-1] + pd.DateOffset(hours=-9)
                    df_old.drop(index=df_old.index[-1], inplace=True)
                    last_day = str(last)[:10]
                    last_time = str(last)[11:]
                    start_time = self.exchange.parse8601(f'{last_day}T{last_time}Z')
                    df_new = self.get_db_bybit(ticker, bong, start_time)
                    df = pd.concat([df_old, df_new])
                    df.to_sql(ticker, conn, if_exists='replace')
            else:
                start_time = self.exchange.parse8601(f'2020-01-01T00:00:00Z')
                # end_time = self.exchange.milliseconds()  # 현재 시간
                df_new = self.get_db_bybit(ticker, bong, start_time)
                df_new.to_sql(ticker, conn, if_exists='replace')
            # raise
            cursor.close()
            conn.close()
            # print(table_list)
            # for i, t in enumerate(table_list):
            #     table_list[i] = str(t)[:t.index('_')]
            # table_list = list(set(table_list))

            table_list.insert(0, '전체')
            self.QCB_ticker.clear()
            self.QCB_ticker.addItems(table_list)

        elif market == '국내주식' or market == '국내선옵':
            cursor = self.conn_DB.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            try:
                list_table = np.concatenate(cursor.fetchall()).tolist()
            except:
                list_table = []
            cursor.close()

            # if not 'stocks_info' in list_table:
            #     if market == '국내주식':
            #         ticker = self.QCB_ticker.currentText()
            #     elif market == '국내선옵':
            #         pass

            dict_ticker_reverse = dict(zip(self.dict_ticker.values(), self.dict_ticker.keys()))
            try:
                ticker = dict_ticker_reverse[ticker]  # dict_ticker에 종목이 있을 경우
            except:  # dict_ticker에 종목이 없을경우
                if market == '국내주식':
                    print('종목명 확인 필요')
                elif market == '국내선옵' and (ticker[:3] == '201' or ticker[:3] == '301'):
                    ticker = ticker[:4] + 'A' + ticker[-3:]  # A는 근월물, B는 차월물 차월물은 확인할 필요 없기 때문에 A로 통일

            self.save_DB_CYBOS(market, ticker, list_table)

            # if market == '국내주식':
            #     stock_list = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
            #     stock_list.종목코드 = stock_list.종목코드.map('{:06d}'.format)  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
            #     stock_list = stock_list[['회사명', '종목코드', '업종', '주요제품', '상장일']]  # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
            #
            # if not ticker == '': #티커가 명시되어 있을 경우
            #     stock_code = stock_list.loc[stock_list['종목코드']==self.QLE_DB_ticker.text()]
            # else: #티커가 명시되어 있지 않을 경우 ticker 로딩에 표시되어있는 종목을 저장
            #     raise print('티커 명시 할 것')
            #
            # if self.QCB_bong.currentText() != '일봉':
            #     raise '일봉 이외에는 지원하지 않음'
            # # ticker_bong = self.QLE_DB_ticker.text() + '_' + dict_bong[self.QCB_bong.currentText()]
            # url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
            # json_data = json.loads(requests.get(url).text)
            # df = pd.DataFrame(json_data['result']['etfItemList'])
            # stock_code = df.loc[df['itemcode'] == self.QLE_DB_ticker.text()]
            # stock_name = stock_code.loc[stock_code.index[0],'itemname']
            # print(f"{stock_name} DB 저장 중...")
            # stock_code_name = self.QLE_DB_ticker.text()
            #
            # today = datetime.now().strftime('%Y-%m-%d')
            # start_day = '2000-01-01'
            # conn = sqlite3.connect('DB/DB_stock.db')
            #
            # df.rename(columns={'Open':'시가','High':'고가','Low':'저가','Close':'종가','Volume':'거래량'}, inplace=True)  # 컬럼명 변경
            # df.index.rename('날짜',inplace = True) #인덱스명 변경
            # df.to_sql(stock_code_name,conn,if_exists='replace')
            # print('저장 완료')
        else:
            raise print('데이터를 저장 할 시장을 선택해주세요.')

        print('DB저장 완료')

    def save_DB_CYBOS(self, market, ticker, list_table):
        import win32com.client
        try:
            instCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
        except:
            print('32비트로 실행했는지 확인 필요')
            return
        if instCpCybos.IsConnect == 1:
            # print(instCpCybos.IsConnect)
            print('대신증권 연결완료')
        else:
            # print(instCpCybos.IsConnect)
            raise '연결 실패 코드가 맞는지 32비트로 실행 되었는지 관리자 권한으로 실행했는지 확인 필요'
        if market == '국내주식':
            instChart = win32com.client.Dispatch("CpSysDib.StockChart")  # 주식 데이터 연결
            # table_list = [x[:6] for x in table_list] #앞에 6자리만 잘라서 리스트로 다시 저장
            ticker_name = 'A' + ticker
        elif market == '국내선옵':
            instChart = win32com.client.Dispatch("CpSysDib.FutOptChart")  # 선물/옵션 데이터 연결
            ticker_name = ticker
        else:
            instChart = ''
            ticker_name = ticker

        bong_detail = self.QCB_bong_detail.currentText()

        if ticker + '_' + self.dict_bong[bong_detail] in list_table:
            df_old = pd.read_sql(f"SELECT * FROM '{ticker + '_' + self.dict_bong[bong_detail]}'",
                                 self.conn_DB).set_index('날짜')
            df_old.index = pd.to_datetime(df_old.index)  # datime형태로 변환
            start_day = df_old.index[-1].date()  # 인덱스의 마지막요소 추출
            start_day = datetime.strftime(start_day, '%Y%m%d')
            start_day = int(start_day)
        else:
            start_day = 20100101
            df_old = pd.DataFrame()
        end_day = datetime.now().strftime("%Y%m%d")

        print(f"{market= }, {ticker_name= }, 다운로드 대상= {bong_detail}, {start_day= }, {end_day= }", end='...')

        db_down = CYBOS_DB.db_down()
        df = db_down.get_candle(instChart, market, ticker_name, bong_detail, start_day, end_day)
        if bong_detail == '일봉' or bong_detail == '주봉' or bong_detail == '월봉':
            df.drop(df.index[0], inplace=True)  # 가장 최근행은 아직 갱신중일 수 있으므로 삭제
        df = df[::-1]  # 거꾸로 뒤집기
        df = pd.concat([df_old, df])
        df = df.loc[~df.index.duplicated(keep='last')]  # 중복인덱스 제거

        df = round(df, 2)
        df.to_sql(ticker + '_' + self.dict_bong[bong_detail], self.conn_DB, if_exists='replace')

    def save_stg_buy(self):
        self.BTN_efect(self.QPB_stg_buy_save)
        conn = sqlite3.connect('DB/strategy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()
        cursor.close()
        if self.QCB_market.currentText() == '국내주식' or self.QCB_market.currentText() == '국내선옵':
            if not table_list:
                df = pd.DataFrame(columns=['전략코드'])
                df['전략코드'] = pd.Series([self.QTE_stg_buy.toPlainText()], index=[self.QLE_stg_buy.text()])
                df.to_sql('krx_buy', conn, if_exists='replace')
            else:
                table_list = np.concatenate(table_list).tolist()
                if 'krx_buy' in table_list:
                    df = pd.read_sql(f"SELECT * FROM 'krx_buy'", conn).set_index('index')
                    if self.QLE_stg_buy.text() == '':
                        df.loc[self.QCB_stg_buy.currentText(), '전략코드'] = self.QTE_stg_buy.toPlainText()
                    elif not self.QLE_stg_buy.text() == '':
                        df.loc[self.QLE_stg_buy.text(), '전략코드'] = self.QTE_stg_buy.toPlainText()
                elif not 'krx_buy' in table_list:
                    df = pd.DataFrame(columns=['전략코드'])
                    df['전략코드'] = pd.Series([self.QTE_stg_buy.toPlainText()], index=[self.QLE_stg_buy.text()])
            df.to_sql('krx_buy', conn, if_exists='replace')
        elif self.QCB_market.currentText() == '코인':
            if not table_list:
                df = pd.DataFrame(columns=['전략코드'])
                df['전략코드'] = pd.Series([self.QTE_stg_buy.toPlainText()], index=[self.QLE_stg_buy.text()])
                df.to_sql('coin_buy', conn, if_exists='replace')
            else:
                table_list = np.concatenate(table_list).tolist()
                if 'coin_buy' in table_list:
                    df = pd.read_sql(f"SELECT * FROM 'coin_buy'", conn).set_index('index')
                    if self.QLE_stg_buy.text() == '':
                        df.loc[self.QCB_stg_buy.currentText(), '전략코드'] = self.QTE_stg_buy.toPlainText()
                    elif not self.QLE_stg_buy.text() == '':
                        df.loc[self.QLE_stg_buy.text(), '전략코드'] = self.QTE_stg_buy.toPlainText()
                elif not 'coin_buy' in table_list:
                    df = pd.DataFrame(columns=['전략코드'])
                    df['전략코드'] = pd.Series([self.QTE_stg_buy.toPlainText()], index=[self.QLE_stg_buy.text()])
            df.to_sql('coin_buy', conn, if_exists='replace')
        cursor.close()
        conn.close()
        self.QCB_stg_buy.clear()
        self.QCB_stg_buy.addItems(df.index.tolist())
        if self.QLE_stg_buy.text() != '':
            self.QCB_stg_buy.setCurrentText(self.QLE_stg_buy.text())

    # def stg_buy_loading(self):

    def save_stg_sell(self):
        self.BTN_efect(self.QPB_stg_sell_save)
        conn = sqlite3.connect('DB/strategy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()
        cursor.close()
        if self.QCB_market.currentText() == '국내주식' or self.QCB_market.currentText() == '국내선옵':
            if not table_list:
                df = pd.DataFrame(columns=['전략코드'])
                df['전략코드'] = pd.Series([self.QTE_stg_sell.toPlainText()], index=[self.QLE_stg_sell.text()])
                df.to_sql('krx_sell', conn, if_exists='replace')
            else:
                table_list = np.concatenate(table_list).tolist()
                if 'krx_sell' in table_list:
                    df = pd.read_sql(f"SELECT * FROM 'krx_sell'", conn).set_index('index')
                    if self.QLE_stg_sell.text() == '':
                        df.loc[self.QCB_stg_sell.currentText(), '전략코드'] = self.QTE_stg_sell.toPlainText()
                    elif not self.QLE_stg_sell.text() == '':
                        df.loc[self.QLE_stg_sell.text(), '전략코드'] = self.QTE_stg_sell.toPlainText()
                elif not 'krx_sell' in table_list:
                    df = pd.DataFrame(columns=['전략코드'])
                    df['전략코드'] = pd.Series([self.QTE_stg_sell.toPlainText()], index=[self.QLE_stg_sell.text()])
            df.to_sql('krx_sell', conn, if_exists='replace')
        elif self.QCB_market.currentText() == '코인':
            if not table_list:
                df = pd.DataFrame(columns=['전략코드'])
                df['전략코드'] = pd.Series([self.QTE_stg_sell.toPlainText()], index=[self.QLE_stg_sell.text()])
                df.to_sql('coin_sell', conn, if_exists='replace')
            else:
                table_list = np.concatenate(table_list).tolist()
                if 'coin_sell' in table_list:
                    df = pd.read_sql(f"SELECT * FROM 'coin_sell'", conn).set_index('index')
                    if self.QLE_stg_sell.text() == '':
                        df.loc[self.QCB_stg_sell.currentText(), '전략코드'] = self.QTE_stg_sell.toPlainText()
                    elif not self.QLE_stg_sell.text() == '':
                        df.loc[self.QLE_stg_sell.text(), '전략코드'] = self.QTE_stg_sell.toPlainText()
                elif not 'coin_sell' in table_list:
                    df = pd.DataFrame(columns=['전략코드'])
                    df['전략코드'] = pd.Series([self.QTE_stg_sell.toPlainText()], index=[self.QLE_stg_sell.text()])
            df.to_sql('coin_sell', conn, if_exists='replace')
        cursor.close()
        conn.close()
        self.QCB_stg_sell.clear()
        self.QCB_stg_sell.addItems(df.index.tolist())
        if self.QLE_stg_sell.text() != '':
            self.QCB_stg_sell.setCurrentText(self.QLE_stg_sell.text())

    def del_stg_buy(self):
        conn = sqlite3.connect('DB/strategy.db')
        table = 'coin_buy' if self.QCB_market.currentText() == '코인' else 'krx_buy'
        if self.QCB_stg_buy.currentText() != '':
            df_stg = pd.read_sql(f"SELECT * FROM {table}", conn).set_index('index')
            df_stg.drop([f'{self.QCB_stg_buy.currentText()}'], inplace=True)
            self.QCB_stg_buy.clear()
            self.QCB_stg_buy.addItems(df_stg.index.tolist())
            df_stg.to_sql(table, conn, if_exists='replace')
            self.QLE_stg_buy.setText(self.QCB_stg_buy.currentText())
        conn.close()

    def del_stg_sell(self):
        conn = sqlite3.connect('DB/strategy.db')
        table = 'coin_sell' if self.QCB_market.currentText() == '코인' else 'krx_sell'
        if self.QCB_stg_sell.currentText() != '':
            df_stg = pd.read_sql(f"SELECT * FROM {table}", conn).set_index('index')
            df_stg.drop([f'{self.QCB_stg_sell.currentText()}'], inplace=True)
            self.QCB_stg_sell.clear()
            self.QCB_stg_sell.addItems(df_stg.index.tolist())
            df_stg.to_sql(table, conn, if_exists='replace')
            self.QLE_stg_sell.setText(self.QCB_stg_sell.currentText())
        conn.close()

    def selectedCombo_stg_buy(self):
        conn = sqlite3.connect('DB/strategy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()
        if not table_list:
            print('* DB 테이블이 비어있음 - 확인 필요 *')
        elif self.QCB_market.currentText() == '국내주식' or self.QCB_market.currentText() == '국내선옵':
            table_list = np.concatenate(
                table_list).tolist()
            if 'krx_buy' in table_list:
                df = pd.read_sql(f"SELECT * FROM 'krx_buy'", conn).set_index('index')
                text_stg = df.loc[self.QCB_stg_buy.currentText(), '전략코드']
                self.QTE_stg_buy.clear()
                self.QTE_stg_buy.setText(text_stg)
                self.QLE_stg_buy.setText(self.QCB_stg_buy.currentText())
        elif self.QCB_market.currentText() == '코인':
            table_list = np.concatenate(
                table_list).tolist()
            if 'coin_buy' in table_list:
                df = pd.read_sql(f"SELECT * FROM 'coin_buy'", conn).set_index('index')
                text_stg = df.loc[self.QCB_stg_buy.currentText(), '전략코드']
                self.QTE_stg_buy.clear()
                self.QTE_stg_buy.setText(text_stg)
                self.QLE_stg_buy.setText(self.QCB_stg_buy.currentText())
        cursor.close()
        conn.close()

    def selectedCombo_stg_sell(self):
        conn = sqlite3.connect('DB/strategy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()
        if not table_list:
            print('* DB 테이블이 비어있음 - 확인 필요 *')
        elif self.QCB_market.currentText() == '국내주식' or self.QCB_market.currentText() == '국내선옵':
            table_list = np.concatenate(table_list).tolist()
            if 'krx_sell' in table_list:
                df = pd.read_sql(f"SELECT * FROM 'krx_sell'", conn).set_index('index')
                text_stg = df.loc[self.QCB_stg_sell.currentText(), '전략코드']
                self.QTE_stg_sell.clear()
                self.QTE_stg_sell.setText(text_stg)
                self.QLE_stg_sell.setText(self.QCB_stg_sell.currentText())
        elif self.QCB_market.currentText() == '코인':
            table_list = np.concatenate(table_list).tolist()
            if 'coin_sell' in table_list:
                df = pd.read_sql(f"SELECT * FROM 'coin_sell'", conn).set_index('index')
                text_stg = df.loc[self.QCB_stg_sell.currentText(), '전략코드']
                self.QTE_stg_sell.clear()
                self.QTE_stg_sell.setText(text_stg)
                self.QLE_stg_sell.setText(self.QCB_stg_sell.currentText())
        cursor.close()
        conn.close()

    def select_ticker(self):
        ticker = self.QCB_ticker.currentText()
        self.QLE_DB_ticker.setText(ticker)
        market = self.QCB_market.currentText()
        if market == '국내주식' or market == '국내선옵':
            dict_ticker_reverse = dict(zip(self.dict_ticker.values(), self.dict_ticker.keys()))
            try:
                ticker = dict_ticker_reverse[ticker]
                # ticker = dict_ticker_reverse[ticker]
            except:
                if market == '국내주식':
                    print('종목명 확인 필요')
                elif market == '국내선옵' and (ticker[:3] == '201' or ticker[:3] == '301'):
                    ticker = ticker

        elif market == '코인':
            ticker = ticker
        new_text = f"진입대상 = '{ticker}'"
        line_num = 0
        self.replace_QTE_line(self.QTE_stg_buy, new_text, line_num)

        # list_bong = [x[x.index('_') + 1:] for x in self.table_list_DB if x[:x.index('_')] == ticker]  # 해당 ticker가 갖고있는 db를 리스트화 [1m,3m,5m...]
        # list_standard_bong = [self.dict_bong_reverse[x] for x in list_bong]
        # list_standard_bong.insert(0, '봉')
        #
        # list_detail_bong = list(self.dict_bong.keys())
        # list_detail_bong.insert(0, '봉')
        # print(self.table_list_DB)
        # self.QCB_bong_detail.clear()
        # self.QCB_bong_detail.addItems(list_detail_bong)
        #
        # if not '1분봉' in list_standard_bong:
        #     list_detail_bong.remove('1분봉')
        #     list_detail_bong.remove('3분봉')
        # elif (not '5분봉' in list_standard_bong) and (not '1분봉' in list_standard_bong):
        #     list_detail_bong.remove('1분봉')
        #     list_detail_bong.remove('3분봉')
        #     list_detail_bong.remove('5분봉')

        # self.QCB_bong.clear()
        # self.QCB_bong.addItems(list_detail_bong)

        if market == '국내주식':
            self.QCB_bong.setCurrentText('일봉')
            self.QCB_bong_detail.setCurrentText('1분봉')
        elif market == '국내선옵':
            self.QCB_bong.setCurrentText('5분봉')
            self.QCB_bong_detail.setCurrentText('1분봉')
        elif market == '코인':
            self.QCB_bong.setCurrentText('4시간봉')
            self.QCB_bong_detail.setCurrentText('1분봉')

    def select_bong(self):
        bong = self.QCB_bong.currentText()
        new_text = f"봉 = {{{bong}:10}}"
        line_num = 1
        self.replace_QTE_line(self.QTE_stg_buy, new_text, line_num)

    def select_bet(self):
        new_text = f"초기자금 = {self.QLE_bet.text()}"
        line_num = 3
        self.replace_QTE_line(self.QTE_stg_buy, new_text, line_num)

    def select_market(self, market):
        list_stg_buy = []
        list_stg_sell = []
        conn_stg = sqlite3.connect('DB/strategy.db')
        if market == '국내주식':
            self.exchange = self.make_exchange_kis()
            self.conn_DB = sqlite3.connect('DB/DB_stock.db', check_same_thread=False)
            self.QLE_bet.setText('1000000')

            market_name = 'krx'
            self.stocks_info = pd.read_sql(f"SELECT * FROM 'stocks_info'", self.conn_DB).set_index('종목코드')
        elif market == '국내선옵':
            self.exchange = self.make_exchange_kis()
            self.conn_DB = sqlite3.connect('DB/DB_futopt.db', check_same_thread=False)
            self.QLE_bet.setText('10000000')
            # conn_stg = sqlite3.connect('DB/stg_futopt.db')

            market_name = 'krx'
        elif market == '코인':
            self.exchange, self.ex_pybit = common_def.make_exchange_bybit(False)
            self.conn_DB = sqlite3.connect('DB/DB_bybit.db', check_same_thread=False)
            self.QLE_bet.setText('100')
            #             conn_stg = sqlite3.connect('DB/stg_bybit.db')

            market_name = 'coin'
            # self.stocks_info = pd.DataFrame()
            # self.QCB_bong_detail.setCurrentText('1분봉')
            # self.QCB_bong_detail.setEnabled(False)
        else:
            market_name = ''

        cursor = self.conn_DB.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        self.table_list_DB = cursor.fetchall()
        cursor.close()
        if not self.table_list_DB:
            print(f"{self.table_list_DB= }")
            print('* DB 테이블이 비어있음 - 확인 필요 *')
            # raise
        else:
            self.table_list_DB = np.concatenate(self.table_list_DB).tolist()

        list_ticker = []
        # for x in self.table_list_DB:
        #     if '_' in x:
        #         x = x[:x.index('_')]
        #     list_ticker.append(x)
        # list_tickers = [x[:x.index('_')] for x in self.table_list_DB if '_' in x]  # ticker 리스트화
        # list_ticker = list(set(list_tickers))
        if market == '국내주식':
            list_ticker.remove('stocks')
            self.dict_ticker = dict(zip(self.stocks_info.index.tolist(), self.stocks_info['종목명']))
            list_ticker = [self.dict_ticker[x] for x in list_ticker if x in self.stocks_info.index.tolist()]
        elif market == '국내선옵':
            global 콜옵션, 콜옵션_위클리, 풋옵션, 풋옵션_위클리
            콜옵션 = '콜옵션'
            콜옵션_위클리 = '콜옵션_위클리'
            풋옵션 = '풋옵션'
            풋옵션_위클리 = '풋옵션_위클리'
            self.dict_ticker = {'코스피200선물':'10100', '미니코스피200선물':'10500', '코스닥150선물':'10600', {콜옵션:""}:'',{콜옵션_위클리:""}:'', {풋옵션:""}:'',{풋옵션_위클리:""}:'' }
            # new_list_ticker = []
            # for x in list_ticker:
            #     if x in self.dict_ticker.keys():
            #         new_list_ticker.append(self.dict_ticker[x])
            #     else:
            #         new_list_ticker.append(x)
            # list_ticker = [self.dict_ticker[x] for x in list_ticker if x in self.dict_ticker.keys()]

            list_ticker = list(self.dict_ticker.keys())
        cursor_stg = conn_stg.cursor()
        cursor_stg.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor_stg.fetchall()
        if not table_list:
            print('* DB 테이블이 비어있음 - 확인 필요 *')
        else:
            # self.table_list = np.concatenate(self.table_list).tolist()
            df_stg_buy = pd.read_sql(f"SELECT * FROM '{market_name}_buy'", conn_stg).set_index('index')
            list_stg_buy = df_stg_buy.index.tolist()

            df_stg_sell = pd.read_sql(f"SELECT * FROM '{market_name}_sell'", conn_stg).set_index('index')
            list_stg_sell = df_stg_sell.index.tolist()
        cursor_stg.close()
        conn_stg.close()

        list_ticker.insert(0, '전체')
        self.QCB_ticker.clear()
        self.QCB_ticker.addItems(list_ticker)
        self.QCB_ticker.setCurrentText(list_ticker[0])
        self.QCB_stg_buy.clear()
        self.QCB_stg_buy.addItems(list_stg_buy)
        self.QCB_stg_sell.clear()
        self.QCB_stg_sell.addItems(list_stg_sell)
        self.QTE_stg_buy.clear()
        self.QTE_stg_sell.clear()
        if not self.QCB_stg_buy.currentText() == '':
            self.QTE_stg_buy.setText(df_stg_buy.loc[self.QCB_stg_buy.currentText(), '전략코드'])
        if not self.QCB_stg_sell.currentText() == '':
            self.QTE_stg_sell.setText(df_stg_sell.loc[self.QCB_stg_sell.currentText(), '전략코드'])

        return list_ticker
    def get_db_bybit(self,ticker, bong, start_time):
        total_data = []
        i = 0
        num_error = 0
        while True:
            i += 1
            try:
                # OHLCV 데이터를 조회합니다.
                ohlcv = self.exchange.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=self.dict_bong[bong],
                                                  since=start_time, limit=1000)
                time.sleep(0.5)
                # 다음 조회를 위해 마지막으로 조회된 데이터의 시간을 업데이트합니다.
                if ohlcv:
                    start_time = ohlcv[-1][0] + 1  # 다음 조회는 이전 데이터의 다음 시간부터 시작
                    print(
                        f"{common_def.cyan(ticker) + 'USDT'} DB 저장 중...start time - {datetime.fromtimestamp(math.trunc(start_time / 1000))}[{i}]")
                    # 조회된 데이터를 출력하거나 다른 작업을 수행할 수 있습니다.
                    total_data = total_data + ohlcv
                else:
                    break

                # 1분 간격으로 조회를 반복합니다. 필요에 따라 이 값을 조절하세요.
            except ccxt.NetworkError as e:
                print(f"{common_def.red('NetworkError:')} {common_def.green(e)}")
                # 필요에 따라 재시도 로직을 추가할 수 있습니다.
                num_error += 1
                if num_error == 10:
                    break

            except ccxt.ExchangeError as e:
                print(f"{common_def.red('ExchangeError:')} {common_def.green(e)}")
                # 필요에 따라 예외 처리를 추가할 수 있습니다.
                num_error += 1
                if num_error == 10:
                    break

            except Exception as e:
                print(f"{common_def.red('Error:')} {common_def.green(e)}")
                # 기타 예외 처리를 추가할 수 있습니다.
                num_error += 1
                if num_error == 10:
                    break
        df_new = pd.DataFrame(total_data, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
        df_new['날짜'] = pd.to_datetime(df_new['날짜'], utc=True, unit='ms')
        df_new['날짜'] = df_new['날짜'].dt.tz_convert("Asia/Seoul")
        df_new['날짜'] = df_new['날짜'].dt.tz_localize(None)
        df_new.set_index('날짜', inplace=True)
        return df_new
    def compare_price(self, price, vars):
        i_min = price.min()  # 현재가.min
        i_max = price.max()
        return price.apply(self.mapping, args=(i_min, i_max, vars.min(), vars.max()))

    def mapping(self, x, i_min, i_max, o_min, o_max):
        return (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # mapping()함수 정의.

    def replace_tabs_with_spaces(self, text):  # 스페이스랑 탭 혼용 시 에러 방지용
        space_count = 4
        return text.replace('\t', ' ' * space_count)

    def replace_QTE_line(self, text_edit, new_text, line_num):
        # 전체 텍스트 가져오기
        all_text = text_edit.toPlainText()

        # 줄 단위로 분리
        lines = all_text.splitlines()

        # 첫째 줄 변경
        if lines:
            lines[line_num] = new_text
        else:
            lines.append(new_text)  # 비어 있으면 첫째 줄 추가

        # 수정된 텍스트를 다시 설정
        text_edit.setPlainText('\n'.join(lines))
    # def make_start_stop(self, df_detail, detail_stamp):
    #     # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
    #     df_detail['장시작시간'] = np.nan
    #     serise_start_t = df_detail.groupby(df_detail.index.date).transform(
    #         lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
    #     df_detail['장시작시간'] = serise_start_t
    #     df_detail['장종료시간'] = np.nan
    #     serise_end_t = df_detail.groupby(df_detail.index.date).transform(
    #         lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
    #     df_detail['장종료시간'] = serise_end_t
    #     # 시작 시간과 종료 시간 확인
    #     start_time = df_detail.index.min()
    #     end_time = df_detail.index.max()
    #     # 전체 1분 단위의 시간 인덱스 생성
    #     full_time_index = pd.date_range(start=start_time, end=end_time, freq=f'{detail_stamp}min')
    #     # 기존 데이터프레임을 새로운 인덱스에 맞춰 재인덱싱
    #     df_detail = df_detail.reindex(full_time_index)
    #     # 누락된 데이터를 바로 위의 데이터로 채우기
    #     # df_detail = df_detail.fillna(method='ffill')
    #     df_detail.ffill(inplace=True)
    #     # '장시작시간', '장종료시간'열을 딕셔너리로 만들기
    #     df_time = df_detail[['장시작시간', '장종료시간']]
    #     df_time = df_time.drop_duplicates()
    #     result_dict = df_time.set_index('장시작시간')['장종료시간'].to_dict()
    #     # 빈 리스트를 생성하여 각 시간 범위에 해당하는 데이터프레임을 저장
    #     dfs = []
    #     # 시간 범위 딕셔너리를 순회하며 데이터프레임 슬라이싱
    #     for start_time, end_time in result_dict.items():
    #         start_time = pd.to_datetime(start_time)
    #         end_time = pd.to_datetime(end_time)
    #         sliced_df = df_detail[start_time:end_time]
    #         dfs.append(sliced_df)
    #     df_detail = pd.concat(dfs)
    #     return df_detail
    #
    # def make_df(self,dict_info):
    #     dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
    #                        '주봉': 10080}
    #     market = dict_info['market']
    #     ticker = dict_info['ticker']
    #     bong = dict_info['bong']
    #     bong_detail = dict_info['bong_detail']
    #     # start_day = dict_info['start_day']
    #     # end_day = dict_info['end_day']
    #     conn_DB = dict_info['connect']
    #     # table_list_DB = dict_info['table_list_DB']
    #     # trade_market = dict_info['trade_market']
    #     dict_bong = dict_info['dict_bong']
    #     # dict_bong_reverse = dict_info['dict_bong_reverse']
    #     ticker_detail = ticker+'_'+dict_bong[bong_detail]
    #     df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", conn_DB).set_index('날짜')
    #     df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
    #     if market == '코인':
    #         df_detail.index = df_detail.index - pd.Timedelta(hours=9)
    #         df, df_detail = common_def.detail_to_spread(df_detail,bong,bong_detail)
    #         df_detail.index = df_detail.index + pd.Timedelta(hours=9)
    #         df.index = df.index + pd.Timedelta(hours=9)
    #         for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
    #             start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
    #             end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
    #             df_detail.loc[start_time:end_time, '장시작시간'] = start_time
    #             df_detail.loc[start_time:end_time, '장종료시간'] = end_time
    #     else:
    #         df_detail.index = df_detail.index - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
    #         # df_detail = df_detail[df_detail.index >= datetime.strptime("20200326","%Y%m%d")]
    #         df, df_detail = common_def.detail_to_spread(df_detail,bong,bong_detail)
    #         df_detail = self.make_start_stop(df_detail, dict_bong_stamp[bong_detail])
    #
    #     df_detail['현재시간'] = df_detail.index
    #     if bong == '일봉':
    #         df_detail['종료시간'] = df_detail['장종료시간'].copy()
    #     elif bong != '일봉' and bong != '주봉' and bong != '월봉':
    #         # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
    #         df_detail_end_time = df_detail['현재시간'].resample(f'{dict_bong_stamp[bong]}min').last()
    #         df_detail_end_time = pd.Series(df_detail_end_time, name='종료시간')  # 추출한 시리즈의 이름을 종료시간으로 변경
    #         df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
    #         df_detail.ffill(inplace=True)
    #
    #     save = True
    #     df['매수가'] = np.nan
    #     df['매도가'] = np.nan
    #     df['수량'] = np.nan
    #     df['수익률'] = np.nan
    #     df['최고수익률'] = np.nan
    #     df['최저수익률'] = np.nan
    #     df['수익금'] = np.nan
    #     df['전략수익률'] = np.nan
    #     df['매수금액'] = np.nan
    #     df['매도금액'] = np.nan
    #     df['잔고'] = np.nan
    #     df['수수료'] = np.nan
    #     df['자산'] = np.nan
    #     return df,df_detail,save

    def do_backtest(self):
        self.QPB_stop.setEnabled(True)
        self.stg_buy = self.QTE_stg_buy.toPlainText()
        self.stg_buy = self.replace_tabs_with_spaces(self.stg_buy)
        self.stg_sell = self.QTE_stg_sell.toPlainText()
        self.stg_sell = self.replace_tabs_with_spaces(self.stg_sell)
        global 등락률상위, 거래량상위, 거래대금상위, 시가총액상위, 시간외잔량상위, 체결강도상위, 관심종목등록상위
        global long, short
        long = 'long'
        short = 'short'
        등락률상위 = '등락률상위'
        거래량상위 = '거래량상위'
        거래대금상위 = '거래대금상위'
        시가총액상위 = '시가총액상위'
        시간외잔량상위 = '시간외잔량상위'
        체결강도상위 = '체결강도상위'
        관심종목등록상위 = '관심종목등록상위'

        locals_dict_buy = {}
        object = self.stg_buy.split("\n", 1)[0]  # 첫줄 읽기 추출
        exec(object, None, locals_dict_buy)
        object = locals_dict_buy.get('진입대상')
        bong = self.stg_buy.split("\n", 2)[1]  # 둘줄 읽기 추출
        exec(bong, None, locals_dict_buy)
        bong = locals_dict_buy.get('봉')
        bet = self.stg_buy.split("\n", 4)[3]
        exec(bet, None, locals_dict_buy)
        bet = locals_dict_buy.get('초기자금')

        locals_dict_sell = {}
        division_sell = self.stg_sell.split("\n", 1)[0]  # 첫줄 읽기 추출
        exec(division_sell, None, locals_dict_sell)
        division_sell = locals_dict_sell.get('분할매도')

        # ticker = self.QCB_ticker.currentText()
        market = self.QCB_market.currentText()
        bong_detail = self.QCB_bong_detail.currentText()
        bong = list(bong.keys())[0]
        if type(object) == dict:
            ticker = list(object.keys())[0]
        else:
            # if object in self.table_list_DB:
            ticker = object
            # raise Exception (f'ticker 확인 필요 {object= }   {self.table_list_DB= } ')

        if market == '국내주식':
            증거금률 = 1
            direction = 'long'
            거래승수 = 1
            if ticker in self.stocks_info['종목명'].tolist():
                dict_ticker_reverse = dict(zip(self.dict_ticker.values(), self.dict_ticker.keys()))
                ticker = dict_ticker_reverse[ticker]
                self.trade_market = self.stocks_info.loc[ticker, '시장구분']
            else:
                raise
        elif market == '국내선옵':
            self.dic_multiplier = {'101': 250000, '201': 250000, '301': 250000, '209': 250000, '309': 250000,
                                   '2AF': 250000, '3AF': 250000,  # 코스피200
                                   '105': 50000, '205': 50000, '305': 50000,  # 미니코스피200
                                   '106': 10000, '206': 10000, '306': 10000,  # 코스닥150
                                   }
            division_buy = self.stg_buy.split("\n", 5)[4]
            exec(division_buy, None, locals_dict_buy)
            division_buy = locals_dict_buy.get('분할매수')

            증거금률 = 1
            direction = 'long'
            거래승수 = self.dic_multiplier[ticker[:3]]
            if ticker in self.dict_ticker.values():
                dict_ticker_reverse = dict(zip(self.dict_ticker.values(), self.dict_ticker.keys()))
                ticker = dict_ticker_reverse[ticker]
                self.trade_market = '선물' if ticker[:1] == '1' else '옵션'
            else:
                ticker = ticker
                self.trade_market = '선물' if ticker[:1] == '1' else '옵션'

        elif market == '코인':
            direction = self.stg_buy.split("\n", 3)[2]
            exec(direction, None, locals_dict_buy)
            direction = locals_dict_buy.get('방향')
            증거금률 = self.stg_buy.split("\n", 5)[4]
            exec(증거금률, None, locals_dict_buy)
            증거금률 = locals_dict_buy.get('레버리지')
            division_buy = self.stg_buy.split("\n", 6)[5]
            exec(division_buy, None, locals_dict_buy)
            division_buy = locals_dict_buy.get('분할매수')
            self.trade_market = 'bybit'
            거래승수 = 1


        self.dict_info = {'market': market, 'ticker': ticker, 'bong': bong, 'bong_detail': bong_detail,
                          'start_day': self.QLE_start.text(),
                          'end_day': self.QLE_end.text(), 'connect': self.conn_DB, 'table_list_DB': self.table_list_DB,
                          'trade_market': self.trade_market, 'dict_bong': self.dict_bong, 'exchange': self.exchange,
                          'stg_buy': self.stg_buy, 'stg_sell': self.stg_sell, 'bet': bet,
                          'dict_bong_reverse': self.dict_bong_reverse, 'division_buy': division_buy,
                          'division_sell': division_sell,
                          'direction': direction, '거래승수': 거래승수, '증거금률': 증거금률}


        if self.db_name != f"{ticker}_{bong}_{bong_detail}_{self.QLE_start.text()}_{self.QLE_end.text()}":
            self.db_name = f"{ticker}_{bong}_{bong_detail}_{self.QLE_start.text()}_{self.QLE_end.text()}"
            print(f"DB 생성 - {self.db_name} ")

            # self.worker = get_df.WorkerThread(self.dict_info)
            # self.worker = get_df.WorkerThread_min_to_bong(self.dict_info)
            # self.worker.result_ready.connect(self.run_backtest)
            # self.worker.start()
            # df, df_detail,save = self.worker.run()

            # df, df_detail,save = self.make_df(self.dict_info)

            self.thread_make = make_data(self, self.dict_info)
            self.thread_make.start()
            self.thread_make.val.connect(self.run_backtest)

            # print(df_detail)
            # print(df)
            # print(df_detail.dtypes)
            # print(df.dtypes)
            # quit()
            # common_def.export_sql(df,'df')
            # common_def.export_sql(df_detail,'df_detail')
            # self.run_backtest(df,df_detail,save,self.dict_info)
        else:
            df = self.df.copy()
            df_detail = self.df_detail.copy()
            # save =False
            self.run_backtest(df, df_detail)

    def run_backtest(self, df, df_detail):
        # print(self.stg_buy)
        # print(self.stg_sell)
        # 백테시간 줄이기용
        # print('===============')
        # print(df_detail)
        # for factor in df_detail.columns.tolist():
        #     if not factor in str(self.stg_buy + self.stg_sell):  # 실제 전략에 필요한 팩터만 남기고 데이터프레임에서 삭제
        #         if not factor in ['상세시가', '상세고가', '상세저가', '상세종가', '시가', '고가', '저가', '종가', '종료시간',
        #                           '현재시간', '장시작시간', '장종료시간']:  # 삭제에서 제외
        #             df_detail.drop(factor, axis=1, inplace=True)
        # print(df_detail)
        # print(f'********{datetime.now()}*******')

        self.length_index = len(df_detail.index)
        if sys.maxsize > self.length_index:  # df_detail.index의 값이 int형의 최대값보다 작을 경우만 백테스트 진행
            print('백테스트 시작')
            self.df = df.copy()
            self.df_detail = df_detail.copy()
            # if save == True:
            #     self.df = df.copy()
            #     self.df_detail = df_detail.copy()

            # self.thread = ATOM_bt_thread_numpy.backtest_np(self,df, df_detail,self.dict_info)
            self.thread = ATOM_backtest_numpy.backtest_np(self, df, df_detail, self.dict_info)

            self.thread.start()
            self.thread.val_bar.connect(self.progress_loading)
            self.thread.val_df.connect(self.view_chart)

            self.QPB_start.setEnabled(False)
        else:
            print(f"데이터 최대값 초과 : 백테스트 기간을 더 단축하세요   {sys.maxsize=}    {self.length_index=}")

    def view_chart(self, df):
        if (df['잔고'] == df.loc[df.index[0], '잔고']).all():
            print('잔고 변함 없음 매수 0 회')
            QMessageBox.about(self, '알람', '잔고 변함 없음 매수 0 회')

        else:
            # 데이터타입이 object 이거나 전부 nan으로 되어있는열이 있으면 에러발생하기 때문에 그런열은 삭제 해줘야 됨
            # dtype이 object인 열 이름 추출
            object_columns = df.select_dtypes(include='object').columns.tolist()
            if object_columns:
                for del_col in object_columns:
                    df.drop(del_col, axis=1, inplace=True)
            start_day = datetime.strftime(df.index[0], '%Y-%m-%d')
            self.QLE_start.setText(start_day)
            list_columns = df.columns.tolist()
            if self.QCB_chart.isChecked() == True:
                df_chart_table = self.chart_table.input(df, self.QCB_market.currentText())
                self.chart_table.chart_show(self.QCB_market.currentText(), self.QCB_ticker.currentText())
            self.result_chart(df)
            # df.to_sql('backtest', sqlite3.connect('DB/bt.db'), if_exists='replace')

    def result_chart(self, df):

        # df.index = df.index.astype(str).str[:10]

        # df['holding'] = np.log1p(df['holding'])
        df['ror'] = (df['종가'] - df['시가'][0]) / df['시가'][0]
        df['holding'] = int(self.QLE_bet.text()) + (df['ror'] * int(self.QLE_bet.text()))
        df['holding'] = df['holding'] / df['holding'][0]
        amount = df['수익금'].sum()
        df['DD'] = df['strategy'] / df['strategy'].cummax() - 1
        df['MDD'] = df['DD'].cummin()

        df['전략수익률'] = round(df['strategy'] / df['strategy'][0], 2)
        diff = df.index[-1] - df.index[0]
        N = diff.days / 365
        기간수익률 = df['전략수익률'][-1]
        연복리수익률 = ((기간수익률 ** (1 / N)) - 1) * 100
        # df['index'] = self.compare_price(df['종가'], df['전략수익률'])
        df['index'] = round(self.compare_price(df['종가'], df['전략수익률']), 2)
        # df_benefit = df[['MDD','DD']]
        # df_benefit.to_sql('수익금',sqlite3.connect('DB/bt.db'), if_exists='replace')
        games = df['수익금'].count()
        win = len(df.loc[df['수익금'] > 0])  # 횟수
        lose = len(df.loc[df['수익금'] < 0])
        win_sum = df.loc[df['수익금'] > 0].수익금.sum()  # 금액
        loss_sum = df.loc[df['수익금'] < 0].수익금.sum()
        avg_profit = win_sum / win
        avg_loss = loss_sum / lose
        pov = win / games * 100

        grid = GridSpec(4, 1, wspace=0.3, hspace=0.5)
        fig = plt.figure(figsize=(16, 9))

        ax1 = fig.add_subplot(grid[0:3, 0:1])
        ax2 = fig.add_subplot(grid[3:4, 0:1], sharex=ax1)

        ax1.plot(df.index, df['전략수익률'], label='전략수익률')
        # ax1.plot(df['strategy'],label='strategy')
        ax1.plot(df['index'], label=self.QCB_ticker.currentText())
        ax1.plot(df['holding'], label='holding')
        ax1.legend(loc='upper left', ncol=3, shadow=True)
        ax1.set_ylabel(f'{self.QCB_ticker.currentText()}')

        ax2.plot(df.DD, c='y', lw=1, label='DD')
        ax2.hlines(df.DD.mean(), df.index.min(), df.index.max(), color='g', ls='--')
        ax2.plot(df.MDD, c='r', lw=1, label='MDD')
        ax2.legend(loc=1, ncol=3, shadow=True)
        ax2.set_ylabel('Drawdown')

        self.배팅금액 = format(int(self.QLE_bet.text()), ',')
        self.수익금 = format(round(amount), ',')
        self.수익률 = round(amount / int(self.QLE_bet.text()) * 100)
        self.연복리수익률 = round(연복리수익률, 1)
        self.거래횟수 = games
        idx_day = df.index.astype(str).str[:10]
        거래일 = len(df.groupby(idx_day).size().index)
        self.일평균거래횟수 = round(games / 거래일, 1)
        self.승률 = round(pov, 1)
        self.손익비 = round(avg_profit / abs(avg_loss), 1)
        self.MDD = df['MDD'][-1].round(1)

        try:
            plt.title(
                f"종목명: {self.QCB_ticker.currentText()},  배팅금액{self.배팅금액},  매매기간: {self.QLE_start.text() + '~' + self.QLE_end.text()},  "
                f"봉: {self.QCB_bong.currentText()},  총 수익금: {self.수익금},  수익률: {self.수익률} %, 연복리수익률(CAGR): {self.연복리수익률},\n"
                f"거래횟수: {self.거래횟수},  일평균 거래횟수: {self.일평균거래횟수},  거래일: {거래일}  승률: {self.승률}%,  손익비: {self.손익비}%, "
                f"MDD: {self.MDD},  TradingEdge: {round(pov * avg_profit - (1 - pov) * avg_loss)},  P&L ration: {round((1 - pov) / pov, 1)} ")
        except:
            df_nan = df.loc[np.isnan(df['strategy'])]
            plt.title(f"배팅금액{format(int(self.QLE_bet.text()), ',')}  총 수익금: 청산  거래횟수: {games}  승률: {round(pov, 1)}%,  "
                      # f"청산일: {df_nan.index[0]}"
                      f"")
        plt.legend()
        plt.show()
        self.plt = plt

    def progress_loading(self, val):
        self.QPB_bar.setValue(val)
        # if val == 100: self.on_stop()

    def on_stop(self):
        self.thread.stop()
        self.QPB_start.setEnabled(True)
        self.QPB_stop.setEnabled(False)
        self.QPB_bar.setValue(0)

    def save_bt(self):
        self.BTN_efect(self.QPB_save_bt)
        path = 'DB/images/' + str(datetime.now().strftime('%Y-%m-%d_%H%M')) + '.png'
        plt.savefig(path, dpi=200, facecolor='#eeeeee', edgecolor='blue', bbox_inches='tight')
        data = {'ticker': self.QCB_ticker.currentText(), '배팅금액': self.배팅금액, '수익금': self.수익금, '수익률': self.수익률,
                '연복리수익률': self.연복리수익률, '거래횟수': self.거래횟수, '일평균거래횟수': self.일평균거래횟수, '승률': self.승률,
                '손익비': self.손익비, 'MDD': self.MDD, '매매기간': self.QLE_start.text() + '~' + self.QLE_end.text(),
                '봉': self.QCB_bong.currentText(), '매수전략': self.QTE_stg_buy.toPlainText(),
                '매도전략': self.QTE_stg_sell.toPlainText()}
        df = pd.DataFrame(data=data, index=[str(datetime.now().strftime('%Y-%m-%d_%H%M'))])
        # columns=['ticker', '배팅금액', '수익금', '수익률', '연복리수익률', '거래횟수',
        #          '일평균거래횟수', '승률', '손익비', 'MDD', '매매기간', '봉','매수전략', '매도전략'])
        # df = pd.DataFrame(data, index=[datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        #                   columns=['ticker', '배팅금액', '수익금', '수익률', '연복리수익률', '거래횟수',
        #                            '일평균거래횟수', '승률', '손익비', 'MDD', '매매기간', '봉','매수전략', '매도전략'])
        db_file = 'DB/images/bt_history.db'
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()
        print(table_list)
        table_list = np.concatenate(table_list).tolist()
        print(table_list)
        if 'history' in table_list:
            df_old = pd.read_sql(f"SELECT * FROM 'history'", conn).set_index('index')
            df = pd.concat([df_old, df], ignore_index=False)
        # else:
        #     df =  pd.DataFrame(data, columns=['ticker','배팅금액', '수익금', '수익률', '연복리수익률', '거래횟수',
        #                                       '일평균거래횟수','승률','손익비','MDD','기간','매수전략','매도전략'])
        df.to_sql('history', conn, if_exists='replace')
        cursor.close()
        conn.close()
        print('백테스트 데이터 저장 완료')
    def show_calendar_popup_start(self, event):
        """QLineEdit 클릭 시 달력 팝업 표시"""
        popup = CalendarPopup(self)
        popup.move(self.QLE_start.mapToGlobal(self.QLE_start.rect().bottomLeft()))  # 팝업 위치 설정

        if popup.exec_():  # 팝업 실행
            self.QLE_start.setText(popup.selected_date)  # 선택된 날짜를 QLineEdit에 설정
    def show_calendar_popup_end(self, event):
        """QLineEdit 클릭 시 달력 팝업 표시"""
        popup = CalendarPopup(self)
        popup.move(self.QLE_end.mapToGlobal(self.QLE_end.rect().bottomLeft()))  # 팝업 위치 설정

        if popup.exec_():  # 팝업 실행
            self.QLE_end.setText(popup.selected_date)  # 선택된 날짜를 QLineEdit에 설정
    def make_candle(self, df):
        matplotlib.rcParams['font.family'] = 'NanumGothic'
        matplotlib.rcParams['axes.unicode_minus'] = False
        matplotlib.rcParams['font.size'] = 12

        x = list(map(lambda x: x.strftime('%m.%d'), df.index))
        opn = df['시가']
        high = df['고가']
        low = df['저가']
        close = df['종가']
        volume = df['거래량']
        df['Change'] = (df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1)
        change = df['Change']

        from matplotlib import gridspec

        plt.figure(figsize=(12, 5))  # (12, 5) 크기의 판을 만든다.
        gs = gridspec.GridSpec(nrows=2, ncols=1,  # 커다란 판을 위 아래 2개로 구획한다.
                               height_ratios=[5, 1])  # 각 구획의 높이 비율을 5:1로 한다.

        ##############################################
        plt.subplot(gs[0])  # 1번 구획을 불러들인다.
        # 캔들스틱 그리는 코드 넣을 자리

        plt.subplot(gs[1])  # 2번 구획을 불러들인다.
        # 거래량 막대 그래프 그리는 코드 넣을 자리

        ##############################################

        plt.subplots_adjust(wspace=0, hspace=0)  # 구획(subplot) 간의 간격을 없앤다.
        plt.show()

        cmap = list(map(lambda x: 'orange' if x > 0 else 'c', change))

        from matplotlib import gridspec

        plt.figure(figsize=(12, 5))  # (12, 5) 크기의 판을 만든다.
        gs = gridspec.GridSpec(nrows=2, ncols=1,  # 커다란 판을 위 아래 2개로 구획한다.
                               height_ratios=[5, 1])  # 각 구획의 높이 비율을 5:1로 한다.

        ##############################################
        plt.subplot(gs[0])  # 1번 구획을 불러들린다.
        plt.title("삼성전자 (2020.01.02 ~)", fontsize=15)
        plt.bar(x, height=close - opn, bottom=opn, width=1, color=cmap)
        plt.vlines(x, low, high, colors=cmap)
        plt.xticks([])

        plt.subplot(gs[1])  # 2번 구획을 불러들린다.
        plt.bar(x, volume, width=0.8, color=cmap)
        plt.xticks(range(0, len(x)), x, rotation=40)

        ##############################################

        plt.subplots_adjust(wspace=0, hspace=0)  # 구획(subplot) 간의 간격을 없앤다.
        plt.show()

    def make_exchange_bybit(self):
        conn = sqlite3.connect('DB/setting.db')
        df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
        conn.close()
        api = df.loc['BYBIT_api', 'value']
        secret = df.loc['BYBIT_secret', 'value']
        exchange = ccxt.bybit(config={
            'apiKey': api,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                'position_mode': True,
            }, })
        return exchange

    def make_exchange_kis(self):
        key = 'test'
        secret = 'test'
        acc_no = "01-01"
        market = '주식'
        mock = True
        exchange = KIS.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, market=market, mock=mock)
        return exchange

    def BTN_efect(self, QPB):
        QPB.setEnabled(False)
        QTest.qWait(250)
        QPB.setEnabled(True)

    def init_file(self):
        import os
        stg_file = ['DB/DB_stock.db', 'DB/DB_bybit.db', 'DB/DB_futopt.db']
        for market in stg_file:
            if not os.path.isfile(market):  # stg_file.db 파일이 없으면
                sqlite3.connect(market)
        file = 'DB/strategy.db'
        if not os.path.isfile(file):
            sqlite3.connect(file)
            conn = sqlite3.connect(file)
            list_stg = ['coin_buy', 'coin_sell', 'krx_buy', 'krx_sell']
            for stg in list_stg:
                df = pd.DataFrame(columns=['전략코드'])
                df.to_sql(stg, conn, if_exists='replace')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window(tab_chart_table.Window())
    window.setGeometry(2000, 800, 700, 600)  # x,y,width,height
    window.show()
    sys.exit(app.exec_())