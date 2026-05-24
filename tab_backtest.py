import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject, Qt

import sqlite3
import pandas as pd
import numpy as np
import ATOM_stg_numpy
import requests
import json
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
import tab_chart_table
import time
import datetime
import ccxt
from PyQt5.QtTest import *
import ATOM_backtest_numpy
import ATOM_bt_thread_numpy
import KIS
from pprint import pprint
import CYBOS_DB
import common_def
import math
from dateutil.relativedelta import relativedelta

pd.set_option('display.max_columns', None)  # 모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1500)
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment', None)  # SettingWithCopyWarning 경고를 끈다


class make_data(QThread):
    # 작업이 끝났을 때 신호를 발생시킨다.
    # finished = pyqtSignal()
    signal_bt_df = pyqtSignal(pd.DataFrame, pd.DataFrame,str,str)

    signal_light = pyqtSignal(bool)
    signal_bar = pyqtSignal(int)

    def __init__(self, parent, dict_info):
        super().__init__(parent)

        self.dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '1시간봉': 60, '4시간봉': 240,
                                '일봉': 1440, '주봉': 10080}
        # self.dict_bong = dict_info['dict_bong']
        self.dict_info = dict_info
        self.market = dict_info['market']
        self.ticker = dict_info['ticker']
        self.val_range = dict_info['val_range']
        self.bong = dict_info['봉']
        self.bong_detail = dict_info['상세봉']
        # self.conn_DB = dict_info['connect']
        self.start_day = dict_info['시작일']
        self.end_day = dict_info['종료일']

    def run(self):
        conn_DB = sqlite3.connect(self.dict_info['db_file'], check_same_thread=False)
        if self.val_range == None: #검색종목이 아닐 경우
            df_detail = pd.read_sql(f"SELECT * FROM '{self.ticker}_{self.bong_detail}'", conn_DB).set_index('날짜')
            conn_DB.close()
            df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환

            df_detail = df_detail.loc[(df_detail.index >= self.start_day) & (df_detail.index <= self.end_day)]

            if self.market == 'bybit':
                df_detail.index = df_detail.index - pd.Timedelta(hours=9)
                df, df_detail = common_def.detail_to_spread(self.market,df_detail, self.bong, self.bong_detail, False)
                df_detail.index = df_detail.index + pd.Timedelta(hours=9)
                df.index = df.index + pd.Timedelta(hours=9) # 판다스 버전차이로 아래로 변경
                # df.index = df.index.shift(9, freq='H')
                for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
                    start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
                    end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=self.dict_bong_stamp[self.bong_detail])
                    df_detail.loc[start_time:end_time, '장시작시간'] = start_time
                    df_detail.loc[start_time:end_time, '장종료시간'] = end_time
            else:
                df_detail.index = df_detail.index - pd.Timedelta(minutes=self.dict_bong_stamp[self.bong_detail])
                # df_detail = df_detail[df_detail.index >= datetime.datetime.strptime("20200326","%Y%m%d")]
                df, df_detail = common_def.detail_to_spread(self.market,df_detail, self.bong, self.bong_detail, False)
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
        else:
            upper = float(self.val_range[self.val_range.index('~') + 1:])
            lower = float(self.val_range[:self.val_range.index('~')])
            print(f"조건 검색 백테스트 {self.val_range}   {upper=}   {lower=}")

            cursor = conn_DB.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            list_table = np.concatenate(cursor.fetchall()).tolist()
            list_ticker = []

            if self.market == 'bybit':
                pass
            elif self.market == '국내선옵':
                for ticker in list_table:
                    if ticker[:len(self.ticker)] == self.ticker:
                        if ticker[len(self.ticker)+1:].isdigit():
                            list_ticker.append(ticker)
            for ticker in list_ticker:
                print(ticker)
                df_detail = pd.read_sql(f"SELECT * FROM '{ticker}'", conn_DB).set_index('날짜')
                df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환

                df_detail = df_detail.loc[(df_detail.index >= self.start_day) & (df_detail.index <= self.end_day+datetime.timedelta(days=1))] # end_day의 0시로 인식해서 해당일은 포함 안하기 때문에 +1일을 해줌
                if not df_detail.empty:
                    if self.market == 'bybit':
                        df_detail.index = df_detail.index - pd.Timedelta(hours=9)
                    else:
                        df_detail.index = df_detail.index - pd.Timedelta(minutes=self.dict_bong_stamp[self.bong_detail])
                        df, df_detail = common_def.detail_to_spread(df_detail, self.bong, self.bong_detail, False)
                        df_detail = self.make_start_stop(df_detail, self.dict_bong_stamp[self.bong_detail])
                    df_detail['현재시간'] = df_detail.index
            cursor.close()
            conn_DB.close()
        df_detail['데이터길이'] = df_detail['데이터길이'].fillna(1)  # nan을 1로 채우기 4시간봉으로 할 경우 df_detail이 nan,2,3,4 로 시작
        df_detail['시분초'] = df_detail.index.hour * 10000 + df_detail.index.minute * 100 + df_detail.index.second
        df['매수가'] = np.nan
        df['매도가'] = np.nan
        df['보유수량'] = np.nan
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
        self.signal_bt_df.emit(df, df_detail,self.ticker,self.bong)  # 첫 번째 작업이 끝났음을 신호로 알림


    def make_start_stop(self, df_detail, detail_stamp):
        # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
        # 시작 시간과 종료 시간 확인
        # df_detail['장시작시간'] = np.nan
        # serise_start_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[0]).장시작시간  # 날짜별 시작 시간을 같은행에 넣기
        # df_detail['장시작시간'] = serise_start_t
        # print(df_detail)
        # df_detail['장종료시간'] = np.nan
        # print(df_detail)
        # serise_end_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
        # print(df_detail)
        # df_detail['장종료시간'] = serise_end_t

###########################################################################
        # 백터화 된 방법으로 변경
        # 날짜 추출
        dates = pd.Series(df_detail.index.date, index=df_detail.index)

        # 첫/마지막 인덱스
        first_idx = dates.drop_duplicates(keep='first').index
        last_idx = dates.drop_duplicates(keep='last').index

        # 딕셔너리 생성
        date_to_times = {
            'first': dict(zip(df_detail.loc[first_idx].index.date,
                              df_detail.loc[first_idx].index)),
            'last': dict(zip(df_detail.loc[last_idx].index.date,
                             df_detail.loc[last_idx].index))
        }

        # 매핑
        date_array = pd.Series(df_detail.index.date)
        df_detail['장시작시간'] = date_array.map(date_to_times['first']).values
        df_detail['장종료시간'] = date_array.map(date_to_times['last']).values
###########################################################################
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


