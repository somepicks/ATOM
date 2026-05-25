import datetime
import pandas as pd
# import pyupbit
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, \
    QAbstractItemView, QHBoxLayout, QTimeEdit,QDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QTimer, QRegExp, QTime, pyqtSignal
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics, QFont, QColor, QSyntaxHighlighter, QTextCharFormat
import numpy as np
import chart_real
import time
from pprint import pprint
import sqlite3
import ATOM_trade_numpy
import ATOM_WS
import subprocess
import common_def
import json  # 리스트를 문자열로 변환하기 위해 필요
import tab_chart_table
import os
# from pykrx import stock
import schedule
import ATOM_websocket
import pickle
import ctypes
# from ex import df_holiday

pd.set_option('display.max_columns', None)  # 모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment', None)  # SettingWithCopyWarning 경고를 끈다
# import schedule
import KIS

class Window(QMainWindow):
    send_orders = pyqtSignal(dict)
    send_ohlcv = pyqtSignal(dict,list)
    send_chart = pyqtSignal(pd.DataFrame)
    send_trading = pyqtSignal(pd.DataFrame,dict)
    def __init__(self):
        super().__init__()
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m','15분봉': '15m', '30분봉': '30m', '1시간봉': '60m','4시간봉': '4h', '일봉': 'd'}
        self.dict_bong_stamp = {'1분봉': 60, '3분봉': 180, '5분봉': 300, '30분봉': 1800, '4시간봉': 14400, '일봉': 86400}
        self.dict_bong_int = {'1분봉': 1, '3분봉': 3, '5분봉': 5,'15분봉': 15, '30분봉': 30,'1시간봉': 60, '4시간봉': 4*60, '일봉': 24*60}
        # self.dict_bong_reverse = dict(zip(self.dict_bong_int.values(), self.dict_bong_int.keys()))
        # self.dict_bong_time_datetime = {1: datetime.timedelta(minutes=1), 3: datetime.timedelta(minutes=3),
        #                                 5: datetime.timedelta(minutes=5), 15: datetime.timedelta(minutes=15),
        #                                 30: datetime.timedelta(minutes=30),60: datetime.timedelta(minutes=60),
        #                                 240: datetime.timedelta(minutes=240), 1440: datetime.timedelta(days=1)}
        self.set_UI()
        self.init_file()
        self.time_sync()
        self.no_saving_mode()
        self.state_real_chart = False
        self.state_manual_trade = False
        self.fee_upbit_market = 0.05
        self.QPB_start.clicked.connect(self.signal_start)
        self.QPB_stop.clicked.connect(self.slot_clicked_button)
        self.QPB_save_stg.clicked.connect(self.save_stg)
        self.QPB_del_stg.clicked.connect(self.del_stg)
        self.QPB_chart.clicked.connect(self.view_chart)

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
        self.QCB_market.activated[str].connect(self.select_market)
        self.QT_trade_open.cellClicked.connect(lambda: self.cellclick_table("open"))
        self.QT_trade_open.cellDoubleClicked.connect(lambda:self.cell_doubleclick_trading_table(self.QT_trade_open,self.df_stg))
        self.QT_trade_closed.cellClicked.connect(lambda: self.cellclick_table("closed"))
        self.QT_trade_closed.cellDoubleClicked.connect(lambda:self.cell_doubleclick_trading_table(self.QT_trade_closed,self.df_history))
        self.QT_trade_closed.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 더블클릭 시 수정 금지
        self.QT_tickers.cellClicked.connect(lambda: self.cellclick_ticker_table())
        self.QT_tickers.cellDoubleClicked.connect(lambda:self.cell_doubleclick_ticker_table())
        self.QT_tickers.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 더블클릭 시 수정 금지
        self.QPB_API_save.clicked.connect(self.save_setting)
        self.QPB_manual.clicked.connect(self.manual_trade)
        if self.QCB_auto_start.isChecked() == True:
            self.QCB_market.setCurrentText(self.df_set.loc['자동시작마켓','value'])
            self.select_market()
            QTimer.singleShot(2000, self.QPB_start.click) #2초 있다가 스타트버튼 클릭


    def set_UI(self):

        self.setWindowTitle(f'TRADE')
        self.QTE_stg_buy = common_def.CodeEditor()
        self.QTE_stg_sell = common_def.CodeEditor()
        self.QT_trade_closed = QTableWidget()
        self.QT_trade_open = QTableWidget()
        self.QT_tickers = QTableWidget()
        self.QGL_menu = QGridLayout()
        self.QCB_mock = QCheckBox('모의매매')
        self.QCB_mock.setChecked(True)
        self.QCB_market = QComboBox()
        self.list_market = ['', 'bybit', '국내주식','국내선옵','텔레그램','업비트','미국주식']
        self.QCB_market.addItems(self.list_market)
        self.QLE_chart_ticker = QLineEdit()
        self.QLE_bet = QLineEdit()
        self.QCB_hoga_buy = QComboBox()
        self.QCB_hoga_sell = QComboBox()
        self.QPB_manual = QPushButton('수동매매')
        self.QPB_manual.setStyleSheet("background-color: #cccccc;")
        self.QCB_manual_qty = QComboBox()
        self.list_qty = ['수량', '1', '2','3','4','5','6','7', '8','9','10']
        self.QCB_manual_qty.addItems(self.list_qty)
        self.QL_amount = QLabel()
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
        self.QPB_chart = QPushButton('리얼차트')
        self.QPB_chart.setStyleSheet("background-color: #cccccc;")
        self.QCB_chart_bong = QComboBox()
        self.QCB_chart_duration = QComboBox()
        self.QCB_tele = QCheckBox('텔레그램')

        dict_grid = {
            self.QCB_market: self.QCB_mock,
            self.QCB_stg1: self.QCB_stg5,
            self.QCB_stg2: self.QCB_stg6,
            self.QCB_stg3: self.QCB_stg7,
            self.QCB_stg4: self.QCB_stg8,
            self.QPB_start: self.QPB_stop,
            self.QLE_stg: self.QCB_stgs,
            self.QPB_save_stg: self.QPB_del_stg,
            QLabel("■■"):QLabel("■■"),
            self.QPB_manual: self.QCB_manual_qty,
            QLabel('종목명'): self.QLE_chart_ticker,
            QLabel('배팅금액'): self.QLE_bet,
            # QLabel('매수호가'): self.QCB_hoga_buy,
            self.QCB_hoga_buy: self.QCB_hoga_sell,
            QLabel('레버리지'): self.QLE_leverage,
            self.QCB_division_buy: self.QCB_division_sell,
            QLabel('→ : 시장가[롱]'): QLabel('← : 시장가[숏]'),
            QLabel('↑ : 지정가[롱]'): QLabel('↓ : 지정가[숏]'),
            QLabel('매입금액'): self.QL_amount,
            QLabel('수익률'): self.QL_ror,
            QLabel('수익금'): self.QL_benefit,
            QLabel("■■"):QLabel("■■"),
            self.QCB_chart_duration: self.QCB_tele,
            self.QCB_chart_bong: self.QPB_chart,
            # self.QCB_chart_bong_detail: self.QPB_chart_stop
        }

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
        # self.QCB_chart_bong_detail.addItems(list(self.dict_bong.keys()))
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
        self.real_chart = chart_real.Graph(self,'empty')
        QSV_main.addWidget(self.real_chart.chart_main)
        QSV_main.addWidget(QSH_qte_stg)
        QSV_main.addWidget(QSH_table)

        QSH_main = QSplitter(Qt.Horizontal)
        QSH_main.addWidget(QSV_main)
        QSH_main.addWidget(self.QT_tickers)

        self.QCB_auto_start = QCheckBox('자동시작')
        self.QCB_auto_finish = QCheckBox('자동종료')
        self.QTE_finish = QTimeEdit()
        self.QTE_finish.setDisplayFormat("HH:mm:ss")  # 24시간제 포맷
        self.QLE_API = QLineEdit()
        self.QLE_secret = QLineEdit()
        self.QLE_account = QLineEdit()
        self.QLE_id = QLineEdit()
        self.QCB_short_acc_no = QCheckBox('선옵매도계좌:')
        self.QPB_API_save = QPushButton('설정 저장')
        self.QL_standard = QLabel('||')

        QHB_set = QHBoxLayout()
        QHB_set.addWidget(self.QCB_auto_start)
        QHB_set.addWidget(self.QCB_auto_finish)
        QHB_set.addWidget(QLabel('종료시간'))
        QHB_set.addWidget(self.QTE_finish)
        QHB_set.addWidget(QLabel('API:'))
        QHB_set.addWidget(self.QLE_API)
        QHB_set.addWidget(QLabel('SECRET:'))
        QHB_set.addWidget(self.QLE_secret)
        QHB_set.addWidget(QLabel('계좌:'))
        QHB_set.addWidget(self.QLE_account)
        QHB_set.addWidget(QLabel('ID:'))
        QHB_set.addWidget(self.QLE_id)
        QHB_set.addWidget(self.QCB_short_acc_no)
        QHB_set.addWidget(self.QPB_API_save)
        QHB_set.addWidget(self.QL_standard)
        QW_set = QWidget()
        QW_set.setLayout(QHB_set)
        QW_set.setFixedHeight(40)  # 세로 고정 때문에 widget으로 묶어서 보냄

        QVB_main = QVBoxLayout()
        QVB_main.addWidget(QSH_main)
        QVB_main.addWidget(QW_grid)
        QVB_main.addWidget(QW_set)
        QW_main.setLayout(QVB_main)


        # self.QCB_krx.setChecked(True)
        # self.QCB_stg1.activated[str].connect(lambda :self.selectedCombo_stg())
        self.QTE_stg_buy.setTabStopWidth(QFontMetrics(QFont('나눔고딕')).width(' ' * 4))
        self.QTE_stg_sell.setTabStopWidth(QFontMetrics(QFont('나눔고딕')).width(' ' * 4))


        self.highlighter_buy = common_def.PythonHighlighter(self.QTE_stg_buy.document())
        self.highlighter_sell = common_def.PythonHighlighter(self.QTE_stg_sell.document())


        # self.QCB_tele.setChecked(True)


    def init_file(self):
        # list_db_file = ['DB/stg_stock.db', 'DB/stg_bybit.db', 'DB/stg_futopt.db','DB/stg_upbit.db', 'DB/stg_futopt_oversea.db']
        li_col = ['전략명','market', '진입대상','비교대상', 'ticker', '봉', '방향', '초기자금','배팅금액', '매입금액', '레버리지',
                  '진입전략', '청산전략',  '현재가', '주문가','평단가', '주문수량', '보유수량','진입시간', '청산시간',
                  '수익률', '최고수익률', '최저수익률', '수익금', '평가금액', '상태', 'id', '수수료', '수수료율', '승률(win/all)', '누적수익금',
                  '잔고', '봉길이', '현재봉시간', 'table', '분할매수', '분할매도', '분할상태', '분할주문가','매입율','주문방식',
                  # '상세봉','청산가','분할청산가','주문시간',,'청산신호시간'  ,
                  '분할주문수량', '분할보유수량', '분할매입금액', '분할청산금액', '분할수수료', '분할id',
                  '분할평가금액','분할진입시간','분할청산시간','매도전환','주문취소시간']
        db_file = 'DB/stg_trade.db'

        self.conn_stg = sqlite3.connect(db_file)
        cursor = self.conn_stg.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # if not os.path.isfile(db_file):
        try: #파일이 있을 경우
            list_table = np.concatenate(cursor.fetchall()).tolist()
            self.df_set = pd.read_sql(f"SELECT * FROM 'set'", self.conn_stg).set_index('index')
        except: #파일이 없을 경우
            list_table = ['stg_upbit','stg_stock','stg_futopt','stg_bybit','history_upbit','history_stock','history_futopt','history_bybit']
            df = pd.DataFrame(columns=li_col)
            for stg in list_table:
                df.to_sql(stg, self.conn_stg, if_exists='replace')
            self.df_set = pd.DataFrame()
            self.df_trend = pd.DataFrame()
            self.df_set.loc['자동시작','check'] = False
            self.df_set.loc['자동시작마켓','value'] = ''
            self.df_set.loc['모의매매','check'] = True
            self.df_set.loc['자동종료','check'] = False
            self.df_set.loc['자동종료시간','value'] = self.QTE_finish.text()
            self.df_set.loc['텔레그램','check'] = False
            self.df_set.loc['차트기간','value'] = self.QCB_chart_duration.currentText()
            self.df_set.loc['차트봉','value'] = self.QCB_chart_bong.currentText()
            self.df_set.loc['텔레그램_API', 'value'] = ''
            self.df_set.loc['텔레그램_SECRET', 'value'] = ''
            self.df_set.to_sql('set', self.conn_stg, if_exists='replace')
        cursor.close()
        # self.conn_stg.close()

        self.QCB_chart_duration.setCurrentText(self.df_set.loc['차트기간', 'value'])
        self.QCB_chart_bong.setCurrentText(self.df_set.loc['차트봉', 'value'])
        self.QCB_mock.setChecked(bool(self.df_set.loc['모의매매', 'check']))
        self.QCB_tele.setChecked(bool(self.df_set.loc['텔레그램', 'check']))
        self.QCB_auto_start.setChecked(bool(self.df_set.loc['자동시작', 'check']))
        self.QCB_auto_finish.setChecked(bool(self.df_set.loc['자동종료', 'check']))
        time_str = self.df_set.loc['자동종료시간', 'value']
        hours, minutes, seconds = map(int, time_str.split(":"))
        self.QTE_finish.setTime(QTime(hours, minutes, seconds))

        self.df_manul = pd.DataFrame(index=['수동매매'],columns=li_col)

    def display_futopt(self):
        def create_separator_row(columns):
            return pd.DataFrame({col: '===' for col in columns}, index=[0])
        today = datetime.datetime.now()
        ticker_fut, past_expiry_fut, expiry_fut, df_fut,_ = self.dict_option["exchange"].get_expiry_date(target='선물',now_dt=today)
        _, past_expiry_fut_mini, expiry_fut_mini, df_fut_mini,_ = self.dict_option["exchange"].get_expiry_date(target='미니선물',now_dt=today)
        _, past_expiry_opt_week, expiry_opt_week, df_opt, self.cond_mrkt = self.dict_option["exchange"].get_expiry_date(target='위클리옵션',now_dt=today)
        if self.cond_mrkt == '만기주':
            _, past_expiry_opt, expiry_opt, df_opt,_ = self.dict_option["exchange"].get_expiry_date(target='본옵션',now_dt=today)
        # 공통된 컬럼명 찾기
        self.dict_option['cond_mrkt'] = self.cond_mrkt
        common_columns = list(set(df_fut.columns).intersection(df_opt.columns)) #공통된 컬럼 찾기
        df_fut = df_fut[common_columns]
        df_fut_mini = df_fut_mini[common_columns]
        df_opt = df_opt[common_columns]
        if self.dict_option["주간야간"] == '야간':
            night=True
        else:
            night=False
        price = float(self.dict_option["exchange"].fetch_price(list(ticker_fut.keys())[0],night)['현재가'])
        # df_opt = df_opt[(df_opt['이론가/행사가'] < price * 1.2) & (df_opt['이론가/행사가'] > price * 0.8)]
        # df_opt_week = df_opt_week[(df_opt_week['이론가/행사가'] < price * 1.2) & (df_opt_week['이론가/행사가'] > price * 0.8)]

        # df_opt = df_opt.loc[df_opt['현재가']<5]
        # df_opt_week = df_opt_week.loc[df_opt_week['현재가']<5]
        if self.cond_mrkt == '만기주':
            df_call = df_opt[df_opt['종목명'] == '콜옵션']
            df_put = df_opt[df_opt['종목명'] == '풋옵션']
        else:
            df_call = df_opt[df_opt['종목명'] == '위클리콜옵션']
            df_put = df_opt[df_opt['종목명'] == '위클리풋옵션']
        # 거래량 기준 내림차순 정렬 후 상위 20개
        df_call_top = df_call.sort_values(by='거래량', ascending=False).head(19)
        df_call_top = df_call_top.sort_values(by='이론가/행사가', ascending=False)
        df_put_top = df_put.sort_values(by='거래량', ascending=False).head(19)
        df_put_top = df_put_top.sort_values(by='이론가/행사가', ascending=False)

        df1_with_separator = pd.concat([df_fut, create_separator_row(common_columns)], ignore_index=True)
        df2_with_separator = pd.concat([df_fut_mini, create_separator_row(common_columns)], ignore_index=True)
        df3_with_separator = pd.concat([df_call_top, create_separator_row(common_columns)], ignore_index=True)
        df4_with_separator = pd.concat([df_put_top, create_separator_row(common_columns)], ignore_index=True)
        df_combined = pd.concat([df1_with_separator, df2_with_separator,df3_with_separator, df4_with_separator], ignore_index=True)
        df_combined = df_combined[['종목코드', '현재가', '이론가/행사가', '거래량', '전일대비','미결제약정', '종목명', '만기일', '지난만기일']]
        return df_combined

    def select_market(self):  # 국내시장인지 bybit인지 선택합니다.
        self.market = self.QCB_market.currentText()
        self.set_table_make(self.QT_trade_open, pd.DataFrame())
        self.set_table_make(self.QT_trade_closed, pd.DataFrame())
        self.QLE_stg.clear()
        self.QT_tickers.clear()
        self.dict_option = {}
        self.dict_option["market"] = self.market
        self.dict_option["mock"] = self.QCB_mock.isChecked()
        self.QTE_stg_buy.clear()
        self.QTE_stg_sell.clear()
        self.df_tickers = pd.DataFrame()
        token_file = "DB/token.dat"
        if not os.path.isfile(token_file): #파일이 없을 경우
            data={}
            data['bybit'] = {'api':'','secret':''}
            data['한국투자증권_국내_주식_실전'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한국투자증권_국내_주식_모의'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한국투자증권_국내_선옵_실전'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한국투자증권_국내_선옵_모의'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한국투자증권_국내_선옵_실전_매도'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한투_웹소켓_국내주식_실전'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한투_웹소켓_국내주식_모의'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한투_웹소켓_국내선옵_실전'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['한투_웹소켓_국내선옵_모의'] = {'api':'','secret':'','acc_no':'','user_id':''}
            data['업비트'] = {'api':'','secret':''}
            with open(token_file, "wb") as f:
                pickle.dump(data, f)
        if self.market == 'bybit':
            ex_bybit,ex_pybit = common_def.make_exchange_bybit()
            self.dict_option["exchange"] = ex_bybit
            self.dict_option["ex_pybit"] = ex_pybit
            fetch_tickers = self.dict_option["exchange"].fetch_tickers()
            df_tickers = self.bybit_set_tickers(fetch_tickers)
            df_tickers = df_tickers[df_tickers.index.str[-10:]=='/USDT:USDT']
            # df_tickers.index = [x[:-10] for x in df_tickers.index.tolist() if x[-4:] == 'USDT' and x[:6] != 'GASDAO']  #GASDAO 종목 삭제
            df_tickers.index = [x[:-10] for x in df_tickers.index.tolist() ]
            df_tickers['종목코드'] = df_tickers.index
            self.df_tickers = df_tickers[['종목코드','quoteVolume','volume24h','percentage','change']]
            self.dict_option['real_chart'] = '코인_리얼'
        elif self.market == '업비트':
            f = open(token_file, "rb")
            data = pickle.load(f)
            self.dict_option["exchange"] = common_def.make_exchange_upbit(api=data['업비트']['api'],secret=data['업비트']['secret'])
            self.dict_option["ex_ws"] = common_def.make_exchange_upbit_ws()
            self.dict_option['real_chart'] = '코인_리얼'
        elif self.market == '국내주식' :
            # try:
            self.dict_option["exchange"] = KIS.KoreaInvestment(market='국내주식',api_key=self.QLE_API.text(),secret_key=self.QLE_secret.text(),mock=self.QCB_mock.isChecked())
            # except:
            # self.pop_message('에러','국내주식 API 확인')
            # return
            # self.df_tickers = pd.DataFrame()
            holiday = self.dict_option["exchange"].check_holiday_now()
            print(f"휴일 확인: {holiday}")
            self.dict_option['real_chart'] = '주식_리얼'
        elif self.market == '국내선옵':
            import websocket_kis
            try:
                self.dict_option["exchange"] = KIS.KoreaInvestment(market='국내선옵',mock=self.QCB_mock.isChecked(),only_short=False)
                self.dict_option["주간야간"] = self.dict_option["exchange"].check_holiday()
                market = '야간선옵' if self.dict_option["주간야간"] == '야간' else '국내선옵'
                dict_info = {'key':'','secret':'','market':market,'mock':False,
                             'user_id':self.dict_option["exchange"].user_id,'night':self.dict_option["주간야간"]}
                self.thread_ws= websocket_kis.KISReal(dict_info=dict_info,dict_orders={})
                self.thread_ws.price_updated.connect(self.price_data)
                self.thread_ws.order_filled.connect(self.chegyeol_closed)
                self.send_orders.connect(self.thread_ws.update_order)
                # self.thread_ws.subscribe('H0STCNI9','somepick')
                self.thread_ws.start()
                # self.dict_option["주간야간"] = self.dict_option["exchange"].check_holiday_now()

                if self.dict_option["exchange"].access_token == None:
                    # self.df_tickers = pd.DataFrame()
                    self.pop_message('에러','국내선옵 API 확인 [issue_access_token]')
                    return
                else:
                    self.df_tickers = self.display_futopt()

                self.dict_option['df_tickers'] = self.df_tickers
            except IOError as e:
                print(e)
                self.pop_message('에러','국내선옵 API 확인')
                return
            print(f"휴일: {self.dict_option['주간야간']}")
            self.dict_option['real_chart'] = '선옵_리얼'
            self.dict_codes_info = self.make_tickers_info()
        else:
            stg_file = ''
            return
        self.real_chart.chart_table(self.dict_option['real_chart'])
        # self.QCB_chart_bong_detail.setCurrentText('1분봉')
        # self.QCB_chart_bong_detail.setEnabled(False)
        self.QCB_chart_bong.setCurrentText('5분봉')

        self.set_table_make(self.QT_tickers,self.df_tickers)

        if not self.market == '':
            if self.QCB_market.currentText() == 'bybit':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {'4시간봉':10}\n"
                                         "배팅금액 = 100\n"
                                         "분할매수 = []\n"
                                         "방향 = 'long'\n"
                                         "레버리지 = 3\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "")
                self.stg_market = 'stg_bybit'
                self.history_market = 'history_bybit'
            elif self.QCB_market.currentText() == '국내주식':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {일봉:365}\n"
                                         "배팅금액 = 1000000\n"
                                         "분할매수 = []\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "")
                self.stg_market = 'stg_stock'
                self.history_market = 'history_stock'
            elif self.QCB_market.currentText() == '국내선옵':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {'5분봉':5}\n"
                                         "배팅금액 = 10000000\n"
                                         "분할매수 = []\n"
                                         "방향 = 'long'\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "")
                self.stg_market = 'stg_futopt'
                self.history_market = 'history_futopt'
            elif self.QCB_market.currentText() == '업비트':
                self.QTE_stg_buy.setText("진입대상 = ''\n"
                                         "봉 = {'5분봉':5}\n"
                                         "배팅금액 = 100000\n"
                                         "분할매수 = []\n"
                                         "####################\n"
                                         "매수가 = \n"
                                         "")
                self.stg_market = 'stg_upbit'
                self.history_market = 'history_upbit'

            self.QTE_stg_sell.setText("분할매도 = [] #분할매도 시 리스트 형식으로 비율을 저장할 것 예)[30,30,40] \n"
                                      "####################\n"
                                      "매도가 = 시장가 #분할매도 시 리스트 형식으로 저장할 것\n"
                                      "")
            # self.df_old = pd.DataFrame(columns=['ticker', '진입시간', '진입가', '주문수량',
            #                                     '청산가', '청산시간', '상태', 'id', '현재봉시간'])
            # else:
            #     self.df_old = self.df_stg[['ticker', '진입시간', '진입가', '주문수량',
            #                                '청산가', '청산시간', '상태', 'id', '상세봉', '현재봉시간']]
            self.df_stg = pd.read_sql(f"SELECT * FROM {self.stg_market}", self.conn_stg).set_index('index')
            self.df_stg.sort_values('table', inplace=True)
            self.reset_stg_table()
            self.QCB_stgs.clear()
            if not self.df_stg.empty:
                self.QCB_stgs.addItems(self.df_stg['전략명'].tolist())

        print(f"{self.QCB_market.currentText()} 선택")
        self.thread_common = common_def.common(self.market,self.dict_option)
        self.thread_common.df_real_chart.connect(self.push_chart)
        self.thread_common.send_make_df.connect(self.get_df)
        self.thread_common.send_trend_df.connect(self.get_trend)
        self.send_ohlcv.connect(self.thread_common.make_df)
        if self.market == '국내선옵':
            self.timer_trend = QTimer()
            self.timer_trend.timeout.connect(self.thread_common.trend_time)

    # def sell_only(self):
    #     self.select_market()
    def fetch_balance(self):
        if self.QCB_market.currentText() == '국내선옵':
            if self.QPB_manual.isChecked() == True:
                self.select_market()
                asset,df_instock = self.ex_kis.fetch_balance()
                # self.df_compare = df[['ticker', '진입시간', '청산가', '청산시간', '상태', '분할상태',
                #                       '현재봉시간', '매입금액', '잔고', '분할보유수량', '매도전환']]
                df_instock.rename(
                    columns={'체결평균단가': '진입가','청산가능수량': '보유수량',
                             '평가손익': '수익금', '종목코드': 'ticker',}, inplace=True)

                df_instock['진입시간'] = datetime.datetime.now().replace(second=0, microsecond=0)
                df_instock['table'] = range(1, len(df_instock) + 1) #테이블열에 순차적으로 번호 넣기
                # df_instock['청산가'] = 0
                df_instock['청산시간'] = datetime.datetime.now().replace(second=0, microsecond=0)
                df_instock['상태'] = 0
                df_instock['분할상태'] = 0
                df_instock['현재봉시간'] = 0
                df_instock['잔고'] = 0
                df_instock['분할보유수량'] = 0
                df_instock['매도전환'] = 0
                df_instock['market'] = 0
                df_instock['전략명'] = 0
                df_instock['수익률'] = 0
                df_instock['최고수익률'] = 0
                df_instock['최저수익률'] = 0
                df_instock['현재가'] = 0
                df_instock['주문수량'] = 0
                df_instock['승률(win/all)'] = 0
                df_instock['수수료율'] = 0

                self.qtable_open(df_instock)
                # df_instock.to_sql('stg_sell_only',self.conn_stg,if_exists='replace')
            else:
                print('매도만을 체크하세요.')
    def save_stg(self):
        global 분봉1, 분봉3, 분봉5, 분봉15, 분봉30, 시간봉1, 시간봉4, 일봉, 주봉, 월봉
        global long, short
        분봉1 = '1분봉'  # 시가CN(bong,pre) bong자리에 넣기 위함 변수로 숫자가 앞에 올 수는 없기 때문
        분봉3 = '3분봉'
        분봉5 = '5분봉'
        분봉15 = '15분봉'
        분봉30 = '30분봉'
        시간봉1 = '1시간봉'
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
        exec(self.QTE_stg_buy.toPlainText().split("\n", 1)[0], None, locals_dict_buy)  # 첫줄 읽기 추출
        object = locals_dict_buy.get('진입대상')
        exec(self.QTE_stg_buy.toPlainText().split("\n", 2)[1], None, locals_dict_buy)
        bong = locals_dict_buy.get('봉')
        exec(self.QTE_stg_buy.toPlainText().split("\n", 3)[2], None, locals_dict_buy)
        bet = locals_dict_buy.get('배팅금액')
        exec(self.QTE_stg_buy.toPlainText().split("\n", 4)[3], None, locals_dict_buy)
        division_buy = locals_dict_buy.get('분할매수')
        direction = 'long'
        leverage = 1


        if type(object) == dict:
            ticker = ''
        else:
            ticker = object
        if self.QCB_market.currentText() == '국내주식' and self.QLE_stg.text() != '':
            direction = long
            trade_market = '주식'
            if type(object) == list:
                ticker = ''
            else:
                # trade_market = self.df_tickers.loc[object, '시장구분']
                ticker = object

        elif self.QCB_market.currentText() == '국내선옵' and self.QLE_stg.text() != '':
            exec(self.QTE_stg_buy.toPlainText().split("\n", 4)[3], None, locals_dict_buy)
            direction = locals_dict_buy.get('방향')
            if type(object) == list or type(object) == dict :
                trade_market = '조건검색'
                ticker = list(object.keys())[0]
            else:
                trade_market = '선물' if object[:1] == '1' else '콜옵션' if object[:1] == '2' else '풋옵션' if object[:1] == '3' else '스프레드'
                ticker = object

        elif self.QCB_market.currentText() == 'bybit' and self.QLE_stg.text() != '':
            exec(self.QTE_stg_buy.toPlainText().split("\n", 4)[3], None, locals_dict_buy)
            direction = locals_dict_buy.get('방향')
            exec(self.QTE_stg_buy.toPlainText().split("\n", 5)[4], None, locals_dict_buy)
            leverage = locals_dict_buy.get('레버리지')
            trade_market = 'bybit'

        elif self.QCB_market.currentText() == '업비트' and self.QLE_stg.text() != '':
            trade_market = '업비트'

        locals_dict_sell = {}
        division_sell = self.QTE_stg_sell.toPlainText().split("\n", 1)[0]  # 셋줄 읽기 추출
        exec(division_sell, None, locals_dict_sell)
        division_sell = locals_dict_sell.get('분할매도')

        stg_buy = common_def.replace_tabs_with_spaces(self.QTE_stg_buy.toPlainText())
        stg_sell = common_def.replace_tabs_with_spaces(self.QTE_stg_sell.toPlainText())
        list_compare = self.check_compare_ticker(stg_buy, stg_sell)
        if self.QLE_stg.text() != '':
            if stg_name in self.df_stg.index.tolist():
                print(f'{trade_market} - {stg_name} 기존전략에 덮어쓰기 {bet= }')
                if self.df_stg.loc[stg_name, 'ticker'] != '' and type(object) == list and self.df_stg.loc[stg_name, '상태'] != '대기':
                    ticker = self.df_stg.loc[stg_name, 'ticker']
                elif self.df_stg.loc[stg_name, '상태'] == '대기' and type(object) == list:
                    ticker = ''
            else:
                print(f'{trade_market} - {stg_name} 새로운전략 저장 {bet= }')

            if type(object) == list or type(object) == dict:
                object = json.dumps(object, ensure_ascii=False)
            dict_data = {'전략명': self.QLE_stg.text(), 'market': trade_market, '진입대상': object,
                         '비교대상': json.dumps(list_compare), 'ticker': ticker,
                         '봉': self.dict_bong_int[list(bong.keys())[0]], '방향': direction, '초기자금': bet, '배팅금액': bet,
                         '매입금액': 0,
                         '레버리지': leverage, '진입전략': stg_buy, '청산전략': stg_sell, '현재가': 0, '평단가': 0,'주문가': 0,
                         '주문수량': 0, '보유수량': 0, '진입시간': '', '청산시간': '', '수익률': 0,
                         '최고수익률': 0, '최저수익률': 0, '수익금': 0, '평가금액': bet, '상태': '대기', 'id': '', '수수료': 0,
                         '수수료율': 0, '승률(win/all)': '0/0(0%)', '누적수익금': 0, '잔고': bet, '매입율': 0, '주문방식':'',
                         # '상세봉':bong_detail ,'청산가': 0,'분할청산가': json.dumps([]),'청산금액': 0,'주문시간': '','청산신호시간': ''
                         '봉길이': bong[list(bong.keys())[0]], '현재봉시간': '','주문취소시간': '', 'table': 0,
                         '분할매수': json.dumps(division_buy),
                         '분할매도': json.dumps(division_sell), '분할상태': json.dumps([]), '분할주문가': json.dumps([]),
                         '분할주문수량': json.dumps([]), '분할보유수량': json.dumps([]),
                         '분할매입금액': json.dumps([]), '분할청산금액': json.dumps([]), '분할수수료': json.dumps([]),
                         '분할id': json.dumps([]), '분할진입시간': json.dumps([]), '분할청산시간': json.dumps([]), '매도전환': "False",
                         '분할평가금액': json.dumps([]), '분할주문시간': json.dumps([]),'분할주문취소시간': json.dumps([]),
                         }
            self.df_stg.loc[stg_name] = dict_data

        elif self.QLE_stg.text() == '':
            print(f"{self.QLE_stg.text()} 전략명이 비어있음")
            return
        else:
            print(f'{trade_market} - {stg_name} 저장 에러')
            raise

        if not self.QLE_stg.text() == '': #분할매수 또는 분할 매도일 경우
            if len(division_buy) > 0 or len(division_sell) > 0: #분할일 경우
                list_state = ['대기' for x in range(len(division_buy))]
                # print(f"{list_state=}")
                # print(f"{type(list_state)=}")
                division_zero = [0 for x in range(len(division_buy))]
                division_zero_sell = [0 for x in range(len(division_sell))]
                division_id = ["" for x in range(len(division_buy))]
                self.df_stg.loc[stg_name, '분할상태'] = json.dumps(list_state,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할주문가'] = json.dumps(division_zero)
                # self.df_stg.loc[stg_name, '분할청산가'] = json.dumps(division_zero_sell)
                self.df_stg.loc[stg_name, '분할주문수량'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할보유수량'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할매입금액'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할청산금액'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할수수료'] = json.dumps(division_zero)
                self.df_stg.loc[stg_name, '분할id'] = json.dumps(division_id,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할진입시간'] = json.dumps(division_id,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할청산시간'] = json.dumps(division_id,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할주문시간'] = json.dumps(division_id,ensure_ascii=False)
                self.df_stg.loc[stg_name, '분할주문취소시간'] = json.dumps(division_id,ensure_ascii=False)
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

        # print(self.df_stg[['분할상태','분할주문가','분할청산가','분할주문수량','분할보유수량','분할매입금액','분할청산금액','분할진입수수료','분할id','분할진입시간','분할청산시간']])
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
            self.df_stg.to_sql(self.stg_market, self.conn_stg, if_exists='replace')
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



    def save_setting(self):
        self.df_set.loc['자동시작','check'] = self.QCB_auto_start.isChecked()
        self.df_set.loc['자동시작마켓','value'] = self.QCB_market.currentText()
        self.df_set.loc['모의매매','check'] = self.QCB_mock.isChecked()
        self.df_set.loc['자동종료','check'] = self.QCB_auto_finish.isChecked()
        self.df_set.loc['자동종료시간','value'] = self.QTE_finish.text()
        self.df_set.loc['텔레그램','check'] = self.QCB_tele.isChecked()
        token_file = "DB/token.dat"
        f = open(token_file, "rb")
        data = pickle.load(f)
        pprint(data)
        mock = '모의' if self.QCB_mock.isChecked() else '실전'
        if not self.QLE_API.text() == '':
            if self.market == '국내주식' or self.market == '국내선옵':
                if self.QCB_short_acc_no.isChecked():
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}_매도']['api'] = self.QLE_API.text()
                else:
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}']['api'] = self.QLE_API.text()
            else:
                data[f'{self.market}']['api'] = self.QLE_API.text()
            with open(token_file, "wb") as f:
                pickle.dump(data, f)
            self.QLE_API.clear()
        if not self.QLE_secret.text() == '':
            if self.market == '국내주식' or self.market == '국내선옵':
                if self.QCB_short_acc_no.isChecked():
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}_매도']['secret'] = self.QLE_secret.text()
                else:
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}']['secret'] = self.QLE_secret.text()
            else:
               data[f'{self.market}']['secret'] = self.QLE_secret.text()
            with open(token_file, "wb") as f:
                pickle.dump(data, f)
            self.QLE_secret.clear()
        if not self.QLE_account.text() == '':
            if self.market == '국내주식' or self.market == '국내선옵':
                if self.QCB_short_acc_no.isChecked():
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}_매도']['acc_no'] = self.QLE_account.text()
                else:
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}']['acc_no'] = self.QLE_account.text()
            # else:
            #    data[f'{self.market}']['acc_no'] = self.QLE_account.text()
                with open(token_file, "wb") as f:
                    pickle.dump(data, f)
                self.QLE_account.clear()
        if not self.QLE_id.text() == '':
            if self.market == '국내주식' or self.market == '국내선옵':
                if self.QCB_short_acc_no.isChecked():
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}_매도']['user_id'] = self.QLE_id.text()
                else:
                    data[f'한국투자증권_{self.market[:2]}_{self.market[2:]}_{mock}']['user_id'] = self.QLE_id.text()
                with open(token_file, "wb") as f:
                    pickle.dump(data, f)
                self.QLE_id.clear()
        pprint(data)
        db_file = 'DB/stg_trade.db'
        conn = sqlite3.connect(db_file)
        self.df_set.to_sql('set', conn, if_exists='replace')
        self.pop_message('확인', '설정이 저장 되었습니다.')

    def del_stg(self):
        if self.QCB_stgs.currentText() != '':
            self.df_stg = pd.read_sql(f"SELECT * FROM {self.stg_market}", self.conn_stg).set_index('index')
            self.df_stg.drop([f'{self.QCB_stgs.currentText()}'], inplace=True)
            self.QCB_stgs.clear()
            self.QCB_stgs.addItems(self.df_stg.index.tolist())
            self.reset_stg_table()
            self.df_stg.to_sql(self.stg_market, self.conn_stg, if_exists='replace')

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

                self.df_history = pd.read_sql(f"SELECT * FROM {self.history_market}", self.conn_stg).set_index('index')
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
        self.df_stg = pd.read_sql(f"SELECT * FROM {self.stg_market}", self.conn_stg).set_index('index')
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
        dict_info = {"req":"real_chart","check_compare":False}
        dict_info['ticker'] = self.QLE_chart_ticker.text()
        # dict_info['봉'] = self.QCB_chart_bong.currentText()
        bong = self.QCB_chart_bong.currentText()
        dict_info['봉'] = self.dict_bong_int[bong]
        self.bool_light_chart = False
        if self.state_real_chart == False:
            self.state_real_chart = True
            if dict_info['ticker'] != '':
                duration = 1 if self.QCB_chart_duration.currentText() == '기간(일)' else int(self.QCB_chart_duration.currentText())
                dict_info['duration'] = duration
                if self.market == '업비트' or self.market == 'bybit':
                    ohlcv = []
                    # for ticker, li_bong in self.dict_ticker_bong_limit.items():
                    date_old = datetime.datetime.now() - datetime.timedelta(days=duration)
                    stamp_date_old = common_def.datetime_to_stamp(date_old)
                    self.ohlcv_real = common_def.get_coin_initial_data(market=self.market, dict_option=self.dict_option,
                                                                         ohlcv=ohlcv, since=stamp_date_old,
                                                                         ticker=dict_info['ticker'],
                                                                         limit=200,
                                                                         bong_detail="1분봉")  # 최대 200개 숫자 늘리면 안됨
                elif self.market == '국내선옵':
                    conn = sqlite3.connect('DB/DB_futopt_kis.db')
                    now_dt = datetime.datetime.now()
                    dict_symbol = {'선물':'선물','통합선물':'선물','야간선물':'선물',
                                   '미니선물':'미니선물','통합미니선물':'미니선물','야간미니선물':'미니선물'}
                    ticker_symbol = dict_symbol[dict_info['ticker']]
                    dict_info['symbol'] = self.dict_codes_info[ticker_symbol]['ticker']

                    expiry_dt = self.df_tickers.loc[self.df_tickers['종목명'] == ticker_symbol, '만기일'].tolist()[0]
                    dict_info['expiry_dt'] = datetime.datetime.strptime(expiry_dt,'%Y-%m-%d %H:%M:%S')
                    past_expiry_dt = self.df_tickers.loc[self.df_tickers['종목명'] == ticker_symbol, '지난만기일'].tolist()[0]
                    dict_info['past_expiry_dt'] = datetime.datetime.strptime(past_expiry_dt,'%Y-%m-%d %H:%M:%S')
                    if dict_info['ticker'].startswith('통합'):
                        df = pd.read_sql(f"SELECT * FROM {dict_info['ticker'].replace('통합', '')}", conn).set_index('날짜')  # 주간데이터
                        df_night = pd.read_sql(f"SELECT * FROM {dict_info['ticker'].replace('통합', '야간')}", conn).set_index('날짜')  # 야간데이터
                        df = pd.concat([df, df_night], axis=0)
                        df = df.sort_index()
                    else:
                        df = pd.read_sql(f"SELECT * FROM {dict_info['ticker']}", conn).set_index('날짜')

                    from_dt = pd.to_datetime(df.index[-1])
                    if dict_info['ticker'].startswith('야간'):
                        output = self.dict_option["exchange"].fetch_1m_ohlcv_night(symbol=dict_info['symbol'],
                                                                                 now_dt=now_dt,
                                                                                 from_dt=from_dt,
                                                                                 expiry_dt=dict_info['expiry_dt'],
                                                                                 past_expiry_dt=dict_info['past_expiry_dt'],
                                                                                 ohlcv=[])
                    else:
                        output = self.dict_option["exchange"].fetch_1m_ohlcv(symbol=dict_info['symbol'],
                                                                           now_dt=now_dt,
                                                                           from_dt=from_dt,
                                                                           expiry_dt=dict_info['expiry_dt'],
                                                                           past_expiry_dt=dict_info['past_expiry_dt'],
                                                                           ohlcv=[])
                    df.index = pd.to_datetime(df.index)
                    result = (df.groupby(df.index.date).apply(lambda x: list(x.index)).sort_index()).index.tolist() #인덱스를 날짜로 그룹으로 묶어서 리스트로 추출
                    if duration < len(result):
                        duration_d = result[-duration]
                        df = df[df.index >= duration_d.strftime("%Y-%m-%d")]
                    ohlcv = self.dict_option["exchange"].change_to_list(df)
                    output.extend(ohlcv)
                    self.ohlcv_real = output
                    # self.ohlcv_real = ohlcv
                self.chart_thread = self.real_chart
                # self.chart_thread.make_init_data(self.dict_option,dict_info)
                self.chart_thread.make_init_data(self.dict_option)
                # self.send_real_data.connect(self.chart_thread.update_plot_data)
                self.send_chart.connect(self.chart_thread.update_plot_data)
                self.timer_real_chart = QTimer()
                self.timer_real_chart.timeout.connect(lambda:self.do_real_chart(dict_info))
                self.timer_real_chart.start(1000)  # 1000ms = 1초마다 실행
            else:
                print('ticker 확인')
        elif self.state_real_chart == True:
            self.state_real_chart = False
            self.send_chart.emit(pd.DataFrame())
            # self.chart_thread.stop()
            self.timer_real_chart.stop()
            self.QPB_chart.setStyleSheet("background-color: #cccccc;")


    def do_real_chart(self,dict_info):
        # ticker = self.QLE_chart_ticker.text()
        self.effect_chart()
        if self.market == '업비트' or self.market == 'bybit':
            limit = (time.time() - (self.ohlcv_real[-1][0] / 1000)) // 60
            stamp_date_old = self.ohlcv_real[-3][0] / 1000  # 마지막에서 3번째 시간
            self.ohlcv_real = common_def.get_coin_ohlcv_real(dict_option=self.dict_option,
                                                               ohlcv=self.ohlcv_real, since=stamp_date_old,
                                                               ticker=dict_info['ticker'], limit=limit + 5, bong_detail="1분봉")
        elif self.market == '국내선옵':
            now_dt = datetime.datetime.now()
            # dict_symbol = {'선물': '선물', '통합선물': '선물', '야간선물': '선물',
            #                '미니선물': '미니선물', '통합미니선물': '미니선물', '야간미니선물': '미니선물'}
            # ticker_symbol = dict_symbol[ticker]
            # symbol = self.dict_codes_info[ticker_symbol]['ticker']
            # expiry_dt = self.df_tickers.loc[self.df_tickers['종목명']==ticker_symbol,'만기일'][0]
            # expiry_dt = datetime.datetime.strptime(expiry_dt, '%Y-%m-%d %H:%M:%S')
            # past_expiry_dt = self.df_tickers.loc[self.df_tickers['종목명']==ticker_symbol,'지난만기일'][0]
            # past_expiry_dt = datetime.datetime.strptime(past_expiry_dt, '%Y-%m-%d %H:%M:%S')
            from_dt = datetime.datetime.strptime(self.ohlcv_real[0]['stck_bsop_date'] + self.ohlcv_real[0]['stck_cntg_hour'],"%Y%m%d%H%M%S")
            if dict_info['ticker'].startswith('야간'):
                # print(f"{symbol=} {from_dt=}  {expiry_dt=}  {past_expiry_dt}")
                self.ohlcv_real = self.dict_option["exchange"].fetch_1m_ohlcv_night(symbol=dict_info['symbol'],
                                                                                    now_dt=now_dt,
                                                                                    from_dt=from_dt,
                                                                                    expiry_dt=dict_info['expiry_dt'],
                                                                                    past_expiry_dt=dict_info['past_expiry_dt'],
                                                                                    ohlcv=self.ohlcv_real)
                # print(pd.DataFrame(self.ohlcv_real))
                # quit()
            else:
                self.ohlcv_real = self.dict_option["exchange"].fetch_1m_ohlcv(symbol=dict_info['symbol'],
                                                                              now_dt=now_dt,
                                                                              from_dt=from_dt,
                                                                              expiry_dt = dict_info['expiry_dt'],
                                                                              past_expiry_dt=dict_info['past_expiry_dt'],
                                                                              ohlcv=self.ohlcv_real)

        self.send_ohlcv.emit(dict_info,self.ohlcv_real)
        # df = common_def.make_df(market=self.market,ticker=ticker,ohlcv=self.ohlcv_real,
        #                          bong=self.dict_bong_int[self.QCB_chart_bong.currentText()],
        #                         check_compare=False,dict_option=self.dict_option)
    def push_chart(self,df):
        # 데이터를 전부 float으로
        # df = df.apply(pd.to_numeric, errors='coerce')
        # self.chart_thread.update_plot_data(df)
        # self.send_chart = df
        self.send_chart.emit(df)
    # def view_chart_stop(self):
    #     if self.chart_thread is not None:
    #         self.chart_thread.stop()
    #         self.chart_thread = None
    def effect_chart(self):
        self.bool_light_chart = not self.bool_light_chart
        if self.bool_light_chart == True:
            self.QPB_chart.setStyleSheet("background-color: #fa3232;")
        else:
            self.QPB_chart.setStyleSheet("background-color: #cccccc;")

    def effect_start(self):
        self.bool_light = not self.bool_light
        if self.bool_light == True:
            self.QPB_start.setStyleSheet("background-color: #fa3232;")

            # today = datetime.datetime.now()
            # df_history = self.df_history.copy()
            # df_history['청산시간'] = pd.to_datetime(df_history['청산시간'], utc=True)
            # df_history = df_history[df_history['청산시간'].dt.date == today.date()]
            # win = len(df_history.loc[df_history['수익금'] > 0])
            # # df_compare = self.df_compare.copy()
            # df_trade = df_trade[df_trade['상태'] != '대기']
            # df = pd.concat([df_history,df_trade])
            # benefit_closed = df['수익금'].sum()
            # try:
            #     df['가중치'] = df['매입금액'] / df['매입금액'].sum()  # 비중 계산
            #     가중평균 = (df['수익률'] * df['가중치']).sum()
            # except:
            #     print(f"error: {df['매입금액']= }    {df['매입금액'].sum()= }")
            #     가중평균 = 0
            # # print(f"가중 평균 수익률: {가중평균:.2f}%  수익금: {benefit_closed}")
            # self.QL_ror.setText(f"{가중평균:,.2f}%")
            # self.QL_benefit.setText(f"{benefit_closed:,.1f}")
            # if len(df_history) == 0:
            #     self.QL_amount.setText(f"{0}%")
            # else:
            #     self.QL_amount.setText(f"{(win/len(df_history))*100:,.1f}%")
            #
            # self.set_table_make(self.QT_tickers,df_tickers)

        if self.bool_light == False:
            self.QPB_start.setStyleSheet("background-color: #cccccc;")
    def make_dict_ticker_bong(self):
        dict_ticker_bong_limit = {}
        df_tickers = self.df_trade.copy()
        for idx, row in df_tickers.iterrows():
            if row['ticker'] in dict_ticker_bong_limit.keys():
                if dict_ticker_bong_limit[row['ticker']] < row['봉'] * row['봉길이']:
                    dict_ticker_bong_limit[row['ticker']] = row['봉'] * row['봉길이']
            else:
                dict_ticker_bong_limit[row['ticker']] = row['봉'] * row['봉길이']
            list_compare = json.loads(row['비교대상'])
            for li in list_compare:
                ticker = li[:li.index('_')]
                df_tickers.loc[li, 'ticker'] = ticker
                bong = li[li.index('_') + 1:]
                df_tickers.loc[li, '봉'] = self.dict_bong_int[bong]
                if ticker in dict_ticker_bong_limit.keys():

                    if dict_ticker_bong_limit[ticker] < row['봉'] * row['봉길이']:
                        dict_ticker_bong_limit[ticker] = row['봉'] * row['봉길이']
                    else:
                        df_tickers.loc[li, '봉길이'] = 0
                else:
                    dict_ticker_bong_limit[ticker] = row['봉'] * row['봉길이']
                    df_tickers.loc[li, '봉길이'] = row['봉'] * row['봉길이']
        return dict_ticker_bong_limit
    def signal_start(self):
        self.df_stg = pd.read_sql(f"SELECT * FROM {self.stg_market}", self.conn_stg).set_index('index')
        self.df_trade = self.df_stg[self.df_stg['table'] != 0] # 현재 테이블에 저장된 전략만 갖고오기
        now_dt = datetime.datetime.now().replace(second=0, microsecond=0)

        self.bool_light = False
        self.thread = ATOM_trade_numpy.Trade_np(self.dict_option, self.df_set)
        self.thread.send_save_stg.connect(self.update_save_stg)
        self.thread.send_stg.connect(self.update_stg)
        self.send_trading.connect(self.thread.trading)
        dict_orders = self.make_dict_orders()
        self.dict_ticker_bong_limit = self.make_dict_ticker_bong()
        if self.market == '국내주식' or self.market == '국내선옵':
            if self.market == '국내주식':
                for ticker in self.dict_ticker_bong_limit.keys():
                    globals()[ticker] = self.dict_option['exchange'].fetch_1m_ohlcv(symbol=ticker, from_dt=datetime,
                                                now_dt=now_dt, past_expiry_dt=now_dt,ohlcv=[])
            elif self.market == '국내선옵':
                print(f"1 {self.dict_ticker_bong_limit=}")
                print(f"2 {self.dict_ticker_bong_limit= }")
                self.dict_option['주간야간'] = '주간'

                if self.dict_option['주간야간'] == '주간':
                    self.dict_ticker_bong_limit = {k: v for k, v in self.dict_ticker_bong_limit.items() if not k.startswith('야간')}
                elif self.dict_option['주간야간'] == '야간':
                    remove_keys = {'선물', '미니선물'} # 해당하는 키값 삭제
                    self.dict_ticker_bong_limit = {k: v for k, v in self.dict_ticker_bong_limit.items() if k not in remove_keys}
                else:
                    print(f"signal_start {self.dict_option['주간야간']= }")
                    quit()
                print(f"3 {self.dict_ticker_bong_limit= }")
                if list(set(self.dict_ticker_bong_limit.keys()) & set(['선물','야간선물','통합선물'])):
                    if self.dict_codes_info.get('선물'):
                        expiry_date = self.df_tickers.loc[self.df_tickers['종목명'] == '선물', '만기일'].tolist()[0]
                        self.dict_codes_info['선물']['만기일'] = pd.to_datetime(expiry_date)
                        past_expiry_date = self.df_tickers.loc[self.df_tickers['종목명'] == '선물', '지난만기일'].tolist()[0]
                        self.dict_codes_info['선물']['지난만기일'] = pd.to_datetime(past_expiry_date)

                if list(set(self.dict_ticker_bong_limit.keys()) & set(['미니선물','야간미니선물','통합미니선물'])):
                    if self.dict_codes_info.get('미니선물'):
                        expiry_date = self.df_tickers.loc[self.df_tickers['종목명'] == '미니선물', '만기일'].tolist()[0]
                        self.dict_codes_info['미니선물']['만기일'] = pd.to_datetime(expiry_date)
                        past_expiry_date = self.df_tickers.loc[self.df_tickers['종목명'] == '미니선물', '지난만기일'].tolist()[0]
                        self.dict_codes_info['미니선물']['지난만기일'] = pd.to_datetime(past_expiry_date)
                print(self.df_tickers)
                conn = sqlite3.connect('DB/DB_futopt_kis.db')
                for ticker, li_bong in self.dict_ticker_bong_limit.items():
                    if ticker.startswith('통합'):
                        df = pd.read_sql(f"SELECT * FROM {ticker.replace('통합','')}", conn).set_index('날짜') #주간데이터
                        df_night = pd.read_sql(f"SELECT * FROM {ticker.replace('통합','야간')}", conn).set_index('날짜') #야간데이터
                        df = pd.concat([df, df_night], axis=0)
                        df = df.sort_index()
                        remark = "통합_old_"
                    else:
                        if ticker.startswith('야간'):
                            remark = "야간_old_"
                        else:
                            remark = "주간_old_"
                        df = pd.read_sql(f"SELECT * FROM {ticker}", conn).set_index('날짜')
                        self.dict_codes_info[self.dict_trade[ticker]]['from_dt'] = pd.to_datetime(df.index[-1])

                    if len(df) > self.dict_ticker_bong_limit[ticker]:
                        df = df[self.dict_ticker_bong_limit[ticker]:]
                    #기존에 받아놓은 데이터프레임 리스트로 가공 후 저장
                    globals()[f"{remark}{self.dict_trade[ticker]}"] = self.dict_option["exchange"].change_to_list(df)
                    # df = self.dict_option['exchange'].get_kis_ohlcv(globals()[f"{remark}{self.dict_trade[ticker]}"])
                    # df.to_sql(f"{remark}{self.dict_trade[ticker]}", sqlite3.connect("DB/bt.db"), if_exists='replace')
                print(f"5 {self.dict_ticker_bong_limit= }")
                mini_keys = {'미니선물', '야간미니선물', '통합미니선물'} #미니선물 관련된게 있을 경우 미니선물로 통일
                futures_keys = {'선물', '야간선물', '통합선물'} #선물 관련된게 있을 경우 선물로 통일
                normalized = {}
                for k, v in self.dict_ticker_bong_limit.items():
                    if k in mini_keys:
                        normalized['미니선물'] = max(normalized.get('미니선물', float('-inf')), v)
                    elif k in futures_keys:
                        normalized['선물'] = max(normalized.get('선물', float('-inf')), v)
                    else:
                        normalized[k] = v
                self.dict_ticker_bong_limit = normalized
                print(f"6 {self.dict_ticker_bong_limit= }")
                for ticker, li_bong in self.dict_ticker_bong_limit.items():
                    # 신규 데이터
                    symbol = self.dict_codes_info[ticker]['ticker']
                    past_expiry_dt = self.dict_codes_info[ticker]['지난만기일']
                    expiry_dt = self.dict_codes_info[ticker]['만기일']
                    from_dt = self.dict_codes_info[ticker]['from_dt']
                    print(f"{ticker= }   {symbol= }    {from_dt=}    {self.dict_option['주간야간']=} {now_dt= }   {expiry_dt=}    {past_expiry_dt=}")
                    if self.dict_option['주간야간'] == '주간':
                        globals()[f"{ticker}_ohlcv"] = self.dict_option["exchange"].fetch_1m_ohlcv(symbol=symbol,
                                                                                           now_dt=now_dt,
                                                                                           from_dt=from_dt,
                                                                                           past_expiry_dt=past_expiry_dt,
                                                                                           expiry_dt = expiry_dt,
                                                                                           ohlcv = [])
                    elif self.dict_option['주간야간'] == '야간':
                        globals()[f"{ticker}_ohlcv"] = self.dict_option["exchange"].fetch_1m_ohlcv_night(symbol=symbol,
                                                                                            now_dt=now_dt,
                                                                                            from_dt=from_dt,
                                                                                            expiry_dt=expiry_dt,
                                                                                            past_expiry_dt=past_expiry_dt,
                                                                                            ohlcv = [])
                    else:
                        print('휴일 error')
                        print(f"{self.dict_option['주간야간']}")
                        raise
                conn.close()
            self.df_trend = pd.DataFrame()
            while True:
                현재시간 = datetime.datetime.now().replace(microsecond=0)
                if self.dict_option['주간야간'] == '주간' and 현재시간 > datetime.datetime.now().replace(hour=14,minute=45,second=0):
                    break
                elif self.dict_option['주간야간'] == '야간' and 현재시간 > datetime.datetime.now().replace(hour=18,minute=0,second=0):
                    break



        elif self.market == "업비트":
            print("self.market == '업비트'")
            pprint(self.dict_option)
            self.thread_ws = ATOM_websocket.Thread_coin(self.dict_option,dict_orders)
            self.thread_ws.price_updated.connect(self.price_data)
            self.thread_ws.order_filled.connect(self.chegyeol_closed)
            self.send_orders.connect(self.thread_ws.check_dict_orders)
            self.thread_ws.start()
            ohlcv = []
            for ticker, li_bong in self.dict_ticker_bong_limit.items():
                date_old = datetime.datetime.now() - datetime.timedelta(minutes=self.dict_ticker_bong_limit[ticker])
                stamp_date_old = common_def.datetime_to_stamp(date_old)
                globals()[ticker] = common_def.get_coin_initial_data(market="업비트",dict_option=self.dict_option,
                                                                     ohlcv=ohlcv, since=stamp_date_old,ticker=ticker,
                                                                     limit=200,bong_detail="1분봉") #최대 200개 숫자 늘리면 안됨
            # 기존에 주문 걸어놨던거 확인을 하는게 필요할듯

        elif self.market == 'bybit':
            print(f"{now_time=}   {ticker=}   {bong=} ")
            start_time = now_time - (self.dict_bong_time_datetime[bong]*(bong_detail+5)) # 여분 5 정도


        self.timer_trade = QTimer()
        self.timer_trade.timeout.connect(self.do_trade)
        self.timer_trade.start(5000)  # 1000ms = 1초마다 실행

        self.timer_ohlcv = QTimer()
        self.timer_ohlcv.timeout.connect(self.gather_ohlcv)
        self.timer_ohlcv.start(10000)  # 1000ms = 1초마다 실행

        self.timer_trend = QTimer()
        self.timer_trend.timeout.connect(self.trend_time)
        self.timer_trend.start(20000)

    def trend_time(self):
        현재시간 = datetime.datetime.now().replace(second=0,microsecond=0)
        self.df_trend = self.dict_option['exchange'].add_trend(현재시간=현재시간, df_trend=self.df_trend,COND_MRKT=self.cond_mrkt)
        print(self.df_trend)
    def gather_ohlcv(self):
        현재시간 = datetime.datetime.now().replace(microsecond=0)
        for ticker, li_bong in self.dict_ticker_bong_limit.items():
            if self.market == '업비트' or self.market == 'bybit': # 데이터 갖고오기
                limit = (time.time()-(globals()[ticker][-1][0]/1000))//60
                stamp_date_old = globals()[ticker][-3][0]/1000 #마지막에서 3번째 시간
                globals()[ticker] = common_def.get_coin_ohlcv_real(dict_option=self.dict_option, ohlcv=globals()[ticker],since=stamp_date_old, ticker=ticker,limit=limit+5,bong_detail="1분봉")
            elif self.market == '국내선옵':
                symbol = self.dict_codes_info[self.dict_trade[ticker]]['ticker']
                past_expiry_dt = self.dict_codes_info[self.dict_trade[ticker]]['지난만기일']
                expiry_dt = self.dict_codes_info[self.dict_trade[ticker]]['만기일']
                if globals()[f"{ticker}_ohlcv"]:
                    lastest_data = globals()[f"{ticker}_ohlcv"][0]
                    lastest_dt = datetime.datetime.strptime(lastest_data['stck_bsop_date']+lastest_data['stck_cntg_hour'],"%Y%m%d%H%M%S")
                    if (현재시간-datetime.timedelta(minutes=1)) > lastest_dt:
                        print(f"ohlcv 생성 {ticker=}     {현재시간=}     {lastest_dt=}")
                        if self.dict_option["주간야간"] == '주간':
                            globals()[f"{ticker}_ohlcv"] = self.dict_option["exchange"].fetch_1m_ohlcv(symbol=symbol, now_dt = 현재시간,
                                from_dt=현재시간,expiry_dt=expiry_dt,past_expiry_dt=past_expiry_dt,ohlcv=globals()[f"{ticker}_ohlcv"])
                        elif self.dict_option["주간야간"] == '야간':
                            globals()[f"{ticker}_ohlcv"] = self.dict_option["exchange"].fetch_1m_ohlcv_night(symbol=symbol, now_dt=현재시간,
                                from_dt=현재시간, expiry_dt=expiry_dt,past_expiry_dt=past_expiry_dt,ohlcv=globals()[f"{ticker}_ohlcv"])
                else: # 장 시작 전에는 계속 데이터 확인
                    if self.dict_option["주간야간"] == '주간':
                        globals()[f"{ticker}_ohlcv"] = self.dict_option["exchange"].fetch_1m_ohlcv(symbol=symbol,now_dt=현재시간,from_dt=현재시간,expiry_dt=expiry_dt,past_expiry_dt=past_expiry_dt,ohlcv=globals()[f"{ticker}_ohlcv"])
                    elif self.dict_option["주간야간"] == '야간':
                        globals()[f"{ticker}_ohlcv"] = self.dict_option["exchange"].fetch_1m_ohlcv_night(symbol=symbol,now_dt=현재시간,from_dt=현재시간,expiry_dt=expiry_dt,past_expiry_dt=past_expiry_dt,ohlcv=globals()[f"{ticker}_ohlcv"])

    def do_trade(self):
        schedule.every().hour.at(":00").do(self.time_sync)  #매시각 정시마다
        self.effect_start()
        현재시간 = datetime.datetime.now().replace(microsecond=0)
        self.df_trade['현재시간'] = 현재시간

        # 진인대상과 비교대상을 구분해서 미리 데이터프레임을 만들어놓고 합치기만 하는방법을 구상해보자
        for stg, row in self.df_trade.iterrows():
            ohlcv = []  #output
            if self.market == '국내선옵':
                print(f"{self.dict_trade[row['ticker']]= }")
                ohlcv = globals()[f"{self.dict_trade[row['ticker']]}_ohlcv"].copy()
                if row["ticker"].startswith('통합'):
                    ohlcv.extend(globals()[row['ticker']])
                else:
                    if self.dict_option["주간야간"] == '야간':
                        if row['ticker'].startswith('야간'):
                            ohlcv.extend(globals()[f"{row['ticker']}"])
                        else:
                            # print(f"countinue 야간   =   {row['ticker']}")
                            continue
                    elif self.dict_option["주간야간"] == '주간':
                        if '야간' in row['ticker']:
