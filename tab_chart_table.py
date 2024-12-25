from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
import numpy as np
#import pyqtgraph as pg
import sqlite3
from PyQt5.QtTest import QTest
import pandas as pd
# from pymongo import MongoClient
import ATOM_chart
import ATOM_chart_numpy
import tab_backtest
import os
from pprint import pprint
#import datetime
import ATOM
class Window(QWidget):
    # def __init__(self,df):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)

        self.set_UI()
        self.init_file()
        self.QPB_show.clicked.connect(self.push_show)
        self.QPB_save.clicked.connect(lambda:self.save_table(self.QCB_market.currentText()))
        self.QCB_market.activated[str].connect(lambda :self.select_market(self.QCB_market.currentText()))
        backtest = tab_backtest.Window(self)
        backtest.QCB_market.activated[str].connect(lambda :self.change_market(backtest.QCB_market.currentText()))


    def set_UI(self):
        self.setWindowTitle('chart table')
        self.QTE_var_buy = QTextEdit()
        self.QTE_var_sell = QTextEdit()
        self.QTE0_0 = QTextEdit()
        self.QTE0_1 = QTextEdit()
        self.QTE0_2 = QTextEdit()
        self.QTE0_3 = QTextEdit()
        self.QTE0_4 = QTextEdit()
        self.QTE1_0 = QTextEdit()
        self.QTE1_1 = QTextEdit()
        self.QTE1_2 = QTextEdit()
        self.QTE1_3 = QTextEdit()
        self.QTE1_4 = QTextEdit()
        self.QTE2_0 = QTextEdit()
        self.QTE2_1 = QTextEdit()
        self.QTE2_2 = QTextEdit()
        self.QTE2_3 = QTextEdit()
        self.QTE2_4 = QTextEdit()
        self.QTE3_0 = QTextEdit()
        self.QTE3_1 = QTextEdit()
        self.QTE3_2 = QTextEdit()
        self.QTE3_3 = QTextEdit()
        self.QTE3_4 = QTextEdit()

        self.QPB_save = QPushButton('차트저장')
        self.QPB_show = QPushButton('차트보기')
        self.QCB_market = QComboBox()

        # self.QW_main = QWidget()
        self.QHB_var = QHBoxLayout()
        self.QHB0 = QHBoxLayout()
        self.QHB1 = QHBoxLayout()
        self.QHB2 = QHBoxLayout()
        self.QHB3 = QHBoxLayout()
        self.QHB4 = QHBoxLayout()
        self.QVB_main = QVBoxLayout()


        self.QHB_var.addWidget(self.QTE_var_buy)
        self.QHB_var.addWidget(self.QTE_var_sell)
        self.QHB0.addWidget(self.QTE0_0)
        self.QHB0.addWidget(self.QTE0_1)
        self.QHB0.addWidget(self.QTE0_2)
        self.QHB0.addWidget(self.QTE0_3)
        self.QHB0.addWidget(self.QTE0_4)
        self.QHB1.addWidget(self.QTE1_0)
        self.QHB1.addWidget(self.QTE1_1)
        self.QHB1.addWidget(self.QTE1_2)
        self.QHB1.addWidget(self.QTE1_3)
        self.QHB1.addWidget(self.QTE1_4)
        self.QHB2.addWidget(self.QTE2_0)
        self.QHB2.addWidget(self.QTE2_1)
        self.QHB2.addWidget(self.QTE2_2)
        self.QHB2.addWidget(self.QTE2_3)
        self.QHB2.addWidget(self.QTE2_4)
        self.QHB3.addWidget(self.QTE3_0)
        self.QHB3.addWidget(self.QTE3_1)
        self.QHB3.addWidget(self.QTE3_2)
        self.QHB3.addWidget(self.QTE3_3)
        self.QHB3.addWidget(self.QTE3_4)
        self.QHB4.addWidget(self.QPB_save)
        self.QHB4.addWidget(self.QPB_show)
        self.QHB4.addWidget(self.QCB_market)
        self.QVB_main.addLayout(self.QHB_var)
        self.QVB_main.addLayout(self.QHB0)
        self.QVB_main.addLayout(self.QHB1)
        self.QVB_main.addLayout(self.QHB2)
        self.QVB_main.addLayout(self.QHB3)
        self.QVB_main.addLayout(self.QHB4)
        self.setLayout(self.QVB_main)


        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 11pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 11pt 나눔고딕; "
        self.QTE_var_buy.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE_var_sell.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE0_0.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE0_1.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE0_2.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE0_3.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE1_0.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE1_1.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE1_2.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE1_3.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE2_0.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE2_1.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE2_2.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE2_3.setStyleSheet(StyleSheet_Qtextedit)


        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: #353535; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 11pt 나눔고딕; "
        StyleSheet_Qtextedit = "color: #B4B4B4; background-color: #353535; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 11pt 나눔고딕; "
        self.QTE0_4.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE1_4.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE2_4.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE3_0.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE3_1.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE3_2.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE3_3.setStyleSheet(StyleSheet_Qtextedit)
        self.QTE3_4.setStyleSheet(StyleSheet_Qtextedit)


        self.QCB_market.addItems(['','코인','국내주식','국내선옵','리얼차트'])

    def BTN_effect(self, QPB):
        QPB.setEnabled(False)
        QTest.qWait(250)
        QPB.setEnabled(True)

    def select_market(self,market):
        self.QTE0_0.clear()
        self.QTE0_1.clear()
        self.QTE0_2.clear()
        self.QTE0_3.clear()
        self.QTE0_4.clear()
        self.QTE1_0.clear()
        self.QTE1_1.clear()
        self.QTE1_2.clear()
        self.QTE1_3.clear()
        self.QTE1_4.clear()
        self.QTE2_0.clear()
        self.QTE2_1.clear()
        self.QTE2_2.clear()
        self.QTE2_3.clear()
        self.QTE2_4.clear()
        self.QTE3_0.clear()
        self.QTE3_1.clear()
        self.QTE3_2.clear()
        self.QTE3_3.clear()
        self.QTE3_4.clear()

        conn = sqlite3.connect('DB/chart_table.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # list_table = cursor.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
        # try:
        #     list_table = np.concatenate(list_table).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
        #     # print(list_table)
        # except:
        #     row = 4
        #     col = 5
        #     df_chart = pd.DataFrame()
        #     for r in range(row):
        #         for c in range(col):
        #             df_chart.loc[f'p{r}_{c}', 'chart'] = '종가'
        #     df_chart.to_sql(f'{market}', conn, if_exists='replace')
        # cursor.close()
        if not market == '':
            df_chart_table = pd.read_sql(f"SELECT * FROM '{market}'", conn).set_index('index')
            conn.close()

            self.QTE0_0.setText(df_chart_table.loc['p0_0','chart'])
            self.QTE0_1.setText(df_chart_table.loc['p0_1','chart'])
            self.QTE0_2.setText(df_chart_table.loc['p0_2','chart'])
            self.QTE0_3.setText(df_chart_table.loc['p0_3','chart'])
            self.QTE0_4.setText(df_chart_table.loc['p0_4','chart'])
            self.QTE1_0.setText(df_chart_table.loc['p1_0','chart'])
            self.QTE1_1.setText(df_chart_table.loc['p1_1','chart'])
            self.QTE1_2.setText(df_chart_table.loc['p1_2','chart'])
            self.QTE1_3.setText(df_chart_table.loc['p1_3','chart'])
            self.QTE1_4.setText(df_chart_table.loc['p1_4','chart'])
            self.QTE2_0.setText(df_chart_table.loc['p2_0','chart'])
            self.QTE2_1.setText(df_chart_table.loc['p2_1','chart'])
            self.QTE2_2.setText(df_chart_table.loc['p2_2','chart'])
            self.QTE2_3.setText(df_chart_table.loc['p2_3','chart'])
            self.QTE2_4.setText(df_chart_table.loc['p2_4','chart'])
            self.QTE3_0.setText(df_chart_table.loc['p3_0','chart'])
            self.QTE3_1.setText(df_chart_table.loc['p3_1','chart'])
            self.QTE3_2.setText(df_chart_table.loc['p3_2','chart'])
            self.QTE3_3.setText(df_chart_table.loc['p3_3','chart'])
            self.QTE3_4.setText(df_chart_table.loc['p3_4','chart'])

            var_buy = f""" - 매수 시 사용가능 팩터 -  \n 캔들은 5분봉, 15분봉, 30분봉, 60분봉, 일봉, 주봉이 지원됩니다.
시가, 고가, 저가, 종가, 시가N(pre), 고가N(pre), 저가N(pre), 종가N(pre), 거래량N(pre), 거래량이평3N(pre), 거래량이평20N(pre), 거래량이평60N(pre), 당일거래대금N(pre), 고저평균대비등락율N(pre),  구간최고시가(pre), 구간최저시가(pre), 구간최고고가(pre), 구간최저고가(pre), 구간최고저가(pre), 구간최저저가(pre), 구간최고종가(pre), 구간최저종가(pre), 구간최고시가N(pre,N), 구간최저시가N(pre,N), 구간최고고가N(pre,N), 구간최저고가N(pre,N), 구간최고저가N(pre,N), 구간최저저가N(pre,N), 구간최고종가N(pre,N), 구간최저종가N(pre,N), 시가CN(bong,pre), 고가CN(bong,pre), 저가CN(bong,pre), 종가CN(bong,pre), 이평20CN(bong,pre), 이평60CN(bong,pre), 이평5N(pre), 이평20N(pre), 이평60N(pre), 이평120N(pre), 이평240N(pre), RSI14N(pre), RSI18N(pre), RSI30N(pre), ATRN(pre), TRANGEN(pre), 이격도20이평N(pre), 밴드상N(pre), 밴드중N(pre), 밴드하N(pre), MACD(pre), MACD_SIGNALN(pre), MACD_HISTN(pre), 등락율N(pre), 변화율N(pre)"""
            var_sell = f""" - 매도 시 사용가능 팩터 -  \n 캔들은 5분봉, 15분봉, 30분봉, 60분봉, 일봉, 주봉이 지원됩니다.
시가, 고가, 저가, 종가, 시가N(pre), 고가N(pre), 저가N(pre), 종가N(pre), 거래량N(pre), 거래량이평3N(pre), 거래량이평20N(pre), 거래량이평60N(pre), 당일거래대금N(pre), 고저평균대비등락율N(pre),  구간최고시가(pre), 구간최저시가(pre), 구간최고고가(pre), 구간최저고가(pre), 구간최고저가(pre), 구간최저저가(pre), 구간최고종가(pre), 구간최저종가(pre), 구간최고시가N(pre,N), 구간최저시가N(pre,N), 구간최고고가N(pre,N), 구간최저고가N(pre,N), 구간최고저가N(pre,N), 구간최저저가N(pre,N), 구간최고종가N(pre,N), 구간최저종가N(pre,N), 시가CN(bong,pre), 고가CN(bong,pre), 저가CN(bong,pre), 종가CN(bong,pre), 이평20CN(bong,pre), 이평60CN(bong,pre), 이평5N(pre), 이평20N(pre), 이평60N(pre), 이평120N(pre), 이평240N(pre), RSI14N(pre), RSI18N(pre), RSI30N(pre), ATRN(pre), TRANGEN(pre), 이격도20이평N(pre), 밴드상N(pre), 밴드중N(pre), 밴드하N(pre), MACD(pre), MACD_SIGNALN(pre), MACD_HISTN(pre), 등락율N(pre), 변화율N(pre), 수익율N(pre), 종료시간N(pre),"""


            self.QTE_var_buy.setText(var_buy)
            self.QTE_var_sell.setText(var_sell)

    def save_table(self,market):
        self.BTN_effect(self.QPB_save)
        li_table=[
            self.QTE0_0.toPlainText(),
            self.QTE0_1.toPlainText(),
            self.QTE0_2.toPlainText(),
            self.QTE0_3.toPlainText(),
            self.QTE0_4.toPlainText(),
            self.QTE1_0.toPlainText(),
            self.QTE1_1.toPlainText(),
            self.QTE1_2.toPlainText(),
            self.QTE1_3.toPlainText(),
            self.QTE1_4.toPlainText(),
            self.QTE2_0.toPlainText(),
            self.QTE2_1.toPlainText(),
            self.QTE2_2.toPlainText(),
            self.QTE2_3.toPlainText(),
            self.QTE2_4.toPlainText(),
            self.QTE3_0.toPlainText(),
            self.QTE3_1.toPlainText(),
            self.QTE3_2.toPlainText(),
            self.QTE3_3.toPlainText(),
            self.QTE3_4.toPlainText()]
        list_chart_idx = [
            'p0_0', 'p0_1', 'p0_2', 'p0_3', 'p0_4',
            'p1_0', 'p1_1', 'p1_2', 'p1_3', 'p1_4',
            'p2_0', 'p2_1', 'p2_2', 'p2_3', 'p2_4',
            'p3_0', 'p3_1', 'p3_2', 'p3_3', 'p3_4',
        ]

        df_chart_table = pd.DataFrame(index=list_chart_idx)
        df_chart_table['chart'] = li_table
        df_chart_table.index.name = 'index'
        file = os.getcwd()+'/DB/chart_table.db'
        conn = sqlite3.connect(file)

        # df_chart_table = pd.read_sql(f"SELECT * FROM '{market}'", conn).set_index('index')
        # print(df_chart_table)
        if market != '':
            df_chart_table.to_sql(f'{market}', conn, if_exists='replace')
            conn.close()
            print(f'{market} 차트 테이블 저장' )
        else:
            print('테이블명 확인')
        return df_chart_table

    def input(self,df,market):
        df_chart_table = self.save_table(market)
        self.df_chart_table = df_chart_table
        self.df = df
        return df_chart_table

    def df_to_show(self,df,market):
        conn = sqlite3.connect('DB/chart_table.db')
        self.df_chart_table = pd.read_sql(f"SELECT * FROM '{market}'", conn).set_index('index')
        conn.close()
        self.df = df

    def push_show(self):
        market = self.QCB_market.currentText()
        self.input(self.df,market)
        ticker = '123456789'
        self.chart_show(market,ticker)

    def init_file(self):
        import os
        file = '/DB/chart_table.db'
        if not os.path.isfile(os.getcwd()+file):
            for market in ['코인','국내주식','국내선옵','리얼차트']:
                self.save_table(market)

    def change_market(self,market):
        self.QCB_market.setCurrentText(market)
        self.select_market(market)

    def chart_show(self,market,ticker):
        self.df.index.rename('index', inplace=True)  # 인덱스명 변경
        # print(self.df)
        # print(self.df_chart_table)
        dict_plot = ATOM_chart_numpy.chart_np(self.df, self.df_chart_table)

        # self.df.index = pd.to_datetime(self.df.index)  # db가 str 타입으로 저장 됨

        # df.index = df.index.astype(int)
        # self.chart_table.chart_show(df, dict_plot)

        self.chart = ATOM_chart.Window(self.df, dict_plot,market, ticker)
        self.chart.setGeometry(0, 30, 3840, 2100)
        self.chart.show()


        # sys.exit(app.exec_())
    def purple(self, text):
        return f'\033[38;2;215;95;215m{text}\033[0m'
    def red(self, text):
        return f'\033[31m{text}\033[0m'
    def fie(self, text):
        return f'\033[91m{text}\033[0m'
    def blue(self, text):
        return f'\033[34m{text}\033[0m'
    def cyan(self, text):
        return f'\033[36m{text}\033[0m'
    def yellow(self, text):
        return f'\033[33m{text}\033[0m'
    def green(self, text):
        return f'\033[32m{text}\033[0m'
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())