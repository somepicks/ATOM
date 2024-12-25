from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
# import numpy as np
#import pyqtgraph as pg
# import sqlite3
import pandas as pd
# from pymongo import MongoClient
# import ATOM_chart
# import ATOM_chart_numpy
#import datetime
import ccxt
# import math
# import color as cl
# import chart_real
# from collections import deque
#from pymongo import MongoClient
# import time
# from pprint import pprint
# import multiprocessing as mp
# import tab_chart_table
#import color as cl
#import sys
import sqlite3
import KIS
from PyQt5.QtTest import QTest
import talib
class Window(QWidget):
    # def __init__(self,df):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.init_file()
        self.set_UI()
        self.QPB_save.clicked.connect(self.save_setting)
    def init_file(self):
        import os
        if not os.path.isfile('DB/setting.db'):
            list_set_idx = [
                'KIS_stock_api',
                'KIS_stock_secret',
                'KIS_stock_account',
                'KIS_id',
                'KIS_stock_mock_api',
                'KIS_stock_mock_secret',
                'KIS_stock_mock_account',
                'KIS_futopt_api',
                'KIS_futopt_secret',
                'KIS_futopt_account',
                'KIS_futopt_mock_api',
                'KIS_futopt_mock_secret',
                'KIS_futopt_mock_account',
                'KIS_stock_oversea_api',
                'KIS_stock_oversea_secret',
                'KIS_stock_oversea_account',
                'KIS_stock_oversea_mock_api',
                'KIS_stock_oversea_mock_secret',
                'KIS_stock_oversea_mock_account',
                'KIS_futopt_oversea_api',
                'KIS_futopt_oversea_secret',
                'KIS_futopt_oversea_account',
                'KIS_futopt_oversea_mock_api',
                'KIS_futopt_oversea_mock_secret',
                'KIS_futopt_oversea_mock_account',
                'CYBOS_api',
                'CYBOS_secret',
                'BYBIT_api',
                'BYBIT_secret',
                'BYBIT_mock_api',
                'BYBIT_mock_secret',
                'TELE_api',
                'TELE_secret'
            ]
            index = list_set_idx
            dict_data = {'value': ''}
            df = pd.DataFrame(data=dict_data, index=index)
            conn = sqlite3.connect('DB/setting.db')
            df.to_sql('set', conn, if_exists='replace')
            conn.close()
    def set_UI(self):
        self.setWindowTitle(f'SET')

        self.QLE_KIS_stock_api = QLineEdit()
        self.QLE_KIS_stock_secret = QLineEdit()
        self.QLE_KIS_stock_account = QLineEdit()
        self.QLE_KIS_id = QLineEdit()
        self.QLE_KIS_stock_mock_api = QLineEdit()
        self.QLE_KIS_stock_mock_secret = QLineEdit()
        self.QLE_KIS_stock_mock_account = QLineEdit()
        self.QLE_KIS_futopt_api = QLineEdit()
        self.QLE_KIS_futopt_secret = QLineEdit()
        self.QLE_KIS_futopt_account = QLineEdit()
        self.QLE_KIS_futopt_mock_api = QLineEdit()
        self.QLE_KIS_futopt_mock_secret = QLineEdit()
        self.QLE_KIS_futopt_mock_account = QLineEdit()
        self.QLE_KIS_stock_oversea_api = QLineEdit()
        self.QLE_KIS_stock_oversea_secret = QLineEdit()
        self.QLE_KIS_stock_oversea_account = QLineEdit()
        self.QLE_KIS_stock_oversea_mock_api = QLineEdit()
        self.QLE_KIS_stock_oversea_mock_secret = QLineEdit()
        self.QLE_KIS_stock_oversea_mock_account = QLineEdit()
        self.QLE_KIS_futopt_oversea_api = QLineEdit()
        self.QLE_KIS_futopt_oversea_secret = QLineEdit()
        self.QLE_KIS_futopt_oversea_account = QLineEdit()
        self.QLE_KIS_futopt_oversea_mock_api = QLineEdit()
        self.QLE_KIS_futopt_oversea_mock_secret = QLineEdit()
        self.QLE_KIS_futopt_oversea_mock_account = QLineEdit()
        self.QLE_CYBOS_api = QLineEdit()
        self.QLE_CYBOS_secret = QLineEdit()
        self.QLE_BYBIT_api = QLineEdit()
        self.QLE_BYBIT_secret = QLineEdit()
        self.QLE_BYBIT_mock_api = QLineEdit()
        self.QLE_BYBIT_mock_secret = QLineEdit()
        self.QLE_TELE_api = QLineEdit()
        self.QLE_TELE_secret = QLineEdit()

        self.QPB_save = QPushButton('설정저장')

        QVB_main = QVBoxLayout()
        QHB_KIS_stock = QHBoxLayout()
        QHB_KIS_stock_mock = QHBoxLayout()
        QHB_KIS_futopt = QHBoxLayout()
        QHB_KIS_futopt_mock = QHBoxLayout()
        QHB_KIS_stock_oversea = QHBoxLayout()
        QHB_KIS_stock_oversea_mock = QHBoxLayout()
        QHB_KIS_futopt_oversea = QHBoxLayout()
        QHB_KIS_futopt_oversea_mock = QHBoxLayout()
        QHB_CYBOS = QHBoxLayout()
        QHB_BYBIT = QHBoxLayout()
        QHB_BYBIT_mock = QHBoxLayout()
        QHB_TELE = QHBoxLayout()
        QHB_KIS_stock.addWidget(QLabel('API KEY: '))
        QHB_KIS_stock.addWidget(self.QLE_KIS_stock_api)
        QHB_KIS_stock.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_stock.addWidget(self.QLE_KIS_stock_secret)
        QHB_KIS_stock.addWidget(QLabel('계좌: '))
        QHB_KIS_stock.addWidget(self.QLE_KIS_stock_account)
        QHB_KIS_stock.addWidget(QLabel('ID: '))
        QHB_KIS_stock.addWidget(self.QLE_KIS_id)

        QHB_KIS_stock_mock.addWidget(QLabel('API KEY: '))
        QHB_KIS_stock_mock.addWidget(self.QLE_KIS_stock_mock_api)
        QHB_KIS_stock_mock.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_stock_mock.addWidget(self.QLE_KIS_stock_mock_secret)
        QHB_KIS_stock_mock.addWidget(QLabel('계좌: '))
        QHB_KIS_stock_mock.addWidget(self.QLE_KIS_stock_mock_account)

        QHB_KIS_futopt.addWidget(QLabel('API KEY: '))
        QHB_KIS_futopt.addWidget(self.QLE_KIS_futopt_api)
        QHB_KIS_futopt.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_futopt.addWidget(self.QLE_KIS_futopt_secret)
        QHB_KIS_futopt.addWidget(QLabel('계좌: '))
        QHB_KIS_futopt.addWidget(self.QLE_KIS_futopt_account)

        QHB_KIS_futopt_mock.addWidget(QLabel('API KEY: '))
        QHB_KIS_futopt_mock.addWidget(self.QLE_KIS_futopt_mock_api)
        QHB_KIS_futopt_mock.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_futopt_mock.addWidget(self.QLE_KIS_futopt_mock_secret)
        QHB_KIS_futopt_mock.addWidget(QLabel('계좌: '))
        QHB_KIS_futopt_mock.addWidget(self.QLE_KIS_futopt_mock_account)

        QHB_KIS_stock_oversea.addWidget(QLabel('API KEY: '))
        QHB_KIS_stock_oversea.addWidget(self.QLE_KIS_stock_oversea_api)
        QHB_KIS_stock_oversea.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_stock_oversea.addWidget(self.QLE_KIS_stock_oversea_secret)
        QHB_KIS_stock_oversea.addWidget(QLabel('계좌: '))
        QHB_KIS_stock_oversea.addWidget(self.QLE_KIS_stock_oversea_account)

        QHB_KIS_stock_oversea_mock.addWidget(QLabel('API KEY: '))
        QHB_KIS_stock_oversea_mock.addWidget(self.QLE_KIS_stock_oversea_mock_api)
        QHB_KIS_stock_oversea_mock.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_stock_oversea_mock.addWidget(self.QLE_KIS_stock_oversea_mock_secret)
        QHB_KIS_stock_oversea_mock.addWidget(QLabel('계좌: '))
        QHB_KIS_stock_oversea_mock.addWidget(self.QLE_KIS_stock_oversea_mock_account)

        QHB_KIS_futopt_oversea.addWidget(QLabel('API KEY: '))
        QHB_KIS_futopt_oversea.addWidget(self.QLE_KIS_futopt_oversea_api)
        QHB_KIS_futopt_oversea.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_futopt_oversea.addWidget(self.QLE_KIS_futopt_oversea_secret)
        QHB_KIS_futopt_oversea.addWidget(QLabel('계좌: '))
        QHB_KIS_futopt_oversea.addWidget(self.QLE_KIS_futopt_oversea_account)

        QHB_KIS_futopt_oversea_mock.addWidget(QLabel('API KEY: '))
        QHB_KIS_futopt_oversea_mock.addWidget(self.QLE_KIS_futopt_oversea_mock_api)
        QHB_KIS_futopt_oversea_mock.addWidget(QLabel('SECRET KEY: '))
        QHB_KIS_futopt_oversea_mock.addWidget(self.QLE_KIS_futopt_oversea_mock_secret)
        QHB_KIS_futopt_oversea_mock.addWidget(QLabel('계좌: '))
        QHB_KIS_futopt_oversea_mock.addWidget(self.QLE_KIS_futopt_oversea_mock_account)

        QHB_CYBOS.addWidget(QLabel('API KEY: '))
        QHB_CYBOS.addWidget(self.QLE_CYBOS_api)
        QHB_CYBOS.addWidget(QLabel('SECRET KEY: '))
        QHB_CYBOS.addWidget(self.QLE_CYBOS_secret)

        QHB_BYBIT.addWidget(QLabel('API KEY: '))
        QHB_BYBIT.addWidget(self.QLE_BYBIT_api)
        QHB_BYBIT.addWidget(QLabel('SECRET KEY: '))
        QHB_BYBIT.addWidget(self.QLE_BYBIT_secret)

        QHB_BYBIT_mock.addWidget(QLabel('API KEY: '))
        QHB_BYBIT_mock.addWidget(self.QLE_BYBIT_mock_api)
        QHB_BYBIT_mock.addWidget(QLabel('SECRET KEY: '))
        QHB_BYBIT_mock.addWidget(self.QLE_BYBIT_mock_secret)

        QHB_TELE.addWidget(QLabel('TOKEN: '))
        QHB_TELE.addWidget(self.QLE_TELE_api)
        QHB_TELE.addWidget(QLabel('ID: '))
        QHB_TELE.addWidget(self.QLE_TELE_secret)


        QVB_main.addWidget(QLabel('한국투자증권: [주식]-실전'))
        QVB_main.addLayout(QHB_KIS_stock)
        QVB_main.addWidget(QLabel('한국투자증권: [주식]-모의'))
        QVB_main.addLayout(QHB_KIS_stock_mock)
        QVB_main.addWidget(QLabel('한국투자증권: [선옵]-실전'))
        QVB_main.addLayout(QHB_KIS_futopt)
        QVB_main.addWidget(QLabel('한국투자증권: [선옵]-모의'))
        QVB_main.addLayout(QHB_KIS_futopt_mock)
        QVB_main.addWidget(QLabel('한국투자증권: [해외주식]-실전'))
        QVB_main.addLayout(QHB_KIS_stock_oversea)
        QVB_main.addWidget(QLabel('한국투자증권: [해외주식]-모의'))
        QVB_main.addLayout(QHB_KIS_stock_oversea_mock)
        QVB_main.addWidget(QLabel('한국투자증권: [해외선옵]-실전'))
        QVB_main.addLayout(QHB_KIS_futopt_oversea)
        QVB_main.addWidget(QLabel('한국투자증권: [해외선옵]-모의'))
        QVB_main.addLayout(QHB_KIS_futopt_oversea_mock)
        QVB_main.addWidget(QLabel('대신증권'))
        QVB_main.addLayout(QHB_CYBOS)
        QVB_main.addWidget(QLabel('바이비트: 실전'))
        QVB_main.addLayout(QHB_BYBIT)
        QVB_main.addWidget(QLabel('바이비트: 실전'))
        QVB_main.addLayout(QHB_BYBIT_mock)
        QVB_main.addWidget(QLabel('텔레그램'))
        QVB_main.addLayout(QHB_TELE)

        QVB_main.addWidget(self.QPB_save)
        self.setLayout(QVB_main)
        # StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
        #                        "border-color: black; header-color: black;font: 12pt 나눔고딕; "
        # self.setStyleSheet(StyleSheet_Qtextedit)

    def save_setting(self):
        self.BTN_effect(self.QPB_save)
        li=[
            self.QLE_KIS_stock_api.text(),
            self.QLE_KIS_stock_secret.text(),
            self.QLE_KIS_stock_account.text(),
            self.QLE_KIS_id.text(),
            self.QLE_KIS_stock_mock_api.text(),
            self.QLE_KIS_stock_mock_secret.text(),
            self.QLE_KIS_stock_mock_account.text(),
            self.QLE_KIS_futopt_api.text(),
            self.QLE_KIS_futopt_secret.text(),
            self.QLE_KIS_futopt_account.text(),
            self.QLE_KIS_futopt_mock_api.text(),
            self.QLE_KIS_futopt_mock_secret.text(),
            self.QLE_KIS_futopt_mock_account.text(),
            self.QLE_KIS_stock_oversea_api.text(),
            self.QLE_KIS_stock_oversea_secret.text(),
            self.QLE_KIS_stock_oversea_account.text(),
            self.QLE_KIS_stock_oversea_mock_api.text(),
            self.QLE_KIS_stock_oversea_mock_secret.text(),
            self.QLE_KIS_stock_oversea_mock_account.text(),
            self.QLE_KIS_futopt_oversea_api.text(),
            self.QLE_KIS_futopt_oversea_secret.text(),
            self.QLE_KIS_futopt_oversea_account.text(),
            self.QLE_KIS_futopt_oversea_mock_api.text(),
            self.QLE_KIS_futopt_oversea_mock_secret.text(),
            self.QLE_KIS_futopt_oversea_mock_account.text(),
            self.QLE_CYBOS_api.text(),
            self.QLE_CYBOS_secret.text(),
            self.QLE_BYBIT_api.text(),
            self.QLE_BYBIT_secret.text(),
            self.QLE_BYBIT_mock_api.text(),
            self.QLE_BYBIT_mock_secret.text(),
            self.QLE_TELE_api.text(),
            self.QLE_TELE_secret.text()
        ]

        conn = sqlite3.connect('DB/setting.db')
        df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
        for i, text in enumerate(li):
            if text != '':
                df.loc[df.index[i],'value'] = text
            if (not text in df.index.tolist()) and text != '':
                df.loc[df.index[i],'value'] = text

        df.to_sql('set', conn, if_exists='replace')
        conn.close()

        self.QLE_KIS_id.clear()
        self.QLE_KIS_stock_api.clear()
        self.QLE_KIS_stock_secret.clear()
        self.QLE_KIS_stock_account.clear()
        self.QLE_KIS_stock_mock_api.clear()
        self.QLE_KIS_stock_mock_secret.clear()
        self.QLE_KIS_stock_mock_account.clear()
        self.QLE_KIS_futopt_api.clear()
        self.QLE_KIS_futopt_secret.clear()
        self.QLE_KIS_futopt_account.clear()
        self.QLE_KIS_futopt_mock_api.clear()
        self.QLE_KIS_futopt_mock_secret.clear()
        self.QLE_KIS_futopt_mock_account.clear()
        self.QLE_KIS_stock_oversea_api.clear()
        self.QLE_KIS_stock_oversea_secret.clear()
        self.QLE_KIS_stock_oversea_account.clear()
        self.QLE_KIS_stock_oversea_mock_api.clear()
        self.QLE_KIS_stock_oversea_mock_secret.clear()
        self.QLE_KIS_stock_oversea_mock_account.clear()
        self.QLE_KIS_futopt_oversea_api.clear()
        self.QLE_KIS_futopt_oversea_secret.clear()
        self.QLE_KIS_futopt_oversea_account.clear()
        self.QLE_KIS_futopt_oversea_mock_api.clear()
        self.QLE_KIS_futopt_oversea_mock_secret.clear()
        self.QLE_KIS_futopt_oversea_mock_account.clear()
        self.QLE_CYBOS_api.clear()
        self.QLE_CYBOS_secret.clear()
        self.QLE_BYBIT_api.clear()
        self.QLE_BYBIT_secret.clear()
        self.QLE_BYBIT_mock_api.clear()
        self.QLE_BYBIT_mock_secret.clear()
        self.QLE_TELE_api.clear()
        self.QLE_TELE_secret.clear()

    def BTN_effect(self, QPB):
        QPB.setEnabled(False)
        QTest.qWait(250)
        QPB.setEnabled(True)

    #
    #
    # def make_exchange_bybit(self):
    #     exchange = ccxt.bybit(config={
    #         'apiKey': 'ZFEksBSBjIHk7drUou',
    #         'secret': 'MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI',
    #         'enableRateLimit': True,
    #         'options': {
    #             'position_mode': True,
    #         }, })
    #     return exchange


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())