#                             print(f"countinue 주간  =   {row['ticker']}")
                            continue
                        else:
                            ohlcv.extend(globals()[f"주간{row['ticker']}"])

            elif self.market == '업비트':
                ohlcv = globals()[row["ticker"]]
            # self.df_trade.loc[stg,'현재시간'] = 현재시간

            # if row["ticker"] == '야간미니선물':
            #     # df = self.dict_option['exchange'].get_kis_ohlcv(ohlcv)
            #     df = self.dict_option['exchange'].get_kis_ohlcv(globals()[f"{self.dict_trade[row['ticker']]}_ohlcv"])
            #     df.to_sql(f"{row['ticker']}_err_row_ohlcv", sqlite3.connect("DB/bt.db"), if_exists='replace')
            #     df = self.dict_option['exchange'].get_kis_ohlcv(globals()[row['ticker']])
            #     df.to_sql(f"{row['ticker']}_err_row", sqlite3.connect("DB/bt.db"), if_exists='replace')
            #     df = self.dict_option['exchange'].get_kis_ohlcv(ohlcv)
            #     df.to_sql(f"ohlcv", sqlite3.connect("DB/bt.db"), if_exists='replace')
            #     quit()
            stg_data = self.df_trade.loc[stg]
            dict_info = stg_data.to_dict()
            dict_info['check_compare'] = False
            dict_info['req'] = "trade"
            dict_info['현재시간'] = 현재시간
            self.send_ohlcv.emit(dict_info, ohlcv)

            # df = common_def.make_df(market=self.market,ticker=row["ticker"],ohlcv=ohlcv,
            #                          bong=row["봉"],check_compare=False,dict_option=self.dict_option)

            # list_compare = json.loads(row['비교대상'])
            # for compare in list_compare:
            #     ticker_compare = compare[:compare.index('_')]
            #     bong_compare = compare[compare.index('_') + 1:]
            #     df_compare = common_def.make_df(market=self.market,ticker=ticker_compare,ohlcv=globals()[ticker_compare],
            #                              bong=bong_compare,check_compare=True,dict_option=self.dict_option)
            #     df = pd.merge(df, df_compare, left_index=True, right_index=True, how='outer').sort_index()

    def get_df(self,df,dict_info):
        self.df_trade.loc[dict_info['전략명'],'현재가'] = df.loc[df.index[-1], '상세종가']
        # self.thread.trading(df,dict_info)
        self.send_trading.emit(df,dict_info)
    def get_trend(self,df):
        self.df_trend = df.copy()
    def make_dict_orders(self):
        dict_orders = {}
        for idx, row in self.df_trade.iterrows():
            if row['상태'] == '매수주문' or row['상태'] == '매도주문' or row['상태'] == '분할매수주문' or row['상태'] == '분할매도주문' :
                if not row['id'] == '':
                    if self.market == '업비트':
                        dict_orders[row['id']] = f"{row['ticker']}/KRW"
                    elif self.market == '국내선옵':
                        if row['ticker'] in ['선물','야간선물','통합선물']:
                            dict_orders[row['id']] = '선물'
                        elif row['ticker'] in ['미니선물','야간미니선물','통합미니선물']:
                            dict_orders[row['id']] = '미니선물'
        return dict_orders
    def make_tickers_info(self):
        dict_codes = self.df_tickers.set_index('종목코드')['종목명'].to_dict()
        from collections import defaultdict
        self.dict_trade = {'선물': '선물', '야간선물': '선물', '통합선물': '선물',
                           '미니선물': '미니선물', '야간미니선물': '미니선물', '통합미니선물': '미니선물', }
        di = defaultdict(lambda: {'ticker': []})
        for ticker, t_market in dict_codes.items():
            if ticker == "===":
                continue
            if t_market in ['선물', '미니선물']:
                di[t_market]['ticker'] = ticker
            else:
                di[t_market]['ticker'].append(ticker)
        dict_codes_info = dict(di)
        print(dict_codes_info)
        return dict_codes_info

    @pyqtSlot(dict)
    def update_stg(self,dict_stg):
        self.df_trade.loc[dict_stg['전략명']] = dict_stg
        self.qtable_open(self.df_trade)

    @pyqtSlot(dict)
    def update_save_stg(self,dict_stg):
        self.df_trade.loc[dict_stg['전략명']] = dict_stg
        # for col in self.df_trade.select_dtypes(include='datetime64[ns]').columns:
        #     self.df_trade[col] = self.df_trade[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        dict_orders = self.make_dict_orders()
        self.send_orders.emit(dict_orders)
        self.df_trade.to_sql(self.stg_market, self.conn_stg, if_exists='replace')
        self.qtable_open(self.df_trade)
    def update_history_stg(self,dict_stg):
        self.df_trade.loc[dict_stg['id']] = dict_stg
        self.df_trade.to_sql(self.history_market, self.conn_stg, if_exists='replace')
    def price_data(self,dict_info):
        # 증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1 / 레버리지 if trade_market == 'bybit' else 1
        ticker = list(dict_info.keys())[0]
        if self.market == "업비트":
            ticker = ticker[:-4]
            if ticker == 'BTC':
                self.QL_standard.setText(f"{dict_info['BTC/KRW']['close']:,} 원")
            self.df_trade.loc[self.df_trade['ticker']==ticker,'현재가'] = dict_info[f'{ticker}/KRW']['close']
            # 증거금률 = 1
            decimal_rate = 0
            fee = self.fee_upbit_market
        self.df_trade['평가금액'] = self.df_trade['보유수량'] * self.df_trade['현재가']
        기존최고수익률 = self.df_trade.loc[self.df_trade['ticker'] == ticker, '최고수익률'][0]
        기존최저수익률 = self.df_trade.loc[self.df_trade['ticker'] == ticker, '최저수익률'][0]

        self.df_trade['수익금'] = np.where(self.df_trade['방향']=='long' ,
                                        self.df_trade['평가금액'] - self.df_trade['매입금액'],
                                        self.df_trade['매입금액'] - self.df_trade['평가금액'])
        self.df_trade['수익금'] = (self.df_trade['수익금']-
                                (round(self.df_trade['매입금액'] * fee / 100, decimal_rate)) - #진입 수수료
                                (round(self.df_trade['평가금액'] * fee / 100, decimal_rate))) #청산 수수료
        self.df_trade['수익금'] = self.df_trade['수익금'].round(decimal_rate)
        self.df_trade['수익률'] = round((self.df_trade['수익금'] / (self.df_trade['매입금액'] * (1/self.df_trade['레버리지'])) * 100), 1)
        self.df_trade['수익률'] = self.df_trade['수익률'].fillna(0)


        self.df_trade['최고수익률'] = np.where(self.df_trade['수익률'] > self.df_trade['최고수익률'],
                                                self.df_trade['수익률'], self.df_trade['최고수익률'])
        self.df_trade['최저수익률'] = np.where(self.df_trade['수익률'] < self.df_trade['최저수익률'],
                                                self.df_trade['수익률'], self.df_trade['최저수익률'])
        self.qtable_open(self.df_trade)
        최고수익률 = self.df_trade.loc[self.df_trade['ticker'] == ticker, '최고수익률'][0]
        최저수익률 = self.df_trade.loc[self.df_trade['ticker'] == ticker, '최저수익률'][0]
        if 최고수익률 > 기존최고수익률 or 최저수익률 < 기존최저수익률:
            self.df_trade.to_sql(self.stg_market, self.conn_stg, if_exists='replace')


    def chegyeol_closed(self,dict_info):
        print(f"{dict_info= }")
        uuid = list(dict_info.keys())[0]
        if uuid in self.df_trade['id'].tolist():
            stg = self.df_trade.loc[self.df_trade['id']==uuid,'전략명']
            stg = stg[0]
            before_state = self.df_trade.loc[stg,'상태']
            평단가 = self.df_trade.loc[stg,'평단가']
            기존보유수량 = self.df_trade.loc[stg,'보유수량']
            # 매입금액 = self.df_trade.loc[stg,'매입금액']
            if dict_info[uuid]['state'] == '취소':
                if before_state == '대기' or before_state == '매수주문':
                    self.df_trade.loc[stg, '상태'] = '대기'
                else:
                    self.df_trade.loc[stg, '상태'] = '에러'
            elif dict_info[uuid]['state'] == '체결':
                if before_state == '매수주문':
                    if 기존보유수량 == 0:
                        보유수량 = dict_info[uuid]['amount']
                        평단가 = dict_info[uuid]['price']
                    else:
                        평단가 = ((기존보유수량*평단가)+(dict_info[uuid]['amount']*dict_info[uuid]['price']))/(기존보유수량 + dict_info[uuid]['amount'])
                        보유수량 = 기존보유수량 + dict_info[uuid]['amount']
                    self.df_trade.loc[stg, '매입금액'] = 평단가 * 보유수량
                    수수료 = 평단가 * dict_info[uuid]['amount'] * (self.df_trade.loc[stg, '수수료율']/100)
                    self.df_trade.loc[stg, '잔고'] = self.df_trade.loc[stg, '잔고']-self.df_trade.loc[stg, '매입금액']-self.df_trade.loc[stg, '수수료']
                    self.df_trade.loc[stg, '상태'] = '매수'
                    self.df_trade.loc[stg, 'id'] = ''
                    self.df_trade.loc[stg, '주문가'] = 0
                    self.df_trade.loc[stg, '주문수량'] = 0
                    self.df_trade.loc[stg, '평단가'] = 평단가
                    self.df_trade.loc[stg, '수수료'] = 수수료
                    self.df_trade.loc[stg, '보유수량'] = 보유수량

                elif before_state == '매도주문':
                    self.df_trade.loc[stg, '상태'] = '매도'
                    self.df_trade.loc[stg, 'id'] = ''
                    self.df_trade.loc[stg, '주문가'] = 0
                    self.df_trade.loc[stg, '주문수량'] = 0
                    보유수량 = dict_info[uuid]['amount']
                    평단가 = dict_info[uuid]['price']
                    수수료 = 평단가 * 보유수량 * (self.df_trade.loc[stg, '수수료율']/100)
                    수익금 = (보유수량 * 평단가) - 수수료
                    self.df_trade.loc[stg, '보유수량'] = 보유수량
                    self.df_trade.loc[stg, '수수료'] = 수수료
                    self.df_trade.loc[stg, '평단가'] = 평단가
                    self.df_trade.loc[stg, '잔고'] = self.df_trade.loc[stg, '잔고'] + 수익금
                    cursor = self.QTE_stg_buy.textCursor()
                    # 문서의 시작으로 이동
                    cursor.movePosition(cursor.Start)
                    # 아래로 2번 이동 (0번째 = 1번째 줄이므로)
                    cursor.movePosition(cursor.Down)
                    cursor.movePosition(cursor.Down)
                    # 현재 줄 선택
                    cursor.select(cursor.LineUnderCursor)
                    # 텍스트 교체
                    cursor.insertText(f"배팅금액 = {self.df_trade.loc[stg, '잔고']}")
                else:
                    state = '에러'
            elif dict_info[uuid]['state'] == '미체결':
                return

            print(self.df_trade)
            dict_orders = self.make_dict_orders()
            self.send_orders.emit(dict_orders)
            self.df_trade.to_sql(self.stg_market, self.conn_stg, if_exists='replace')
            self.qtable_open(self.df_trade)
            df = self.df_trade.loc[[stg]].copy()
            self.qtable_closed(df)
        else:
            print(f"id 없음 {uuid=}   |   {self.df_trade['id'].tolist()}")

    @pyqtSlot()
    def slot_clicked_button(self):
        """
        사용자정의 슬롯
        쓰레드의 status 상태 변경
        버튼 문자 변경
        쓰레드 재시작
        """
        # self.thread.toggle_status()
        # self.pb.setText({True: "Pause", False: "Resume"}[self.th.status])
        self.QPB_start.setStyleSheet("background-color: #cccccc;")
        self.timer.stop()
        self.thread_ws.stop()
    def qtable_open(self, df):
        df['상태[분할]'] = df['분할상태'].copy()
        df['보유수량[분할]'] = df['분할보유수량'].copy()
        df_active = df[['전략명', 'ticker', '상태', '수익률','수익금', '최고수익률', '최저수익률', '매입금액','평단가', '현재가','주문가', '상태[분할]',
                        '주문수량', '보유수량', '보유수량[분할]', '승률(win/all)', '평가금액', '잔고', '진입시간', '매도전환']].copy()
        df_active['평단가'] = df_active['평단가'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['현재가'] = df_active['현재가'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['주문가'] = df_active['주문가'].apply(lambda int_num : "{:,}".format(int_num))
        # df_active['수익금'] = df_active['수익금'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['매입금액'] = df_active['매입금액'].round()
        df_active['매입금액'] = df_active['매입금액'].apply(lambda int_num : "{:,}".format(int_num))
        # df_active['평가금액'] = df_active['평가금액'].apply(lambda int_num : "{:,}".format(int_num))
        df_active['잔고'] = df_active['잔고'].apply(lambda int_num : "{:,}".format(int_num))
        # df = df.loc[df['상태'] != '청산'] # 청산 상태가 아닌 행을 저장
        # df_active = df.loc[df['상태'] != '매수주문'] # 매수주문 상태가 아닌 행을 저장
        # df_active['전략명'] = df_active.index
        # df_active = df_active[['market','전략명','ticker','수익률','최고수익률','최저수익률','진입가','현재가','상태','승률(win/all)','수익금','진입시간']]
        self.set_table_make(self.QT_trade_open, df_active)

    def qtable_closed(self, df):
        if df.empty:
            pass
        else:
            if not self.df_history.equals(df): # 초기에 qtable에 history를 표기하기위해 기존의 데이터를 불러오기 때문에 기존데이터를 위, 아래로 붙이므로 중복행일 경우는 무시하고 신규 데이터 일 때만 위라래로 붙임
                self.df_history = pd.concat([self.df_history, df])  # 데이터프레임끼리 위, 아래로 붙이기
                try:
                    self.df_history.to_sql('history', self.conn_stg, if_exists='replace')
                    self.df_history['전략명'] = self.df_history.index
                except:
                    list_col = self.df_history.columns.tolist()
                    print('tab_trade  qtable_open : ')
                    print(f"{list_col= }")
                    for i, col in enumerate(list_col):
                        df_copy = self.df_history[[col]]
                        self.df_history = self.df_history.drop(col, axis=1)

                        try:
                            self.df_history.to_sql('history', self.conn_stg, if_exists='replace')
                            # time.sleep(1)
                            print('qtable_open 에러----')
                            print(f"{i= }")
                            print(f"{col= }")
                            print(f"{df_copy}")
                            # print(f"{self.df_stg[col].dtype= }")
                            quit()
                        except:
                            pass
        df_history = self.df_history[['market', '전략명', 'ticker', '수익률', '최고수익률', '최저수익률', '수익금',
                                      '누적수익금', '잔고','매입금액','수수료','진입시간', '청산시간']]
        df_history = df_history[df_history['청산시간'].str[:10]==datetime.datetime.now().date().strftime('%Y-%m-%d')] #오늘 청산한 전략만
        # df_history['평단가'] = df_history['평단가'].apply(lambda int_num : "{:,}".format(int_num))
        # df_history['청산가'] = df_history['청산가'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['수익금'] = df_history['수익금'].apply(lambda int_num : "{:,}".format(int_num))
        #nan 값을 0으로 대체
        # df_history['누적수익금'] = df_history['누적수익금'].fillna(0).apply(lambda x: "{:,}".format(int(x)))
        df_history['누적수익금'] = df_history['누적수익금'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['수수료'] = df_history['수수료'].apply(lambda int_num : "{:,}".format(int_num))
        df_history['매입금액'] = df_history['매입금액'].apply(lambda int_num : "{:,}".format(int_num))
        # df_history['청산금액'] = df_history['청산금액'].apply(lambda int_num : "{:,}".format(int_num))
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
        if num == "open": # table_open 클릭 시
            row = self.QT_trade_open.currentRow()
            stg = self.QT_trade_open.item(int(row), 0).text()
        elif num == "closed": # table_close 클릭 시
            row = self.QT_trade_closed.currentRow()
            stg = self.QT_trade_closed.item(int(row), 0).text()

        stg_buy = self.df_trade.loc[stg, '진입전략']
        stg_sell = self.df_trade.loc[stg, '청산전략']
        ticker = self.df_trade.loc[stg, 'ticker']
        self.QTE_stg_buy.setText(stg_buy)
        self.QTE_stg_sell.setText(stg_sell)
        self.QLE_stg.setText(stg)
        self.QCB_stgs.setCurrentText(stg)
        # if ticker != "":
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
        # bong_detail = self.QCB_chart_bong_detail.currentText()
        bong_since = self.QCB_chart_duration.currentText()
        market = self.QCB_market.currentText()
        present = datetime.datetime.now()

        ticker_full_name = ticker+'_chart'
        if bong_since == '기간(일)':
            bong_since = 1
        date_old = present.date() - datetime.timedelta(days=int(bong_since))
        since = common_def.datetime_to_stamp(date_old)
        ohlcv = []
        if market == 'bybit' or market == 'binance' :
            ohlcv = common_def.get_coin_ohlcv(market, self.dict_option["exchange"], ohlcv, since, ticker, bong_detail)
            df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
            df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
            df['날짜'] = df['날짜'].dt.tz_localize(None)
            df.set_index('날짜', inplace=True)
            df.index = df.index - pd.Timedelta(hours=9)
            df_standard, df = common_def.detail_to_spread(df, bong, bong_detail,False)
            # df.index = df.index + pd.Timedelta(hours=9)
        if market == '국내선옵' or market == '국내주식' :
            ohlcv = self.dict_option["exchange"].fetch_1m_ohlcv(symbol=ticker, limit=int(bong_since),ohlcv=[],
                                               now_day=datetime.datetime.strftime(present,"%Y%m%d"),
                                               now_time=datetime.datetime.strftime(present,"%H%M%S"),
                                               night=False)
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
        # bong_detail = self.QCB_chart_bong_detail.currentText()
        bong_since = self.QCB_chart_duration.currentText()
        market = self.QCB_market.currentText()
        present = datetime.datetime.now()
        ticker_full_name = ticker+'_chart'
        if bong_since == '기간(일)':
            bong_since = 1
        date_old = datetime.datetime.now().date() - datetime.timedelta(days=int(bong_since))
        since = common_def.datetime_to_stamp(date_old)
        ohlcv = []
        if market == 'bybit' or market == 'binance' :
            df = common_def.get_coin_ohlcv(market, self.dict_option["ex_bybit"], ohlcv, since, ticker, bong_detail)
            df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
            df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
            df['날짜'] = df['날짜'].dt.tz_localize(None)
            df.set_index('날짜', inplace=True)
            df.index = df.index - pd.Timedelta(hours=9)
            df_standard, df = common_def.detail_to_spread(df, bong, bong_detail,False)
            # df.index = df.index + pd.Timedelta(hours=9)
        if market == '국내선옵' :
            ohlcv = self.ex_kis.fetch_1m_ohlcv(symbol=ticker, limit=int(bong_since),ohlcv=[],
                                               now_day=datetime.datetime.strftime(present,"%Y%m%d"),
                                               now_time=datetime.datetime.strftime(present,"%H%M%S"))
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
            buy_price_division = json.loads(df_stg.iloc[i, list_col.index('분할주문가')])
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
            # sell_price_division = json.loads(df_stg.iloc[i, list_col.index('분할청산가')])
            for j, time in enumerate(sell_time_division):
                if time != '':
                    time = time[:-2] + '00'
                    time = common_def.str_to_datetime(time)
                    if sell_price_division[j] != 0:
                        dict_sell[time] = sell_price_division[j]
            sell_time = df_stg.iloc[i, list_col.index('청산시간')]
            # sell_price = df_stg.iloc[i, list_col.index('청산가')]
            if sell_price != 0:
                sell_time = sell_time[:-2] + '00'
                sell_time = common_def.str_to_datetime(sell_time)
                dict_sell[sell_time] = sell_price


            buy_time_division = json.loads(df_stg.iloc[i, list_col.index('주문시간')])
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

    def check_compare_ticker(self, stg_buy, stg_sell):
        lines = stg_buy.splitlines()  # 줄로 나누기
        stg_buy = "\n".join(lines[5:])  # 첫 줄 제외하고 다시 합치기
        stg = stg_buy + stg_sell
        list_compare = []
        list_tickers = ['미니선물','선물','BTC','ETH','XRP','KODEX레버리지']
        for ticker in list_tickers:
            while ticker in stg:
                ticker_full_name = stg[stg.index(ticker):stg.index('봉') + 1]
                stg = stg.replace(ticker_full_name, '*')
                list_compare.append(ticker_full_name)
        # if '풋옵션' in stg and ticker[:1] == '2':
            # symbol = '3' + ticker[1:]
            #                 stg = stg.replace('풋옵션', symbol)
            # list_compare.append('풋옵션')
        # if '콜옵션' in stg and ticker[:1] == '3':
            # symbol = '2' + ticker[1:]
            #                 stg = stg.replace('콜옵션', symbol)
            # list_compare.append('콜옵션')
        return list_compare
    def load_compare_data(self,list_compare,stg):
        for symbol in list_compare:
            #                 print(f"{symbol= }")
            if symbol in stg:
                #                 #     print(f"--------in--------")
                stg_sum_copy = stg
                list_bong = []
                while symbol in stg_sum_copy:
                    #                         print(stg_sum_copy)
                    #                         print('***************')
                    stg_sum_copy = stg_sum_copy[stg_sum_copy.index(symbol):]
                    #                         print(stg_sum_copy)
                    #                         print('***************')
                    if '봉' in stg_sum_copy:
                        ticker_full_name = stg_sum_copy[:stg_sum_copy.index('봉') + 1]
                        stg_sum_copy = stg_sum_copy.replace(ticker_full_name, '')
                        bong = ticker_full_name[ticker_full_name.index('_') + 1:]
                        list_bong.append(bong)
                    #                             print(f"{dict_stg_stg['비교대상']=}")
                    else:
                        break
                #                         print('----------------------')
                dict_stg_stg[symbol] = list_bong
        # if '외인' in stg or '개인' in stg or '기관' in stg:
        #     dict_stg_stg['수급동향'] = True
        # dict_stg_stg['비교대상']['301W01337'] = '5분봉'
        return dict_stg_stg
    def show_shutdown_dialog(self):
        # self.onStopButtonClicked()
        print('프로그램 종료')
        # self.close() #프로그램 종료
        # 종료 알람 다이얼로그 표시
        self.shutdown_dialog = ShutdownDialog()
        self.shutdown_dialog.exec_()

        # 다이얼로그가 닫힌 후 버튼 상태 복원
        # self.start_button.setEnabled(True)
        # self.start_button.setText('시작')
    def manual_trade(self):
        self.state_manual_trade = not self.state_manual_trade
        if self.state_manual_trade == True:
            self.QPB_manual.setStyleSheet("background-color: #fa3232;")
            self.dict_option["exchange_ws"].subscribe('H0MFCNT0', ['A01606','A05606'])  # 야간선물 체결
            self.dict_option["exchange_ws"].start()
        else:
            self.QPB_manual.setStyleSheet("background-color: #cccccc;")
    def keyPressEvent(self, event):
        if self.state_manual_trade == True:
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
    def pop_message(self,title,message):
        QMessageBox.about(self,title,message)
    def time_sync(self):
        print(datetime.datetime.now())
        subprocess.Popen('python timesync.py')
    def no_saving_mode(self):
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001

        # 절전모드 방지 시작
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        )
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
        self.shutdown_button = QPushButton('윈도우종료')
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

        print('윈도우 종료')
        os.system("shutdown /s /t 0") #윈도우 죵료

        # print('윈도우 절전모드')
        # os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0") #윈도우 절전모드
        self.close()

    def cancel_shutdown(self):
        self.shutdown_timer.stop()
        print('윈도우 종료 취소')
        self.close()


if __name__ == "__main__":
    # pg.setConfigOption('background', 'k')
    # pg.setConfigOption('foreground', 'w')

    app = QApplication([])
    main_table = Window()
    main_table.setMinimumSize(600, 400)
    main_table.show()
    app.exec()

    # main()
