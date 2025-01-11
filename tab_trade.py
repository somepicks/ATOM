from datetime import datetime, timedelta
import pandas as pd
# from pandas import to_numeric
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, QAbstractItemView
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QTimer, QRegExp
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics, QFont, QColor, QSyntaxHighlighter, QTextCharFormat
# from PyQt5.QtGui import *
# from PyQt5 import QtWidgets, QtCore
# from PyQt5 import QtWidgets, QtCore
import numpy as np
# import pyqtgraph as pg
# import ccxt
# import math
# import color as cl
import chart_real
# from collections import deque
import time
# from pprint import pprint
# import multiprocessing as mp
# import tab_chart_table
# import color as cl
# import sys
import sqlite3
import ATOM_trade_numpy
import subprocess
# import ntplib
# from time import ctime
# import random
import common_def
import json  # 리스트를 문자열로 변환하기 위해 필요
import tab_chart_table

pd.set_option('display.max_columns', None)  # 모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment', None)  # SettingWithCopyWarning 경고를 끈다
import schedule
import KIS

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m','15분봉': '15m', '30분봉': '30m', '60분봉': '60m','4시간봉': '4h', '일봉': 'd'}
        # self.dict_bong_stamp = {'1분봉': 60, '3분봉': 180, '5분봉': 300, '30분봉': 1800, '4시간봉': 14400, '일봉': 86400}
        self.dict_bong_time_datetime = {'1분봉': timedelta(minutes=1), '3분봉': timedelta(minutes=3),
                                        '5분봉': timedelta(minutes=5), '15분봉': timedelta(minutes=15),
                                        '30분봉': timedelta(minutes=30),'60분봉': timedelta(minutes=60),
                                        '4시간봉': timedelta(minutes=240), '일봉': timedelta(days=1)}
        self.set_UI()
        self.init_file()
        # self.time_acync()

        self.QPB_start.clicked.connect(self.do_trade)
        self.QPB_stop.clicked.connect(self.slot_clicked_button)

        self.QPB_save_stg.clicked.connect(self.save_stg)
        self.QPB_del_stg.clicked.connect(self.del_stg)
        self.QPB_chart_start.clicked.connect(self.view_chart)
        self.QPB_chart_stop.clicked.connect(self.view_chart_stop)
        subprocess.Popen('python timesync.py')


        self.QCB_stg1.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg1))
        self.QCB_stg2.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg2))
        self.QCB_stg3.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg3))
        self.QCB_stg4.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg4))
        self.QCB_stg5.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg5))
        self.QCB_stg6.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg6))
        self.QCB_stg7.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg7))
        self.QCB_stg8.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg8))
        # self.QCB_stg_current.activated[str].connect(lambda: self.selectedCombo_stg(self.QCB_stg_current))
        # self.QCB_stg_current.activated[str].connect(lambda: self.QLE_stg.setText(self.QCB_stg_current.currentText()))
        self.QCB_market.activated[str].connect(lambda: self.select_market())
        self.QT_trade_open.cellClicked.connect(lambda: self.cellclick_table(1))
        self.QT_trade_closed.cellClicked.connect(lambda: self.cellclick_table(2))
        self.QT_tickers.cellClicked.connect(lambda: self.cellclick_ticker_table())

        self.QT_tickers.cellDoubleClicked.connect(lambda:self.cell_doubleclick_ticker_table())
        self.QT_tickers.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 더블클릭 시 수정 금지
        self.QT_trade_closed.cellDoubleClicked.connect(lambda:self.cell_doubleclick_trading_table(self.QT_trade_closed,self.df_history))
        self.QT_trade_open.cellDoubleClicked.connect(lambda:self.cell_doubleclick_trading_table(self.QT_trade_open,self.df_stg))
        self.QT_trade_closed.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 더블클릭 시 수정 금지
    def set_UI(self):
        self.real_chart = chart_real.Graph(self)

        self.setWindowTitle(f'TRADE')

        # self.QTE_stg_buy = QTextEdit()
        # self.QTE_stg_sell = QTextEdit()

        self.QTE_stg_buy = common_def.CodeEditor()
        self.QTE_stg_sell = common_def.CodeEditor()

        self.QT_trade_closed = QTableWidget()
        self.QT_trade_open = QTableWidget()
        self.QT_tickers = QTableWidget()

        self.QGL_menu = QGridLayout()
        self.QCB_simul = QCheckBox('모의매매')
        self.QCB_simul.setChecked(True)
        self.QCB_market = QComboBox()
        self.QCB_market.addItems(['', '코인', '국내주식','국내선옵'])
        self.QLE_chart_ticker = QLineEdit()
        self.QLE_bet = QLineEdit()
        self.QCB_hoga_buy = QComboBox()
        self.QCB_hoga_sell = QComboBox()
        self.QL_mdd = QLabel()
        self.QL_ror = QLabel()
        self.QL_benefit = QLabel()
        self.QL_qty = QLabel()
        self.QPB_start = QPushButton('START')
        self.QPB_stop = QPushButton('STOP')
        self.QCB_stgs = QComboBox()
        self.QPB_save_stg = QPushButton('전략저장')
        self.QPB_del_stg = QPushButton('전략삭제')
        self.QLE_stg = QLineEdit()
        self.QLE_leverage = QLineEdit()
        self.QCB_stg1 = QComboBox()
        self.QCB_stg2 = QComboBox()
        self.QCB_stg3 = QComboBox()
        self.QCB_stg4 = QComboBox()
        self.QCB_stg5 = QComboBox()
        self.QCB_stg6 = QComboBox()
        self.QCB_stg7 = QComboBox()
        self.QCB_stg8 = QComboBox()
        self.QCB_division_buy = QComboBox()
        self.QCB_division_sell = QComboBox()
        self.QPB_chart_start = QPushButton('리얼차트')
        self.QCB_chart_bong = QComboBox()
        self.QCB_chart_bong_detail = QComboBox()
        self.QCB_chart_duration = QComboBox()
        self.QCB_tele = QCheckBox('텔레그램')
        self.QPB_chart_stop = QPushButton('중지')
        dict_grid = {
            self.QCB_market: self.QCB_simul,
            self.QCB_stg1: self.QCB_stg5,
            self.QCB_stg2: self.QCB_stg6,
            self.QCB_stg3: self.QCB_stg7,
            self.QCB_stg4: self.QCB_stg8,
            self.QPB_start: self.QPB_stop,
            self.QLE_stg: self.QCB_stgs,
            self.QPB_save_stg: self.QPB_del_stg,
            QLabel("||"):QLabel("||"),
            QLabel('종목명'): self.QLE_chart_ticker,
            QLabel('배팅금액'): self.QLE_bet,
            # QLabel('매수호가'): self.QCB_hoga_buy,
            self.QCB_hoga_buy: self.QCB_hoga_sell,
            QLabel('레버리지'): self.QLE_leverage,
            self.QCB_division_buy: self.QCB_division_sell,
            QLabel('→ : 시장가[롱]'): QLabel('← : 시장가[숏]'),
            QLabel('↑ : 지정가[롱]'): QLabel('↓ : 지정가[숏]'),
            QLabel('MDD'): self.QL_mdd,
            QLabel('수익률'): self.QL_ror,
            QLabel('수익금'): self.QL_benefit,
            QLabel("||"):QLabel("||"),
            self.QCB_chart_duration: self.QCB_tele,
            self.QCB_chart_bong: self.QPB_chart_start,
            self.QCB_chart_bong_detail: self.QPB_chart_stop,}
        for i, key in enumerate(dict_grid):
            self.QGL_menu.addWidget(key, 0, i)
            self.QGL_menu.addWidget(dict_grid[key], 1, i)
        # StyleSheet_Qtextedit = "bborder-radius:5px;font: 10pt 나눔고딕;"
        StyleSheet_Qtextedit = "font: 10pt 나눔고딕; "
        QW_grid = QWidget()
        QW_grid.setStyleSheet(StyleSheet_Qtextedit)
        QW_grid.setLayout(self.QGL_menu)
        QW_grid.setMaximumSize(1980,80)
        # QW_grid.setMaximumSize(1980,70)
        list_bong =  list(self.dict_bong.keys())
        # del list_bong[0] # 1분봉 삭제
        # del list_bong[0] # 5분봉 삭제
        self.QCB_chart_bong.addItems(list_bong)
        self.QCB_hoga_buy.addItems(['매수호가','매도1호가','매도2호가','매도3호가','매도4호가','매도5호가'])
        self.QCB_hoga_sell.addItems(['매도호가','매수1호가','매수2호가','매수3호가','매수4호가','매수5호가'])
        self.QCB_division_buy.addItems(['분할매수','1','2','3','4','5'])
        self.QCB_division_sell.addItems(['분할매도','1','2','3','4','5'])
        self.QCB_chart_bong_detail.addItems(list(self.dict_bong.keys()))
        self.QCB_chart_duration.addItems(['기간(일)','1','2','3','4','5','6','7','8','9','10','15','20','30','60','90','120','150','240','300','400','600'])

        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 12pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 12pt 나눔고딕; "
        self.QTE_stg_buy.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE_stg_sell.setStyleSheet(StyleSheet_Qtextedit)

        # StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                     "border-color: black; header-color: black;font: 12pt 나눔고딕; "
        StyleSheet_Qtable = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                            "border-color: black; font: 12pt 나눔고딕; "
        self.QT_trade_closed.setStyleSheet(StyleSheet_Qtable)
        self.QT_trade_open.setStyleSheet(StyleSheet_Qtable)
        self.QT_tickers.setStyleSheet(StyleSheet_Qtable)
        self.QPB_start.setStyleSheet(" background-color: #cccccc;")
        self.QPB_stop.setStyleSheet("background-color: #cccccc;")

        QW_main = QWidget()

        self.setCentralWidget(QW_main)

        QSH_qte_stg = QSplitter(Qt.Horizontal)
        QSH_qte_stg.addWidget(self.QTE_stg_buy)
        QSH_qte_stg.addWidget(self.QTE_stg_sell)

        QSH_table = QSplitter(Qt.Horizontal)
        QSH_table.addWidget(self.QT_trade_open)
        QSH_table.addWidget(self.QT_trade_closed)

        QSV_main = QSplitter(Qt.Vertical)
        QSV_main.addWidget(self.real_chart.chart_main)
        QSV_main.addWidget(QSH_qte_stg)
        QSV_main.addWidget(QSH_table)

        QSH_main = QSplitter(Qt.Horizontal)
        QSH_main.addWidget(QSV_main)
        QSH_main.addWidget(self.QT_tickers)

        # QSV_main_main = QSplitter(Qt.Vertical)

        # QSH_final = QSplitter(Qt.Horizontal)
        # QSH_final.addWidget(QSV_main)
        # QSH_final.addWidget(self.QT_tickers)
        # QSV_main.setStretchFactor(500,100)
        # QSV_main.setStretchFactor(1,2)
        # QSV_main.setStretchFactor(0,1)
        # QSV_main.setStretchFactor(0,1)

        # QVB_main.addWidget(QSV_main)
        QVB_main = QVBoxLayout()
        QVB_main.addWidget(QSH_main)
        QVB_main.addWidget(QW_grid)
        QW_main.setLayout(QVB_main)


        # self.QCB_krx.setChecked(True)
        # self.QCB_stg1.activated[str].connect(lambda :self.selectedCombo_stg())
        self.QTE_stg_buy.setTabStopWidth(QFontMetrics(QFont('나눔고딕')).width(' ' * 4))
        self.QTE_stg_sell.setTabStopWidth(QFontMetrics(QFont('나눔고딕')).width(' ' * 4))


        self.highlighter_buy = common_def.PythonHighlighter(self.QTE_stg_buy.document())
        self.highlighter_sell = common_def.PythonHighlighter(self.QTE_stg_sell.document())


        self.QCB_tele.setChecked(True)


    def init_file(self):
        import os
        stg_file = ['DB/stg_stock.db', 'DB/stg_bybit.db', 'DB/stg_futopt.db']
        # index = ['전략명']
        # dict_data = {'market': '', '진입대상': '', 'ticker': '', '봉': '', '방향': '', '배팅금액': 0, '매입금액': 0, '레버리지': 0, '진입전략': '',
        #              '청산전략': '',  '현재가': 0, '진입가': 0, '주문수량': 0, '진입시간': '', '청산가': 0, '청산시간': '', '수익률': 0,
        #              '최고수익률': 0, '최저수익률': 0, '수익금': 0, '평가금액': 0, '상태': '대기', 'id': '', '수수료': 0, '승률(win/all)': '', '누적수익금': 0,
        #              '잔고': 0, '상세봉': 0, '현재봉시간': '', 'table': 0}
        # dict_table = {'stg1': '', 'stg2': '', 'stg3': '', 'stg4':'', 'stg5': '' , 'stg6': '', 'stg7': '' , 'stg8':''}
        li_col = ['전략명','market', '진입대상', 'ticker', '봉', '방향', '초기자금','배팅금액', '매입금액','청산금액', '레버리지',
                  '진입전략', '청산전략',  '현재가', '진입가', '주문수량', '체결수량','보유수량','진입시간', '청산가', '청산시간',
                  '수익률', '최고수익률', '최저수익률', '수익금', '평가금액', '상태', 'id', '수수료', '진입수수료', '승률(win/all)', '누적수익금',
                  '잔고', '봉제한', '현재봉시간', 'table', '분할매수', '분할매도', '분할상태', '분할진입가','매입율',
                  # '상세봉',
                  '분할청산가', '분할주문수량', '분할보유수량', '분할매입금액', '분할청산금액', '분할진입수수료', '분할id',
                  '분할평가금액','분할진입시간','분할청산시간','매도전환','진입신호시간','청산신호시간']
        for market in stg_file:
            if not os.path.isfile(market):  # stg_file.db 파일이 없으면
                conn = sqlite3.connect(market)
                df = pd.DataFrame(columns=li_col)
                # df.drop(index=0, inplace=True)  # 최초 데이터 생성 시 '전략명'이라는 인덱스가 생기며 이를 삭제
                df.to_sql('stg', conn, if_exists='replace')
                df.to_sql('history', conn, if_exists='replace')
                conn.close()

                #
                # index = ['종목코드']
                # dict_data = {'잔고수량':'','체결평균단가':'','평가금액':'','정산단가':'','지수종가':'','청산가능수량':'','매입금액':'','평가손익':'',
                #                  '상품번호':'','상품명':'','상품유형코드':'','종목코드':'','매도매수구분명':'','매매손익금액':''}
                # df = pd.DataFrame(data=dict_data, index=index)

        self.df_manul = pd.DataFrame(index=['수동매매'],columns=li_col)
        # print(self.df_manul)

    def display_futopt(self):
        # def convert_column_types(df):
        #     for col in df.columns:
        #         try:
        #             df[col] = pd.to_numeric(df[col], errors='raise')
        #         except ValueError:
        #             pass
        #     return df
        QTest.qWait(500)
        df_f = self.ex_kis.display_fut()
        df_f = common_def.convert_column_types(df_f)
        #
        현재가 = df_f.loc[df_f.index[0], '현재가']
        today = datetime.now()
        QTest.qWait(500)
        # expiry_date = self.nth_weekday(today,2,3) #이번달의 두번째 주, 목요일 구하기
        df_c, df_p = self.ex_kis.display_opt(today)
        df_c = common_def.convert_column_types(df_c)
        df_p = common_def.convert_column_types(df_p)
        # print(1)
        QTest.qWait(500)
        # expiry_date_week = self.nth_weekday(today,2,3) #이번달의 두번째 주, 목요일 구하기
        df_c_weekly, df_p_weekly,self.COND_MRKT = self.ex_kis.display_opt_weekly(today)
        df_c_weekly = common_def.convert_column_types(df_c_weekly)
        df_p_weekly = common_def.convert_column_types(df_p_weekly)
        # df_c_thur, df_p_thur = self.ex_kis.display_opt_weekly_thur()
        # df_c_thur = common_def.convert_column_types(df_c_thur)
        # df_p_thur = common_def.convert_column_types(df_p_thur)

        # print(2)
        # 조건에 '시가_풋옵션_5분봉' 과같은 팩터가 올 수 있으니 비율을 똑같이 해줘야 함
        df_c = df_c[df_c['행사가'] > 현재가 - 30]
        df_c = df_c[df_c['행사가'] < 현재가 + 30]
        df_c['종목명'] = '콜옵션'
        df_p = df_p[df_p['행사가'] > 현재가 - 30]
        df_p = df_p[df_p['행사가'] < 현재가 + 30]
        df_p['종목명'] = '풋옵션'

        df_f.rename(columns={'이론가': '이론가/행사가'}, inplace=True)
        df_c.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
        df_p.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
        # df = ex.fetch_closed_roder(side='매수',ticker='005930')

        # 공통된 컬럼명 찾기
        common_columns = list(set(df_f.columns).intersection(df_c.columns).intersection(df_p.columns))

        # 공통된 컬럼명만 추출하여 새로운 데이터프레임 생성
        df_f_common = df_f[common_columns]
        df_c_common = df_c[common_columns]
        df_p_common = df_p[common_columns]

        # 구분 표시 행 생성 함수
        def create_separator_row(columns):
            return pd.DataFrame({col: '===' for col in columns}, index=[0])

        # 각 데이터프레임에 구분 행 추가
        df1_with_separator = pd.concat([df_f_common, create_separator_row(common_columns)], ignore_index=True)
        df2_with_separator = pd.concat([df_c_common, create_separator_row(common_columns)], ignore_index=True)
        df3_with_separator = pd.concat([df_p_common, create_separator_row(common_columns)], ignore_index=True)

        # 모든 데이터프레임을 합치기
        df_combined = pd.concat([df1_with_separator, df2_with_separator, df3_with_separator], ignore_index=True)

        if not df_c_weekly.empty and not df_p_weekly.empty:
            if self.COND_MRKT == "WKM":
                yoil = '월'
            elif self.COND_MRKT == "WKI":
                yoil = '목'
            else:
                yoil = '만기'

            df_c_weekly = df_c_weekly[df_c_weekly['행사가'] > 현재가 - 30]
            df_c_weekly = df_c_weekly[df_c_weekly['행사가'] < 현재가 + 30]
            df_c_weekly['종목명'] = '콜'+'_위클리_'+yoil

            df_p_weekly = df_p_weekly[df_p_weekly['행사가'] > 현재가 - 30]
            df_p_weekly = df_p_weekly[df_p_weekly['행사가'] < 현재가 + 30]
            df_p_weekly['종목명'] = '풋'+'_위클리_'+yoil

            df_c_weekly.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
            df_p_weekly.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
            df_c_weekly_common = df_c_weekly[common_columns]
            df_p_weekly_common = df_p_weekly[common_columns]
            df4_with_separator = pd.concat([df_c_weekly_common, create_separator_row(common_columns)], ignore_index=True)
            df5_with_separator = pd.concat([df_p_weekly_common, create_separator_row(common_columns)], ignore_index=True)
            df_combined = pd.concat([df_combined, df4_with_separator, df5_with_separator], ignore_index=True)

        df_combined = df_combined[['종목코드', '현재가', '이론가/행사가', '거래량', '전일대비', '매수호가', '매도호가', '종목명']]
        # 결과 출력
        self.set_table_make(self.QT_tickers, df_combined)
        return df_combined

    def select_market(self):  # 국내시장인지 코인인지 선택합니다.
        self.set_table_make(self.QT_trade_open, pd.DataFrame())
        self.set_table_make(self.QT_trade_closed, pd.DataFrame())
        self.QLE_stg.clear()
        if self.QCB_market.currentText() == '국내주식' :
            self.QTE_stg_buy.clear()
            self.QTE_stg_sell.clear()
            stg_file = 'DB/stg_stock.db'
            con_db = sqlite3.connect('DB/DB_stock.db')
            self.df_stock_info = pd.read_sql(f"SELECT * FROM 'stocks_info'", con_db).set_index('종목코드')
            # con_info.close()
            df_qt_stocks = self.df_stock_info[self.df_stock_info['PER']!=0] #per 0 제외
            df_qt_stocks = df_qt_stocks[df_qt_stocks['시장구분']!='ETF'] #per 0 제외
            df_qt_stocks = df_qt_stocks[['종목명','시장구분','업종','BPS','PER','PBR' ,'EPS','DIV','DPS']]
            # 종목 맨 앞에 코스피200이 와야됨 왜냐하면
            self.QT_tickers.clear()
            self.set_table_make(self.QT_tickers,df_qt_stocks)

        elif self.QCB_market.currentText() == '국내선옵':
            self.QTE_stg_buy.clear()
            self.QTE_stg_sell.clear()
            stg_file = 'DB/stg_futopt.db'
            # ex = common_def.make_exchange_kis('실전주식') #모의투자는 휴장일정보를 지원하지 않음
            # today = datetime.today()
            # res = ex.check_holiday_domestic_stock(today.strftime("%Y%m%d"))
            # output = res['output']
            # self.list_close_day = [x['bass_dt'] for x in output if x['opnd_yn'] == 'N']  # 개장일
            # list_duple_day = [x['bass_dt'] for x in output if x['opnd_yn'] == 'N' and (
            #             x['wday_dvsn_cd'] == '02' or x['wday_dvsn_cd'] == '05')]  # 옵션만기일(월,목)과 휴일이 겹치는날
            self.ex_kis = common_def.make_exchange_kis('모의선옵')
            self.QT_tickers.clear()
            self.df_tickers = self.display_futopt()
            self.QCB_chart_bong_detail.setCurrentText('1분봉')
            self.QCB_chart_bong_detail.setEnabled(False)
            self.QCB_chart_bong.setCurrentText('5분봉')

        elif self.QCB_market.currentText() == '코인':
            self.QTE_stg_buy.clear()
            self.QTE_stg_sell.clear()
            stg_file = 'DB/stg_bybit.db'
            self.ex_bybit,self.ex_pybit  = common_def.make_exchange_bybit(False)  # do_trade에서 exchange를 넘겨주는 방법은 안될까
            fetch_tickers = self.ex_bybit.fetch_tickers()
            df_tickers = self.bybit_set_tickers(fetch_tickers)
            df_tickers = df_tickers[df_tickers.index.str[-10:]=='/USDT:USDT']
            # df_tickers.index = [x[:-10] for x in df_tickers.index.tolist() if x[-4:] == 'USDT' and x[:6] != 'GASDAO']  #GASDAO 종목 삭제
            df_tickers.index = [x[:-10] for x in df_tickers.index.tolist() ]
            df_tickers['종목코드'] = df_tickers.index
            self.df_tickers = df_tickers[['종목코드','quoteVolume','volume24h','percentage','change']]
            self.QT_tickers.clear()
            self.COND_MRKT = None
            self.set_table_make(self.QT_tickers,self.df_tickers)

        else:
            stg_file = ''

        if not self.QCB_market.currentText() == '':
            self.conn_stg = sqlite3.connect(stg_file)
            cursor = self.conn_stg.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_list = np.concatenate(cursor.fetchall()).tolist()
            # if 'stg' in table_list:
            self.df_stg = pd.read_sql(f"SELECT * FROM 'stg'", self.conn_stg).set_index('index')
            # if self.df_stg.empty:
            if self.QCB_market.currentText() == '코인':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {'4시간봉':10}\n"
                                         "방향 = 'long'\n"
                                         "초기자금 = 100\n"
                                         "레버리지 = 3\n"
                                         "분할매수 = []\n"
                                         "분할매도 = []\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         # "매수 = False\n"
                                         "")
                self.QTE_stg_sell.setText("매도가 = \n"
                                         # "매도=False\n"
                                         "")
            elif self.QCB_market.currentText() == '국내주식':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {일봉:365}\n"
                                         "초기자금 = 1000000\n"
                                         "분할매수 = []\n"
                                         "분할매도 = []\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         # "매수 = False\n"
                                         "")
                self.QTE_stg_sell.setText("매도가 = \n"
                                         # "매도 = False\n"
                                         "")
            elif self.QCB_market.currentText() == '국내선옵':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {'5분봉':5}\n"
                                         "방향 = 'long'\n"
                                         "초기자금 = 10000000\n"
                                         "분할매수 = []\n"
                                         "분할매도 = []\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         # "매수 = False\n"
                                         "")
                self.QTE_stg_sell.setText("매도가 = \n"
                                         # "매도 = False\n"
                                         "")
            self.df_old = pd.DataFrame(columns=['ticker', '진입시간', '진입가', '주문수량',
                                                '청산가', '청산시간', '상태', 'id', '현재봉시간'])
            # else:
            #     self.df_old = self.df_stg[['ticker', '진입시간', '진입가', '주문수량',
            #                                '청산가', '청산시간', '상태', 'id', '상세봉', '현재봉시간']]
            self.df_stg.sort_values('table', inplace=True)
            self.reset_stg_table()

            self.QCB_stgs.clear()
            if not self.df_stg.empty:
                self.QCB_stgs.addItems(self.df_stg['전략명'].tolist())




            # 리얼 차트를 위한
            list_ticker = self.df_stg['ticker'].tolist()
            list_ticker = list(set(list_ticker))
            # list_ticker.insert(0, '전체')
            # self.QCB_chart_ticker.clear()
            # self.QCB_chart_ticker.addItems(list_ticker)
            # if list_ticker:
                # self.QCB_chart_ticker.setCurrentText(list_ticker[0])
        print(f"{self.QCB_market.currentText()} 선택")
    def save_stg(self):
        global 분봉1, 분봉3, 분봉5, 분봉15, 분봉30, 분봉60, 시간봉4, 일봉, 주봉, 월봉
        global long, short
        분봉1 = '1분봉'  # 시가CN(bong,pre) bong자리에 넣기 위함 변수로 숫자가 앞에 올 수는 없기 때문
        분봉3 = '3분봉'
        분봉5 = '5분봉'
        분봉15 = '15분봉'
        분봉30 = '30분봉'
        분봉60 = '60분봉'
        시간봉4 = '4시간봉'
        일봉 = '일봉'
        주봉 = '주봉'
        월봉 = '월봉'
        long = 'long'
        short = 'short'
        self.BTN_effect(self.QPB_save_stg)

        locals_dict_buy = {}
        self.QTE_stg_buy.toPlainText()
        stg_name = self.QLE_stg.text()
        global 등락률상위, 거래량상위, 거래대금상위, 시가총액상위, 시간외잔량상위, 체결강도상위, 관심종목등록상위
        등락률상위 = '등락률상위'
        거래량상위 = '거래량상위'
        거래대금상위 = '거래대금상위'
        시가총액상위 = '시가총액상위'
        시간외잔량상위 = '시간외잔량상위'
        체결강도상위 = '체결강도상위'
        관심종목등록상위 = '관심종목등록상위'
        global 콜옵션, 풋옵션, 콜옵션_위클리, 풋옵션_위클리
        콜옵션 = '콜옵션'
        풋옵션 = '풋옵션'
        콜옵션_위클리 = '콜옵션_위클리'
        풋옵션_위클리 = '풋옵션_위클리'
        if self.QCB_market.currentText() == '국내주식' and self.QLE_stg.text() != '':
            object = self.QTE_stg_buy.toPlainText().split("\n", 1)[0]  # 첫줄 읽기 추출
            exec(object, None, locals_dict_buy)
            object = locals_dict_buy.get('진입대상')
            bong = self.QTE_stg_buy.toPlainText().split("\n", 2)[1]  # 둘줄 읽기 추출
            exec(bong, None, locals_dict_buy)
            bong = locals_dict_buy.get('봉')
            bet = self.QTE_stg_buy.toPlainText().split("\n", 3)[2]  # 넷줄 읽기 추출
            exec(bet, None, locals_dict_buy)
            bet = locals_dict_buy.get('초기자금')
            division_buy = self.QTE_stg_buy.toPlainText().split("\n", 4)[3]  # 셋줄 읽기 추출
            exec(division_buy, None, locals_dict_buy)
            division_buy = locals_dict_buy.get('분할매수')
            division_sell = self.QTE_stg_buy.toPlainText().split("\n", 5)[4]  # 셋줄 읽기 추출
            exec(division_sell, None, locals_dict_buy)
            division_sell = locals_dict_buy.get('분할매도')
            direction = long
            leverage = 1
            # bong_detail = 분봉1
            if type(object) == list:
                trade_market = '주식'
                ticker = ''
            else:
                trade_market = self.df_stock_info.loc[object, '시장구분']
                ticker = object

        elif self.QCB_market.currentText() == '국내선옵' and self.QLE_stg.text() != '':
            object = self.QTE_stg_buy.toPlainText().split("\n", 1)[0]  # 첫줄 읽기 추출
            exec(object, None, locals_dict_buy)
            object = locals_dict_buy.get('진입대상')
            bong = self.QTE_stg_buy.toPlainText().split("\n", 2)[1]  # 둘줄 읽기 추출
            exec(bong, None, locals_dict_buy)
            bong = locals_dict_buy.get('봉')
            direction = self.QTE_stg_buy.toPlainText().split("\n", 3)[2]  # 셋줄 읽기 추출
            exec(direction, None, locals_dict_buy)
            direction = locals_dict_buy.get('방향')
            bet = self.QTE_stg_buy.toPlainText().split("\n", 4)[3]  # 셋줄 읽기 추출
            exec(bet, None, locals_dict_buy)
            bet = locals_dict_buy.get('초기자금')
            division_buy = self.QTE_stg_buy.toPlainText().split("\n", 5)[4]  # 셋줄 읽기 추출
            exec(division_buy, None, locals_dict_buy)
            division_buy = locals_dict_buy.get('분할매수')
            division_sell = self.QTE_stg_buy.toPlainText().split("\n", 6)[5]  # 셋줄 읽기 추출
            exec(division_sell, None, locals_dict_buy)
            division_sell = locals_dict_buy.get('분할매도')
            # bong_detail = 분봉1
            leverage = 1
            if type(object) == list or type(object) == dict :
                trade_market = '조건검색'
                ticker = ''
            else:
                trade_market = '선물' if object[:1] == '1' else '콜옵션' if object[:1] == '2' else '풋옵션' if object[:1] == '3' else '스프레드'
                ticker = object


        elif self.QCB_market.currentText() == '코인' and self.QLE_stg.text() != '':
            object = self.QTE_stg_buy.toPlainText().split("\n", 1)[0]  # 첫줄 읽기 추출
            exec(object, None, locals_dict_buy)
            object = locals_dict_buy.get('진입대상')
            bong = self.QTE_stg_buy.toPlainText().split("\n", 2)[1]  # 둘줄 읽기 추출
            exec(bong, None, locals_dict_buy)
            bong = locals_dict_buy.get('봉')
            direction = self.QTE_stg_buy.toPlainText().split("\n", 3)[2]
            exec(direction, None, locals_dict_buy)
            direction = locals_dict_buy.get('방향')
            bet = self.QTE_stg_buy.toPlainText().split("\n", 4)[3]
            exec(bet, None, locals_dict_buy)
            bet = locals_dict_buy.get('초기자금')
            leverage = self.QTE_stg_buy.toPlainText().split("\n", 5)[4]
            exec(leverage, None, locals_dict_buy)
            leverage = locals_dict_buy.get('레버리지')
            division_buy = self.QTE_stg_buy.toPlainText().split("\n", 6)[5]  # 셋줄 읽기 추출
            exec(division_buy, None, locals_dict_buy)
            division_buy = locals_dict_buy.get('분할매수')
            division_sell = self.QTE_stg_buy.toPlainText().split("\n", 7)[6]  # 셋줄 읽기 추출
            exec(division_sell, None, locals_dict_buy)
            division_sell = locals_dict_buy.get('분할매도')
            if type(object) == dict:
                ticker = ''
            else:
                ticker = object
            trade_market = 'bybit'


        if (stg_name in self.df_stg.index.tolist()) and stg_name != '':
            print(f'{trade_market} - {stg_name} 기존전략에 덮어쓰기 {bet= }')
            if self.df_stg.loc[stg_name, 'ticker'] != '' and type(object) == list and self.df_stg.loc[stg_name, '상태'] != '대기':
                ticker = self.df_stg.loc[stg_name, 'ticker']
            elif self.df_stg.loc[stg_name, '상태'] == '대기' and type(object) == list:
                ticker = ''
            self.df_stg.loc[stg_name, '진입전략'] = common_def.replace_tabs_with_spaces(self.QTE_stg_buy.toPlainText())
            self.df_stg.loc[stg_name, '청산전략'] = common_def.replace_tabs_with_spaces(self.QTE_stg_sell.toPlainText())

            if type(object) == list or type(object) == dict:
                object = json.dumps(object, ensure_ascii=False)
            self.df_stg.loc[stg_name, '진입대상'] = object
            self.df_stg.loc[stg_name, 'ticker'] = ticker
            self.df_stg.loc[stg_name, '봉'] = list(bong.keys())[0]  # 딕셔너리로 받는 봉정보의 키값
            self.df_stg.loc[stg_name, '봉제한'] = bong[list(bong.keys())[0]]  # 딕셔너리로 받는 봉정보의 밸류값
            self.df_stg.loc[stg_name, 'market'] = trade_market
            self.df_stg.loc[stg_name, '방향'] = direction
            self.df_stg.loc[stg_name, '초기자금'] = bet
            self.df_stg.loc[stg_name, '배팅금액'] = bet
            self.df_stg.loc[stg_name, '레버리지'] = leverage
            self.df_stg.loc[stg_name, '전략명'] = stg_name
            self.df_stg.loc[stg_name, '잔고'] = bet # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '상태'] = '대기'
            self.df_stg.loc[stg_name, '청산금액'] = 0
            self.df_stg.loc[stg_name, '수익금'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '누적수익금'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '최고수익률'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '최저수익률'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '수익률'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '진입가'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '주문수량'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '진입수수료'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '체결수량'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '보유수량'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '매입금액'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '평가금액'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '매입율'] = 0 # 나중에 전략명은 그대로에 전략만 변경될 경우 주석처리 할 것
            self.df_stg.loc[stg_name, '분할매수'] = json.dumps(division_buy) # 5. 리스트를 JSON 문자열로 변환하여 삽입
            self.df_stg.loc[stg_name, '분할매도'] = json.dumps(division_sell) # 5. 리스트를 JSON 문자열로 변환하여 삽입
            self.df_stg.loc[stg_name, '분할상태'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할진입가'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할청산가'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할주문수량'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할보유수량'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할매입금액'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할청산금액'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할진입수수료'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할id'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할평가금액'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할진입시간'] = json.dumps([])
            self.df_stg.loc[stg_name, '분할청산시간'] = json.dumps([])
            self.df_stg.loc[stg_name, '매도전환'] = "False"
            self.df_stg.loc[stg_name, '진입신호시간'] = json.dumps([])
            self.df_stg.loc[stg_name, '청산신호시간'] = json.dumps([])
        elif not stg_name in self.df_stg.index.tolist() and self.QLE_stg.text() != '':
            print(f'{trade_market} - {stg_name} 새로운전략 저장 {bet= }')
            if type(object) == list  or type(object) == dict:
                object = json.dumps(object, ensure_ascii=False)
            dict_data = {'전략명':self.QLE_stg.text(),'market': trade_market, '진입대상': object, 'ticker': ticker,
                         '봉': list(bong.keys())[0], '방향': direction, '초기자금': bet,'배팅금액': bet,  '매입금액': 0, '청산금액': 0,
                         '레버리지': leverage, '진입전략': common_def.replace_tabs_with_spaces(self.QTE_stg_buy.toPlainText()),
                         '청산전략': common_def.replace_tabs_with_spaces(self.QTE_stg_sell.toPlainText()), '현재가': 0, '진입가': 0,
                         '주문수량': 0, '체결수량':0, '보유수량':0, '진입시간': '', '청산가': 0, '청산시간': '', '수익률': 0,
                         '최고수익률': 0, '최저수익률': 0, '수익금': 0, '평가금액': bet, '상태': '대기', 'id': '', '수수료': 0,
                         '진입수수료': 0, '승률(win/all)': '0/0(0%)', '누적수익금': 0, '잔고': bet,'매입율':0,
                         # '상세봉':bong_detail ,
                         '봉제한':bong[list(bong.keys())[0]],  '현재봉시간': '', 'table': 0,
                         '분할매수':json.dumps(division_buy),
                         '분할매도':json.dumps(division_sell),'분할상태':json.dumps([]),'분할진입가':json.dumps([]),
                         '분할청산가':json.dumps([]),'분할주문수량':json.dumps([]),'분할보유수량':json.dumps([]),
                         '분할매입금액':json.dumps([]),'분할청산금액':json.dumps([]),'분할진입수수료':json.dumps([]),
                         '분할id':json.dumps([]),'분할진입시간':json.dumps([]),'분할청산시간':json.dumps([]),'매도전환':"False",
                         '분할평가금액':json.dumps([]),'진입신호시간': json.dumps([]), '청산신호시간': json.dumps([])}
            self.df_stg.loc[stg_name] = dict_data
        elif self.QLE_stg.text() == '':
            print(f"{self.QLE_stg.text()} 전략명이 비어있음")
            pass
        else:
            print(f'{trade_market} - {stg_name} 저장 에러')
            raise
        ##
        # print("=======================================")
        # print(f"{stg_name= }   {ticker=}   {len(division_buy)= }")
        # print(f"{stg_name= }   {ticker=}   {len(division_sell)= }")
        if not self.QLE_stg.text() == '':
            if len(division_buy) > 0 or len(division_sell) > 0: #분할일 경우
                list_state = ['대기' for x in range(len(division_buy))]
                # print(f"{list_state=}")
                # print(f"{type(list_state)=}")
                division_zero = [0 for x in range(len(division_buy))]
                division_zero_sell = [0 for x in range(len(division_sell))]
                division_id = ["" for x in range(len(division_buy))]
                self.df_stg.loc[stg_name, '분할상태'] = json.dumps(list_state,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할진입가'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할청산가'] = json.dumps(division_zero_sell)
                self.df_stg.loc[stg_name, '분할주문수량'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할보유수량'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할매입금액'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할청산금액'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할진입수수료'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할id'] = json.dumps(division_id,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할진입시간'] = json.dumps(division_id,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할청산시간'] = json.dumps(division_id,ensure_ascii=False)
                # self.df_stg.loc[stg_name, '분할체결수량'] = json.dumps(division_price,ensure_ascii=False)

        list_QCB_text = [self.QCB_stg1.currentText(),
                         self.QCB_stg2.currentText(),
                         self.QCB_stg3.currentText(),
                         self.QCB_stg4.currentText(),
                         self.QCB_stg5.currentText(),
                         self.QCB_stg6.currentText(),
                         self.QCB_stg7.currentText(),
                         self.QCB_stg8.currentText()]

        ####### 제대로 table이 저장이 안될 때가 있어서 추가
        self.df_stg['table'] = 0


        # # 진입대상 전체의 경우 전략 1개당 1개의 QCB_stg 할당할 때
        for i, QCB_stg in enumerate(list_QCB_text):
            if not QCB_stg == '':
                self.df_stg.loc[QCB_stg, 'table'] = i + 1
            elif QCB_stg == '':
                stg = self.df_stg[self.df_stg['table'] == i + 1]
                if not stg.empty:
                    stg = (self.df_stg[self.df_stg['table'] == i + 1]).index[0]
                    print(i, stg)
                    self.df_stg.loc[stg, 'table'] = 0

        # print(self.df_stg[['분할상태','분할진입가','분할청산가','분할주문수량','분할보유수량','분할매입금액','분할청산금액','분할진입수수료','분할id','분할진입시간','분할청산시간']])
        # # 진입대상 전체의 경우 전략 1개당 복수의 QCB_stg 할당할 때 (동일 전략으로 여러종목에 배팅하고싶을 때)
        # 동일전략 복수 종목을 시도해보려했으나 trade_numpy에서 값을 갖고오는게 전략, 열 이라 인덱스를 테이블 번호나 이런걸로 바꿔야됨
        # print(list_QCB_text)
        # list_duplicate = []
        # for i, QCB_stg in enumerate(list_QCB_text):
        #     print(f'     {i=}')
        #     if not QCB_stg == '':
        #         if QCB_stg in list_duplicate:
        #             df_new = self.df_stg[self.df_stg['전략명']==QCB_stg] #전략명이 같은 행을 추출
        #             df_new = df_new[:1] # 같은전략을 3개 이상 사용할 수 있으니 제일 위에 행만 추출
        #             print(df_new)
        #             print(df_new[0])
        #             self.df_stg = pd.concat([self.df_stg,df_new[0]])
        #         else:
        #             self.df_stg.loc[QCB_stg, 'table'] = i + 1
        #             list_duplicate.append(QCB_stg)
        #             print('미중복')
        #     elif QCB_stg == '':
        #         stg = self.df_stg[self.df_stg['table'] == i + 1]
        #         print('elif QCB_stg == '':')
        #         print(stg)
        #         if not stg.empty:
        #             stg = (self.df_stg[self.df_stg['table'] == i + 1]).index[0]
        #             print('if not stg.empty:')
        #             print(stg)
        #             print(i, stg)
        #             self.df_stg.loc[stg, 'table'] = 0
        #     print('===========')
        # self.df_stg
        # print(self.df_stg)

        self.QCB_stgs.clear()
        self.QCB_stgs.addItems(self.df_stg.index.tolist())
        self.df_stg.sort_values('table',inplace=True)
        try:
            self.df_stg.to_sql('stg', self.conn_stg, if_exists='replace')
        except:
            # 열별로 저장 시도
            for column in self.df_stg.columns:
                try:
                    temp_df = self.df_stg[[column]]  # 문제 열만 선택
                    temp_df.to_sql('temp_table', self.conn_stg, if_exists='replace', index=False)
                    print(f"Column '{column} {type(column)}' saved successfully.")
                except Exception as e:
                    print(f"Error with column '{column}  {type(column)}': {e}")
        self.reset_stg_table()

    def del_stg(self):
        if self.QCB_stgs.currentText() != '':
            self.df_stg = pd.read_sql(f"SELECT * FROM 'stg'", self.conn_stg).set_index('index')
            self.df_stg.drop([f'{self.QCB_stgs.currentText()}'], inplace=True)
            self.QCB_stgs.clear()
            self.QCB_stgs.addItems(self.df_stg.index.tolist())
            self.reset_stg_table()
            self.df_stg.to_sql('stg', self.conn_stg, if_exists='replace')

    def reset_stg_table(self):
        stgs = self.df_stg.index.tolist()
        stgs.insert(0, '')
        self.QCB_stg1.clear()
        self.QCB_stg1.addItems(stgs)
        self.QCB_stg2.clear()
        self.QCB_stg2.addItems(stgs)
        self.QCB_stg3.clear()
        self.QCB_stg3.addItems(stgs)
        self.QCB_stg4.clear()
        self.QCB_stg4.addItems(stgs)
        self.QCB_stg5.clear()
        self.QCB_stg5.addItems(stgs)
        self.QCB_stg6.clear()
        self.QCB_stg6.addItems(stgs)
        self.QCB_stg7.clear()
        self.QCB_stg7.addItems(stgs)
        self.QCB_stg8.clear()
        self.QCB_stg8.addItems(stgs)

        stgs = self.df_stg.index.tolist()
        stgs.insert(0, '전략선택')
        # self.QCB_stg_current.clear()
        # self.QCB_stg_current.addItems(stgs)
        if self.df_stg.empty:
            print('실행전략 비어있음')
            # self.qtable_open(pd.DataFrame(columns=['market', '전략명', 'ticker', '수익률', '최고수익률', '최저수익률',
            #                                        '진입가', '현재가', '상태', '주문수량', '승률(win/all)', '수익금', '진입시간']))

        else:
            self.df_trade = self.df_stg[self.df_stg['table'] != 0]
            list_table = self.df_trade['table'].tolist()
            if list_table == []:
                pass
                # self.qtable_open(pd.DataFrame())
            else:
                self.qtable_open(self.df_trade)

                self.df_history = pd.read_sql(f"SELECT * FROM 'history'", self.conn_stg).set_index('index')
                self.qtable_closed(self.df_history)

                for i in list_table:
                    if i == 1:
                        self.QCB_stg1.setCurrentText(self.df_trade[self.df_trade['table'] == 1].index[0])
                    if i == 2:
                        self.QCB_stg2.setCurrentText(self.df_trade[self.df_trade['table'] == 2].index[0])
                    if i == 3:
                        self.QCB_stg3.setCurrentText(self.df_trade[self.df_trade['table'] == 3].index[0])
                    if i == 4:
                        self.QCB_stg4.setCurrentText(self.df_trade[self.df_trade['table'] == 4].index[0])
                    if i == 5:
                        self.QCB_stg5.setCurrentText(self.df_trade[self.df_trade['table'] == 5].index[0])
                    if i == 6:
                        self.QCB_stg6.setCurrentText(self.df_trade[self.df_trade['table'] == 6].index[0])
                    if i == 7:
                        self.QCB_stg7.setCurrentText(self.df_trade[self.df_trade['table'] == 7].index[0])
                    if i == 8:
                        self.QCB_stg8.setCurrentText(self.df_trade[self.df_trade['table'] == 8].index[0])


    def selectedCombo_stg(self, QCB):
        stg_name = QCB.currentText()
        self.QLE_stg.setText(stg_name)
        self.df_stg = pd.read_sql(f"SELECT * FROM 'stg'", self.conn_stg).set_index('index')
        if stg_name == '' or stg_name == '전략선택':
            self.QCB_stg1.setStyleSheet("background-color: ;")
            self.QCB_stg2.setStyleSheet("background-color: ;")
            self.QCB_stg3.setStyleSheet("background-color: ;")
            self.QCB_stg4.setStyleSheet("background-color: ;")
            self.QCB_stg5.setStyleSheet("background-color: ;")
            self.QCB_stg6.setStyleSheet("background-color: ;")
            self.QCB_stg7.setStyleSheet("background-color: ;")
            self.QCB_stg8.setStyleSheet("background-color: ;")
            # self.QCB_stg_current.setStyleSheet("background-color: ;")
            QCB.setStyleSheet("selection-color: yellow;")
            self.QTE_stg_buy.clear()
            self.QTE_stg_sell.clear()
        else:
            self.QCB_stg1.setStyleSheet("background-color: ;")
            self.QCB_stg2.setStyleSheet("background-color: ;")
            self.QCB_stg3.setStyleSheet("background-color: ;")
            self.QCB_stg4.setStyleSheet("background-color: ;")
            self.QCB_stg5.setStyleSheet("background-color: ;")
            self.QCB_stg6.setStyleSheet("background-color: ;")
            self.QCB_stg7.setStyleSheet("background-color: ;")
            self.QCB_stg8.setStyleSheet("background-color: ;")
            # self.QCB_stg_current.setStyleSheet("background-color: ;")
            # print(self.df_stg)
            text_stg_buy = self.df_stg.loc[stg_name, '진입전략']
            text_stg_sell = self.df_stg.loc[stg_name, '청산전략']
            self.QTE_stg_buy.clear()
            self.QTE_stg_sell.clear()
            self.QTE_stg_buy.setText(text_stg_buy)
            self.QTE_stg_sell.setText(text_stg_sell)
            QCB.setStyleSheet("selection-color: yellow;")


    def view_chart(self):
        ticker = self.QLE_chart_ticker.text()
        bong = self.QCB_chart_bong.currentText()
        bong_detail = self.QCB_chart_bong_detail.currentText()
        market = self.QCB_market.currentText()
        list_ticker = self.df_tickers['종목코드'].tolist()
        if ticker != '':
            self.chart_thread = self.real_chart
            duration = 1 if self.QCB_chart_duration.currentText() == '기간(일)' else int(self.QCB_chart_duration.currentText())
            self.chart_thread.make_init_data(market,ticker,bong,bong_detail,duration,list_ticker)
            self.chart_thread.start()
        else:
            print('ticker 확인')

    def view_chart_stop(self):
        if self.chart_thread is not None:
            self.chart_thread.stop()
            self.chart_thread = None

    def effect_start(self, light):
        if light == True:
            self.QPB_start.setStyleSheet("background-color: #fa3232;")
            self.QL_ror.setText('0')
            self.df_stg

            print(self.df_history)
        if light == False:
            self.QPB_start.setStyleSheet("background-color: #cccccc;")

    def do_trade(self):
        self.light_start = False
        self.df_stg = pd.read_sql(f"SELECT * FROM 'stg'", self.conn_stg).set_index('index')
        self.df_stg = self.set_table_modify(self.QT_trade_open, self.df_stg)
        # self.df_instock = pd.read_sql(f"SELECT * FROM 'instock'", self.conn_stg).set_index('index')
        list_tickers = self.df_tickers['종목코드'].tolist()
        print(f"{list_tickers= }")
        self.thread = ATOM_trade_numpy.Trade_np(self, self.QCB_market.currentText(), self.QCB_simul, self.df_stg,
                                                self.QCB_chart_duration.currentText(),self.QCB_tele.isChecked(),
                                                list_tickers, self.COND_MRKT)
        self.thread.start()
        # self.QPB_start.setText({True: "정지", False: "시작"}[self.thread.status])
        self.thread.qt_open.connect(self.qtable_open)
        self.thread.qt_closed.connect(self.qtable_closed)
        self.thread.val_light.connect(self.effect_start)
        # self.thread.val_instock.connect(self.save_instock)

    @pyqtSlot()
    def slot_clicked_button(self):
        """
        사용자정의 슬롯
        쓰레드의 status 상태 변경
        버튼 문자 변경
        쓰레드 재시작
        """
        self.thread.toggle_status()
        # self.pb.setText({True: "Pause", False: "Resume"}[self.th.status])
        self.QPB_start.setStyleSheet("background-color: #cccccc;")
        # self.timer.stop()

    def qtable_open(self, df):
        df_compare = df[['ticker', '진입시간', '청산가', '청산시간', '상태', '분할상태', '현재봉시간','매입금액', '잔고', '분할보유수량']]
        if not self.df_old.equals(df_compare):
            self.df_stg = df.combine_first(self.df_stg)
            self.df_stg.sort_values('table', inplace=True)

            # self.df_stg.to_sql('stg', self.conn_stg, if_exists='replace')

            #저장 시 에러날 때는 아래 구문 사용하여 확인

            try:
                self.df_stg.to_sql('stg', self.conn_stg, if_exists='replace')
            except:
                list_col = self.df_stg.columns.tolist()
                print('tab_trade  qtable_open : ')
                print(f"{list_col= }")
                for i,col in enumerate(list_col):
                    df_copy = self.df_stg[[col]]
                    self.df_stg = self.df_stg.drop(col,axis=1)

                    try:
                        self.df_stg.to_sql('stg', self.conn_stg, if_exists='replace')
                        # time.sleep(1)
                        print('qtable_open 에러----')
                        print(f"{i= }")
                        print(f"{col= }")
                        print(f"{df_copy }")
                        # print(f"{self.df_stg[col].dtype= }")
                        quit()
                    except:
                        pass
            self.df_old = df_compare.copy()

        # df['전략명'] = df.index

        # 분할상태, 분할id, 분할보유수량 이런거 넣으면 ["매수" "매도주문"] 이렇게 쉼표가 빠지면서 에러 됨
        df['상태[분할]'] = df['분할상태'].copy()
        df['보유수량[분할]'] = df['분할보유수량'].copy()
        df_active = df[['market', '전략명', 'ticker', '수익률', '최고수익률', '최저수익률', '진입가', '현재가', '상태', '상태[분할]',
                        '주문수량', '체결수량', '보유수량', '보유수량[분할]', '승률(win/all)', '수익금', '매입금액', '진입수수료',
                        '평가금액', '잔고', '진입시간', '매도전환']].copy()
        df_active['진입가'] = df_active['진입가'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['현재가'] = df_active['현재가'].apply(lambda int_num : "{:,}".format(int_num))
        # df_active['수익금'] = df_active['수익금'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['매입금액'] = df_active['매입금액'].apply(lambda int_num : "{:,}".format(int_num))
        # df_active['평가금액'] = df_active['평가금액'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['잔고'] = df_active['잔고'].apply(lambda int_num : "{:,}".format(int_num))
        # df = df.loc[df['상태'] != '청산'] # 청산 상태가 아닌 행을 저장
        # df_active = df.loc[df['상태'] != '매수주문'] # 매수주문 상태가 아닌 행을 저장
        # df_active['전략명'] = df_active.index
        # df_active = df_active[['market','전략명','ticker','수익률','최고수익률','최저수익률','진입가','현재가','상태','승률(win/all)','수익금','진입시간']]
        self.set_table_make(self.QT_trade_open, df_active)

    def qtable_closed(self, df):
        # df_history = pd.read_sql(f"SELECT * FROM 'history'", self.conn_stg).set_index('index')
        # if self.df_history.empty:
        #     if df.empty:
        #         pass
        #     else:
        #         # df_history = df_history.append(df_closed, ignore_index=False)
        #         self.df_history = pd.concat([self.df_history, df])  # 데이터프레임끼리 위, 아래로 붙이기
        #         self.df_history.to_sql('history', self.conn_stg, if_exists='replace')
        #         self.df_history['전략명'] = self.df_history.index
        #     df_history = self.df_history[['market', '전략명', 'ticker', '수익률', '최고수익률', '최저수익률', '수익금',
        #                                   '누적수익금', '진입가', '청산가', '잔고', '진입시간', '청산시간']]
        #     self.set_table_make(self.QT_trade_closed, df_history)
        #
        # else:
        if df.empty:
            pass
        else:
            # df_history = df_history.append(df_closed, ignore_index=False)
            if not self.df_history.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
                self.df_history = pd.concat([self.df_history, df])  # 데이터프레임끼리 위, 아래로 붙이기
                self.df_history.to_sql('history', self.conn_stg, if_exists='replace')
                self.df_history['전략명'] = self.df_history.index
        df_history = self.df_history[['market', '전략명', 'ticker', '수익률', '최고수익률', '최저수익률', '수익금',
                                      '누적수익금', '진입가', '청산가', '잔고','매입금액','청산금액','수수료', '진입수수료',
                                      '진입시간', '청산시간']]
        df_history = df_history[df_history['청산시간'].str[:10]==datetime.now().date().strftime('%Y-%m-%d')] #오늘 청산한 전략만
        df_history['진입가'] = df_history['진입가'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['청산가'] = df_history['청산가'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['수익금'] = df_history['수익금'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['누적수익금'] = df_history['누적수익금'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['수수료'] = df_history['수수료'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['매입금액'] = df_history['매입금액'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['청산금액'] = df_history['청산금액'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['잔고'] = df_history['잔고'].apply(lambda int_num : "{:,}".format(int_num))
        self.set_table_make(self.QT_trade_closed, df_history)


    def bybit_set_tickers(self,fetch_tickers):
        for ticker in fetch_tickers.keys():
            try:
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
            except:
                pass
            del fetch_tickers[ticker]['info']
        df = pd.DataFrame.from_dict(data=fetch_tickers, orient='index')  # 딕셔너리로 데이터프레임  만들기 키값으로 행이름을 사용
        return df
    def set_table_make(self, table, df):
        table.setSortingEnabled(False)
        table.clear()
        table.setRowCount(len(df.index))
        table.setColumnCount(len(df.columns))
        header = table.horizontalHeader()  # 컬럼내용에따라 길이 자동조절
        for i in range(len(df.columns)):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(df.columns[i]))
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)  # 컬럼내용에따라 길이 자동조절
        # for i in range(len(df.index)):
        #     table.setVerticalHeaderItem(i, QTableWidgetItem(str(df.index[i])[5:10]))
        table.verticalHeader().setVisible(False)  # 인덱스 삭제
        for row in range(len(df.index)):
            for column in range(len(df.columns)):
                val = df.iloc[row, column]
                if type(val) != str and type(val) != float and type(val) != int and val != None and type(val) != bool:
                    val = val.item()  # numpy.float 을 float으로 변환
                it = QTableWidgetItem()
                it.setData(Qt.DisplayRole, val)  # 정렬 시 문자형이 아닌 숫자크기로 바꿈
                table.setItem(row, column, it)
        table.horizontalHeader().setStretchLastSection(True)
        # table.verticalHeader().setStretchLastSection(True)
        table.setSortingEnabled(True)  # 소팅한 상태로 로딩 시 데이터가 이상해져 맨 앞과 뒤에 추가

    def set_table_modify(self, table, df):
        row_count = table.rowCount()
        li_col =[table.horizontalHeaderItem(x).text() for x in range(table.columnCount())]
        for row in range(row_count):
            stg = table.item(row,li_col.index('전략명')).text()
            for i,col in enumerate(li_col):
                val = table.item(row,i).text()
                val = val.replace(',', '')
                if val.isdigit(): #정수일 경우
                    df.loc[stg,col] = int(val)
                else:
                    try:
                        df.loc[stg,col] = float(val) #float일 경우
                    except:
                        df.loc[stg,col] = val #str일 경우
                        pass
        return df

    def cellclick_table(self, num):
        self.QTE_stg_buy.clear()
        self.QTE_stg_sell.clear()
        if num == 1: # table_open 클릭 시
            row = self.QT_trade_open.currentRow()
            stg = self.QT_trade_open.item(int(row), 1).text()
            # print(stg)
        elif num == 2: # table_close 클릭 시
            row = self.QT_trade_closed.currentRow()
            stg = self.QT_trade_closed.item(int(row), 1).text()

        stg_buy = self.df_trade.loc[stg, '진입전략']
        stg_sell = self.df_trade.loc[stg, '청산전략']
        ticker = self.df_trade.loc[stg, 'ticker']
        self.QTE_stg_buy.setText(stg_buy)
        self.QTE_stg_sell.setText(stg_sell)
        self.QLE_stg.setText(stg)
        self.QCB_stgs.setCurrentText(stg)
        # print(ticker)
        # print(type(ticker))
        if ticker != "":
            self.QLE_chart_ticker.setText(ticker)
    # def save_instock(self,df_instock):
    #     df_instock.to_sql('instock',self.conn_stg,if_exists='replace')
    def cellclick_ticker_table(self):
        row = self.QT_tickers.currentRow()
        ticker = self.QT_tickers.item(int(row), 0).text()
        self.QLE_chart_ticker.setText(ticker)
    def cell_doubleclick_ticker_table(self):
        row = self.QT_tickers.currentRow()
        ticker = self.QT_tickers.item(int(row), 0).text()
        bong = self.QCB_chart_bong.currentText()
        bong_detail = self.QCB_chart_bong_detail.currentText()
        bong_since = self.QCB_chart_duration.currentText()
        market = self.QCB_market.currentText()

        ticker_full_name = ticker+'_chart'
        if bong_since == '기간(일)':
            bong_since = 1
        date_old = datetime.now().date() - timedelta(days=int(bong_since))
        stamp_date_old = common_def.datetime_to_stamp(date_old)
        ohlcv = []
        if market == '코인' :
            df = common_def.get_bybit_ohlcv(self.ex_bybit, ohlcv, stamp_date_old, ticker_full_name, ticker, bong,bong_detail)
            df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
            df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
            df['날짜'] = df['날짜'].dt.tz_localize(None)
            df.set_index('날짜', inplace=True)
            df.index = df.index - pd.Timedelta(hours=9)
            df_standard, df = common_def.detail_to_spread(df, bong, bong_detail,False)
            # df.index = df.index + pd.Timedelta(hours=9)
        if market == '국내선옵' :
            ohlcv = self.ex_kis.fetch_futopt_1m_ohlcv(symbol=ticker, limit=int(bong_since))
            df = common_def.get_kis_ohlcv(market, ohlcv)
            df_standard, df = common_def.detail_to_spread(df, bong, bong_detail,False)
        df['매수가'] = np.nan
        df['매도가'] = np.nan
        df['진입신호'] = np.nan
        df['청산신호'] = np.nan

        self.chart_table = tab_chart_table.Window()
        df_chart_table = self.chart_table.df_to_show(df, market)
        self.chart_table.chart_show(market, ticker)
    def cell_doubleclick_trading_table(self,Qtable,df_stg):
        row = Qtable.currentRow()
        ticker = Qtable.item(int(row), 2).text()

        bong = self.QCB_chart_bong.currentText()
        bong_detail = self.QCB_chart_bong_detail.currentText()
        bong_since = self.QCB_chart_duration.currentText()
        market = self.QCB_market.currentText()

        ticker_full_name = ticker+'_chart'
        if bong_since == '기간(일)':
            bong_since = 1
        date_old = datetime.now().date() - timedelta(days=int(bong_since))
        stamp_date_old = common_def.datetime_to_stamp(date_old)
        ohlcv = []
        if market == '코인' :
            df = common_def.get_bybit_ohlcv(self.ex_bybit, ohlcv, stamp_date_old, ticker_full_name, ticker, bong, bong_detail)
            df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
            df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
            df['날짜'] = df['날짜'].dt.tz_localize(None)
            df.set_index('날짜', inplace=True)
            df.index = df.index - pd.Timedelta(hours=9)
            df_standard, df = common_def.detail_to_spread(df, bong, bong_detail,False)
            # df.index = df.index + pd.Timedelta(hours=9)
        if market == '국내선옵' :
            ohlcv = self.ex_kis.fetch_futopt_1m_ohlcv(symbol=ticker, limit=int(bong_since))
            df = common_def.get_kis_ohlcv(market, ohlcv)
            df_standard, df = common_def.detail_to_spread(df, bong, bong_detail,False)


        stg = Qtable.item(int(row), 1).text()
        df_stg = df_stg.loc[df_stg['전략명']==stg]
        list_col = df_stg.columns.tolist()
        dict_buy = {}
        dict_sell = {}
        dict_signal_buy = {}
        dict_signal_sell = {}
        for i, idx in enumerate(df_stg.index):
            buy_time_division = json.loads(df_stg.iloc[i, list_col.index('분할진입시간')])
            buy_price_division = json.loads(df_stg.iloc[i, list_col.index('분할진입가')])
            # if buy_time_division:  # 분할일 경우
            for j, time in enumerate(buy_time_division):
                if time != '':
                    time = time[:-2] + '00'
                    time = common_def.str_to_datetime(time)
                    if buy_price_division[j] != 0:
                        dict_buy[time] = buy_price_division[j]
            # else:
            buy_time = df_stg.iloc[i, list_col.index('진입시간')]
            buy_price = df_stg.iloc[i, list_col.index('진입가')]
            if buy_price != 0:
                buy_time = buy_time[:-2] + '00'
                buy_time = common_def.str_to_datetime(buy_time)
                dict_buy[buy_time] = buy_price


            sell_time_division = json.loads(df_stg.iloc[i, list_col.index('분할청산시간')])
            sell_price_division = json.loads(df_stg.iloc[i, list_col.index('분할청산가')])
            for j, time in enumerate(sell_time_division):
                if time != '':
                    time = time[:-2] + '00'
                    time = common_def.str_to_datetime(time)
                    if sell_price_division[j] != 0:
                        dict_sell[time] = sell_price_division[j]
            sell_time = df_stg.iloc[i, list_col.index('청산시간')]
            sell_price = df_stg.iloc[i, list_col.index('청산가')]
            if sell_price != 0:
                sell_time = sell_time[:-2] + '00'
                sell_time = common_def.str_to_datetime(sell_time)
                dict_sell[sell_time] = sell_price


            buy_time_division = json.loads(df_stg.iloc[i, list_col.index('진입신호시간')])
            print(f"{buy_time_division= }")
            if buy_time_division != None:
                buy_time_division = list(set(buy_time_division))
                for j, time in enumerate(buy_time_division):
                    if time != '':
                        time = time[:-2] + '00'
                        time = common_def.str_to_datetime(time)
                        try:
                            dict_signal_buy[time] = df.loc[time,'종가_1분봉']
                        except:
                            print('차트구간 확인')

            sell_time_division = json.loads(df_stg.iloc[i, list_col.index('청산신호시간')])
            if sell_time_division != None:
                sell_time_division = list(set(sell_time_division))
                for j, time in enumerate(sell_time_division):
                    if time != '':
                        time = time[:-2] + '00'
                        time = common_def.str_to_datetime(time)
                        try:
                            dict_signal_sell[time] = df.loc[time,'종가_1분봉']
                        except:
                            print('차트구간 확인')

        if dict_buy:
            df['매수가'] = df.index.map(dict_buy)
        else:
            df['매수가'] = np.nan
        if dict_sell:
            df['매도가'] = df.index.map(dict_sell)
        else:
            df['매도가'] = np.nan
        if dict_signal_buy:
            df['진입신호'] = df.index.map(dict_signal_buy)
        else:
            df['진입신호'] = np.nan
        if dict_signal_sell:
            df['청산신호'] = df.index.map(dict_signal_sell)
        else:
            df['청산신호'] = np.nan

        # df.to_sql('bt_',sqlite3.connect('DB/bt.db'),if_exists='replace')
        self.chart_table = tab_chart_table.Window()
        df_chart_table = self.chart_table.df_to_show(df, market)
        self.chart_table.chart_show(market, ticker)



    def stamp_to_int(self, stamp_time):
        dt = datetime.fromtimestamp(stamp_time)
        dt = dt.strftime('%Y%m%d%H%M')
        return int(dt)

    def int_to_stamp(self, int_time):
        dt = datetime.strptime(str(int_time), '%Y%m%d%H%M')
        return int(dt.timestamp())

    def int_to_datetime(self, int_time):
        int_time = datetime.strptime(str(int_time), '%Y%m%d%H%M')

    def stamp_to_datetime(self, stamp_time):
        int_time = self.stamp_to_int(stamp_time)
        return datetime.strptime(str(int_time), '%Y%m%d%H%M')
    # def current_hoga_table(self):
    #     self.QL_hoga.setText(f"<span style='color:red'>{list(self.list_betting_hoga_short)}</span>"
    #                          f"<span style='color:crimson'>{self.che_short}</span>"
    #                          f"<span style='color:black'>{self.current_price}</span>"
    #                          f"<span style='color:blue'>{self.che_long}</span>"
    #                          f"<span style='color:green'>{list(self.list_betting_hoga_long)}</span>")
        # self.QL_time.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def keyPressEvent(self, event):
        if self.QLE_chart_ticker.text() != "" and self.QLE_bet.text() != "" and self.QCB_hoga_buy.text() != ""and self.QCB_hoga_sell.text() != "":
            if event.key() == Qt.Key_Escape:
                self.close()
            elif event.key() == Qt.Key_Right: #long 수동 주문
                if self.df_manul.loc['수동매매','상태'] == '대기':
                    pass
                elif self.df_manul.loc['수동매매', '상태'] == '매수':
                    print('매수')
                print('pushed right')
            elif event.key() == Qt.Key_Left: #short 수동 주문
                if self.df_manul.loc['수동매매','상태'] == '대기':
                    pass
                print('pushed left')

            elif event.key() == Qt.Key_Up:  # long 수동 지정가 주문
                if self.df_manul.loc['수동매매','상태'] == '대기':
                    pass
                print('pushed up')

            elif event.key() == Qt.Key_Down: #short 수동 지정가 주문
                if self.df_manul.loc['수동매매','상태'] == '대기':
                    pass
                print('pushed down')






    def BTN_effect(self, QPB):
        QPB.setEnabled(False)
        QTest.qWait(250)
        QPB.setEnabled(True)

if __name__ == "__main__":
    # pg.setConfigOption('background', 'k')
    # pg.setConfigOption('foreground', 'w')

    app = QApplication([])
    main_table = Window()
    main_table.setMinimumSize(600, 400)
    main_table.show()
    app.exec()

    # main()