class TextPopupBuy(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("매수변수")
        self.setGeometry(200, 200, 400, 300)

        # 다이얼로그 전체 스타일
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: #B4B4B4;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-family: Arial;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #B4B4B4;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        txt = """등락율, 변화율, 이평5, 이평20, 이평60, 이평100, 이평120, 이평200, 이평240, 거래량이평3, 거래량이평20, 거래량이평60, MACD, MACD_SIGNAL, MACD_HIST, RSI14, RSI18, RSI30, ATR, TRANGE, 이격도20이평, 이격도60이평, 밴드상, 고저평균대비등락율, 데이터길이, 당일저가, 전일저가, 당일고가, 전일고가"""
        self.text_edit.setPlainText(txt)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class TextPopupSell(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("매도변수")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        txt = """
        """
        self.text_edit.setPlainText(txt)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


class Window(QWidget):
    def __init__(self, chart_table):
        super().__init__()
        self.chart_table = chart_table
        self.init_file()
        # self.dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '1시간봉': '60m',
        #                   '4시간봉': '4h', '일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
        # self.dict_bong_reverse = dict(zip(self.dict_bong.values(), self.dict_bong.keys()))
        self.set_UI()

        self.QCB_market.activated[str].connect(self.select_market)
        self.QCB_ticker.activated[str].connect(self.select_ticker)
        self.QCB_bong.activated[str].connect(self.select_bong)
        self.QPB_DB_load.clicked.connect(self.load_DB)
        self.QPB_DB_save.clicked.connect(self.save_DB)

        self.QCB_stg_buy.activated[str].connect(self.select_stg_buy)
        self.QPB_save_stg_buy.clicked.connect(self.save_stg_buy)
        self.QPB_stg_sell_save.clicked.connect(self.save_stg_sell)
        self.QCB_stg_sell.activated[str].connect(self.select_stg_sell)

        self.QPB_start.clicked.connect(self.do_backtest)
        self.QPB_stop.clicked.connect(self.on_stop)
        self.QPB_save_bt.clicked.connect(self.save_bt)
        self.QPB_stg_buy_del.clicked.connect(self.del_stg_buy)
        self.QPB_stg_sell_del.clicked.connect(self.del_stg_sell)
        # self.QLE_bet.textChanged.connect(self.select_bet)
        self.QPB_vars_buy.clicked.connect(self.pop_vars_buy)
        self.QPB_vars_sell.clicked.connect(self.pop_vars_sell)
        self.QLE_start.mousePressEvent = self.show_calendar_popup_start  # 클릭 시 팝업 호출
        self.QLE_end.mousePressEvent = self.show_calendar_popup_end  # 클릭 시 팝업 호출
        self.QPB_stop.setEnabled(False)

    def set_UI(self):
        self.QTE_stg_buy = QTextEdit()
        self.QTE_stg_sell = QTextEdit()
        self.setWindowTitle(f'BACKTEST')
        QVB_stg = QVBoxLayout()
        QVB_stg.addWidget(self.QTE_stg_buy)
        QVB_stg.addWidget(self.QTE_stg_sell)
        QGL = QGridLayout()
        self.QCB_market = QComboBox()
        self.QCB_market.addItems(['', 'bybit','국내주식', '국내선옵'])
        self.QCB_chart = QCheckBox('차트보기')
        self.QCB_chart.setChecked(True)
        self.QCB_ticker = QComboBox()
        self.QCB_bong = QComboBox()
        self.QCB_bong.addItems(['봉','5분봉','15분봉','30분봉','1시간봉','4시간봉','12시간봉','일봉','주봉'])
        self.QCB_bong_detail = QComboBox()
        self.QCB_bong_detail.addItems(['상세봉','1분봉','5분봉'])
        self.QPB_DB_load = QPushButton('DB 로딩')
        self.QPB_DB_save = QPushButton('DB 저장')
        self.QCB_stg_buy = QComboBox()
        self.QLE_stg_buy = QLineEdit()
        self.QLE_division_buy = QLineEdit()
        self.QPB_save_stg_buy = QPushButton('매수전략 저장')
        self.QPB_stg_buy_del = QPushButton('매수전략 삭제')
        self.QPB_stg_sell_del = QPushButton('매도전략 삭제')
        QL_start_day = QLabel('시작일')
        self.QLE_start = QLineEdit()
        # QL_bet = QLabel('배팅사이즈')
        # self.QLE_bet = QLineEdit('100')
        QL_end_day = QLabel('종료일')
        self.QLE_end = QLineEdit()
        self.QCB_stg_sell = QComboBox()
        self.QLE_stg_sell = QLineEdit()
        self.QLE_division_sell = QLineEdit()
        self.QPB_stg_sell_save = QPushButton('매도전략 저장')
        self.QPB_start = QPushButton('백테스트')
        self.QPB_stop = QPushButton('중지')
        self.QPB_save_bt = QPushButton('백테스트저장')
        self.QLE_start.setText('2010-01-01')
        self.QLE_end.setText(datetime.datetime.now().strftime('%Y-%m-%d'))
        self.QLE_start.setReadOnly(True)  # 직접 입력 방지
        self.QLE_end.setReadOnly(True)  # 직접 입력 방지
        self.QCB_history = QComboBox()
        self.QPB_vars_buy = QPushButton('매수 변수')
        self.QPB_vars_sell = QPushButton('매도 변수')
        self.QPB_bar = QProgressBar(self)
        self.QTE_state = QTextEdit()
        # self.QL_DB_name = QLabel("|")
        QT_history = QTableWidget()
        QT_history_detail = QTableWidget()


        self.QCB_market.setFixedWidth(100)
        self.QCB_ticker.setFixedWidth(100)
        self.QCB_bong.setFixedWidth(100)
        self.QCB_bong_detail.setFixedWidth(100)
        self.QCB_stg_buy.setFixedWidth(100)
        self.QLE_stg_buy.setFixedWidth(100)
        self.QPB_save_stg_buy.setFixedWidth(100)
        self.QPB_stg_buy_del.setFixedWidth(100)
        self.QLE_division_buy.setFixedWidth(100)
        QL_start_day.setFixedWidth(100)
        self.QLE_start.setFixedWidth(100)
        self.QPB_DB_load.setFixedWidth(100)
        self.QPB_DB_save.setFixedWidth(100)
        QL_end_day.setFixedWidth(100)
        self.QLE_end.setFixedWidth(100)
        self.QCB_stg_sell.setFixedWidth(100)
        self.QLE_stg_sell.setFixedWidth(100)
        self.QPB_stg_sell_save.setFixedWidth(100)
        self.QPB_stg_sell_del.setFixedWidth(100)
        self.QLE_division_sell.setFixedWidth(100)
        self.QPB_start.setFixedWidth(100)
        self.QPB_stop.setFixedWidth(100)
        # QL_bet.setFixedWidth(100)
        # self.QLE_bet.setFixedWidth(100)
        self.QTE_state.setFixedHeight(50)
        QGL.setSpacing(10)
        QL_start_day.setStyleSheet("""QLabel {qproperty-alignment: 'AlignRight | AlignVCenter';padding: 5px;width: 500px;height: 500px;}""") # 오른쪽 정렬
        QL_end_day.setStyleSheet("""QLabel {qproperty-alignment: 'AlignRight | AlignVCenter';padding: 5px;}""") # 오른쪽 정렬
        # QL_bet.setStyleSheet("""QLabel {qproperty-alignment: 'AlignRight | AlignVCenter';padding: 5px;}""") # 오른쪽 정렬

        QGL.addWidget(self.QCB_market, 0, 0)
        QGL.addWidget(self.QCB_ticker, 0, 1)
        QGL.addWidget(self.QCB_bong, 1, 0)
        QGL.addWidget(self.QCB_bong_detail, 1, 1)
        QGL.addWidget(self.QPB_DB_load, 2, 0)
        QGL.addWidget(self.QPB_DB_save, 2, 1)
        QGL.addWidget(self.QCB_stg_buy, 3, 0)
        QGL.addWidget(self.QLE_stg_buy, 3, 1)
        QGL.addWidget(self.QPB_save_stg_buy, 4, 0)
        QGL.addWidget(self.QPB_stg_buy_del, 4, 1)
        QGL.addWidget(QL_start_day, 5, 0)
        QGL.addWidget(self.QLE_start, 5, 1)
        QGL.addWidget(QL_end_day, 6, 0)
        QGL.addWidget(self.QLE_end, 6, 1)
        # QGL.addWidget(QL_bet, 7, 0)
        # QGL.addWidget(self.QLE_bet, 7, 1)
        QGL.addWidget(self.QPB_start, 7, 0)
        QGL.addWidget(self.QPB_stop, 7, 1)
        QGL.addWidget(self.QPB_save_bt, 8, 0)
        QGL.addWidget(self.QCB_chart, 8, 1)
        QGL.addWidget(self.QCB_stg_sell, 9, 0)
        QGL.addWidget(self.QLE_stg_sell, 9, 1)
        QGL.addWidget(self.QPB_stg_sell_save, 10, 0)
        QGL.addWidget(self.QPB_stg_sell_del, 10, 1)
        QGL.addWidget(self.QPB_vars_buy, 11, 0)
        QGL.addWidget(self.QPB_vars_sell, 11, 1)
        QGL.addWidget(self.QPB_bar, 12, 0, 1, 2)
        # QGL.addWidget(self.QL_DB_name, 14, 0)
        # QGL.addWidget(self.QTE_state, 14, 0, 1, 2)

        QVB_history = QVBoxLayout()
        QVB_history.addWidget(self.QCB_history)
        QVB_history.addWidget(QT_history)
        QVB_history.addWidget(QT_history_detail)

        QHB_main = QHBoxLayout()
        QHB_main.addLayout(QVB_stg)
        QHB_main.addLayout(QGL)
        QHB_main.addLayout(QVB_history)

        QVB_main = QVBoxLayout()
        QVB_main.addLayout(QHB_main)
        QVB_main.addWidget(self.QTE_state)

        self.setLayout(QVB_main)
        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 12pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 14pt 나눔고딕; "
        self.QTE_stg_buy.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE_stg_sell.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE_state.setStyleSheet(StyleSheet_Qtextedit)
        # StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                     "border-color: black; font: 12pt 나눔고딕; "
        QT_history.setStyleSheet(StyleSheet_Qtextedit)
        QT_history_detail.setStyleSheet(StyleSheet_Qtextedit)
        font = QFont('나눔고딕')
        self.QTE_stg_buy.setTabStopWidth(QFontMetrics(font).width(' ' * 4))
        self.QTE_stg_sell.setTabStopWidth(QFontMetrics(font).width(' ' * 4))
        self.highlighter_buy = common_def.PythonHighlighter(self.QTE_stg_buy.document())
        self.highlighter_sell = common_def.PythonHighlighter(self.QTE_stg_sell.document())
        self.QPB_start.setEnabled(False)
        # self.setFixedSize(1200,800)
        # self.QCB_bong_detail.setCurrentText('5분봉')
        # self.QCB_bong_detail.setEnabled(False)

    def save_DB(self):
        from pandas import to_numeric
        self.BTN_efect(self.QPB_DB_save)

        market = self.QCB_market.currentText()
        # ticker = self.QPB_DB_load.text()
        ticker = self.QCB_ticker.currentText()
        conn_DB = sqlite3.connect(self.dict_DB_info['db_file'])
        cursor = conn_DB.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        try:
            list_table = np.concatenate(cursor.fetchall()).tolist()
        except:
            list_table = []
        cursor.close()
        # 펀딩비 구하고자 할 경우 ticker = fungding
        if ticker == '':  # 티커가 명시되어 있지 않을 경우
            raise Exception('ticker 확인 필요')
        # pprint(self.dict_DB_info)
        if market == 'bybit' or market == 'binance' :
            bong = self.dict_DB_info['상세봉']
            self.dict_ex = {'bybit':self.dict_DB_info['bybit']}
            if not ticker == 'funding':
                if ticker in list_table:
                    df_old = pd.read_sql(f"SELECT * FROM '{ticker}'", conn_DB).set_index('날짜')
                    if df_old.empty:
                        if market == 'bybit':
                            since = self.dict_ex['bybit'].parse8601(f'2020-01-01T00:00:00Z')
                        elif market == 'binance':
                            since = self.dict_ex['spot'].parse8601(f'2020-01-01T00:00:00Z')
                        since = since // 1000  # 밀리초 -> 초로 변환 후 인자 전달
                        # df_new = self.get_db_bybit(ticker, bong, since)
                        ohlcv = []
                        total_data = common_def.get_coin_initial_data(market= market,dict_ex=self.dict_ex, ohlcv=ohlcv,
                                                                since=since, ticker=ticker, bong_detail=bong)
                        df_new = pd.DataFrame(total_data, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
                        df_new = common_def.stamp_to_df(df_new)
                        df_new.to_sql(ticker, conn_DB, if_exists='replace')
                    else:
                        df_old.index = pd.to_datetime(df_old.index)  # datime형태로 변환
                        last = df_old.index[-1] + pd.DateOffset(hours=-9)
                        # df_old.drop(index=df_old.index[-1], inplace=True)
                        last_day = str(last)[:10]
                        last_time = str(last)[11:]
                        if market == 'bybit':
                            since = self.dict_ex['bybit'].parse8601(f'{last_day}T{last_time}Z')
                        elif market == 'binance':
                            since = self.dict_ex['spot'].parse8601(f'{last_day}T{last_time}Z')
                        # df_new = self.get_db_bybit(ticker, bong, since)

                        # 위에랑 데이터 비교
                        ohlcv = []
                        since = since//1000
                        total_data = common_def.get_coin_initial_data(market= market,dict_ex=self.dict_ex, ohlcv=ohlcv,
                                                                since=since, ticker=ticker, bong_detail=bong)
                        df_new = pd.DataFrame(total_data, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
                        df_new = common_def.stamp_to_df(df_new)
                        if df_old.index[-1] == df_new.index[0]:
                            df_old.drop(index=df_old.index[-1],inplace=True)
                        df = pd.concat([df_old, df_new])
                        df.to_sql(ticker, conn_DB, if_exists='replace')
                else:
                    if market == 'bybit':
                        since = self.dict_DB_info['bybit'].parse8601(f'2020-01-01T00:00:00Z')
                    elif market == 'binance':
                        since = self.dict_DB_info['spot'].parse8601(f'2020-01-01T00:00:00Z')
                    since = since//1000 #초로 변환 후 인자 전달
                    ohlcv = []
                    total_data = common_def.get_coin_ohlcv(market= market,dict_ex=self.dict_ex, ohlcv=ohlcv,
                                                            since=since, ticker=ticker, bong_detail=bong)
                    df_new = pd.DataFrame(total_data, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
                    print(df_new)
                    df_new = common_def.stamp_to_df(df_new)
                    print(df_new)
                    df_new.to_sql(ticker, conn_DB, if_exists='replace')
                    conn_DB.close()
            else: # 펀딩비 데이터 저장
                print('funding rate 조회') #펀딩비 저장하고자 할 경우 ticker에 funding이라고 쓸 것
                list_inverse = common_def.fetch_inverse_list(market,self.dict_ex)
                df = common_def.get_funding_rates(market, self.dict_ex, list_inverse)
                df.index = pd.to_datetime(df.index, unit='ms', utc=True).tz_convert('Asia/Seoul')
                df.index = df.index.tz_localize(None)
                df = df.sort_index()
                df.to_sql(f'funding_rate', conn_DB, if_exists='replace')
            list_table.extend(['BTC','ETH','XRP'])
            list_table.insert(0, '전체')
            list_table = list(set(list_table))
            self.QCB_ticker.clear()
            self.QCB_ticker.addItems(list_table)
        elif market == '국내주식':
            dict_ticker_reverse = dict(zip(self.dict_ticker.values(), self.dict_ticker.keys()))
            try:
                ticker = dict_ticker_reverse[ticker]  # dict_ticker에 종목이 있을 경우
            except:  # dict_ticker에 종목이 없을경우
                print(f"종목명 확인 필요 {ticker= }")
                self.save_DB_CYBOS(market, ticker, list_table)
        elif market == '국내선옵':
            exchange = KIS.KoreaInvestment(market='국내선옵')
            conn = sqlite3.connect('DB/DB_futopt_kis.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            try:
                list_table = np.concatenate(cursor.fetchall()).tolist()
            except:
                list_table = []
            if not 'holiday' in list_table:
                df_holiday = pd.DataFrame()
            else:
                df_holiday = pd.read_sql(f"SELECT * FROM 'holiday'", conn).set_index('날짜')
            now_time = datetime.datetime.now().time()
            today = datetime.datetime.today()
            for target in ['선물', '미니선물', '본옵션', '위클리옵션', '야간선물', '야간미니선물', '야간본옵션', '야간위클리옵션']:
                # for target in ['위클리옵션','야간본옵션', '야간위클리옵션']:
                list_ticker, past_expiry_date, expiry_date = exchange.get_expiry_date(target=target, today=today)
                for symbol in list_ticker:
                    ticker_symbol = exchange.get_futopt_symbol(target=target, symbol=symbol, expiry_date=expiry_date)
                    if ticker_symbol in list_table:  # 연속저장 (기존데이터가 있을 경우)
                        df_exist = pd.read_sql(f"SELECT * FROM '{ticker_symbol}'", conn).set_index('날짜')
                    else:
                        df_exist = pd.DataFrame()

                    df = exchange.get_futopt_df(target=target, ticker_symbol=ticker_symbol, symbol=symbol,
                                               past_expiry_date=past_expiry_date, expiry_date=expiry_date,
                                               df_exist=df_exist, today=today, now_time=now_time,list_table=list_table)
                    if not df.empty:
                        df.to_sql(f"{ticker_symbol}", conn, if_exists='replace')
            conn.close()
        else:
            raise print('데이터를 저장 할 시장을 선택해주세요.')

        print(f'{common_def.red(ticker)}: DB저장 완료')

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

        # bong_detail = self.QCB_bong_detail.currentText()
        bong_detail = '1분봉'

        print(f"{ticker= }   {ticker_name= }   {list_table= }     ")

        if ticker in list_table:
            df_old = pd.read_sql(f"SELECT * FROM '{ticker + '_' }'",
                                 self.conn_DB).set_index('날짜')
            df_old.index = pd.to_datetime(df_old.index)  # datime형태로 변환
            start_day = df_old.index[-1].date()  # 인덱스의 마지막요소 추출
            start_day = datetime.datetime.strftime(start_day, '%Y%m%d')
            start_day = int(start_day)
        else:
            start_day = 20100101
            df_old = pd.DataFrame()
        end_day = datetime.datetime.now().strftime("%Y%m%d")

        print(f"{market= }, {ticker_name= }, 다운로드 대상= {bong_detail= }, {start_day= }, {end_day= }", end='...')

        db_down = CYBOS_DB.db_down()
        df = db_down.get_candle(instChart, market, ticker_name, bong_detail, start_day, end_day)
        if bong_detail == '일봉' or bong_detail == '주봉' or bong_detail == '월봉':
            df.drop(df.index[0], inplace=True)  # 가장 최근행은 아직 갱신중일 수 있으므로 삭제
        df = df[::-1]  # 거꾸로 뒤집기
        df = pd.concat([df_old, df])
        df = df.loc[~df.index.duplicated(keep='last')]  # 중복인덱스 제거

        df = round(df, 2) #모든 숫자 데이터를 소수점 둘째 자리까지 반올림
        df.to_sql(ticker, self.conn_DB, if_exists='replace')

    def save_stg_buy(self):
        market = self.QCB_market.currentText()
        txt = self.QTE_stg_buy.toPlainText()
        txt = common_def.replace_indicators(txt) #특정 지표 대문자로 변환
        txt = common_def.replace_tabs_with_spaces(txt)
        self.QTE_stg_buy.setText(txt)
        if self.QLE_stg_buy.text() == '':
            self.df_stg_buy.loc[self.QCB_stg_buy.currentText(), '전략코드'] = txt
        else:
            self.df_stg_buy.loc[self.QLE_stg_buy.text(), '전략코드'] = txt
        self.df_stg_buy.to_sql(f'{market}_buy', self.conn_stg, if_exists='replace')
        # cursor.close()
        self.QCB_stg_buy.clear()
        self.QCB_stg_buy.addItems(self.df_stg_buy.index.tolist())
        if self.QLE_stg_buy.text() != '':
            self.QCB_stg_buy.setCurrentText(self.QLE_stg_buy.text())
            self.pop_message('완료',f'매수전략 [{self.QLE_stg_buy.text()}] 이 저장되었습니다.')
        else:
            self.pop_message('에러','매수전략명을 지정해주세요.')

    def save_stg_sell(self):
        market = self.QCB_market.currentText()
        txt = self.QTE_stg_sell.toPlainText()
        txt = common_def.replace_indicators(txt) #특정 지표 대문자로 변환
        txt = common_def.replace_tabs_with_spaces(txt)
        self.QTE_stg_sell.setText(txt)
        if self.QLE_stg_sell.text() == '':
            self.df_stg_sell.loc[self.QCB_stg_sell.currentText(), '전략코드'] = txt
        else:
            self.df_stg_sell.loc[self.QLE_stg_sell.text(), '전략코드'] = txt
        self.df_stg_sell.to_sql(f'{market}_sell', self.conn_stg, if_exists='replace')
        # cursor.close()
        self.QCB_stg_sell.clear()
        self.QCB_stg_sell.addItems(self.df_stg_sell.index.tolist())
        if self.QLE_stg_sell.text() != '':
            self.QCB_stg_sell.setCurrentText(self.QLE_stg_sell.text())
            self.pop_message('완료',f'매도전략 [{self.QLE_stg_sell.text()}] 이 저장되었습니다.')
        else:
            self.pop_message('에러','매도전략명을 지정해주세요.')
    def del_stg_buy(self):
        if self.QCB_stg_buy.currentText() != '':
            self.df_stg_buy.drop([f'{self.QCB_stg_buy.currentText()}'], inplace=True)
            self.QCB_stg_buy.clear()
            self.QCB_stg_buy.addItems(self.df_stg_buy.index.tolist())
            self.QLE_stg_buy.clear()
            self.df_stg_buy.to_sql(f"{self.QCB_market.currentText()}_buy", self.conn_stg, if_exists='replace')
        self.select_stg_buy()

    def del_stg_sell(self):
        if self.QCB_stg_sell.currentText() != '':
            self.df_stg_sell.drop([f'{self.QCB_stg_sell.currentText()}'], inplace=True)
            self.QCB_stg_sell.clear()
            self.QCB_stg_sell.addItems(self.df_stg_sell.index.tolist())
            self.QLE_stg_sell.clear()
            self.df_stg_sell.to_sql(f"{self.QCB_market.currentText()}_sell", self.conn_stg, if_exists='replace')
        self.select_stg_sell()

    def select_stg_buy(self):
        self.QTE_stg_buy.clear()
        text_stg = self.df_stg_buy.loc[self.QCB_stg_buy.currentText(), '전략코드']
        self.QTE_stg_buy.setText(text_stg)
        self.QLE_stg_buy.setText(self.QCB_stg_buy.currentText())

    def select_stg_sell(self):
        self.QTE_stg_sell.clear()
        text_stg = self.df_stg_sell.loc[self.QCB_stg_sell.currentText(), '전략코드']
        self.QTE_stg_sell.setText(text_stg)
        self.QLE_stg_sell.setText(self.QCB_stg_sell.currentText())

    def select_ticker(self):
        ticker = self.QCB_ticker.currentText()
        # self.QPB_DB_load.setText(ticker)
        market = self.QCB_market.currentText()
        if market == '국내선옵':
            if ticker in ['콜옵션', '풋옵션']:
                ticker = f"{{'{ticker}':'1~2'}}"
        new_text = f"진입대상 = '{ticker}'"
        self.replace_QTE_line(self.QTE_stg_buy, new_text, 0) # 0번째줄의 텍스트 변경

        if market == '국내주식':
            # self.QCB_bong.setCurrentText('일봉')
            self.QCB_bong_detail.setCurrentText('1분봉')
        elif market == '국내선옵':
#             self.QCB_bong.setCurrentText('5분봉')
            self.QCB_bong_detail.setCurrentText('1분봉')
        elif market == 'bybit':
#             self.QCB_bong.setCurrentText('4시간봉')
            self.QCB_bong_detail.setCurrentText('1분봉')

    def select_bong(self):
        bong = self.QCB_bong.currentText()
        new_text = f"봉 = {{'{bong}':10}}"
        line_num = 1
        self.replace_QTE_line(self.QTE_stg_buy, new_text, line_num)

    def select_market(self):
        self.QCB_bong_detail.setEnabled(True)

        market = self.QCB_market.currentText()
        self.dict_DB_info = {"market":market,"ticker":'','상세봉':'',
                             '시작일':datetime.datetime.now().date(),'종료일':datetime.datetime.now().date()}
        if market == 'bybit':
            self.dict_DB_info['db_file'] = 'DB/DB_bybit.db'
            self.dict_DB_info['list_ticker'] = ['BTC','ETH','XRP']
            self.QCB_bong_detail.setCurrentText('1분봉')
            self.QCB_bong_detail.setEnabled(False)
            self.dict_DB_info['상세봉'] = self.QCB_bong_detail.currentText()
        elif market == '국내주식':
            self.dict_DB_info['db_file'] = 'DB/DB_stock.db'
            self.dict_DB_info['list_ticker'] = ['KODEX 레버리지','KODEX 200선물인버스2X']
        elif market == '국내선옵':
            self.dict_DB_info['db_file'] = 'DB/DB_futopt.db'
            # self.dict_DB_info['bet'] = 5000000
            self.dict_DB_info['list_ticker'] = ['선물','미니선물','콜옵션','풋옵션','코스닥150',
                                                '야간선물','야간미니선물','야간콜옵션','야간풋옵션','야간코스닥150',
                                                '종합선물','종합미니선물','종합콜옵션','종합풋옵션','종합코스닥150']
            self.QCB_bong_detail.setCurrentText('1분봉')
            self.QCB_bong_detail.setEnabled(False)
            self.dict_DB_info['상세봉'] = self.QCB_bong_detail.currentText()

        else:
            self.QTE_stg_buy.setText("진입대상 = ''\n" #범위로 지정 시 {ticker:""}
                                     "비교대상 = []\n"
                                     "봉 = {'4시간봉':10}\n"
                                     "배팅금액 = 100\n"
                                     "분할매수 = []\n"
                                     "방향 = 'long'\n"
                                     "레버리지 = 3\n"
                                     # "분할매도 = []\n"
                                     "####################\n"
                                     "매수가 = \n"
                                     # "매수 = False\n"
                                     "")
            self.QTE_stg_sell.setText("분할매도 = [] #분할매도 시 리스트 형식으로 비율을 저장할 것 예)[30,30,40] \n"
                                      "####################\n"
                                      "매도가 = 시장가 #분할매도 시 리스트 형식으로 저장할 것\n"
                                      "")
            return
        print(f"{market}...{self.dict_DB_info['db_file']}")
        # self.conn_DB = sqlite3.connect(self.dict_DB_info['db_file'], check_same_thread=False) #다른 스레드에서 접근 가능
        self.conn_DB = sqlite3.connect(self.dict_DB_info['db_file'])

        self.conn_stg = sqlite3.connect('DB/strategy.db')
        cursor_stg = self.conn_stg.cursor()
        cursor_stg.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list_stg = cursor_stg.fetchall()
        cursor_stg.close()
        if not table_list_stg:
            print(f'* strategy 테이블이 비어있음 - 확인 필요 *')
            return
        else:
            # table_list_stg = np.concatenate(table_list_stg).tolist()
            self.df_stg_buy = pd.read_sql(f"SELECT * FROM '{market}_buy'", self.conn_stg).set_index('index')
            list_stg_buy = self.df_stg_buy.index.tolist()

            self.df_stg_sell = pd.read_sql(f"SELECT * FROM '{market}_sell'", self.conn_stg).set_index('index')
            list_stg_sell = self.df_stg_sell.index.tolist()

        conn_DB = sqlite3.connect(self.dict_DB_info['db_file'])
        cursor_DB = conn_DB.cursor()
        cursor_DB.execute("SELECT name FROM sqlite_master WHERE type='table';")
        list_table = cursor_DB.fetchall()
        cursor_DB.close()
        if not list_table:
            print(f"[select_market] {market}: DB 테이블이 비어있음 - 확인 필요")
            list_table =[]
        else:
            list_table = np.concatenate(list_table).tolist()
            list_table = [x[:x.index('_')] for x in list_table if '_' in x ]
        list_table.extend(self.dict_DB_info['list_ticker'])
        list_table = list(set(list_table))
        list_table.insert(0, '전체')
        self.QCB_ticker.clear()
        self.QCB_ticker.addItems(list_table)
        self.QCB_ticker.setCurrentText(list_table[0])
        self.QCB_stg_buy.clear()
        self.QCB_stg_buy.addItems(list_stg_buy)
        self.QCB_stg_sell.clear()
        self.QCB_stg_sell.addItems(list_stg_sell)
        self.QTE_stg_buy.clear()
        self.QTE_stg_sell.clear()
        if not self.QCB_stg_buy.currentText() == '':
            self.QTE_stg_buy.setText(self.df_stg_buy.loc[self.QCB_stg_buy.currentText(), '전략코드'])
            self.QLE_stg_buy.setText(self.QCB_stg_buy.currentText())
            locals_dict_buy = {}
            stg = self.df_stg_buy.loc[self.QCB_stg_buy.currentText(), '전략코드']
            # text = stg.split("\n", 1)[0]  # 첫줄 읽기 추출
            exec(stg.split("\n", 1)[0], None, locals_dict_buy)
            obj = locals_dict_buy.get('진입대상')
            if not type(obj) == dict:
                self.QCB_ticker.setCurrentText(obj)
            # text = stg.split("\n", 2)[1]  # 둘줄 읽기 추출
            exec(stg.split("\n", 2)[1], None, locals_dict_buy)
            bong = locals_dict_buy.get('봉')
            self.QCB_bong.setCurrentText(list(bong.keys())[0])

        else:
            if market == 'bybit':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "비교대상 = []\n"
                                         "봉 = {'4시간봉':10}\n"
                                         "배팅금액 = 100\n"
                                         "분할매수 = []\n"
                                         "레버리지 = 3\n"
                                         "방향 = 'long'\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "매수 = False"
                                         "")
            elif market == '국내선옵' or market == '국내주식':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "비교대상 = []\n"
                                         "봉 = {'5분봉':5}\n"
                                         "방향 = 'long'\n"
                                         "배팅금액 = 10000000\n"
                                         "분할매수 = []\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "매수 = False"
                                         "")
            elif market == '국내선옵' or market == '국내주식':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "비교대상 = []\n"
                                         "봉 = {'5분봉':5}\n"
                                         "방향 = 'long'\n"
                                         "배팅금액 = 10000000\n"
                                         "분할매수 = []\n"
                                         "방향 = 'long'\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "매수 = False"
                                         "")
        if not self.QCB_stg_sell.currentText() == '':
            self.QTE_stg_sell.setText(self.df_stg_sell.loc[self.QCB_stg_sell.currentText(), '전략코드'])
            self.QLE_stg_sell.setText(self.QCB_stg_sell.currentText())

        else:
            self.QTE_stg_sell.setText("분할매도 = [] #분할매도 시 리스트 형식으로 비율을 저장할 것 예)[30,30,40] \n"
                                      "####################\n"
                                      "매도가 = 시장가 #분할매도 시 리스트 형식으로 저장할 것\n"
                                      "매도 = False"
                                      "")

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

    def load_DB(self):
        self.stg_buy = self.QTE_stg_buy.toPlainText()
        self.stg_buy = self.replace_tabs_with_spaces(self.stg_buy)
        self.stg_sell = self.QTE_stg_sell.toPlainText()
        self.stg_sell = self.replace_tabs_with_spaces(self.stg_sell)
        # global 등락률상위, 거래량상위, 거래대금상위, 시가총액상위, 시간외잔량상위, 체결강도상위, 관심종목등록상위
        # global 전체, 선물, 미니선물, 콜옵션, 풋옵션, 코스닥150, 야간선물, 야간미니선물, 야간콜옵션, 야간풋옵션, 야간코스닥150, 종합선물, 종합미니선물, 종합콜옵션, 종합풋옵션, 종합코스닥150
        # global BTC, ETH, XRP
        global long, short
        long = 'long'
        short = 'short'
        등락률상위 = '등락률상위'
        야간선물 = '야간선물'

        locals_dict_buy = {}
        # obj = self.stg_buy.split("\n", 1)[0]  # 진입대상
        exec(self.stg_buy.split("\n", 1)[0], None, locals_dict_buy)
        obj = locals_dict_buy.get('진입대상')
        exec(self.stg_buy.split("\n", 2)[1], None, locals_dict_buy)
        compare = locals_dict_buy.get('비교대상')
        # bong = self.stg_buy.split("\n", 2)[1]  # 둘줄 읽기 추출
        exec(self.stg_buy.split("\n", 3)[2], None, locals_dict_buy)
        bong = locals_dict_buy.get('봉')

        market = self.QCB_market.currentText()
        bong_detail = self.QCB_bong_detail.currentText()

        bong = list(bong.keys())[0]
        if bong == '봉':
            self.pop_message('에러','기준봉을 설정해 주세요.')
            return
        if bong_detail == '상세봉':
            self.pop_message('에러', '상세봉을 설정해 주세요.')
            return
        if type(obj) == dict:
            ticker = list(obj.keys())[0]
            val_range = list(obj.values())[0]
        else:
            # if obj in list_table:
            ticker = obj
            val_range = None
            # raise Exception (f'ticker 확인 필요 {obj= }   {self.list_table= } ')
        self.QTE_state.setText(f"{market} {obj} {bong} 로딩 중..." )
        if (self.dict_DB_info['market'] != market or self.dict_DB_info['ticker'] != ticker or
                self.dict_DB_info['상세봉'] != bong_detail or self.dict_DB_info['봉'] != bong):
            self.dict_DB_info["ticker"]=ticker
            self.dict_DB_info['봉']=bong
            self.dict_DB_info['상세봉']=self.QCB_bong_detail.currentText()
            self.dict_DB_info['시작일']=datetime.datetime.strptime(self.QLE_start.text(),"%Y-%m-%d")
            self.dict_DB_info['종료일']=datetime.datetime.strptime(self.QLE_end.text(),"%Y-%m-%d")
            self.dict_DB_info['val_range']=val_range
            # if self.dict_DB_info['시작일'] <
            print(f"DB 로딩 - {self.dict_DB_info} ")
            # self.worker = get_df.WorkerThread(self.dict_info)
            # self.worker = get_df.WorkerThread_min_to_bong(self.dict_info)
            # self.worker.result_ready.connect(self.run_backtest)
            # self.worker.start()
            # df, df_detail,save = self.worker.run()
            # df, df_detail,save = self.make_df(self.dict_info)

            self.thread_make_DB = make_data(self, self.dict_DB_info)
            self.thread_make_DB.start()
            self.thread_make_DB.signal_bt_df.connect(self.get_backtest_df)
            self.thread_make_DB.signal_light.connect(self.effect_DB_loading)

        else:
            print(f"DB 기존 - {self.dict_DB_info} ")
        self.QPB_DB_load.setStyleSheet("background-color: #00ffae;")

    def get_backtest_df(self, df, df_detail,ticker,bong):
        self.df = df.copy()
        self.df_detail = df_detail.copy()
        self.pop_message('완료', f'DB파일을 로딩하였습니다.\n {ticker} {bong}')
        self.QPB_DB_load.setEnabled(True)
        start_day_QTE = datetime.datetime.strptime(self.QLE_start.text(), "%Y-%m-%d")
        end_day_QTE = datetime.datetime.strptime(self.QLE_end.text(), "%Y-%m-%d")
        start_day_df = df_detail.index[0]
        end_day_df = df_detail.index[-1]
        # self.thread_make_DB.stop()
        # df = df
        # common_def.export_sql(df,'DB/bt.db','df')
        # common_def.export_sql(df_detail,'DB/bt.db','df_detail')
        if start_day_QTE < start_day_df:
            start_day = start_day_df
            self.QLE_start.setText(start_day.strftime('%Y-%m-%d'))
        if end_day_QTE > end_day_df:
            end_day = end_day_df
            self.QLE_end.setText(end_day.strftime('%Y-%m-%d'))
        txt = self.QTE_state.toPlainText()
        txt = txt.replace("로딩 중...","로딩 완료")
        self.QTE_state.setText(txt)
        self.QPB_start.setEnabled(True)

    def get_dict_bt(self):
        stg_buy = self.replace_tabs_with_spaces(self.QTE_stg_buy.toPlainText())
        stg_sell = self.replace_tabs_with_spaces(self.QTE_stg_sell.toPlainText())
        global 등락률상위, 거래량상위, 거래대금상위, 시가총액상위, 시간외잔량상위, 체결강도상위, 관심종목등록상위
        global long, short
        long = 'long'
        short = 'short'
        # 미니선물 = '미니선물'
        # ticker = self.QCB_ticker.currentText()
        market = self.QCB_market.currentText()
        bong_detail = self.QCB_bong_detail.currentText()

        locals_dict_buy = {}

        obj = stg_buy.split("\n", 1)[0]  # 첫줄 읽기 추출
        exec(obj, None, locals_dict_buy)
        obj = locals_dict_buy.get('진입대상')

        bong = stg_buy.split("\n", 2)[1]
        exec(bong, None, locals_dict_buy)
        bong = locals_dict_buy.get('봉')

        bet = stg_buy.split("\n", 3)[2]
        exec(bet, None, locals_dict_buy)
        bet = locals_dict_buy.get('배팅금액')

        division_buy = stg_buy.split("\n", 4)[3]
        exec(division_buy, None, locals_dict_buy)
        division_buy = locals_dict_buy.get('분할매수')

        if market == '국내선옵' or market == 'bybit':
            direction = stg_buy.split("\n", 5)[4]
            exec(direction, None, locals_dict_buy)
            direction = locals_dict_buy.get('방향')

            if market == 'bybit':
                증거금률 = stg_buy.split("\n", 6)[5]
                exec(증거금률, None, locals_dict_buy)
                증거금률 = locals_dict_buy.get('레버리지', 1)

        locals_dict_sell = {}
        division_sell = stg_sell.split("\n", 1)[0]  # 첫줄 읽기 추출
        exec(division_sell, None, locals_dict_sell)
        division_sell = locals_dict_sell.get('분할매도')

        bong = list(bong.keys())[0]
        if type(obj) == dict:
            ticker = list(obj.keys())[0]
            val_range = list(obj.values())[0]
        else:
            # if obj in list_table:
            ticker = obj
            val_range = None
            # raise Exception (f'ticker 확인 필요 {obj= }   {self.list_table= } ')

        거래승수 = 1
        if market == '국내주식':
            direction = 'long'
            exchange = KIS.KoreaInvestment(market='test')
            증거금률 = 1
            fee = 0.018

            # if ticker in self.stocks_info['종목명'].tolist():
            #     dict_ticker_reverse = dict(zip(self.dict_ticker.values(), self.dict_ticker.keys()))
            #     ticker = dict_ticker_reverse[ticker]
            #     self.trade_market = self.stocks_info.loc[ticker, '시장구분']
            # else:
            #     raise
            self.trade_market = "KOSPI"
        elif market == '국내선옵':  # 거래승수
            dic_multiplier = {'선물': 250000, '콜옵션': 250000, '풋옵션': 250000, '위클리_콜옵션': 250000, '위클리_풋옵션': 250000,
                              '2AF': 250000, '3AF': 250000,  # 코스피200
                              '미니선물': 50000, '205': 50000, '305': 50000,  # 미니코스피200
                              '코스닥선물': 10000, '206': 10000, '306': 10000,  # 코스닥150
                              }

            거래승수 = dic_multiplier[ticker]
            self.trade_market = ticker if ticker == '선물' else '옵션'
            exchange = KIS.KoreaInvestment(market='test')
            증거금률 = 10
            fee = 0.01
        elif market == 'bybit':
            self.trade_market = 'bybit'
            exchange, _ = common_def.make_exchange_bybit()
            fee = 0.055

        # else:
        #     exchange = KIS.KoreaInvestment('국내선옵', 'test')

        start_day_QTE = datetime.datetime.strptime(self.QLE_start.text(), "%Y-%m-%d")
        end_day_QTE = datetime.datetime.strptime(self.QLE_end.text(), "%Y-%m-%d")
        end_day_QTE = end_day_QTE + datetime.timedelta(days=1)
        if obj == None or bong == None or bet == None:
            self.pop_message('에러', f"전략확인 | {obj=} | {bong=} | {bet=}")
            print(f"'에러', 전략확인 | {obj=} | {bong=} | {bet=}")
            return
        dict_bt_info = {'market': market, 'ticker': ticker, 'val_range': val_range, '봉': bong, '상세봉': bong_detail,
                        '시작일': start_day_QTE, '종료일': end_day_QTE, # 'connect': self.conn_DB,
                        'trade_market': self.trade_market, 'exchange': exchange,
                        'stg_buy': stg_buy, 'stg_sell': stg_sell, 'bet': bet,
                        # 'dict_bong_reverse': self.dict_bong_reverse,
                        '분할매수': division_buy, '분할매도': division_sell,
                        'direction': direction, '거래승수': 거래승수, '증거금률': 증거금률,'fee':fee}
        return dict_bt_info

    def do_backtest(self):
        self.QTE_state_text = ''
        self.QPB_stop.setEnabled(True)
        self.dict_bt_info = self.get_dict_bt()
        df = self.df.loc[(self.df.index >= self.dict_bt_info['시작일']) & (self.df.index <= self.dict_bt_info['종료일'])]
        df_detail = self.df_detail.loc[(self.df_detail.index >= self.dict_bt_info['시작일']) & (self.df_detail.index <= self.dict_bt_info['종료일'])]
        # 백테시간 줄이기용
        # print('===============')
        # print(df_detail)
        # st = time.time()
        # for factor in df_detail.columns.tolist():
        #     if not factor in str(self.stg_buy + stg_sell):  # 실제 전략에 필요한 팩터만 남기고 데이터프레임에서 삭제
        #         if not factor in ['상세시가', '상세고가', '상세저가', '상세종가', '시가', '고가', '저가', '종가', '종료시간',
        #                           '현재시간', '장시작시간', '장종료시간','데이터길이']:  # 삭제에서 제외
        #             df_detail.drop(factor, axis=1, inplace=True)
        # print(f"{df.index[0]} ~ {df.index[-1]}")
        # print(f"{df_detail.index[0]} ~ {df_detail.index[-1]}")
        # print(f'********{time.time()-st}*******')

        self.length_index = len(self.df_detail.index)
        if sys.maxsize > self.length_index:  # df_detail.index의 값이 int형의 최대값보다 작을 경우만 백테스트 진행
            print('백테스트 시작')

            # self.thread = ATOM_bt_thread_numpy.backtest_np(self,df, df_detail,self.dict_bt_info)
            self.thread = ATOM_backtest_numpy.backtest_np(self, df, df_detail, self.dict_bt_info)
            self.thread.start()
            self.thread.signal_bar.connect(self.progress_loading)
            self.thread.signal_df.connect(self.view_chart)
            self.thread.signal_state.connect(self.state_bt)
            self.thread.signal_light.connect(self.effect_backtest)
            self.thread.signal_message.connect(self.pop_message)

            self.QPB_start.setEnabled(False)
        else:
            print(f"데이터 최대값 초과 : 백테스트 기간을 더 단축하세요   {sys.maxsize=}    {self.length_index=}")
    def on_stop(self):
        self.thread.stop()
        self.QPB_start.setEnabled(True)
        self.QPB_stop.setEnabled(False)
        self.QPB_bar.setValue(0)
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
            start_day = datetime.datetime.strftime(df.index[0], '%Y-%m-%d')
            self.QLE_start.setText(start_day)
            # list_columns = df.columns.tolist()
            if self.QCB_chart.isChecked() == True:
                # df_chart_table = self.chart_table.input(df, self.QCB_market.currentText())
                self.chart_table.impo_table(df, self.dict_bt_info['market'])
                self.chart_table.chart_show(self.dict_bt_info['market'], self.dict_bt_info['ticker'])
            self.result_chart(df)
            # df.to_sql('backtest', sqlite3.connect('DB/bt.db'), if_exists='replace')
    def result_chart(self, df):
        기간수익률 = df['자산'][-1] / df['자산'][0]
        delta = df.index[-1] - df.index[0]
        N = delta.days / 365
        연복리수익률 =  (기간수익률 ** (1 / N)) - 1

        # df['index'] = round(self.compare_price(df['종가'], df['전략수익률']), 2)
        # df_benefit = df[['MDD','DD']]
        # df_benefit.to_sql('수익금',sqlite3.connect('DB/bt.db'), if_exists='replace')
        buy_count = df['매수가'].count()
        df_profit = df.loc[df['매도가'].notna() & df['매도금액'].notna(),['수익금']] #매도가열과 매도금액 열이 nan이 아닌행만
        win = len(df_profit.loc[df_profit['수익금'] > 0])  # 횟수
        lose = len(df_profit.loc[df_profit['수익금'] < 0])
        win_sum = df_profit.loc[df_profit['수익금'] > 0].수익금.sum()  # 금액
        loss_sum = df_profit.loc[df_profit['수익금'] < 0].수익금.sum()
        avg_profit = win_sum / win
        avg_loss = loss_sum / lose
        if lose == 0:
            avg_loss = 0
        else:
            avg_loss = loss_sum / lose
        pov = win / buy_count * 100


        grid = GridSpec(4, 1, wspace=0.3, hspace=0.5)
        fig = plt.figure(figsize=(16, 9))

        ax1 = fig.add_subplot(grid[0:3, 0:1])
        ax2 = fig.add_subplot(grid[3:4, 0:1], sharex=ax1)

        market = self.dict_bt_info['market']
        if market == 'bybit':
            x_range = df.index
        else:
            x_range = range(len(df))

        # 좌측 y축 (ax1) - index
        ax1.plot(x_range, df['종가'], label=f"{self.dict_bt_info['ticker']} 종가", color='red')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.set_ylabel(f"'{self.dict_bt_info['ticker']}'", color='red')
        ax1.legend(loc='upper right', shadow=True)  # 좌측 상단

        # 우측 y축 (ax1_right) - 전략수익률, holding
        ax1_right = ax1.twinx()
        ax1_right.plot(x_range, df['전략수익률'], label='전략수익률 %', color='orange')
        ax1_right.plot(x_range, df['holding'], label='holding %', color='green')
        ax1_right.set_ylabel('전략수익률 / Holding', color='red')
        ax1_right.tick_params(axis='y', labelcolor='black')
        ax1_right.legend(loc='upper right', shadow=True)  # 우측 상단

        # 범례 통합
        # lines1, labels1 = ax1.get_legend_handles_labels()
        # lines2, labels2 = ax1_right.get_legend_handles_labels()
        # ax1.legend(lines1 , labels1, loc='upper left', ncol=3, shadow=True)


        if market == 'bybit':
            ax2.hlines(df['DD'].mean(), df.index.min(), df.index.max(), color='g', ls='--')
            ax2.plot(df.DD, c='y', lw=1, label='DD')
            ax2.plot(df.MDD, c='r', lw=1, label='MDD')
        else:
            # x축 레이블 설정 (일정 간격으로 날짜 표시)
            step = max(1, len(df) // 10)  # 약 10개 정도의 레이블 표시
            tick_positions = range(0, len(df), step)
            tick_labels = [df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i])
                           for i in tick_positions]
            ax1.set_xticks(tick_positions)
            ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
            ax2.hlines(df['DD'].mean(), 0, len(df)-1, color='g', ls='--')
            ax2.plot(x_range,df['DD'], c='y', lw=1, label='DD')
            ax2.plot(x_range,df['MDD'], c='r', lw=1, label='MDD')
        ax2.legend(loc=1, ncol=3, shadow=True)
        ax2.set_ylabel('Drawdown')
        self.배팅금액 = format(int(self.dict_bt_info['bet']), ',')
        수익금 = round(df['자산'][-1]-int(self.dict_bt_info['bet']))
        self.수익금 = format(수익금, ',')
        self.수익률 = round(수익금 / int(self.dict_bt_info['bet']) * 100)
        self.연복리수익률 = round(연복리수익률*100, 1)
        self.거래횟수 = buy_count
        idx_day = df.index.astype(str).str[:10]
        거래일 = len(df.groupby(idx_day).size().index)
        self.일평균거래횟수 = round(buy_count / 거래일, 1)
        self.승률 = round(pov, 1)
        self.MDD = df['MDD'][-1].round(1)
        import math
        print(f"{avg_profit}")
        print(f"{avg_loss}")
        gcd = math.gcd(int(avg_profit), int(avg_loss))
        self.손익비 = f"{int(avg_profit) // gcd}:{int(avg_loss) // gcd}"

        # try:
        plt.title(
            f"종목명: {self.dict_bt_info['ticker']},  배팅금액{self.배팅금액},  매매기간: {self.dict_bt_info['시작일']} ~ {self.dict_bt_info['종료일']},  "
            f"봉: {self.dict_bt_info['봉']},  총 수익금: {self.수익금} 원,  수익률: {self.수익률} %, 연복리수익률(CAGR): {self.연복리수익률} %,\n"
            f"거래횟수: {self.거래횟수},  일평균 거래횟수: {self.일평균거래횟수},  거래일: {거래일}  승률: {self.승률}%,  손익비: {self.손익비}, "
            f"MDD: {self.MDD*100} %, "
            f" TradingEdge: {round(pov * avg_profit - (1 - pov) * avg_loss)},  "
            f"P&L ration: {round((1 - pov) / pov, 1)} ")
        # except:
        # plt.title(
        #     f"배팅금액{format(int(self.dict_bt_info['bet']), ',')}  총 수익금: 청산  거래횟수: {buy_count}  승률: {round(pov, 1)}%,"
            # f"청산일: {df_nan.index[0]}"
            # )
            # df_nan = df.loc[np.isnan(df['strategy'])]
        plt.legend()
        plt.show()
        self.plt = plt

    def progress_loading(self, val):
        self.QPB_bar.setValue(val)
        # if val == 100: self.on_stop()



    def save_bt(self):
        self.BTN_efect(self.QPB_save_bt)
        path = 'DB/images/' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M')) + '.png'
        plt.savefig(path, dpi=200, facecolor='#eeeeee', edgecolor='blue', bbox_inches='tight')
        data = {'ticker': self.QCB_ticker.currentText(), '배팅금액': self.배팅금액, '수익금': self.수익금, '수익률': self.수익률,
                '연복리수익률': self.연복리수익률, '거래횟수': self.거래횟수, '일평균거래횟수': self.일평균거래횟수, '승률': self.승률,
                '손익비': self.손익비, 'MDD': self.MDD, '매매기간': self.QLE_start.text() + '~' + self.QLE_end.text(),
                '봉': self.QCB_bong.currentText(), '매수전략': self.QTE_stg_buy.toPlainText(),
                '매도전략': self.QTE_stg_sell.toPlainText()}
        df = pd.DataFrame(data=data, index=[str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M'))])
        # columns=['ticker', '배팅금액', '수익금', '수익률', '연복리수익률', '거래횟수',
        #          '일평균거래횟수', '승률', '손익비', 'MDD', '매매기간', '봉','매수전략', '매도전략'])
        # df = pd.DataFrame(data, index=[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
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

    def BTN_efect(self, QPB):
        QPB.setEnabled(False)
        QTest.qWait(250)
        QPB.setEnabled(True)
    def state_bt(self, state):
        txt = ''
        for key, value in state.items():
            txt += f'{key}: {value}, '
            # txt += f'{key}: {value}\n'
        self.QTE_state_text = self.QTE_state_text  + txt
        self.QTE_state.setText(txt)

    def init_file(self):
        import os
        stg_file = ['DB/DB_stock.db', 'DB/DB_futopt.db', 'DB/DB_bybit.db', 'DB/DB_upbit.db']
        for market in stg_file:
            if not os.path.isfile(market):  # stg_file.db 파일이 없으면
                print(f"{market} 파일 없음")
                conn = sqlite3.connect(market)
                if market == 'DB/DB_futopt.db':
                    li_col = ['날짜', '요일', '금융기관업무일', '입출금가능일', '개장일', '지불일']
                    df = pd.DataFrame(columns=li_col)
                    df = df.set_index('날짜', drop=True)
                    df.to_sql('holiday',conn,if_exists='replace')

        file = 'DB/strategy.db'
        if not os.path.isfile(file):
            sqlite3.connect(file)
            conn = sqlite3.connect(file)
            list_stg = ['bybit_buy', 'bybit_sell','업비트_buy', '업비트_sell', '국내주식_buy', '국내주식_sell','국내선옵_buy', '국내선옵_sell']
            for stg in list_stg:
                df = pd.DataFrame(columns=['전략코드'])
                df.to_sql(stg, conn, if_exists='replace')
    def pop_vars_buy(self):
        popup = TextPopupBuy(self)
        popup.exec_()  # 모달 다이얼로그 (메인  창 블록)
    def pop_vars_sell(self):
        popup = TextPopupSell(self)
        popup.exec_()  # 모달 다이얼로그 (메인  창 블록)
    def effect_DB_loading(self, light):
        if light == True:
            self.QPB_DB_load.setStyleSheet("background-color: #fa3232;")
        if light == False:
            self.QPB_DB_load.setStyleSheet("background-color: #cccccc;")
    def effect_backtest(self, light):
        if light == True:
            self.QPB_start.setStyleSheet("background-color: #fa3232;")
        if light == False:
            self.QPB_start.setStyleSheet("background-color: #cccccc;")
    def pop_message(self,title,message):
        QMessageBox.about(self,title,message)
    def progress_state(self, state):
        if state == 'max':
            self.QPB_bar.setValue(self.QPB_bar.maximum())
        elif state == 'min':
            self.QPB_bar.setValue(self.QPB_bar.minimum())
        else:
            self.QPB_bar.setValue(state)
if __name__ == '__main__':

#######################################################################################
    # import sys
    # def ExceptionHook(exctype, value, traceback):
    #     sys.__excepthook__(exctype, value, traceback)
    #     sys.exit(1)
    # sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    # app = QApplication(sys.argv)

#######################################################################################

    app = QApplication(sys.argv)
    window = Window(tab_chart_table.Window())
    window.setGeometry(1000, 500, 700, 600)  # x,y,width,height
    window.show()
    sys.exit(app.exec_())