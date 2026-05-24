import sqlite3
import datetime
import time
from pandas import to_numeric

from pprint import pprint
import pandas as pd
from PyQt5.QtWidgets import QMainWindow,QTableWidgetItem,QHeaderView,QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import numpy as np
import pyqtgraph as pg
# import crosshair
# import tab_ccxt
import color as cl
# import talib as ta
import ccxt
import warnings
# import tab_chart_table
import random
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex,QTimer,pyqtSlot,QObject
warnings.filterwarnings('ignore')
from PyQt5.QtWidgets import QMainWindow,QGridLayout,QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QTableWidget,QSplitter,QApplication,QCheckBox,QTextEdit,QTableWidgetItem,QHeaderView,QComboBox
# import ATOM_trade_numpy
# import talib
import common_def
import ATOM_chart_numpy
from PyQt5.QtTest import *
import KIS


# class DateAxisItem(pg.AxisItem):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def tickStrings(self, values, scale, spacing):
#         return [QtCore.QDateTime.fromSecsSinceEpoch(value, QtCore.Qt.UTC).toTimeZone(
#             QtCore.QTimeZone(b"Asia/Seoul")).toString("yyyy-MM-dd HH:mm") for value in values]


# class Graph(QMainWindow):
# class Graph(QThread):
class Graph(QObject):
    def __init__(self, parent,market):
        super().__init__(parent)
        self.chart_table(market)
        self.chart_main = QMainWindow()
        self.ticker = "ticker"
        self.bong = "bong"
        self.bong_detail = "bong_detail"
        self.set_UI()
        # self.market = market
        # self.dict_bong_since = {'3분봉': 1, '5분봉': 3, '30분봉': 5, '60분봉': 100, '4시간봉': 120,'일봉': 240}  # 3분봉은 15일치의 데이터 일봉은 240일의 데이터를 사용
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
        self.dict_bong_stamp ={'1분봉': 1*60, '3분봉': 3*60, '5분봉': 5*60, '15분봉': 15*60, '30분봉': 30*60, '60분봉': 60*60, '4시간봉': 240*60, '일봉': 1440*60,
                           '주봉': 10080*60}

    def set_UI(self):
        self.sub_chart = SubGraph()
        # self.sub_chart.setMinimumSize(1200, 800)
        # self.setLayout(self.sub_chart)
        self.chart_main.setCentralWidget(self.sub_chart)
        self.chart_tic = 1000
        self.x = np.arange(self.chart_tic)  # 100 time points
        self.nan = np.array([np.nan for _ in range(self.chart_tic)])
        self.bi_close = np.array([np.nan for _ in range(self.chart_tic)])


        for i,li in enumerate(self.list_QTE0_0):
            globals()[f"p0_0_{li}"] = self.sub_chart.p0_0.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE0_1):
            globals()[f"p0_1_{li}"] = self.sub_chart.p0_1.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE0_2):
            globals()[f"p0_2_{li}"] = self.sub_chart.p0_2.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE0_3):
            globals()[f"p0_3_{li}"] = self.sub_chart.p0_3.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE1_0):
            globals()[f"p1_0_{li}"] = self.sub_chart.p1_0.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE1_1):
            globals()[f"p1_1_{li}"] = self.sub_chart.p1_1.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE1_2):
            globals()[f"p1_2_{li}"] = self.sub_chart.p1_2.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE1_3):
            globals()[f"p1_3_{li}"] = self.sub_chart.p1_3.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE2_0):
            globals()[f"p2_0_{li}"] = self.sub_chart.p2_0.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE2_1):
            globals()[f"p2_1_{li}"] = self.sub_chart.p2_1.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE2_2):
            globals()[f"p2_2_{li}"] = self.sub_chart.p2_2.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)
        for i,li in enumerate(self.list_QTE2_3):
            globals()[f"p2_3_{li}"] = self.sub_chart.p2_3.plot(self.x, self.nan, pen=random.choice(cl.li), name=li)

        self.sub_chart.p0_0.setTitle(f"{self.ticker}")
        # self.p_current = self.sub_chart.p0_0.plot(self.x, self.nan, pen=cl.red,width=2, name='current')
        # self.p_ma1680 = self.sub_chart.p0_0.plot(self.x, self.nan, pen=cl.dot_w, name='ma1680')
        # self.p_ma3000 = self.sub_chart.p0_0.plot(self.x, self.nan, pen=cl.dot_g, name='ma3000')
        # # self.p_buy = self.sub_chart.p0_0.plot(self.x, self.nan, pen=cl.dot_r, name='buy')
        # # self.p_long1 =  self.sub_chart.p0_0.plot(self.x, self.nan,symbolBrush=(200,0,0),symbolPen=(51,255,51),symbol='t1',symbolSize=10,name="진입")
        # # self.p_short1 = self.sub_chart.p0_0.plot(self.x, self.nan,pen=None,symbolBrush=(0,0,200),symbolPen=(51,255,51),symbol='t',symbolSize=10,name="청산")
        # self.p_buy = self.sub_chart.p0_0.plot(self.x, self.nan,pen=None,symbolBrush=(0,0,200),symbolPen=(51,255,51),symbol='t1',symbolSize=10,name="롱")
        # self.p_buy_close = self.sub_chart.p0_0.plot(self.x, self.nan,pen=None,symbolBrush=(0,0,200),symbolPen=(51,255,51),symbol='o',symbolSize=10,name="청산")
        # self.p_sell = self.sub_chart.p0_0.plot(self.x, self.nan,pen=None,symbolBrush=(200,0,0),symbolPen=(51,255,51),symbol='t',symbolSize=10,name="숏")
        # self.p_sell_close = self.sub_chart.p0_0.plot(self.x, self.nan,pen=None,symbolBrush=(200,0,0),symbolPen=(51,255,51),symbol='o',symbolSize=10,name="청산")

    # def stop(self):
    #     print('chart stop')
    #     self.df = pd.DataFrame()

    # def run(self):
    #     print('run')
    #     # self.set_UI()
    #     # self.make_init_data(self.market,self.ticker,self.bong,self.bong_detail)
    #     self.time_Var.timeout.connect(self.get_data)
    #     # self.time_Var.timeout.connect(self.make_df)
    #     self.time_Var.start(5000)
    #     self.exec_()  # 이벤트 루프 실행


    # def get_data(self):
    #     ticker_full_name = f'{self.ticker}_{self.bong}_{self.bong_detail}'
    #
    #     self.df = self.make_df(ticker_full_name, self.ticker, self.bong, self.bong_detail, self.duration)
    #     # if self.list_compare:
    #     #     self.df = self.add_compare_df(self.ticker, self.df, self.bong, self.list_compare, self.bong_detail, self.duration)
    #
    #     self.update_plot_data()
    #
    # def make_df(self,ticker_full_name, ticker, bong, bong_detail, bong_since):
    #     if self.dict_option['market'] =='국내주식':
    #         if ticker_full_name in globals():  # 만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
    #             ohlcv = globals()[ticker_full_name]
    #             if bong == '일봉':
    #                 if not ohlcv.empty:
    #                     df = common_def.convert_df(ohlcv)
    #                     dict_output = self.ex_kis.fetch_price(ticker)
    #                     today = pd.to_datetime(datetime.datetime.now().date())
    #                     df.loc[today,'시가'] = int(dict_output['stck_oprc'])
    #                     df.loc[today,'고가'] = int(dict_output['stck_hgpr'])
    #                     df.loc[today,'저가'] = int(dict_output['stck_lwpr'])
    #                     df.loc[today,'종가'] = int(dict_output['stck_prpr'])
    #                     df.loc[today,'거래대금'] = int(dict_output['acml_tr_pbmn'])
    #                     df.loc[today,'거래량'] = int(dict_output['acml_vol'])
    #                     df.loc[today,'전일대비거래량비율'] = float(dict_output['prdy_vrss_vol_rate'])
    #                     df.loc[today,'외국인순매수수량'] = int(dict_output['frgn_ntby_qty'])
    #                     df.loc[today,'프로그램매매순매수수량'] = int(dict_output['pgtr_ntby_qty'])
    #                     df.loc[today,'PER'] = float(dict_output['per'])
    #                     df.loc[today,'PBR'] = float(dict_output['pbr'])
    #                     df.loc[today,'EPS'] = float(dict_output['eps'])
    #                     df.loc[today,'BPS'] = float(dict_output['bps'])
    #                     df.loc[today,'52주최고가'] = int(dict_output['w52_hgpr'])
    #                 else:
    #                     df = ohlcv
    #             else:
    #                 to = ohlcv[0]['stck_cntg_hour']
    #                 output = self.ex_kis._fetch_1m_ohlcv(symbol=ticker,to=datetime.datetime.now().strftime("%H%M%S"),fake_tick=True)  # to = 현재시간, 허봉 포함
    #                 output = output['output2']
    #                 list_cntg_hour = [item['stck_cntg_hour'] for item in output]  # 딕셔너리의 시간을 리스트로 변환
    #                 if to in list_cntg_hour:
    #                     output = output[:list_cntg_hour.index(to) + 1]
    #                     del ohlcv[0]  # 마지막행은 불완전했던 행 이였으므로 삭제
    #                     output.extend(ohlcv)
    #                     ohlcv = output
    #                     globals()[ticker_full_name] = ohlcv
    #         else:  # 최초 생성 시
    #             if bong == '일봉':
    #                 date_old = datetime.datetime.now().date() - datetime.timedelta(days=int(bong_since))
    #                 date_old = datetime.datetime.strftime(date_old,'%Y%m%d')
    #                 df = self.ex_kis.fetch_ohlcv(symbol=ticker,early_day=date_old)
    #                 if not df.empty:
    #                     globals()[ticker_full_name] = df.copy()
    #                     df = common_def.convert_df(df)
    #             else:
    #                 df = common_def.get_kis_ohlcv(self.dict_option['market'],[])
    #                 if ticker_full_name.count('_') == 2:  # 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
    #                     df_standard, df = common_def.detail_to_spread(df, bong, bong_detail, False)
    #                 else:  # 비교대상의 경우 'BTC_5분봉'
    #                     df = common_def.detail_to_compare(df, bong, ticker_full_name)
    #
    #     elif self.dict_option['market'] == '국내선옵':
    #         if ticker_full_name in globals():  # 만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
    #             ohlcv = globals()[ticker_full_name]
    #             # to = ohlcv[0]['stck_cntg_hour']
    #             # output = self.ex._fetch_1m_ohlcv(symbol=ticker,to=datetime.datetime.now().strftime("%H%M%S"),fake_tick=True)  # to = 현재시간, 허봉 포함
    #             # output = output['output2']
    #             # list_cntg_hour = [item['stck_cntg_hour'] for item in output]  # 딕셔너리의 시간을 리스트로 변환
    #             # if to in list_cntg_hour:
    #             #     output = output[:list_cntg_hour.index(to)+1]
    #             #     del ohlcv[0]  # 마지막행은 불완전했던 행 이였으므로 삭제
    #             #     output.extend(ohlcv)
    #             #     ohlcv = output
    #             #     globals()[ticker_full_name] = ohlcv
    #             현재시간 = datetime.datetime.now().replace(second=0, microsecond=0)
    #             now_day = 현재시간.date().strftime("%Y%m%d")
    #             now_time = 현재시간.strftime("%H%M") + "00"  # 마지막에 초는 00으로
    #         else: # 최초 생성 시
    #             now_day = datetime.datetime.now().date()
    #             now_day = now_day.strftime("%Y%m%d")
    #             now_time = datetime.datetime.now().strftime("%H%M%S")
    #             ohlcv = []
    #         ohlcv = self.ex.fetch_1m_ohlcv(symbol=ticker,
    #                                        limit=int(bong_since),
    #                                        ohlcv=ohlcv,
    #                                        now_day=now_day,
    #                                        now_time=now_time)
    #         globals()[ticker_full_name] = ohlcv
    #         df = common_def.get_kis_ohlcv(self.dict_option['market'],ohlcv)
    #         if ticker_full_name.count('_') == 2:  # 진입대상인지 비교대상인지 확인 - 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
    #             df_standard, df = common_def.detail_to_spread(df, bong, bong_detail, False)
    #         else:  # 비교대상의 경우 'BTC_5분봉'
    #             df = common_def.detail_to_compare(df, bong, ticker_full_name)
    #     elif self.dict_option['market'] =='코인':
    #         if f'{ticker_full_name}' in globals(): #만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
    #             ohlcv = globals()[f'{ticker_full_name}']
    #             stamp_date_old = ohlcv[-1][0]/1000
    #             # del globals()[f'{ticker_full_name}'][-1]  # 마지막행은 불완전했던 행 이였으므로 삭제
    #             del ohlcv[-1]  # 마지막행은 불완전했던 행 이였으므로 삭제
    #         else: #만들어진 df가 없을 경우 (최초 DF생성 시)
    #             ohlcv = []
    #             date_old = datetime.datetime.now().date() - datetime.timedelta(days=int(bong_since))
    #             stamp_date_old = common_def.datetime_to_stamp(date_old)
    #         ohlcv = common_def.get_bybit_ohlcv(self.ex, ohlcv, stamp_date_old, ticker_full_name, ticker, bong, bong_detail)
    #         globals()[ticker_full_name] = ohlcv
    #         df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
    #         df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
    #         df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
    #         df['날짜'] = df['날짜'].dt.tz_localize(None)
    #         df.set_index('날짜', inplace=True)
    #         df.index = df.index - pd.Timedelta(hours=9)
    #         if ticker_full_name.count('_') == 2: # 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
    #             df_standard, df = common_def.detail_to_spread(df, bong, bong_detail, False)
    #         else: # 비교대상의 경우 'BTC_5분봉'
    #             df = common_def.detail_to_compare(df, bong, ticker_full_name)
    #         df.index = df.index + pd.Timedelta(hours=9)
    #
    #     else:
    #         df=pd.DataFrame()
    #     return df
    def check_compare_ticker(self, list_table, list_tickers):
        list_compare = []
        for factor in list_table:
            for compare_ticker in list_tickers:
                if compare_ticker in factor:
                    i = factor.index(compare_ticker)
                    factor = factor[i:]
                    while compare_ticker in factor:
                        # list_compare.append(factor)
                        if '봉' in factor:
                            bong_len = factor.index('봉')
                        else:
                            bong_len = 0
                        if bong_len > 10:
                            factor = factor[1:]
                        else:
                            compare_ticker_name = factor[:bong_len + 1]
                            factor = factor.replace(compare_ticker_name, '')
                            list_compare.append(compare_ticker_name)
        list_compare = list(set(list_compare))
        list_compare = [x for x in list_compare if len(x) < 1]
        return  list_compare

    @pyqtSlot(str,str,str,str)
    def make_init_data(self,dict_option):
        print(f'make_init_data')

        # list_table = self.chart_table(dict_option['real_chart'])
        self.dict_option = dict_option
        # self.ticker = ticker
        # self.bong = bong
        # self.duration = duration
        self.set_UI()


        self.list_df_duplicated=[]

        self.dict_chart_0_0 = {}
        self.dict_chart_0_1 = {}
        self.dict_chart_0_2 = {}
        self.dict_chart_0_3 = {}
        self.dict_chart_1_0 = {}
        self.dict_chart_1_1 = {}
        self.dict_chart_1_2 = {}
        self.dict_chart_1_3 = {}
        self.dict_chart_2_0 = {}
        self.dict_chart_2_1 = {}
        self.dict_chart_2_2 = {}
        self.dict_chart_2_3 = {}
        self.ohlcv = []



    def chart_table(self,market):
        if not market=='empty':
            conn = sqlite3.connect('DB/chart_table.db')
            self.df_chart_table = pd.read_sql(f"SELECT * FROM '{market}'", conn).set_index('index')
        else:
            self.df_chart_table = pd.DataFrame(index=['p0_0','p0_1','p0_2','p0_3','p1_0','p1_1','p1_2','p1_3','p2_0','p2_1','p2_2','p2_3'],columns=['chart'])
            self.df_chart_table = self.df_chart_table.fillna('')
        self.list_QTE0_0 = self.df_chart_table.loc['p0_0','chart'].splitlines()
        self.list_QTE0_1 = self.df_chart_table.loc['p0_1','chart'].splitlines()
        self.list_QTE0_2 = self.df_chart_table.loc['p0_2','chart'].splitlines()
        self.list_QTE0_3 = self.df_chart_table.loc['p0_3','chart'].splitlines()
        self.list_QTE1_0 = self.df_chart_table.loc['p1_0','chart'].splitlines()
        self.list_QTE1_1 = self.df_chart_table.loc['p1_1','chart'].splitlines()
        self.list_QTE1_2 = self.df_chart_table.loc['p1_2','chart'].splitlines()
        self.list_QTE1_3 = self.df_chart_table.loc['p1_3','chart'].splitlines()
        self.list_QTE2_0 = self.df_chart_table.loc['p2_0','chart'].splitlines()
        self.list_QTE2_1 = self.df_chart_table.loc['p2_1','chart'].splitlines()
        self.list_QTE2_2 = self.df_chart_table.loc['p2_2','chart'].splitlines()
        self.list_QTE2_3 = self.df_chart_table.loc['p2_3','chart'].splitlines()
        list_table = list(set(self.list_QTE0_0) | set(self.list_QTE0_1) | set(self.list_QTE0_2) | set(self.list_QTE0_3) | set(self.list_QTE1_0) | set(self.list_QTE1_1) | set(self.list_QTE1_2) | set(self.list_QTE1_3) | set(self.list_QTE2_0) | set(self.list_QTE2_1) | set(self.list_QTE2_2) | set(self.list_QTE2_3))
        return list_table

    def add_compare_df(self, ticker_main, df, bong_main, list_compare, bong_detail, bong_since):
        list_idx = df.index.tolist()
        for com_ticker_bong in list_compare:
            if '풋옵션' == com_ticker_bong[:3] or '콜옵션' == com_ticker_bong[:3]:
                t = '3' if ticker_main[:1] == '2' else '2'
                ticker = t + ticker_main[1:]
                if '_' in com_ticker_bong:
                    bong = com_ticker_bong[com_ticker_bong.index('_') + 1:]
                else:
                    bong = bong_main
            elif '_' in com_ticker_bong:
                ticker = com_ticker_bong[:com_ticker_bong.index('_')]
                bong = com_ticker_bong[com_ticker_bong.index('_') + 1:]
            ticker_full_name = f'{ticker}_{bong}'
            df_compare = self.make_df(ticker_full_name, ticker, bong, bong_detail, bong_since)
            if '풋옵션' == com_ticker_bong[:3] or '콜옵션' == com_ticker_bong[:3]:
                df_compare.columns = [col.replace(ticker_full_name, com_ticker_bong) for col in df_compare.columns]
            if bong != '일봉' and bong != '주봉':  # 분봉일 경우
                df = pd.merge(df, df_compare, left_index=True, right_index=True, how='left')
            elif bong == '일봉':
                df['date'] = df.index.date
                df_compare['date'] = df_compare.index.date
                df = df.merge(df_compare, on='date',how='left', suffixes=('', '_daily')) # how='left' df_compare에 값이 없을 경우 nan
                df.drop('date', axis=1, inplace=True)
            elif bong == '주봉':
                df['week'] = df.index.to_period('W').astype(str)
                df_compare['week'] = df_compare.index.to_period('W').astype(str)
                df = df.merge(df_compare, on='week',how='left', suffixes=('', '_weekly'))
                df.drop('week', axis=1, inplace=True)
            if [x for x in df.columns.tolist() if '_y' in x]:
                print('add_compare_df _y 들어가있음')
                quit()
            df.ffill(inplace=True)
            try:
                df.index = list_idx
            except:
                df.index = list_idx
        return df

    def update_plot_data(self,df):
        if self.dict_option['market'] == '국내주식' or self.dict_option['market'] == '국내선옵':
            list_x = [dt.strftime('%H:%M') if dt.minute % 60 == 0 else '' for dt in df.index]
            list_num = np.arange(len(df))
            self.x = dict(zip(list_num,list_x))
            self.x = dict(enumerate(list_x))

            self.sub_chart.bottomAxis0_0.setTicks([self.x.items()])
            # self.sub_chart.bottomAxis0_0.setStyle(tickTextAngle=45)
            self.x = list(self.x.keys())
        elif self.dict_option['market'] == '업비트' or self.dict_option['market'] == 'bybit':
            self.x = np.arange(len(df))
            self.x = [x.timestamp() for x in pd.to_datetime(df.index)]


            # self.sub_chart.p0_0 = self.sub_chart.addPlot(row=0, col=0, title='p0_0', axisItems={'bottom': pg.DateAxisItem()})
            # list_x = [dt.strftime('%H:%M') if dt.minute % 60 == 0 else '' for dt in self.df.index]
            # list_num = np.arange(len(self.df))
            # self.x = dict(zip(list_num,list_x))
            # self.x = dict(enumerate(list_x))
            #
            # self.sub_chart.bottomAxis0_0.setTicks([self.x.items()])
        # print(self.x)

        ################################################################################# 연산으로 표시 가능

        dict_plot = ATOM_chart_numpy.chart_np(df,self.df_chart_table)
        for plot_num in dict_plot.keys():
            for factor, data in dict_plot[plot_num].items():
                # data = np.asarray(data, dtype=float) #데이터 넘기기전에 float으로 변환
                if factor == '매수가' or factor == '매도가' or factor == '전략매수' or factor == '전략매도' \
                        or factor == '맥점매수' or factor == '맥점매도':
                    if '매수가' in factor:
                        globals()[plot_num].setData(x=self.x, y=data, pen=None, symbolBrush=(200, 0, 0),
                                                 symbolPen=(51, 255, 51), symbol='t1', symbolSize=10,
                                                 name="진입")  # 마커
                    elif '매도가' in factor:
                        globals()[plot_num].setData(x=self.x, y=data, pen=None, symbolBrush=(0, 0, 200),
                                                 symbolPen=(51, 255, 51), symbol='t', symbolSize=10, name="청산")
                    elif '전략매수' in factor:
                        globals()[plot_num].setData(x=self.x, y=data, pen=None, symbolBrush=cl.red_1,
                                                 symbolPen=cl.red_1, symbol='d', symbolSize=10, name="전략매수")
                    elif '전략매도' in factor:
                        globals()[plot_num].setData(x=self.x, y=data, pen=None, symbolBrush=cl.ygreen_2,
                                                 symbolPen=cl.ygreen_2, symbol='d', symbolSize=10, name="전략매도")
                # elif '_' in factor:
                #     globals()[plot_num].setData(x=self.x, y=data, pen=cl.dash_k,
                #                              name=factor.replace('<', "＜"))  # 마커

                else:
                    if '.cl' in factor:
                        colors = 'cl=' + factor[factor.rindex('.cl') + 1:]  # cl.red 를 cl=cl.red 로 바꿈
                        locals_dict_vars = {}
                        exec(colors, None,locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
                        globals()[plot_num].setData(x=self.x, y=data, pen=locals_dict_vars.get('cl'),
                                                 name=factor[:factor.index('.cl')])  # 마커
                    elif '.fill' in factor:
                        level = int(factor[factor.index('.fill') + 6:-1])
                        globals()[plot_num].setData(x=self.x, y=data, pen=cl.cyan, fillLevel=level,
                                                 brush=(50, 50, 200, 200),
                                                 name=factor.replace('<', "＜"))  # 마커
                    else:
                        # try:
                        globals()[plot_num+'_'+factor].setData(x=self.x, y=data, name=factor.replace('<', "＜"))  # 마커 < 로 할 경우 짤림
                        # except:
                        #     print(plot_num)
                        #     print(factor)
                        #     pprint(data)
                        #     quit()

                        # if self.market == '코인':
                        #     globals()[plot_num+'_'+factor].setData(x=self.x, y=data, name=factor.replace('<', "＜"))  # 마커 < 로 할 경우 짤림
                        #
                        # elif self.market == '국내주식' or self.market == '국내선옵':
                        #     globals()[plot_num+'_'+factor].setData(x=list(self.x.keys()), y=data, name=factor.replace('<', "＜"))  # 마커 < 로 할 경우 짤림


class SubGraph(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        # bottomAxis_8_0 = pg.AxisItem(orientation='bottom')
        # bottomAxis_8_1 = pg.AxisItem(orientation='bottom')
        # bottomAxis_8_2 = pg.AxisItem(orientation='bottom')
        # bottomAxis_8_3 = pg.AxisItem(orientation='bottom')
        # bottomAxis_8_4 = pg.AxisItem(orientation='bottom')
    # def set_chart(self):
    #     self.win = pg.GraphicsLayoutWidget(self)  # pyqtgraph
    #     self.bottomAxis_0 = pg.AxisItem(orientation='bottom')
    #     self.bottomAxis_0.setTicks([1,2,3])


        # self.p0_0 = self.addPlot(row=0, col=0, title='0_0', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p1_0 = self.addPlot(row=1, col=0, title='1_0', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p2_0 = self.addPlot(row=2, col=0, title='2_0', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p0_1 = self.addPlot(row=0, col=1, title='0_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p1_1 = self.addPlot(row=1, col=1, title='1_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p2_1 = self.addPlot(row=2, col=1, title='2_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p0_2 = self.addPlot(row=0, col=2, title='0_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p1_2 = self.addPlot(row=1, col=2, title='1_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p2_2 = self.addPlot(row=2, col=2, title='2_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p0_3 = self.addPlot(row=0, col=3, title='0_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p1_3 = self.addPlot(row=1, col=3, title='1_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        self.p2_3 = self.addPlot(row=2, col=3, title='2_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})

        ############ 이하 x축 str 타입으로 표기
        self.bottomAxis0_0 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis1_0 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis2_0 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis0_1 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis1_1 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis2_1 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis0_2 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis1_2 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis2_2 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis0_3 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis1_3 = pg.AxisItem(orientation='bottom')
        # self.bottomAxis2_3 = pg.AxisItem(orientation='bottom')
        self.p0_0 = self.addPlot(row=0, col=0, title='0_0', axisItems={'bottom': self.bottomAxis0_0})
        # self.p1_0 = self.addPlot(row=1, col=0, title='1_0', axisItems={'bottom': self.bottomAxis1_0})
        # self.p2_0 = self.addPlot(row=2, col=0, title='2_0', axisItems={'bottom': self.bottomAxis2_0})
        # self.p0_1 = self.addPlot(row=0, col=1, title='0_1', axisItems={'bottom': self.bottomAxis0_1})
        # self.p1_1 = self.addPlot(row=1, col=1, title='1_1', axisItems={'bottom': self.bottomAxis1_1})
        # self.p2_1 = self.addPlot(row=2, col=1, title='2_1', axisItems={'bottom': self.bottomAxis2_1})
        # self.p0_2 = self.addPlot(row=0, col=2, title='0_2', axisItems={'bottom': self.bottomAxis0_2})
        # self.p1_2 = self.addPlot(row=1, col=2, title='1_2', axisItems={'bottom': self.bottomAxis1_2})
        # self.p2_2 = self.addPlot(row=2, col=2, title='2_2', axisItems={'bottom': self.bottomAxis2_2})
        # self.p0_3 = self.addPlot(row=0, col=3, title='0_3', axisItems={'bottom': self.bottomAxis0_3})
        # self.p1_3 = self.addPlot(row=1, col=3, title='1_3', axisItems={'bottom': self.bottomAxis1_3})
        # self.p2_3 = self.addPlot(row=2, col=3, title='2_3', axisItems={'bottom': self.bottomAxis2_3})

        # self.p0_0 = self.addPlot(row=0, col=0, title='0_0', axisItems={'bottom': pg.DateAxisItem()})
        # self.p1_0 = self.addPlot(row=1, col=0, title='1_0', axisItems={'bottom': pg.DateAxisItem()})
        # self.p2_0 = self.addPlot(row=2, col=0, title='2_0', axisItems={'bottom': pg.DateAxisItem()})
        # self.p0_1 = self.addPlot(row=0, col=1, title='0_1', axisItems={'bottom': pg.DateAxisItem()})
        # self.p1_1 = self.addPlot(row=1, col=1, title='1_1', axisItems={'bottom': pg.DateAxisItem()})
        # self.p2_1 = self.addPlot(row=2, col=1, title='2_1', axisItems={'bottom': pg.DateAxisItem()})
        # self.p0_2 = self.addPlot(row=0, col=2, title='0_2', axisItems={'bottom': pg.DateAxisItem()})
        # self.p1_2 = self.addPlot(row=1, col=2, title='1_2', axisItems={'bottom': pg.DateAxisItem()})
        # self.p2_2 = self.addPlot(row=2, col=2, title='2_2', axisItems={'bottom': pg.DateAxisItem()})
        # self.p0_3 = self.addPlot(row=0, col=3, title='0_3', axisItems={'bottom': pg.DateAxisItem()})
        # self.p1_3 = self.addPlot(row=1, col=3, title='1_3', axisItems={'bottom': pg.DateAxisItem()})
        # self.p2_3 = self.addPlot(row=2, col=3, title='2_3', axisItems={'bottom': pg.DateAxisItem()})




        # self.p8_0_4 = self.addPlot(row=0, col=4, title='8_0_4', axisItems={'bottom': bottomAxis_8_4})
        # self.p8_1_4 = self.addPlot(row=1, col=4, title='8_1_4', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
        # self.p8_2_4 = self.addPlot(row=2, col=4, title='8_2_4', axisItems={'bottom': pg.AxisItem(orientation='bottom')})

        self.p0_0.addLegend()
        self.p1_0.addLegend()
        self.p2_0.addLegend()
        self.p0_1.addLegend()
        self.p1_1.addLegend()
        self.p2_1.addLegend()
        self.p0_2.addLegend()
        self.p1_2.addLegend()
        self.p2_2.addLegend()
        self.p0_3.addLegend()
        self.p1_3.addLegend()
        self.p2_3.addLegend()
        # self.p8_0_4.addLegend()
        # self.p8_1_4.addLegend()
        # self.p8_2_4.addLegend()
        self.p0_0.showGrid(x=True, y=True)
        self.p1_0.showGrid(x=True, y=True)
        self.p2_0.showGrid(x=True, y=True)
        self.p0_1.showGrid(x=True, y=True)
        self.p1_1.showGrid(x=True, y=True)
        self.p2_1.showGrid(x=True, y=True)
        self.p0_2.showGrid(x=True, y=True)
        self.p1_2.showGrid(x=True, y=True)
        self.p2_2.showGrid(x=True, y=True)
        self.p0_3.showGrid(x=True, y=True)
        self.p1_3.showGrid(x=True, y=True)
        self.p2_3.showGrid(x=True, y=True)
        # self.p8_0_4.showGrid(x=True, y=True)
        # self.p8_1_4.showGrid(x=True, y=True)
        # self.p8_2_4.showGrid(x=True, y=True)


        self.p1_0.setXLink(self.p0_0)
        self.p2_0.setXLink(self.p0_0)
        self.p0_1.setXLink(self.p0_0)
        self.p1_1.setXLink(self.p0_0)
        self.p2_1.setXLink(self.p0_0)
        self.p0_2.setXLink(self.p0_0)
        self.p1_2.setXLink(self.p0_0)
        self.p2_2.setXLink(self.p0_0)
        self.p0_3.setXLink(self.p0_0)
        self.p1_3.setXLink(self.p0_0)
        self.p2_3.setXLink(self.p0_0)
        # self.p8_0_4.setXLink(self.p0_0)
        # self.p8_1_4.setXLink(self.p0_0)
        # self.p8_2_4.setXLink(self.p0_0)
        pg.setConfigOptions(antialias=True)
        # bottomAxis_8_0.setTicks(xtickts)
        # bottomAxis_8_1.setTicks(xtickts)
        # bottomAxis_8_2.setTicks(xtickts)
        # bottomAxis_8_3.setTicks(xtickts)
        # bottomAxis_8_4.setTicks(xtickts)
    #     self.crosshair8()
    #
    # def crosshair8(self):
        self.vLine1 = pg.InfiniteLine()
        self.vLine1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine2 = pg.InfiniteLine()
        self.vLine2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine3 = pg.InfiniteLine()
        self.vLine3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine4 = pg.InfiniteLine()
        self.vLine4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine5 = pg.InfiniteLine()
        self.vLine5.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine6 = pg.InfiniteLine()
        self.vLine6.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine7 = pg.InfiniteLine()
        self.vLine7.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine8 = pg.InfiniteLine()
        self.vLine8.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine9 = pg.InfiniteLine()
        self.vLine9.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine10 = pg.InfiniteLine()
        self.vLine10.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine11 = pg.InfiniteLine()
        self.vLine11.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine12 = pg.InfiniteLine()
        self.vLine12.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        # self.vLine13 = pg.InfiniteLine()
        # self.vLine13.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        # self.vLine14 = pg.InfiniteLine()
        # self.vLine14.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        # self.vLine15 = pg.InfiniteLine()
        # self.vLine15.setPen(pg.mkPen(QColor(230, 230, 0), width=1))

        # self.hLine1 = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('k', width=1), label='{value:0.1f}',
        #                                     labelOpts={'position':0.1, 'color': (200,0,0), 'movable': True, 'fill': (0, 0, 200, 100)})
        self.hLine1 = pg.InfiniteLine(angle=0)
        self.hLine1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine2 = pg.InfiniteLine(angle=0)
        self.hLine2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine3 = pg.InfiniteLine(angle=0)
        self.hLine3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine4 = pg.InfiniteLine(angle=0)
        self.hLine4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine5 = pg.InfiniteLine(angle=0)
        self.hLine5.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine6 = pg.InfiniteLine(angle=0)
        self.hLine6.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine7 = pg.InfiniteLine(angle=0)
        self.hLine7.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine8 = pg.InfiniteLine(angle=0)
        self.hLine8.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine9 = pg.InfiniteLine(angle=0)
        self.hLine9.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine10 = pg.InfiniteLine(angle=0)
        self.hLine10.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine11 = pg.InfiniteLine(angle=0)
        self.hLine11.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine12 = pg.InfiniteLine(angle=0)
        self.hLine12.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        # self.hLine13 = pg.InfiniteLine(angle=0)
        # self.hLine13.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        # self.hLine14 = pg.InfiniteLine(angle=0)
        # self.hLine14.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        # self.hLine15 = pg.InfiniteLine(angle=0)
        # self.hLine15.setPen(pg.mkPen(QColor(230, 230, 0), width=1))

        self.p0_0.addItem(self.vLine1, ignoreBounds=True)
        self.p0_0.addItem(self.hLine1, ignoreBounds=True)
        self.p1_0.addItem(self.vLine2, ignoreBounds=True)
        self.p1_0.addItem(self.hLine2, ignoreBounds=True)
        self.p2_0.addItem(self.vLine3, ignoreBounds=True)
        self.p2_0.addItem(self.hLine3, ignoreBounds=True)
        self.p0_1.addItem(self.vLine4, ignoreBounds=True)
        self.p0_1.addItem(self.hLine4, ignoreBounds=True)
        self.p1_1.addItem(self.vLine5, ignoreBounds=True)
        self.p1_1.addItem(self.hLine5, ignoreBounds=True)
        self.p2_1.addItem(self.vLine6, ignoreBounds=True)
        self.p2_1.addItem(self.hLine6, ignoreBounds=True)
        self.p0_2.addItem(self.vLine7, ignoreBounds=True)
        self.p0_2.addItem(self.hLine7, ignoreBounds=True)
        self.p1_2.addItem(self.vLine8, ignoreBounds=True)
        self.p1_2.addItem(self.hLine8, ignoreBounds=True)
        self.p2_2.addItem(self.vLine9, ignoreBounds=True)
        self.p2_2.addItem(self.hLine9, ignoreBounds=True)
        self.p0_3.addItem(self.vLine10, ignoreBounds=True)
        self.p0_3.addItem(self.hLine10, ignoreBounds=True)
        self.p1_3.addItem(self.vLine11, ignoreBounds=True)
        self.p1_3.addItem(self.hLine11, ignoreBounds=True)
        self.p2_3.addItem(self.vLine12, ignoreBounds=True)
        self.p2_3.addItem(self.hLine12, ignoreBounds=True)
        # self.p8_0_4.addItem(self.vLine13, ignoreBounds=True)
        # self.p8_0_4.addItem(self.hLine13, ignoreBounds=True)
        # self.p8_1_4.addItem(self.vLine14, ignoreBounds=True)
        # self.p8_1_4.addItem(self.hLine14, ignoreBounds=True)
        # self.p8_2_4.addItem(self.vLine15, ignoreBounds=True)
        # self.p8_2_4.addItem(self.hLine15, ignoreBounds=True)

        self.main_vb = self.p0_0.getViewBox()
        self.sub_vb1 = self.p1_0.getViewBox()
        self.sub_vb2 = self.p2_0.getViewBox()
        self.sub_vb3 = self.p0_1.getViewBox()
        self.sub_vb4 = self.p1_1.getViewBox()
        self.sub_vb5 = self.p2_1.getViewBox()
        self.sub_vb6 = self.p0_2.getViewBox()
        self.sub_vb7 = self.p1_2.getViewBox()
        self.sub_vb8 = self.p2_2.getViewBox()
        self.sub_vb9 = self.p0_3.getViewBox()
        self.sub_vb10 = self.p1_3.getViewBox()
        self.sub_vb11 = self.p2_3.getViewBox()
        # self.sub_vb12 = self.p8_0_4.getViewBox()
        # self.sub_vb13 = self.p8_1_4.getViewBox()
        # self.sub_vb14 = self.p8_2_4.getViewBox()
        # self.sub_vb14 = self.p8_2_4.getViewBox()


        self.p0_0.proxy = pg.SignalProxy(self.p0_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p1_0.proxy = pg.SignalProxy(self.p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p2_0.proxy = pg.SignalProxy(self.p2_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p0_1.proxy = pg.SignalProxy(self.p0_1.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p1_1.proxy = pg.SignalProxy(self.p1_1.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p2_1.proxy = pg.SignalProxy(self.p2_1.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p0_2.proxy = pg.SignalProxy(self.p0_2.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p1_2.proxy = pg.SignalProxy(self.p1_2.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p2_2.proxy = pg.SignalProxy(self.p2_2.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p0_3.proxy = pg.SignalProxy(self.p0_3.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p1_3.proxy = pg.SignalProxy(self.p1_3.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        self.p2_3.proxy = pg.SignalProxy(self.p2_3.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        # self.p8_0_4.proxy = pg.SignalProxy(self.p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        # self.p8_1_4.proxy = pg.SignalProxy(self.p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        # self.p8_2_4.proxy = pg.SignalProxy(self.p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
    def mouseMoved(self, evt):
        pos = evt[0]
        # self.TG.mouseMoved(evt)
        if self.p0_0.sceneBoundingRect().contains(pos):
            mousePoint = self.main_vb.mapSceneToView(pos)
            self.hLine1.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p1_0.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb1.mapSceneToView(pos)
            self.hLine2.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())

        elif self.p2_0.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb2.mapSceneToView(pos)
            self.hLine3.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())

        elif self.p0_1.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb3.mapSceneToView(pos)
            self.hLine4.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p1_1.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb4.mapSceneToView(pos)
            self.hLine5.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p2_1.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb5.mapSceneToView(pos)
            self.hLine6.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p0_2.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb6.mapSceneToView(pos)
            self.hLine7.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p1_2.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb7.mapSceneToView(pos)
            self.hLine8.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p2_2.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb8.mapSceneToView(pos)
            self.hLine9.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p0_3.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb9.mapSceneToView(pos)
            self.hLine10.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p1_3.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb10.mapSceneToView(pos)
            self.hLine11.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        elif self.p2_3.sceneBoundingRect().contains(pos):
            mousePoint = self.sub_vb11.mapSceneToView(pos)
            self.hLine12.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.vLine1.setPos(mousePoint.x())
            self.vLine2.setPos(mousePoint.x())
            self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            self.vLine5.setPos(mousePoint.x())
            self.vLine6.setPos(mousePoint.x())
            self.vLine7.setPos(mousePoint.x())
            self.vLine8.setPos(mousePoint.x())
            self.vLine9.setPos(mousePoint.x())
            self.vLine10.setPos(mousePoint.x())
            self.vLine11.setPos(mousePoint.x())
            self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        # elif self.p8_0_4.sceneBoundingRect().contains(pos):
        #     mousePoint = self.sub_vb12.mapSceneToView(pos)
        #     self.hLine13.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
        #     self.vLine1.setPos(mousePoint.x())
        #     self.vLine2.setPos(mousePoint.x())
        #     self.vLine3.setPos(mousePoint.x())
        #     self.vLine4.setPos(mousePoint.x())
        #     self.vLine5.setPos(mousePoint.x())
        #     self.vLine6.setPos(mousePoint.x())
        #     self.vLine7.setPos(mousePoint.x())
        #     self.vLine8.setPos(mousePoint.x())
        #     self.vLine9.setPos(mousePoint.x())
        #     self.vLine10.setPos(mousePoint.x())
        #     self.vLine11.setPos(mousePoint.x())
        #     self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        # elif self.p8_1_4.sceneBoundingRect().contains(pos):
        #     mousePoint = self.sub_vb13.mapSceneToView(pos)
        #     self.hLine14.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
        #     self.vLine1.setPos(mousePoint.x())
        #     self.vLine2.setPos(mousePoint.x())
        #     self.vLine3.setPos(mousePoint.x())
        #     self.vLine4.setPos(mousePoint.x())
        #     self.vLine5.setPos(mousePoint.x())
        #     self.vLine6.setPos(mousePoint.x())
        #     self.vLine7.setPos(mousePoint.x())
        #     self.vLine8.setPos(mousePoint.x())
        #     self.vLine9.setPos(mousePoint.x())
        #     self.vLine10.setPos(mousePoint.x())
        #     self.vLine11.setPos(mousePoint.x())
        #     self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())
        # elif self.p8_2_4.sceneBoundingRect().contains(pos):
        #     mousePoint = self.sub_vb14.mapSceneToView(pos)
        #     self.hLine15.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
        #     self.vLine1.setPos(mousePoint.x())
        #     self.vLine2.setPos(mousePoint.x())
        #     self.vLine3.setPos(mousePoint.x())
        #     self.vLine4.setPos(mousePoint.x())
        #     self.vLine5.setPos(mousePoint.x())
        #     self.vLine6.setPos(mousePoint.x())
        #     self.vLine7.setPos(mousePoint.x())
        #     self.vLine8.setPos(mousePoint.x())
        #     self.vLine9.setPos(mousePoint.x())
        #     self.vLine10.setPos(mousePoint.x())
        #     self.vLine11.setPos(mousePoint.x())
        #     self.vLine12.setPos(mousePoint.x())
            # self.vLine13.setPos(mousePoint.x())
            # self.vLine14.setPos(mousePoint.x())
            # self.vLine15.setPos(mousePoint.x())


# class TopGraph(pg.GraphicsLayoutWidget):
#     def __init__(self):
#         super().__init__()
#         self.p = self.addPlot()
#         self.p.hideAxis("bottom")
#
#         self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', width=1))
#         self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', width=1), label='{value:0.1f}',
#                                         labelOpts={'position':0.98, 'color': (200,0,0), 'movable': True, 'fill': (0, 0, 200, 100)})
#
#         self.p.addItem(self.vLine, ignoreBounds=True)
#         self.p.addItem(self.hLine, ignoreBounds=True)
#         self.chart8 = SubGraph()
#         self.proxy = pg.SignalProxy(self.p.scene().sigMouseMoved, rateLimit=120, slot=self.mouseMoved)
#
#     def mouseMoved(self, evt):
#         pos = evt[0]
#         if self.p.sceneBoundingRect().contains(pos):
#             self.hLine.show() # show this graph's h line since we are now in control
#
#             mousePoint = self.p.vb.mapSceneToView(pos)
#             x, y = int(mousePoint.x()), int(mousePoint.y())
#             self.vLine.setPos(x)
#             self.hLine.setPos(y)
#             self.other_graph.vLine.setPos(x)
#             self.other_graph.hLine.hide() # hide other graphs h line since we don't controll it here
#             # self.chart8.crosshair8()
#
# class BottomGraph(pg.GraphicsLayoutWidget):
#     def __init__(self):
#         super().__init__()
#         self.p = self.addPlot()
#
#         self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', width=1))
#         self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', width=1), label='{value:0.1f}',
#                                         labelOpts={'position':0.98, 'color': (200,0,0), 'movable': True, 'fill': (0, 0, 200, 100)})
#
#         self.p.addItem(self.vLine, ignoreBounds=True)
#         self.p.addItem(self.hLine, ignoreBounds=True)
#
#         self.proxy = pg.SignalProxy(self.p.scene().sigMouseMoved, rateLimit=120, slot=self.mouseMoved)
#
#     def mouseMoved(self, evt):
#         pos = evt[0]
#         if self.p.sceneBoundingRect().contains(pos):
#             self.hLine.show() # show this graph's h line since we are now in control
#             mousePoint = self.p.vb.mapSceneToView(pos)
#             x, y = int(mousePoint.x()), int(mousePoint.y())
#             self.vLine.setPos(x)
#             self.hLine.setPos(y)
#             self.other_graph.vLine.setPos(x)
#             self.other_graph.hLine.hide() # hide other graphs h line since we don't controll it here



if __name__ == "__main__":
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)

    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')

    app = QApplication([])
    # market = '국내선옵'
    market = '코인'
    # ticker = '101V12'
    ticker = 'ETH'
    list_tickers = ['BTC']
    # ticker = 'BTC'
    bong = '5분봉'
    bong_detail = '1분봉'
    duration = 3

    window_thread = Graph(None,'empty')
    window_thread.make_init_data(market, ticker, bong, bong_detail, duration,list_tickers)
    window_thread.start()
    window_thread.chart_main.show()
    app.exec()


    # main()