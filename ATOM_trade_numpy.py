import datetime
from time import strftime

import pandas as pd
from pandas import to_numeric
from PyQt5.QtWidgets import QMainWindow,QGridLayout,QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QTableWidget,QSplitter,QApplication,QCheckBox,QTextEdit,QTableWidgetItem,QHeaderView,QComboBox
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics,QFont
#from PyQt5.QtGui import *
# from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtWidgets, QtCore
import numpy as np
import ccxt
from pykrx import stock
import math
# import color as cl
import chart_real
from collections import deque
#from pymongo import MongoClient
import time
from pprint import pprint
#import multiprocessing as mp
# import tab_chart_table
#import color as cl
#import sys
import sqlite3
import KIS
import talib

import tab_trade
from common_def import export_sql

# from pykrx import stock
# import pandas_datareader.data as web
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다

import schedule
# import Loop_trade
import asyncio
import telegram
import common_def
import json
import subprocess

def priceSum(self, pre):
    try:
        # if len(self.np_arr) < pre:
        #     return np.nan
        return self.np_arr[-(pre):, 7].sum()
    except:
        return 0


def ma(self, pre):
    np_tik = self.np_arr[:, 7]
    np_tik = np.convolve(np_tik, np.ones(pre), 'valid') / pre
    if len(np_tik) < pre:
        return np.append(np.zeros(pre - 1) + np.nan, np_tik[:])[:len(self.np_arr)]
    data = np.append(np.zeros(pre - 1) + np.nan, np_tik[:])
    return data
def moving_average(np_arry, w):
    return np.convolve(np_arry, np.ones(w), 'valid') / w


def 구간최고시가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('시가')].max()
    else:
        # num = np.argmax(np_tik_length == 데이터길이 - pre)
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('시가')].max()
def 구간최저시가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('시가')].min()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('시가')].min()
def 구간최고고가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('고가')].max()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('고가')].max()
def 구간최저고가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('고가')].min()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('고가')].min()
def 구간최고저가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('저가')].max()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('저가')].max()
def 구간최저저가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('저가')].min()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('저가')].min()
def 구간최고종가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('종가')].max()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('종가')].max()
def 구간최저종가(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('종가')].min()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('종가')].min()
def 구간최저거래량(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('거래량')].min()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('거래량')].min()
def 구간최고거래량(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('거래량')].max()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('거래량')].max()
def 구간최저거래대금(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('거래대금')].min()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('거래대금')].min()
def 구간최고거래대금(pre):
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp):,list_columns.index('거래대금')].max()
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre):,list_columns.index('거래대금')].max()
def 구간최고시가N(pre,N): #이거는 다시 한번 봐야 됨
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('시가')].max()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('시가')].max()
def 구간최저시가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('시가')].min()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('시가')].min()
def 구간최고고가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('고가')].max()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('고가')].max()
def 구간최저고가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('고가')].min()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('고가')].min()
def 구간최고저가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('저가')].max()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('저가')].max()
def 구간최저저가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('저가')].min()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('저가')].min()
def 구간최고종가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('종가')].max()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('종가')].max()
def 구간최저종가N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('종가')].min()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('종가')].min()
def 구간최고거래량N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('거래량')].max()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('거래량')].max()
def 구간최저거래량N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('거래량')].min()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('거래량')].min()
def 구간최고거래대금N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('거래대금')].max()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('거래대금')].max()
def 구간최저거래대금N(pre,N):
    if market == '코인':
        pre_len = int(-pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik_ar[pre_len-div:-div, list_columns.index('거래대금')].min()
    else:
        first_idx = np.argmax(np_tik_length == 데이터길이 - pre - N)
        end_idx = np.argmax(np_tik_length == 데이터길이 - N)
        return np_tik_ar[first_idx:end_idx,list_columns.index('거래대금')].min()


def 시가TN(ticker_bong,pre): # 시가TN('ETH_5분봉',1)
    # print(int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp))
    # print(np_tik_ar)
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('시가_'+ticker_bong)]
def 고가TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('고가_'+ticker_bong)]
def 저가TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('저가_'+ticker_bong)]
def 종가TN(ticker_bong,pre):
    # print(int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp))
    # print(np_tik_ar)
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('종가_'+ticker_bong)]
def 이평5TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('이평5_'+ticker_bong)]
def 이평20TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('이평20_'+ticker_bong)]
def 이평60TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('이평60_'+ticker_bong)]
def 거래량TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('거래량_'+ticker_bong)]
def 거래대금TN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('거래대금_'+ticker_bong)]
def MACDTN(ticker_bong,pre):
    try:
        return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('MACD_'+ticker_bong)]
    except:
        print(259)
        print(f"MACDTN(ticker_bong,pre) {ticker_bong=} , {pre=}")
        quit()
def MACD_SIGNALTN(ticker_bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[ticker_bong[ticker_bong.index('_')+1:]]/bong_detail_stamp), list_columns.index('MACD_SIGNAL_'+ticker_bong)]

def 시가CN(bong,pre): # 시가CN('일봉',1)
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'시가_{bong}')]
def 고가CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'고가_{bong}')]
def 저가CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'저가_{bong}')]
def 종가CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'종가_{bong}')]
def 이평5CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'이평5_{bong}')]
def 이평20CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'이평20_{bong}')]
def 이평60CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'이평60_{bong}')]
def 거래량CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'거래량_{bong}')]
def 거래대금CN(bong,pre):
    return np_tik_ar[int(-pre*dict_bong_stamp[bong]/bong_detail_stamp), list_columns.index(f'거래대금_{bong}')]

# np_tik이나 np_tik_ar로 돌리는거보다 np_df_tik이 더 빠름
def 시가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('시가')]
    else: #국내시장일 경우
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'시가')]
def 고가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('고가')]
    else: #국내시장일 경우(일봉)
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'고가')]
def 저가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('저가')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'저가')]
def 종가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('종가')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'종가')]
def 이평5N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('이평5')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'이평5')]
def 이평20N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('이평20')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'이평20')]
def 이평60N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('이평60')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'이평60')]
def 이평120N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('이평120')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'이평120')]
def 이평240N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('이평240')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'이평240')]
def 거래량N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량')]
    else:
        # print(pre,' | ',np_tik_ar[np.argmax(np_tik_length == 데이터길이 - pre), list_columns.index(f'거래량')])
        return int(np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'거래량')])
def 거래량이평3N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량이평3')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'거래량이평3')]
def 거래량이평20N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량이평20')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'거래량이평20')]
def 거래량이평60N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량이평60')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'거래량이평60')]
def RSI14N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('RSI14')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'RSI14')]
def RSI18N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('RSI18')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'RSI18')]
def RSI30N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('RSI30')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'RSI30')]
def ATRN(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('ATR')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'ATR')]
def TRANGEN(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('TRANGE')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'TRANGE')]
def MACDN(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('MACD')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'MACD')]
def MACD_SIGNALN(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('MACD_SIGNAL')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'MACD_SIGNAL')]
def MACD_HISTN(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('MACD_HIST')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'MACD_HIST')]
def 이격도20이평N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('이격도20이평')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'이격도20이평')]
def 밴드상N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('밴드상')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'밴드상')]
def 밴드중N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('밴드중')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'밴드중')]
def 밴드하N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('밴드하')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'밴드하')]
def 등락율N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('등락율')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'등락율')]
def 변화율N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('변화율')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'변화율')]
def 수익율N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('수익율')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'수익율')]
def 고저평균대비등락율N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('고저평균대비등락율')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'고저평균대비등락율')]
def 당일거래대금N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('당일거래대금')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'당일거래대금')]
def 종료시간N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[int(-pre * bong_stamp/bong_detail_stamp), list_columns.index('캔들종료시간')]
    else:
        return np_tik_ar[np.argmax(np_tik_length == 데이터길이-pre),list_columns.index(f'캔들종료시간')]
def moving_average(np_arry, w):
    return np.convolve(np_arry, np.ones(w), 'valid') / w

# def 이평(pre):
#     if 데이터길이 <= pre:
#         return np.nan
#     return np_tik_ar[row_tik - pre, list_columns.index('종가')]/pre

# def stamp_to_str(stamp_time):
#     date_time = stamp_to_datetime(stamp_time)
#     return datetime.datetime.strftime(date_time,"%Y-%m-%d %H:%M:%S")
# def stamp_to_datetime(stamp_time):
#     int_time=stamp_to_int(stamp_time)
#     return datetime.datetime.strptime(str(int_time),'%Y%m%d%H%M')
# def stamp_to_int(stamp_time):
#     dt = datetime.datetime.fromtimestamp(stamp_time)
#     dt = dt.strftime('%Y%m%d%H%M')
#     return int(dt)

class Trade_np(QThread):
    qt_open = pyqtSignal(pd.DataFrame)
    qt_closed = pyqtSignal(pd.DataFrame)
    # val_sum = pyqtSignal(pd.DataFrame)
    val_light = pyqtSignal(bool,pd.DataFrame)
    # val_instock = pyqtSignal(pd.DataFrame)


    def __init__(self,parent,market,simul,df_stg,chart_duration,tele,list_tickers,COND_MRKT):
        super().__init__(parent)
    # def __init__(self,market,simul,df_stg):
    #     super().__init__()
        # self.conn_stg = conn_stg
        self.market = market
        self.simul = simul
        self.df_stg = df_stg
        # self.df_instock = df_instock
        # self.df_qcb = df_qcb

        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self._status = True
        self.light = False
        self.wait()
        if chart_duration == '기간(일)': chart_duration = 1
        self.duration = int(chart_duration)
        self.dict_bong_stamp ={'1분봉': 1*60, '3분봉': 3*60, '5분봉': 5*60, '15분봉': 15*60, '30분봉': 30*60, '60분봉': 60*60, '4시간봉': 240*60, '일봉': 1440*60,
                           '주봉': 10080*60}
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
        self.dict_bong_reverse = dict(zip(self.dict_bong.values(), self.dict_bong.keys()))
        self.dict_bong_timedelta = {'1분봉':datetime.timedelta(minutes=1), '3분봉':datetime.timedelta(minutes=3),
                                    '5분봉':datetime.timedelta(minutes=5), '15분봉':datetime.timedelta(minutes=15),
                                    '30분봉':datetime.timedelta(minutes=30), '60분봉':datetime.timedelta(minutes=60),
                                    '4시간봉':datetime.timedelta(minutes=240), '일봉':datetime.timedelta(days=1)}
        self.dic_multiplier = {'101':250000,'201':250000,'301':250000,'209':250000,'309':250000,'2AF':250000,'3AF':250000, #코스피200
                               '105':50000,'205':50000,'305':50000, #미니코스피200
                               '106': 10000, '206': 10000, '306': 10000, #코스닥150
                               }
        self.timer_light = QtCore.QTimer()
        self.timer_light.start()
        self.timer_light.setInterval(1000)  #10초에 한번씩 불러오기
        self.bool_light = False


        self.fee_stock = 0.0140527#%
        self.tax_stock = 0.018
        self.fee_future = 0.00185
        self.fee_putopt1 = 0.077346
        self.fee_putopt2 = 0.09
        self.fee_bybit_market = 0.055
        self.fee_bybit_limit = 0.055
        self.위탁증거금률 = 10  # 10%
        self.tele = tele
        self.list_tickers = list_tickers
        self.COND_MRKT = COND_MRKT
        # self.list_close_day = list_close_day


        if self.tele == True:
            conn = sqlite3.connect('DB/setting.db')
            df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
            conn.close()
            self.TOKEN = df.loc['TELE_api', 'value']
            self.chat_id = df.loc['TELE_secret', 'value']
            self.bot = telegram.Bot(token=self.TOKEN)
            # txt = '텔레그램 작동'
            # asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=txt))
        # self.loop_run = Loop_trade.Trade_np(self)

    def run(self):
        self.df_trade = self.df_stg[self.df_stg['table'] != 0] # 현재 테이블에 저장된 전략만 갖고오기
        print(f'거래에 사용할 전략: {self.df_trade.index.tolist()}')
        # self.list_stg_tickers = self.df_trade.loc[self.df_trade['진입대상']!='전체','ticker'].values.tolist()  #데이터프레임 조건 [진입대상이 전체가 아닌 'ticker'열 불러와 np→리스트 저장
        # self.list_stg_tickers.append('WLD') #전략에서 제외되는 코인 추가
        # self.list_stg_tickers = list(set(self.list_stg_tickers))
        # print(f"거래대상이 '전체'인 전략에서 제외되는 종목: {self.list_stg_tickers}")
        if self.simul.isChecked() == False:  # 실매매
            print(f"{self.red('실매매')}")
        elif self.simul.isChecked() == True: #모의매매
            print(f"{self.cyan('모의매매')}")

        if self.market == '국내주식' or self.market == '국내선옵':
            if datetime.datetime.now().time() < datetime.datetime.strptime('00:55:00','%H:%M:%S').time(): #9시 전에 클릭하면 9시 정각에 실행
                schedule.every().day.at("08:55:00").do(self.loop_init)
                while self._status:
                    schedule.run_pending()
                    # time.sleep(1)
                    QTest.qWait(500)
                    self.qt_open.emit(self.df_trade)
                    self.active_light()
            else:
                self.loop_init()
            print('국내 exit')

        elif self.market == '코인':
            # schedule.every().hour.at(":00").do(self.sorting_tickers) #매시각 정시마다 거래대금 순위 정렬해서 불러오기
            # schedule.every().hour.at(":30").do(self.sorting_tickers) #매시각 30분마다 거래대금 순위 정렬해서 불러오기
            schedule.every().hour.at(":00").do(self.time_sync) #매시각 정시마다 거래대금 순위 정렬해서 불러오기
            dict_stg = self.loop_init()
            dt = datetime.datetime.now().replace(second=0, microsecond=0)
            one_minute = dt+datetime.timedelta(minutes=1)
            # print(dict_stg)
            while self._status:
                QTest.qWait(1000)
                장종료시간 = dt + datetime.timedelta(days=30)
                one_minute, dict_stg = self.loop_main(장종료시간,one_minute,dict_stg)
                schedule.run_pending()
                self.qt_open.emit(self.df_trade)
                # self.val_light.emit(self.bool_light)
                # self.bool_light = not self.bool_light
            print('코인 exit')
        self._status = False
    def time_sync(self):
        subprocess.Popen('python timesync.py')
    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.cond.wakeAll()
        elif not self._status:
            self.bool_light = False
            self.val_light.emit(self.bool_light,self.df_trade)
    def active_light(self):
        self.val_light.emit(self.bool_light,self.df_trade)
        self.bool_light = not self.bool_light
    @property
    def status(self):
        return self._status
    def make_loop(self,ticker, bong, bong_detail, ):
        pass
    def loop_init(self):
        # global 장종료시간
        현재시간 = datetime.datetime.now().replace(second=0, microsecond=0)
        진입시간 = 현재시간

        if self.market == '코인':
            장종료시간 = 현재시간 + datetime.timedelta(days=30)
            self.ex_bybit, self.ex_pybit = common_def.make_exchange_bybit(False)
            balanceSpot = self.ex_bybit.fetch_balance()
            print('거래에 사용하고 있지 않은 코인양: ', balanceSpot['USDT']['free'])
            print('거래에 사용하고 있는 코인양: ', balanceSpot['USDT']['used'])
            print('전체 코인양: ', balanceSpot['USDT']['total'])
            self.list_tickers = [x for x in self.list_tickers if len(x) != 1]

        elif self.market == '국내주식' or self.market == '국내선옵':
            # dt = 현재시간.strftime('%Y-%m-%d') + ' 15:30:00'
            장종료시간 = ' '+'15:30:00' #날짜랑 시간 사이 비울 것
            장종료시간 = 현재시간.strftime('%Y-%m-%d') + 장종료시간 #날짜랑 시간 사이 비울 것
            장종료시간 = common_def.str_to_datetime(장종료시간)
            if self.market == '국내주식':
                if self.simul.isChecked() == True:  # 모의매매
                    self.ex_kis = common_def.make_exchange_kis('모의주식')
                elif self.simul.isChecked() == False:  # 실매매
                    self.ex_kis = common_def.make_exchange_kis('실전주식')
            elif self.market == '국내선옵':
                if self.simul.isChecked() == True:  # 모의매매
                    self.ex_kis = common_def.make_exchange_kis('모의선옵')
                elif self.simul.isChecked() == True:  # 실매매
                    self.ex_kis = common_def.make_exchange_kis('실전선옵')

            dict_asset, df_x = self.ex_kis.fetch_balance()  # 자산, 보유종목
            print(f"{dict_asset}")
            if not df_x.empty:
                print('=============================================================')
                print(f"보유종목 \n {df_x}")
                print('=============================================================')
            if 장종료시간 <= datetime.datetime.now().replace(second=0, microsecond=0):
                print(f"{self.red('장 운영시간이 아님')}")
                quit()
            self.df_trend = pd.DataFrame()
            self.add_investor_trend(현재시간)
        # print(f"{self.list_tickers= }")
        # print(self.df_trade)

        # self.dict_sorting_obj = {}

        dict_stg = {}
        for stg in self.df_trade.index:
            obj = self.df_trade.loc[stg, '진입대상']
            bong = self.df_trade.loc[stg, '봉']
            if bong == '일봉' :
                bong_detail = '일봉'
                self.df_trade.loc[stg, '상세봉'] = bong_detail
            else:
                bong_detail = '1분봉'
                self.df_trade.loc[stg, '상세봉'] = '1분봉'
            dict_stg[stg] = {'전략명':stg, '진입대상':obj,'종목코드':'','봉':bong, '상세봉':bong_detail,
                             '봉제한':1, '팩터':[], '비교대상':{'수급동향':False}, '현재시간':현재시간,
                             '장종료시간':장종료시간, '진입시간':진입시간, '검색대상':[]}
            if obj[0] == '{' and obj[-1] == '}' : # 대상이 여러개일 경우
                obj = json.loads(obj)
                dict_stg[stg]['진입대상'] = obj
            ticker = self.df_trade.loc[stg, 'ticker']
            df_same = self.df_trade[(self.df_trade['ticker'] == ticker) & (self.df_trade['봉'] == bong) & (self.df_trade['상세봉'] == bong_detail)]
            bong_since = df_same['봉제한'].max()
            dict_stg[stg]['종목코드'] = ticker
            dict_stg[stg]['봉제한'] = bong_since
        self.sorting_make_df(dict_stg)

        for stg in self.df_trade.index:

            #들여쓰기 에러 방지용
            상태 = self.df_trade.loc[stg, '상태']
            배팅금액 = self.df_trade.loc[stg, '배팅금액']
            stg_buy = self.df_trade.loc[stg, '진입전략']
            stg_sell = self.df_trade.loc[stg, '청산전략']
            self.df_trade.loc[stg, '진입전략'] = common_def.replace_tabs_with_spaces(stg_buy)
            self.df_trade.loc[stg, '청산전략'] = common_def.replace_tabs_with_spaces(stg_sell)

            ticker = dict_stg[stg]['종목코드']
            obj = dict_stg[stg]['진입대상']
            bong = dict_stg[stg]['봉']
            bong_detail = dict_stg[stg]['상세봉']
            bong_since = dict_stg[stg]['봉제한']

                # self.dict_sorting_obj = self.sorting_tickers(stg,obj)

            if type(obj) == str or (type(obj) == dict and 상태 != '대기') and (type(obj) == dict and 상태 != '청산'): #종목이 지정되어있을 경우
                pass
                df = self.make_df(ticker,bong,bong_detail,bong_since,False)
                dict_stg[stg] = self.check_compare_ticker(stg,ticker,dict_stg[stg])
                # if dict_stg[stg]['비교대상']:  # 비교대상이 있을경우 데이터프레임 생성
                df = self.add_compare_df(ticker, df, dict_stg[stg], bong_detail, bong_since)
                # print(f"{stg= }    {ticker= }   {obj= }    {type(obj)=}    {bong= },    {bong_detail= }    {bong_since= }   {dict_stg[stg]= }")
                데이터길이 = df.loc[df.index[-1], '데이터길이']  # df는 상태봉이기 때문에  찾아서 다시 들어가야됨
                idx_bong = df['데이터길이'].tolist().index(데이터길이)
                if 상태 == '대기':
                    self.df_trade.loc[stg, '진입시간'] = common_def.datetime_to_str(df.index[idx_bong])  # 변수로 사용하기 때문에 일단은 만들어둠
                    # idx = self.df_trade[(self.df_trade['ticker'] == ticker) & (self.df_trade['봉'] == bong) & (self.df_trade['상태'] == '대기') & (self.df_trade['상세봉'] == bong_detail)].index
                    # self.df_trade.loc[idx, '현재봉시간'] = common_def.datetime_to_str(df.index[idx_bong])  # 조건: 같은 종목, 같은 봉, 같은 봉제한인 테이블에 동시에 저장
                    self.df_trade.loc[stg, '현재봉시간'] = common_def.datetime_to_str(df.index[idx_bong])
                # 매수주문이나 매도주문등이 된 상태에서 프로그램이 꺼질경우 체결이 되었는지 알 수 없기때문에 최초 한번 돌려줌
                elif 상태 != '대기':
                    # dict_stg[stg]['캔들종료시간'] = 장종료시간 if bong == '일봉' else df.index[idx_bong] + self.dict_bong_timedelta[bong]
                    # self.loop_trade(df, dict_stg[stg], 상태, 배팅금액, 데이터길이)
                    pass
                self.active_light()
            # elif 상태 == '청산':
                    # dict_stg[stg]['캔들종료시간'] = 장종료시간 if bong == '일봉' else 현재시간 + self.dict_bong_timedelta[bong]

            else:  # 현재 매수상태에 있는게 팔리면서 새로운 종목의 데이터를 필요료 할 수 있기 때문에 일단은 전부 불러와야됨
                # 같은 전략에 동일한 종목을 매수할 수 있으므로 그것도 감안
                dict_stg[stg]['검색대상'] = self.sorting_tickers(dict_stg[stg],obj)
                global 검색대상
                검색대상 = dict_stg[stg]['검색대상']
                # print(f"{self.dict_sorting_obj= }")
                # self.dict_sorting_obj[stg] = []
                # print(f"{self.dict_sorting_obj= }")
                if dict_stg[stg]['검색대상']:
                    # print(f"{dict_stg[stg]=}  |  {dict_stg[stg]['검색대상']= } | ")
                    for i, ticker in enumerate(dict_stg[stg]['검색대상']):  # 조건 검색에 있는 종목만
                        df_same = self.df_trade[(self.df_trade['ticker'] == ticker) & (self.df_trade['봉'] == bong) & (self.df_trade['상세봉'] == bong_detail)]
                        if df_same.empty:
                            bong_since = self.df_trade.loc[stg, '봉제한']
                        else:
                            bong_since = df_same['봉제한'].max()
                        df = self.make_df(ticker,bong,bong_detail,bong_since,False)
                        dict_stg[stg]['종목코드'] = ticker
                        dict_stg[stg]['봉제한'] = bong_since
                        dict_stg[stg]['비교대상']['수급동향'] = False
                        dict_stg[stg] = self.check_compare_ticker(stg, ticker,dict_stg[stg])
                        # if dict_stg[stg]['비교대상']:  # 비교대상이 있을경우 데이터프레임생성
                        df = self.add_compare_df(ticker, df, dict_stg[stg], bong_detail, bong_since)

                        데이터길이 = df.loc[df.index[-1], '데이터길이']
                        idx_bong = df['데이터길이'].tolist().index(데이터길이)
                        self.df_trade.loc[stg, '진입시간'] = common_def.datetime_to_str(df.index[idx_bong])  # 변수로 사용하기 때문에 일단은 만들어둠
                        self.df_trade.loc[stg, '현재봉시간'] = common_def.datetime_to_str(df.index[idx_bong])  # 일단은 만들어둠

                        self.active_light()
                else: #해당하는 종목이 없을 경우
                    df = pd.DataFrame()
                    self.df_trade.loc[stg, '진입시간'] = common_def.datetime_to_str(현재시간)  # 변수로 사용하기 때문에 일단은 만들어둠
                    self.df_trade.loc[stg, '현재봉시간'] = common_def.datetime_to_str(현재시간)  # 일단은 만들어둠
            if [x for x in df.columns.tolist() if '_y' in x or '_x' in x]:
                print('에러0')
                quit()#
        if self.market == '코인':
            print(f"{self.blue('bybit 트레이딩 시작')}")
        elif self.market == '국내주식' or self.market == '국내선옵':
            print(f"{self.blue('kis 트레이딩 시작')}")
            dt = datetime.datetime.now().replace(second=0, microsecond=0)
            one_minute = dt+datetime.timedelta(minutes=1)
            while self._status:
                one_minute, dict_stg = self.loop_main(장종료시간, one_minute, dict_stg)
                self.qt_open.emit(self.df_trade)
                # self.val_light.emit(self.bool_light)
                # self.bool_light = not self.bool_light
        return dict_stg
    def loop_main(self,장종료시간, one_minute, dict_stg):
        # global 데이터길이, 현재시간, 캔들종료시간
        현재시간 = datetime.datetime.now().replace(second=0, microsecond=0)

        check_time = False
        # self.list_df_duplicated = [] # 매번 초기화해서 데이터가 동일한 데이터를 두번 부르지 않도록하기 위함
        if 장종료시간 < 현재시간:
            self.market_finish()

        elif 현재시간 >= one_minute:  # 모든종목 대상으로 캔들종료시간 초과 시 한번만 실행하도록
            check_time = True
            if self.market == '코인':
                self.sorting_make_df(dict_stg)
            elif self.market == '국내주식' or self.market == '국내선옵':
                self.add_investor_trend(현재시간)
                self.sorting_make_df(dict_stg)
            one_minute = 현재시간+datetime.timedelta(minutes=1)
            # print(self.df_trend)
        # print(self.df_trade)
        for stg in self.df_trade.index:
            bong = dict_stg[stg]['봉']
            bong_detail = dict_stg[stg]['상세봉']
            bong_since = dict_stg[stg]['봉제한']
            obj = dict_stg[stg]['진입대상']
            dict_stg[stg]['진입시간'] = common_def.str_to_datetime(self.df_trade.loc[stg, '진입시간'])
            dict_stg[stg]['현재시간'] = 현재시간
            # 상태 = self.df_trade.loc[stg, '상태']
            # bong_time = self.df_trade.loc[stg, '현재봉시간']
            # 배팅금액 = self.df_trade.loc[stg, '배팅금액']

            # 증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1/레버리지 if trade_market == 'bybit' else 1
            # bought_rate = 0
            # 매도전환 = False
            bong_time = self.df_trade.loc[stg, '현재봉시간']
            상태 = self.df_trade.loc[stg, '상태']
            배팅금액 = self.df_trade.loc[stg, '배팅금액']
            # 캔들 캔들종료시간 계산용
            if bong != '일봉':
                캔들종료시간 = common_def.str_to_datetime(bong_time) + self.dict_bong_timedelta[bong]
            elif bong == '일봉':
                캔들종료시간 = 장종료시간
            if type(obj) == str or (type(obj) == dict and 상태 != '대기') and (type(obj) == dict and 상태 != '청산'):  # 종목이 지정되어있을 경우
                ticker = dict_stg[stg]['종목코드']
                df = self.make_df(ticker,bong,bong_detail,bong_since,False)
                df = self.add_compare_df(ticker, df, dict_stg[stg], bong_detail, bong_since)
                # print(f"{df= }")
                # print(f"{df.loc[df.index[-1],'종가']= }")
                데이터길이 = df.loc[df.index[-1], '데이터길이']  # df는 상세봉이기 때문에  찾아서 다시 들어가야됨
                # if not np.isnan():
                idx_bong = df['데이터길이'].tolist().index(데이터길이)

                if 캔들종료시간 < 현재시간 and common_def.str_to_datetime(bong_time) < df.index[idx_bong]: #현재시간은 finish보다 앞서도라도 증권사에서 보내주는 봉 시간은 조금 느릴 수 있기 때문에 조건 2개 확인
                    self.df_trade.loc[stg, '현재봉시간'] = common_def.datetime_to_str(df.index[idx_bong])
                    bong_time = self.df_trade.loc[stg, '현재봉시간'] # 시간이 갱신되면 캔들종료시간 시간도 변경되어야 함
                    캔들종료시간 = common_def.str_to_datetime(bong_time) + self.dict_bong_timedelta[bong]
                    if 상태 == '매수주문' or 상태 == '부분매수':
                        상태 = '매수취소'
                    elif 상태 == '분할매수주문' or 상태 == '분할부분매수':
                        상태 = '분할매수취소'
                    elif 상태 == '청산' or 상태 == '매수불가':
                        self.df_trade.loc[stg, '상태'] = '대기'
                    print(f'캔들종료시간 < 현재시간 ======= {stg},bong_time: {bong_time},  idx_bong: {df.index[idx_bong]},  캔들종료시간: {common_def.datetime_to_str(캔들종료시간)} < 현재시간: {common_def.datetime_to_str(현재시간)}  {상태= }')
                if [x for x in df.columns.tolist() if '_y' in x]:
                    print('에러1')
                    quit()
                # self.loop_trade(ticker, stg, df, bong, bong_detail, 상태, 현재시간, 캔들종료시간, 장종료시간,데이터길이,배팅금액, 진입시간)
                self.loop_trade(df, dict_stg[stg], 상태, 배팅금액, 데이터길이)

            else:  # 현재 매수상태에 있는게 팔리면서 새로운 종목의 데이터를 필요료 할 수 있기 때문에 일단은 전부 불러와야됨
                if check_time == True:
                    dict_stg[stg]['검색대상'] = self.sorting_tickers(stg,obj)
                if dict_stg[stg]['검색대상']:
                    # print(f"{stg=}    {dict_stg[stg]['검색대상']= }  {상태= }   {type(dict_stg[stg]['검색대상'])= }")
                    for i, ticker in enumerate(dict_stg[stg]['검색대상']):
                        if ticker != '':
                            dict_stg[stg]['종목코드'] = ticker
                            상태 = self.df_trade.loc[stg, '상태']
                            bong_time = self.df_trade.loc[stg, '현재봉시간']
                            배팅금액 = self.df_trade.loc[stg, '배팅금액']
                            dict_stg[stg]['비교대상']['수급동향'] = False
                            # 비교대상에서 긴 봉제한을 갖고왔을 때 어떡게 df에 접목할지 고민 해봐야 함
                            # dict_stg[stg]['봉제한'] = bong_since
                            df = self.make_df(ticker,bong,bong_detail,bong_since,False)
                            dict_stg[stg] = self.check_compare_ticker(stg, ticker,dict_stg[stg])
                            # if dict_stg[stg]['비교대상']:  # 비교대상이 있을경우 데이터프레임생성
                            df = self.add_compare_df(ticker, df, dict_stg[stg], bong_detail, bong_since)
                            데이터길이 = df.loc[df.index[-1], '데이터길이']
                            # print(f"{stg= }   {ticker= }   {데이터길이= }")
                            idx_bong = df['데이터길이'].tolist().index(데이터길이)

                            if 캔들종료시간 < 현재시간 and common_def.str_to_datetime(bong_time) < df.index[idx_bong]:  # 현재시간은 finish보다 앞서도라도 증권사에서 보내주는 봉 시간은 조금 느릴 수 있기 때문에 조건 2개 확인
                                if i == 0:  # 여러종목일 경우 첫번째로 불러오는 데이터의 봉 시간만 저장
                                    self.df_trade.loc[stg, '현재봉시간'] = common_def.datetime_to_str(df.index[idx_bong])
                                    bong_time = self.df_trade.loc[stg, '현재봉시간']  # 시간이 갱신되면 캔들종료시간 시간도 변경되어야 함
                                    캔들종료시간 = common_def.str_to_datetime(bong_time) + self.dict_bong_timedelta[bong]
                                    if 상태 == '청산' or 상태 == '매수불가':
                                        self.df_trade.loc[stg, '상태'] = '대기'

                            if [x for x in df.columns.tolist() if '_y' in x]:
                                print('에러1')
                                quit()
                            if 상태 == '대기':
                                self.loop_trade(df, dict_stg[stg], 상태, 배팅금액, 데이터길이)
                                if self.df_trade.loc[stg,'상태'] != '대기':
                                    break
            self.active_light()
        # print(self.df_trade[['현재봉시간','캔들종료시간']])
        return one_minute, dict_stg

    # def loop_trade(self, ticker, stg, df_detail, bong, bong_detail, 상태, current_time, candle_endtime, jang_endtime,data_length,배팅금액,enter_time):
    def loop_trade(self, df_detail, dict_stg_stg, 상태, 배팅금액, data_length):
        global np_tik_ar, list_columns, np_tik_idx, np_tik_length
        global 매수가, 매도가, 시장가, 레버리지, 매수, 매도, 재진입금지
        global 수익률, 최고수익률, 최저수익률
        global 상세시가, 상세고가, 상세저가, 상세종가
        global market, stg, 종목코드, 전략명
        global dict_bong_stamp, bong_stamp, bong_detail_stamp
        global 롱, long, 숏, short
        global 분봉1, 분봉3, 분봉5, 분봉15, 분봉30, 분봉60, 시간봉4, 일봉, 주봉, 월봉
        global 현재가, 시가, 고가, 저가, 종가, 거래량, NAV, 거래량이평3, 이격도20이평, 등락율, 시가총액, 이평, 진입가
        global 장종료시간, 데이터길이, 진입시간, 현재시간, 시분초
        global 분할상태, 매입율
        global 콜옵션, 콜옵션_위클리, 풋옵션, 풋옵션_위클리, 거래량상위, 등락률상위
        global 거래대금상위, 시가총액상위, 시간외잔량상위, 체결강도상위, 관심종목등록상위
        ###
        # 현재시간 = current_time
        # 캔들종료시간 = candle_endtime
        # 장종료시간 = jang_endtime
        # 진입시간 = enter_time
        stg = dict_stg_stg['전략명']
        전략명 = stg
        종목코드 = dict_stg_stg['종목코드']
        현재시간 = dict_stg_stg['현재시간']
        # 캔들종료시간 = dict_stg_stg['캔들종료시간']
        장종료시간 = dict_stg_stg['장종료시간']
        진입시간 = dict_stg_stg['진입시간']
        bong = dict_stg_stg['봉']
        bong_detail = dict_stg_stg['상세봉']
        시분초 = common_def.datetime_to_int_time(현재시간)
        매입율 = 0
        데이터길이 = data_length
        시장가 = '시장가'
        # 롱 = 'long'
        # 숏 = 'short'
        long = 'long'
        short = 'short'
        콜옵션 = '콜옵션'
        풋옵션 = '풋옵션'
        콜옵션_위클리 = '콜옵션_위클리'
        풋옵션_위클리 = '풋옵션_위클리'
        거래대금상위 = '거래대금상위'
        시가총액상위 = '시가총액상위'
        # 전략명 = stg
        # 종목코드 = ticker
        for i in range(10):
            globals()[f'매도{i}호가'] = f'매도{i}호가'
        for i in range(10):
            globals()[f'매수{i}호가'] = f'매수{i}호가'
        매수 = False
        매도 = False
        재진입금지 = False

        현재가 = df_detail.loc[df_detail.index[-1],'상세종가']
        최저수익률 = self.df_trade.loc[stg, '최저수익률']
        최고수익률 = self.df_trade.loc[stg, '최고수익률']
        수익률 = self.df_trade.loc[stg, '수익률']
        잔고 = self.df_trade.loc[stg, '잔고']
        방향 = self.df_trade.loc[stg, '방향']
        레버리지 = self.df_trade.loc[stg, '레버리지']

        분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])

        # 평가금액 = self.df_trade.loc[stg, '평가금액']
        # 분할매수 = json.loads(self.df_trade.loc[stg, '분할매수'])
        # 분할매도 = json.loads(self.df_trade.loc[stg, '분할매도'])
        # df_detail = globals()[f'{ticker}_{self.dict_bong[bong]}']
        market = self.market
        dict_bong_stamp = self.dict_bong_stamp
        bong_stamp = dict_bong_stamp[bong]
        bong_detail_stamp = dict_bong_stamp[bong_detail]


        np_tik_ar = df_detail.to_numpy()  # 전체 데이터를 np로 저장
        np_tik_idx = df_detail.index.to_numpy()  # 인덱스를 np로 저장
        list_columns = df_detail.columns.tolist()  # 컬럼명을 리스트로 저장
        np_tik_length = df_detail['데이터길이'].to_numpy()  # 인덱스를 np로 저장
        # if ticker == '309D5W350':
        #     self.test_sql(df_detail,'거래량')

        for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
            globals()[f'{col}'] = np_tik_ar[-1, list_columns.index(f'{col}')]
        if 상태 == '대기' or 상태 == '분할매수대기': # 미 보유 시 진입 주문
            if self.df_trade.loc[stg, '매도전환'] != "재진입금지":
                stg_buy = self.df_trade.loc[stg,'진입전략']
                locals_dict_buy = {}
                exec(stg_buy, None, locals_dict_buy) #전략연산

                매수 = locals_dict_buy.get('매수')

                if 매수 != False and 매수 != None :  # 매수 주문
                    매수가 = locals_dict_buy.get('매수가')
                    self.df_trade.loc[stg, 'ticker'] = 종목코드
                    self.df_trade.loc[stg, '현재가'] = 현재가
                    if type(매수가) == list and type(매수) == list: # 분할매수일 경우
                        상태 = self.buy_on_scale(stg, 매수, 매수가, 방향, 레버리지, 배팅금액, 상태)
                        # print(f"{상태= }")
                        if 상태 == '분할매수대기':
                            누적수익음 = self.cal_ror(stg, 현재가, 방향)  # 나중에 balance_account랑 합쳐야 됨
                    else:
                        상태 = '매수주문'
                        self.df_trade.loc[stg, '분할상태'] = json.dumps(분할상태, ensure_ascii=False)
                        상태, 수량, 진입가, 수수료, id = self.order_buy(stg, 매수, 매수가, 방향, 레버리지, 배팅금액, 상태) #시장가 매수 일 경우 '매수'를 받기 때문에 상태를 반환받아야됨
                    self.df_trade.loc[stg, '상태'] = 상태
                    self.df_trade.loc[stg, '진입시간'] = common_def.datetime_to_str(현재시간)
                    list_enter_sig = json.loads(self.df_trade.loc[stg, '진입신호시간'])
                    list_enter_sig.append(common_def.datetime_to_str(현재시간))
                    # list_enter_sig = [x for x in list_enter_sig if x] #리스트에 빈값""이 있으면 없애기
                    self.df_trade.loc[stg, '진입신호시간'] = json.dumps(list_enter_sig,ensure_ascii=False)
                    # print(self.df_trade)
                elif self.df_trade.loc[stg, 'ticker'] != '':
                    self.df_trade.loc[stg, '현재가'] = 현재가
        elif 상태 == '매수주문' or 상태 == '부분매수' or 상태 == '시장가매수' or 상태 == '매수취소' or \
               상태 == '분할매수주문' or 상태 == '분할부분매수' or 상태 == '분할매수취소': # 진입 주문 시
            self.df_trade.loc[stg, '현재가'] = 현재가
            # print(f"elif 상태 == '매수주문' or 상태 == '부분매수' {stg= }     {종목코드=  }     {상태= }   {분할상태=}" )
            if 상태 == '분할매수주문' or 상태 == '분할부분매수' or 상태 == '분할매수취소': #분할매수일 경우
                self.chegyeol_buy_on_scale(stg, 종목코드, 방향, 현재시간, 상태)
            else:
                누적진입수수료= self.df_trade.loc[stg, '진입수수료']
                주문수량 = self.df_trade.loc[stg, '주문수량']
                보유수량 = self.df_trade.loc[stg, '보유수량']
                매입금액 = self.df_trade.loc[stg, '매입금액']
                진입가 = self.df_trade.loc[stg, '진입가']
                id = self.df_trade.loc[stg, 'id']
                상태, 보유수량, 매입금액, 총진입수수료, 진입가 = self.chegyeol_buy(stg, 종목코드, 방향, 진입가, 현재시간, 상태, 잔고,누적진입수수료,주문수량,보유수량,매입금액,id)
                self.df_trade.loc[stg, '진입수수료'] = 총진입수수료
                self.df_trade.loc[stg, '상태'] = 상태
                if 상태 == '매수':
                    self.df_trade.loc[stg, '매도전환'] = "True"
            self.cal_ror(stg,현재가,방향)
        elif 상태 == '매수' or 상태 == '분할매수' : # 보유 시
            # print(f"elif 상태 == '매수' {stg= }    {종목코드=}    {상태= }     {self.df_trade.loc[stg, '매도전환']}")
            if self.df_trade.loc[stg, '매도전환'] == 'True': #매수가되면 분할매도 때문에 최초 분할 수량을 배정함
                보유수량 = self.df_trade.loc[stg, '보유수량']
                진입수수료 = self.df_trade.loc[stg, '진입수수료']
                분할매도 = json.loads(self.df_trade.loc[stg, '분할매도'])
                decimal_val = self.decimal_places(보유수량)
                분할주문수량 = self.distribute_by_ratio(보유수량, 분할매도, decimal_val)
                decimal_val = self.decimal_places(진입수수료)
                분할진입수수료 = self.distribute_by_ratio(진입수수료, 분할매도, decimal_val)

                empty_zero = [0 for x in range(len(분할주문수량))]
                # 분할청산금액 = [0 for x in range(len(분할주문수량))]
                empty_txt = ['' for x in range(len(분할주문수량))]
                분할상태 = ['매수' for x in range(len(분할주문수량))]
                for i,qty in enumerate(분할주문수량): # 2개 진입했는데 분할이 3개 일 경우
                    if qty == 0:
                        분할상태[i] = '매도'
                self.df_trade.loc[stg, '분할상태'] = json.dumps(분할상태, ensure_ascii=False)
                self.df_trade.loc[stg, '분할주문수량'] = json.dumps(분할주문수량)
                self.df_trade.loc[stg, '분할진입수수료'] = json.dumps(분할진입수수료)
                self.df_trade.loc[stg, '분할보유수량'] = json.dumps(분할주문수량)
                self.df_trade.loc[stg, '분할청산금액'] = json.dumps(empty_zero)
                self.df_trade.loc[stg, '분할청산가'] = json.dumps(empty_zero)  # 코인 모의매매를 위해 필요
                self.df_trade.loc[stg, '분할평가금액'] = json.dumps(empty_zero)  # 코인 모의매매를 위해 필요
                self.df_trade.loc[stg, '분할id'] = json.dumps(empty_txt, ensure_ascii=False)
                self.df_trade.loc[stg, '분할청산시간'] = json.dumps(empty_txt, ensure_ascii=False)
                self.df_trade.loc[stg, '주문수량'] = sum(분할주문수량)
                self.df_trade.loc[stg, '매도전환'] = '매도중'
                상태 = '매수'
                self.df_trade.loc[stg, '상태'] = 상태
                print(f"if self.df_trade.loc[stg, '매도전환'] == True:  {stg= }    {종목코드= }  {상태= } {분할상태= }  {self.df_trade.loc[stg, '매도전환']= }")
            # self.df_trade.loc[stg, '분할상태'] = json.dumps(['매수'], ensure_ascii=False) # chegyeol_sell에서 분할매도인지 아닌지 확인하기 위해 리스트원소를 1개로 초기화 해줌
            # print(f"elif 상태 == '매수' or {stg= }    {종목코드= }   {분할상태= }    {self.df_trade.loc[stg, '매도전환']= }   {type(self.df_trade.loc[stg, '매도전환'])= }")
            self.df_trade.loc[stg, '현재가'] = 현재가
            누적수익금 = self.cal_ror(stg, 현재가, 방향)
            # self.df_trade.drop(['진입전략','청산전략'],axis=1,inplace=True)
            # print(f"{누적수익금= }")
            진입가 = self.df_trade.loc[stg, '진입가']
            stg_sell = self.df_trade.loc[stg,'청산전략']
            locals_dict_sell = {}
            exec(stg_sell, None, locals_dict_sell)
            매도 = locals_dict_sell.get('매도')
            if 매도 == True or type(매도)==list:  # 청산 주문
                매도가 = locals_dict_sell.get('매도가')
                재진입금지 = locals_dict_sell.get('재진입금지')
                print(f"{재진입금지= }")
                if 재진입금지 == True:
                    print('재진입금지')
                    self.df_trade.loc[stg, '매도전환'] = "재진입금지"
                print(f"if 매도 == True or type(매도)==list: {stg= }    {종목코드= }   {분할상태= }   {매도=}    {매도가= }   {type(매도가)= }     {self.df_trade.loc[stg, '매도전환']= }")
                if type(매도가) == list: # 분할매도일 경우
                    상태 = self.sell_on_scale(stg, 매도, 매도가, 방향) #시장가 매도 일 경우 '매수'를 받기 때문에 반환받아야됨
                else:
                    보유수량 = self.df_trade.loc[stg, '보유수량']
                    상태 = '매도주문'
                    상태, 매도가, id = self.order_sell(stg, 매도가, 방향, 보유수량, 상태) #시장가 매도 일 경우 '매수'를 받기 때문에 반환받아야됨
                self.df_trade.loc[stg,'상태'] = 상태
                list_exit_sig = json.loads(self.df_trade.loc[stg, '청산신호시간'])
                list_exit_sig.append(common_def.datetime_to_str(현재시간))
                # list_exit_sig = [x for x in list_exit_sig if x] #리스트에 빈값""이 있으면 없애기
                self.df_trade.loc[stg, '청산신호시간'] = json.dumps(list_exit_sig,ensure_ascii=False)
            if ((누적수익금 / self.df_trade.loc[stg, '초기자금'])*100 < -80): # 80% 이하 전략폐기
                상태 = '전략폐기'
                self.df_trade.loc[stg,'상태'] = 상태
                평가금액 = self.df_trade.loc[stg, '평가금액']
                초기자금 = self.df_trade.loc[stg, '초기자금']
                매입금액 = self.df_trade.loc[stg, '매입금액']
                print(f"전략폐기 elif 상태 == '매수':: {stg} {매입금액= },  {누적수익금= }, {평가금액= }, {초기자금= }, {상태= }")
            # print('=================================================================')
        elif 상태 == '매도주문' or 상태 == '부분매도' or 상태 == '시장가매도' or \
            상태 == '분할매도주문' or 상태 == '분할부분매도': # 청산 주문 시
            self.df_trade.loc[stg, '현재가'] = 현재가
            print(f"loop_trade  -   {stg= }     {종목코드= }    {상태= }    {self.df_trade.loc[stg, '분할상태']}   {self.df_trade.loc[stg, '분할보유수량']} ")
            # 수익금, 누적수익금 = self.cal_ror(stg, 현재가, 방향)
            if 상태 == '분할매도주문' or 상태 == '분할부분매도' or 상태 == '분할매도취소': #분할매도일 경우
                상태, 누적수익금 = self.chegyeol_sell_on_scale(stg, 종목코드, 방향, 현재시간, 상태)
            else:
                보유수량 = self.df_trade.loc[stg, '보유수량']
                매입금액 = self.df_trade.loc[stg, '매입금액']

                주문수량 = self.df_trade.loc[stg, '주문수량']
                청산금액 = self.df_trade.loc[stg, '청산금액']
                진입수수료 = self.df_trade.loc[stg, '진입수수료']
                청산가 = self.df_trade.loc[stg, '청산가']
                id = self.df_trade.loc[stg, 'id']

                상태, 누적수익금, 보유수량, 평가금액, 청산금액 = \
                    self.chegyeol_sell(stg, 종목코드, 방향, 상태, 보유수량, 잔고, 현재가, 현재시간,매입금액,
                                       주문수량, 청산금액, 진입수수료, id, 청산가)

                self.df_trade.loc[stg, '보유수량'] = 보유수량
                self.df_trade.loc[stg, '평가금액'] = 평가금액
                self.df_trade.loc[stg, '최고수익률'] = np.where(수익률 > self.df_trade.loc[stg, '최고수익률'], 수익률,
                                                           self.df_trade.loc[stg, '최고수익률'])
                self.df_trade.loc[stg, '최저수익률'] = np.where(수익률 < self.df_trade.loc[stg, '최저수익률'], 수익률,
                                                           self.df_trade.loc[stg, '최저수익률'])
            # quit()
            self.df_trade.loc[stg, '상태'] = 상태
            진입가 = self.df_trade.loc[stg, '진입가']
            stg_sell = self.df_trade.loc[stg,'청산전략']
            locals_dict_sell = {}
            exec(stg_sell, None, locals_dict_sell)
            매도 = locals_dict_sell.get('매도') #매도주문 중 손절라인등으로 인해 시장가 매도가 나올 수 있으므로
            매도가 = locals_dict_sell.get('매도가')
            # 기존의 지정가주문을 취소한 후 처리해야하며 백테스트에서는 이부분이 반영이 되어있는지도 확인 필요.
            # 매수에서는 이럴경우 어떡게 되어있는지도 확인 필요
            if 매도 == True :
                재진입금지 = locals_dict_sell.get('재진입금지')
                if 재진입금지 == True:
                    self.df_trade.loc[stg, '매도전환'] = "재진입금지"
                if 매도가 == 시장가 and 상태 != '시장가매도' and 상태 != '매도': # 지정가로 매도주문이 나간상태인데 손절라인에 걸려서 시장가 매도 주문이 나가야할 경우
                    print(f'{stg= }, {종목코드= } | 잔량 시장가 매도 - {datetime.datetime.now()}')
                    주문수량 = self.df_trade.loc[stg, '주문수량']
                    보유수량 = self.df_trade.loc[stg, '보유수량']
                    if 상태 == '매도주문' or 상태 == '부분매도': #분할매도 아닐 경우
                        id = self.df_trade.loc[stg, 'id']
                        상태, 잔여수량 = self.order_cancel(stg, 종목코드, 상태, 주문수량, 보유수량, 방향,id, 0,'')
                    else: #분할매도일 경우
                        print('분할매도 시장가 손절')
                        분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
                        분할보유수량 = json.loads(self.df_trade.loc[stg, '분할보유수량'])
                        분할주문수량 = json.loads(self.df_trade.loc[stg, '분할주문수량'])
                        분할id = json.loads(self.df_trade.loc[stg, '분할id'])
                        잔여수량 = 0
                        for num, 세부상태 in enumerate(분할상태):
                            if 세부상태 == '매도주문' or 세부상태 == '시장가매도' or 세부상태 == '부분매도' :
                                상태, 세부잔여수량 = self.order_cancel(stg, 종목코드, 세부상태, 분할주문수량[num], 분할보유수량[num], 방향,분할id[num], 0,'')
                                잔여수량 += 세부잔여수량
                        print(f"if 매도 == True : {분할주문수량=}   {상태=}")
                    상태 = '매도주문'
                    상태, 매도가, id = self.order_sell(stg, 매도가, 방향, 잔여수량, 상태)
                    self.df_trade.loc[stg, '상태'] = 상태
            # elif type(매도)==list: #활성화 하면 분할보유수량이 반영안됨
            #     if type(매도가) == list:  # 분할매도일 경우
            #         상태 = self.sell_on_scale(stg, 매도, 매도가, 방향)  # 시장가 매도 일 경우 '매수'를 받기 때문에 반환받아야됨

            print(f"elif 상태 == '매도주문' or 상태 {stg= }    {누적수익금=}  {상태=}  {수익률= }  {매도= }   {매도가= }")
            if ((누적수익금 / self.df_trade.loc[stg, '초기자금'])*100 < -80):
                상태 = '전략폐기'
                self.df_trade.loc[stg,'상태'] = 상태
                평가금액 = self.df_trade.loc[stg, '평가금액']
                초기자금 = self.df_trade.loc[stg, '초기자금']
                매입금액 = self.df_trade.loc[stg, '매입금액']
                print(f"전략폐기 elif 상태 == '매도주문' or: {stg} {매입금액= },  {누적수익금= }, {평가금액= }, {초기자금= }, {상태= }")
        elif 상태 == '매도':
            # 초기화
            상태 = '청산'
            df_stg = self.df_trade.loc[[stg]]
            self.qt_closed.emit(df_stg)
            self.df_trade.loc[stg, '상태'] = 상태
            self.df_trade.loc[stg, '진입시간'] = common_def.datetime_to_str(현재시간)
            self.df_trade.loc[stg, '진입가'] = 0
            self.df_trade.loc[stg, '체결수량'] = 0
            self.df_trade.loc[stg, '보유수량'] = 0
            self.df_trade.loc[stg, '청산가'] = 0
            self.df_trade.loc[stg, '청산시간'] = ''
            self.df_trade.loc[stg, '매입금액'] = 0
            self.df_trade.loc[stg, '평가금액'] = 0
            self.df_trade.loc[stg, '청산금액'] = 0
            self.df_trade.loc[stg, '수익률'] = 0
            self.df_trade.loc[stg, '최고수익률'] = 0
            self.df_trade.loc[stg, '최저수익률'] = 0
            self.df_trade.loc[stg, '수익금'] = 0
            # self.df_trade.loc[stg, '기준잔고'] = 0
            self.df_trade.loc[stg, '수수료'] = 0
            self.df_trade.loc[stg, '진입수수료'] = 0
            self.df_trade.loc[stg, '현재가'] = 0
            if self.df_trade.loc[stg, '매도전환'] != '재진입금지':
                self.df_trade.loc[stg, '매도전환'] = 'False'
            self.df_trade.loc[stg, '배팅금액'] = self.df_trade.loc[stg, '잔고']

            분할매수 = json.loads(self.df_trade.loc[stg, '분할매수'])
            분할매도 = json.loads(self.df_trade.loc[stg, '분할매도'])

            empty_zero = [0 for x in range(len(분할매수))]
            division_zero_sell = [0 for x in range(len(분할매도))]
            empty_txt = ["" for x in range(len(분할매수))]
            list_state = ["대기" for x in range(len(분할매수))]
            self.df_trade.loc[stg, '분할상태'] = json.dumps(list_state,ensure_ascii=False)
            self.df_trade.loc[stg, '분할진입가'] = json.dumps(empty_zero)
            self.df_trade.loc[stg, '분할청산가'] = json.dumps(division_zero_sell)
            self.df_trade.loc[stg, '분할주문수량'] = json.dumps(empty_zero)
            self.df_trade.loc[stg, '분할보유수량'] = json.dumps(empty_zero)
            self.df_trade.loc[stg, '분할매입금액'] = json.dumps(empty_zero)
            self.df_trade.loc[stg, '분할청산금액'] = json.dumps(empty_zero)
            self.df_trade.loc[stg, '분할진입수수료'] = json.dumps(empty_zero)
            self.df_trade.loc[stg, '분할id'] = json.dumps(empty_txt,ensure_ascii=False)
            self.df_trade.loc[stg, '분할진입시간'] = json.dumps(empty_txt,ensure_ascii=False)
            self.df_trade.loc[stg, '분할청산시간'] = json.dumps(empty_txt,ensure_ascii=False)
            self.df_trade.loc[stg, '진입신호시간'] = json.dumps([])
            self.df_trade.loc[stg, '청산신호시간'] = json.dumps([])

            if self.df_trade.loc[stg, '진입대상'][0] == '[' or self.df_trade.loc[stg, '진입대상'][0] == '{' :
                self.df_trade.loc[stg, 'ticker'] = ''

        elif 상태 == '청산' or 상태 == '매수불가':
            if self.df_trade.loc[stg, 'ticker'] != '':
                self.df_trade.loc[stg, '현재가'] = 현재가 #qt_open에 현재가를 표시해주기 위함
        elif 상태 == '전략폐기':
            print(f"{stg} 전략폐기")
        # print(self.df_trade)

    def chegyeol_buy(self, stg, ticker, 방향, 진입가,현재시간, 상태, 잔고, 누적진입수수료,주문수량,보유수량,매입금액,id):
        trade_market = self.df_trade.loc[stg, 'market']
        레버리지 = self.df_trade.loc[stg, '레버리지']
        증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1 / 레버리지 if trade_market == 'bybit' else 1

        총진입수수료 = 0
        총체결수량 = 0
        # i = 0
        dict_chegyeol=''
        if self.market == '코인':
            보유수량 = float(보유수량)
            매입금액 = float(매입금액)
            if self.simul.isChecked() == False:  # 실매매시
                # while True:
                ord_open = self.fetch_open_orders(id, ticker)
                if ord_open == None:  # 체결일 경우
                    ord_closed = self.fetch_closed_orders(id, ticker)  # open 주문과 close 주문 2중으로 확인
                    진입가 = float(ord_closed['average'])
                    총체결수량 = float(ord_closed['filled'])
                    진입수수료 = float(ord_closed['fee']['cost'])
                    총체결금액 = float(ord_closed['cost'])

                    if 주문수량 >= 총체결수량:
                        if 상태 != '시장가매수' and 상태 != '매수취소' and 총체결수량 > 0:
                            상태 = '부분매수'
                        if 보유수량 < 총체결수량:
                            체결금액 = 총체결금액 - 매입금액
                            매입금액 = 매입금액 + 체결금액
                            self.df_trade.loc[stg, '매입금액'] = 매입금액
                            총진입수수료 = 누적진입수수료 + 진입수수료
                            체결수량 = 총체결수량 - 보유수량
                            self.df_trade.loc[stg, '체결수량'] = 체결수량
                            보유수량 = 보유수량 + 체결수량
                            if 총체결수량 != 보유수량 or 매입금액 != 총체결금액:
                                print(f"chegyeol_buy ---{stg= },{ticker= } {총체결수량= }, {보유수량= }, {체결수량}, {총체결금액= }, {매입금액= }, {체결금액= }")
                                raise
                            self.df_trade.loc[stg, '보유수량'] = 보유수량

                            잔고 = 잔고 - (체결금액 * 증거금률) - 진입수수료
                            if 주문수량 == 보유수량:
                                상태 = '매수'
                                txt = 'open 체결'
                            else:
                                txt = 'open 부분체결'
                            # print(f"chegyeol_buy:  {stg= }, {ticker= }, {주문수량= } , {총체결수량= } {체결금액= }| {보유수량= } * {현재가= } {상태}")
                            self.color_text(state=txt, stg=stg, ticker=ticker, 방향=방향, 진입가=진입가, 주문수량=주문수량, 체결수량=체결수량,
                                            보유수량=보유수량, 체결금액=체결금액, 매입금액=매입금액, 잔고=잔고, 수수료=진입수수료,상태=상태)

                # else: #매수 주문이 있는데 체결이 안되었을 경우
            elif self.simul.isChecked() == True:  # 모의매매시
                # 진입가 = self.df_trade.loc[stg, '진입가']
                if (방향 == 'long' and 현재가 <= 진입가) or (방향 == 'short' and 현재가 >= 진입가) or 상태 == '시장가매수':
                    상태 = '매수'
                    체결수량 = float(주문수량)
                    보유수량 = float(주문수량)
                    self.df_trade.loc[stg, '체결수량'] = 체결수량
                    self.df_trade.loc[stg, '보유수량'] = 체결수량
                    fee = self.fee_bybit_market if 상태 == '시장가매수' else self.fee_bybit_limit
                    진입수수료 = 진입가 * 체결수량 * fee / 100
                    총진입수수료 = 진입수수료
                    self.df_trade.loc[stg, '진입수수료'] = 총진입수수료
                    체결금액 = round(진입가 * 체결수량,2)
                    매입금액 = 체결금액
                    self.df_trade.loc[stg, '매입금액'] = 매입금액
                    잔고 = round(잔고 - (체결금액 * 증거금률) - 진입수수료, 4)
                    self.color_text(state='open 체결', stg=stg, ticker=ticker, 방향=방향, 진입가=진입가, 주문수량=주문수량, 체결수량=체결수량,
                                    보유수량=보유수량, 체결금액=체결금액, 매입금액=매입금액, 잔고=잔고, 수수료=진입수수료)

        elif self.market == '국내주식' or self.market == '국내선옵':
            보유수량 = int(보유수량)
            매입금액 = int(매입금액)
            if 방향 == 'long': dict_chegyeol = self.ex_kis.fetch_closed_order(side='buy',ticker=ticker,id=id)
            elif 방향 == 'short': dict_chegyeol = self.ex_kis.fetch_closed_order(side='sell',ticker=ticker,id=id)
            if dict_chegyeol: # 매수취소여도 체결되었는지 한번 더 확인

                총체결수량 = int(dict_chegyeol['tot_ccld_qty'])
                잔여수량 = int(dict_chegyeol['qty'])
                총체결금액 = int(dict_chegyeol['tot_ccld_amt'])
                if self.market == '국내주식':
                    진입가 = float(dict_chegyeol['avg_prvs'])
                    fee = self.fee_stock
                elif self.market == '국내선옵':
                    진입가 = float(dict_chegyeol['avg_idx'])
                    fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 진입가 > 2.47 or 진입가 < 0.42 else self.fee_putopt2
                # print(f"1:{self.df_trade.loc[stg, '잔고']= } {잔고= }  {stg= }, {ticker= }, {주문수량= } , {총체결수량= } {총체결금액= }| {보유수량= } * {현재가= } {상태}")

                if 주문수량 >= 총체결수량:
                    if 상태 != '시장가매수' and 상태 != '매수취소' and 총체결수량 > 0:
                        상태 = '부분매수'
                    if 보유수량 < 총체결수량:
                        체결금액 = 총체결금액 - 매입금액
                        매입금액 = 매입금액 + 체결금액
                        self.df_trade.loc[stg, '매입금액'] = 매입금액
                        진입수수료 = 체결금액 * fee // 100
                        총진입수수료 = 누적진입수수료 + 진입수수료
                        체결수량 = 총체결수량 - 보유수량
                        self.df_trade.loc[stg, '체결수량'] = 체결수량
                        보유수량 = 보유수량 + 체결수량
                        if 총체결수량 != 보유수량 or 매입금액 != 총체결금액:
                            print(f"chegyeol_buy ---{stg= },{ticker= } {총체결수량= }, {보유수량= }, {체결수량}, {총체결금액= }, {매입금액= }, {체결금액= }")
                            raise
                        self.df_trade.loc[stg, '보유수량'] = 보유수량

                        잔고 = 잔고 - (체결금액 * 증거금률) - 진입수수료
                        if 주문수량 == 보유수량:
                            상태 = '매수'
                            txt = 'open 체결'
                        else:
                            txt = 'open 부분체결'
                        # print(f"chegyeol_buy:  {stg= }, {ticker= }, {주문수량= } , {총체결수량= } {체결금액= }| {보유수량= } * {현재가= } {상태}")

                        self.color_text(state=txt, stg=stg, ticker=ticker,방향=방향,진입가=진입가, 주문수량=주문수량, 체결수량=체결수량, 보유수량=보유수량, 체결금액=체결금액, 매입금액=매입금액, 잔고=잔고, 수수료=진입수수료, 상태=상태)
            # else: #매수 주문이 있는데 체결이 안되었을 경우
            #     print(f"dict_chegyeol: {stg= }, {ticker= }, {dict_chegyeol}")

        if 상태 == '매수취소' :  # 체결시간이 지났을 경우 나머지 취소
            상태, 잔여수량 = self.order_cancel(stg, ticker, 상태, 주문수량, 보유수량, 방향, id, 총체결수량,dict_chegyeol)
        elif 상태 == '시장가매수' and self.market=='국내주식': #선물옵션은 시장가 주문 시 10호가로 지정가 주문 변경
            상태 = '매수주문' if 보유수량 == 0 else '부분매수'
        elif 상태 == '매수' or 상태 == '부분매수': # 부분매수 후 캔들종료시간<현재시간 인 경우는 매수로 전환
            # print(f"if 상태 == '매수' or 상태 == '부분매수': {상태}")
            self.df_trade.loc[stg, '진입가'] = 진입가
            self.df_trade.loc[stg, '잔고'] = 잔고
            # 진입수수료 = round(체결금액 * fee / 100)
            # self.df_trade.loc[stg, '진입수수료'] = 진입수수료
            self.df_trade.loc[stg, '진입시간'] = common_def.datetime_to_str(현재시간)
            # self.df_trade.loc[stg, '매입금액'] = 체결금액
            거래승수 = self.dic_multiplier[ticker[:3]] if self.market == '국내선옵' else 1
            self.df_trade.loc[stg, '평가금액'] = round(보유수량 * 현재가 * 거래승수 - self.df_trade.loc[stg, '진입수수료'])

            if 상태 == '매수':
                self.df_trade.loc[stg, '수수료'] = self.df_trade.loc[stg, '진입수수료']*2
                # self.df_trade.loc[stg, '잔고'] = 잔고 # 루프 돌때마다 다시 부르기때문에 매수 이후로 저장 해야됨
                self.df_trade.loc[stg, '체결수량'] = 0
                self.df_trade.loc[stg, 'id'] = ''
                분할매수 = json.loads(self.df_trade.loc[stg, '분할매수'])
                if len(분할매수) == 0:  #분할로 매수한게 아닐 경우
                    self.df_trade.loc[stg, '매도전환'] = "True"
                    print('if sum(분할보유수량) == 0: - 매수완료 분할매수 아님')
        return 상태, 보유수량, 매입금액, 총진입수수료, 진입가

    def chegyeol_sell(self, stg, ticker, 방향, 상태, 보유수량, 잔고, 현재가, 현재시간, 매입금액,
                      주문수량, 청산금액, 진입수수료, id, 청산가):
        체결수량 = self.df_trade.loc[stg, '체결수량']
        수익금 = self.df_trade.loc[stg, '수익금']
        누적수익금 = self.df_trade.loc[stg, '누적수익금']


        # 주문수량 = self.df_trade.loc[stg, '주문수량']
        # 청산금액 = self.df_trade.loc[stg, '청산금액']
        # 진입수수료 = self.df_trade.loc[stg, '진입수수료']
        # id = self.df_trade.loc[stg, 'id']
        trade_market = self.df_trade.loc[stg, 'market']
        레버리지 = self.df_trade.loc[stg, '레버리지']
        # ticker = self.df_trade.loc[stg, 'ticker']
        거래승수 = self.dic_multiplier[ticker[:3]] if self.market == '국내선옵' else 1
        증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1/레버리지 if trade_market == 'bybit' else 1
        체결 = False # 체결이 됐을 때 만
        if self.market == '코인':
            if self.simul.isChecked() == False:  # 실매매시
                ord_open = self.fetch_open_orders(id, ticker)
                if ord_open == None: # 체결일 경우
                    ord_closed = self.fetch_closed_orders(id, ticker)  # open 주문과 close 주문 2중으로 확인
                    청산가 = float(ord_closed['average'])
                    총체결수량 = float(ord_closed['filled'])
                    청산수수료 = float(ord_closed['fee']['cost'])
                    총체결금액 = float(ord_closed['cost'])
                    # 주문수량 = order_closed['amount']
                    print(f"{청산가=}  {총체결수량=}  {청산수수료=}   {총체결금액=}")
                    if 주문수량 >= 총체결수량:
                        if 상태 != '시장가매도' and 총체결수량 > 0:
                            상태 = '부분매도'
                        if 주문수량 - 보유수량 < 총체결수량:
                            체결 = True
                            체결금액 = float(총체결금액 - 청산금액)
                            청산금액 = float(청산금액 + 체결금액)
                            self.df_trade.loc[stg, '청산금액'] = 청산금액
                            self.df_trade.loc[stg, '수수료'] = self.df_trade.loc[stg, '수수료'] + 청산수수료
                            체결수량 = float(총체결수량 - (주문수량 - 보유수량))
                            보유수량 = float(보유수량 - 체결수량)
                            self.df_trade.loc[stg, '체결수량'] = 체결수량
                            잔고 = float(잔고 + round(체결금액*증거금률) - 청산수수료)
                            self.df_trade.loc[stg, '잔고'] = 잔고
                            fee = 청산수수료
            elif self.simul.isChecked() == True:  # 모의매매시
                # 청산가 = self.df_trade.loc[stg, '청산가']
                # print(f"{방향= }, {현재가= }, {청산가= }")
                if (방향 == 'long' and 현재가 >= 청산가) or (방향 == 'short' and 현재가 <= 청산가) or 상태 == '시장가매도':
                    체결 = True
                    상태 = '매도'
                    체결수량 = 주문수량
                    체결금액 = float(청산가 * 체결수량)
                    청산금액 = 체결금액
                    self.df_trade.loc[stg, '청산금액'] = 청산금액

                    fee = self.fee_bybit_market if 상태 == '시장가매도' else self.fee_bybit_limit
                    청산수수료 = round(체결금액 * fee / 100, 4)
                    self.df_trade.loc[stg, '수수료'] = self.df_trade.loc[stg, '수수료'] + 청산수수료
                    보유수량 = 0
                    # self.df_trade.loc[stg, '보유수량'] = 보유수량
                    self.df_trade.loc[stg, '체결수량'] = 체결수량
                    잔고 = 잔고 + (체결금액*증거금률) - 청산수수료
                    self.df_trade.loc[stg, '잔고'] = 잔고
        elif self.market == '국내주식' or self.market == '국내선옵':
            if self.market == '국내주식':
                dict_chegyeol = self.ex_kis.fetch_closed_order(side='sell',ticker=ticker,id=id)
                fee = self.fee_stock + self.tax_stock
            else : # self.market == '국내선옵' 일 경우
                if 방향 == 'long': dict_chegyeol = self.ex_kis.fetch_closed_order(side='sell',ticker=ticker,id=id)
                if 방향 == 'short': dict_chegyeol = self.ex_kis.fetch_closed_order(side='buy',ticker=ticker,id=id)
                fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 현재가 > 2.47 or 현재가 < 0.42 else self.fee_putopt2
            # print(f"{stg= }")
            # pprint(dict_chegyeol)
            if dict_chegyeol:
                총체결수량 = int(dict_chegyeol['tot_ccld_qty'])
                총체결금액 = int(dict_chegyeol['tot_ccld_amt'])

                print(f"elif self.market == '국내주식' or self.market == '국내선옵'::{stg=}  {주문수량= } , {총체결수량= } | {상태= } : {잔고= }")
                if self.market == '국내주식':
                    청산가 = float(dict_chegyeol['avg_prvs'])
                elif self.market == '국내선옵':
                    청산가 = float(dict_chegyeol['avg_idx'])
                    fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 청산가 > 2.47 or 청산가 < 0.42 else self.fee_putopt2
                    # if trade_market == '선물':  # 선물일 경우 위탁증거금률을 사용하기 때문에
                    #     총체결금액 = 총체결금액 / self.위탁증거금률


                if 주문수량 >= 총체결수량:
                    if 상태 != '시장가매도' and 총체결수량 > 0:
                        상태 = '부분매도'

                    if 주문수량 - 보유수량 < 총체결수량:
                        체결 = True
                        체결금액 = int(총체결금액 - 청산금액)
                        청산금액 = int(청산금액 + 체결금액)
                        self.df_trade.loc[stg, '청산금액'] = 청산금액
                        청산수수료 = int(체결금액 * fee // 100)
                        self.df_trade.loc[stg, '수수료'] = self.df_trade.loc[stg, '수수료'] + 청산수수료
                        체결수량 = int(총체결수량 - (주문수량 - 보유수량))
                        보유수량 = int(보유수량 - 체결수량)
                        self.df_trade.loc[stg, '체결수량'] = 체결수량
                        잔고 = int(잔고 + round(체결금액*증거금률) - 청산수수료)
                        self.df_trade.loc[stg, '잔고'] = 잔고
            else:
                print(f"매도체결 없음 {stg= }, {ticker= }, {상태= }, {보유수량= }, {잔고= }, {현재가= }, {현재시간= },  {id=} {dict_chegyeol}")

        if 상태 == '매도' or 상태 == '부분매도' or (상태 == '시장가매도' and 체결수량 != 0):
            if 체결 == False:
                평가금액 = 청산금액 + (보유수량 * 현재가 * 거래승수)
                # self.df_trade.loc[stg, '평가금액'] = 평가금액
                청산수수료 = (보유수량 * 현재가 * 거래승수) * fee / 100
                if 방향 == 'long': 수익금 = 평가금액 - 매입금액 - 청산수수료 - 진입수수료
                elif 방향 == 'short': 수익금 = 매입금액 - 평가금액 - 청산수수료 - 진입수수료
                수익률 = round((수익금 / (매입금액 * 증거금률) * 100), 2)
            else: #신규 체결이 발생할 경우
                평가금액 = 청산금액 + (보유수량 * 현재가 * 거래승수)  # 선물의 경우 총체결금액이
                # self.df_trade.loc[stg, '평가금액'] = 평가금액
                남은청산수수료 = (보유수량 * 현재가 * 거래승수) * fee / 100
                if 방향 == 'long': 수익금 = 평가금액 - 매입금액 - 청산수수료 - 진입수수료 - 남은청산수수료
                elif 방향 == 'short': 수익금 = 매입금액 - 평가금액 - 청산수수료 - 진입수수료 - 남은청산수수료
                # print(f"{청산금액= }    {보유수량= }   {현재가= }   {(보유수량 * 현재가 * 거래승수)= }   {수익금= }   {평가금액= }    {매입금액= }")
                수익률 = round((수익금 / (매입금액 * 증거금률) * 100), 2)
                print( f"chegyeol_sell: {stg=} {ticker=} {체결수량= }, {상태= }, {평가금액= }, {청산금액= }, {보유수량= }, {현재가= }, {거래승수= }, {체결금액= }, {수익금= }, {매입금액= }, {청산수수료= }, {진입수수료= }, {남은청산수수료=}  {증거금률=}")
                if 보유수량 == 0:
                    상태 = '매도'
                    txt = 'close 체결'
                else:
                    txt = 'close 부분체결'

                self.color_text(state=txt, stg=stg, ticker=ticker, 방향=방향, 청산가=청산가, 주문수량=주문수량, 체결수량=주문수량-보유수량, 보유수량=보유수량,
                                체결금액=체결금액, 매입금액=매입금액, 수익금=수익금, 수익률=수익률, 잔고=잔고, 수수료=self.df_trade.loc[stg, '수수료'], 상태=상태)

            print(f"if 상태 == '매도' or 상태 == '부분 {stg= }, {ticker= }, {청산가=}  {수익금= } = {평가금액= } - {매입금액= } - {청산수수료= } - {진입수수료= }= ")
            self.df_trade.loc[stg, '청산가'] = round(청산가,2) if self.market == '국내선옵' else 청산가
            self.df_trade.loc[stg, '수익금'] = round(수익금,2) if self.market == '코인' else round(수익금)
            self.df_trade.loc[stg, '수익률'] = 수익률

            누적수익금 = 누적수익금 + 수익금
            if 상태 == '매도':
                # print(f"chegyeol_sell- if 상태 == '매도': {stg=} {ticker=} {체결수량= }, {상태= }, {평가금액= }, {청산금액= }, {보유수량= }, {현재가= }, {거래승수= }, {청산금액= }, {체결금액= }, {수익금= }, {누적수익금=}, {매입금액= }, {청산수수료= }, {진입수수료= }")
                self.df_trade.loc[stg, '누적수익금'] = round(누적수익금,2) if self.market == '코인' else round(누적수익금)
                self.df_trade.loc[stg, '체결수량'] = 0
                self.df_trade.loc[stg, '청산시간'] = common_def.datetime_to_str(현재시간)
                # self.df_trade.loc[stg, '잔고'] = round(잔고 - (체결금액 / 레버리지) - 청산수수료, 4)
                분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])

                if len(분할상태) < 2: #분할매도가 아닐경우
                    win_per = self.df_trade.loc[stg, '승률(win/all)']
                    win = win_per[:win_per.index('/')]
                    all = win_per[win_per.index('/') + 1:win_per.index('(')]
                    win = int(win) + 1 if 수익률 > 0 else int(win) + 0
                    self.df_trade.loc[stg, '승률(win/all)'] = f'{win}/{int(all) + 1}({round(win / (int(all) + 1) * 100, 1)})%'

        else: #매도가 안되었을 경우
            # 분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
            # if len(분할상태) < 2: #분할매도가 아닐경우
            평가금액 = 보유수량 * 현재가 * 거래승수
            print(f'매도안됨  {평가금액} = {보유수량} * {현재가} * {거래승수}')
            # print(f"{보유수량= } , {현재가= }   {거래승수= }")
            if self.market == '국내주식': fee = self.fee_stock + self.tax_stock #
            elif self.market == '국내선옵': fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 현재가 > 2.47 or 현재가 < 0.42 else self.fee_putopt2 #
            elif self.market == '코인': fee = self.fee_bybit_market
            청산수수료 = 평가금액 * fee / 100
            if 방향 == 'long': 수익금 = 평가금액 - 매입금액 - 청산수수료 - 진입수수료
            elif 방향 == 'short': 수익금 = 매입금액 - 평가금액 - 청산수수료 - 진입수수료
            # print(f"chegyeol_sell_else: {stg=} {ticker= } {체결수량= }, {상태= }, {평가금액= }, {청산금액= }, {보유수량= }, {현재가= }, {거래승수= }, {청산금액= }, {수익금= }, {매입금액= }, {청산수수료= }, {진입수수료= }")
            # print(f"{수익금} = {평가금액} - {매입금액} - {청산수수료} - {진입수수료}= ")
            self.df_trade.loc[stg, '수익금'] = round(수익금, 2) if self.market == '코인' else round(수익금)
            # 누적수익금 = round(누적수익금, 2) if self.market == '코인' else round(누적수익금)
            수익률 = round((수익금 / (매입금액 * 증거금률) * 100), 2)
            self.df_trade.loc[stg, '수익률'] = 수익률
            누적수익금 = 누적수익금 + 수익금
            청산금액 = 0
                # print(f"{평가금액}, {매입금액= },  {수익률= } , {누적수익금= }   {수익금= }")
            # else: #분할매도일 경우
            #     평가금액 = self.df_trade.loc[stg, '보유수량'] * 현재가 * 거래승수
            #     if self.market == '국내주식': fee = self.fee_stock + self.tax_stock #
            #     elif self.market == '국내선옵': fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 현재가 > 2.47 or 현재가 < 0.42 else self.fee_putopt2 #
            #     elif self.market == '코인': fee = self.fee_bybit_market
            #     청산수수료 = 평가금액 * fee / 100
            #     if 방향 == 'long': 수익금 = 평가금액 - 매입금액 - 청산수수료 - 진입수수료
            #     elif 방향 == 'short': 수익금 = 매입금액 - 평가금액 - 청산수수료 - 진입수수료
            #     수익률 = round((수익금 / (매입금액 * 증거금률) * 100), 2)*레버리지
            #     self.df_trade.loc[stg, '수익금'] = 수익금
            #     # self.df_trade.loc[stg, '평가금액'] = 평가금액
            #     self.df_trade.loc[stg, '수익률'] = 수익률
            #     print(f"chegyeol_sell -  보유수량= {self.df_trade.loc[stg, '보유수량']} {매입금액= }   {증거금률= }  {fee= }  {청산수수료= }  {수익률=}  {수익금= }   {평가금액= } ")

            # print(f"{평가금액= }, {보유수량= } {수익률= } {누적수익금= } {수익금= } {매입금액=} {청산수수료=} {진입수수료=}")
            # print(f"평가금액 = {self.df_trade.loc[stg, '보유수량'] * 현재가 * 거래승수}")
            # quit()
        # if len(json.loads(self.df_trade.loc[stg, '분할상태'])) < 2: #분할매도가 아닐경우
        #     self.df_trade.loc[stg, '최고수익률'] = np.where(수익률 > self.df_trade.loc[stg, '최고수익률'],수익률, self.df_trade.loc[stg, '최고수익률'])
        #     self.df_trade.loc[stg, '최저수익률'] = np.where(수익률 < self.df_trade.loc[stg, '최저수익률'],수익률, self.df_trade.loc[stg, '최저수익률'])

        return 상태, 누적수익금, 보유수량, 평가금액, 청산금액

    def chegyeol_buy_on_scale(self,stg, ticker, 방향, 현재시간, 상태):
        global 매입율, 매도전환
        # print('===================')
        # print('chegyeol_buy_on_scale')
        trade_market = self.df_trade.loc[stg, 'market']
        분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
        분할주문수량 = json.loads(self.df_trade.loc[stg, '분할주문수량'])
        분할보유수량 = json.loads(self.df_trade.loc[stg, '분할보유수량'])
        분할매입금액 = json.loads(self.df_trade.loc[stg, '분할매입금액'])
        분할진입가 = json.loads(self.df_trade.loc[stg, '분할진입가'])
        분할진입수수료 = json.loads(self.df_trade.loc[stg, '분할진입수수료'])
        분할id = json.loads(self.df_trade.loc[stg, '분할id'])
        # 분할매수 = json.loads(self.df_trade.loc[stg, '분할매수'])
        분할진입시간 = json.loads(self.df_trade.loc[stg, '분할진입시간'])

        거래승수 = self.dic_multiplier[ticker[:3]] if self.market == '국내선옵' else 1
        증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1 / 레버리지 if trade_market == 'bybit' else 1

        # print(f"{datetime.datetime.now().replace(microsecond=0)} | {분할상태= }  |  {상태= }")
        # 매입율 = 0
        for num, 세부상태 in enumerate(분할상태):
            if 세부상태 == '매수주문' or 세부상태 == '시장가매수' or 세부상태 == '부분매수' :
                잔고 = self.df_trade.loc[stg, '잔고']
                if 상태 == '분할매수취소':
                    세부상태 = '매수취소'
                # self.df_trade.loc[stg, '주문수량'] = 분할주문수량[num]
                # self.df_trade.loc[stg, '보유수량'] = 분할보유수량[num]
                # self.df_trade.loc[stg, '매입금액'] = 분할매입금액[num]
                # self.df_trade.loc[stg, 'id'] = 분할id[num]

                주문수량 = 분할주문수량[num]
                보유수량 = 분할보유수량[num]
                매입금액 = 분할매입금액[num]
                id = 분할id[num]
                진입수수료=분할진입수수료[num]
                # self.df_trade.loc[stg, '진입가'] = 분할진입가[num]
                self.df_trade.loc[stg, '현재가'] = 현재가
                세부상태, 보유수량, 매입금액, 총진입수수료, 진입가 = self.chegyeol_buy(stg, ticker, 방향,분할진입가[num], 현재시간, 세부상태, 잔고,진입수수료,주문수량,보유수량,매입금액,id)
                분할상태[num] = 세부상태
                분할보유수량[num] = 보유수량
                분할매입금액[num] = 매입금액
                분할진입수수료[num] = 총진입수수료
                분할진입가[num] = 진입가
            if 세부상태 == '매수':
                분할진입시간[num] = common_def.datetime_to_str(현재시간)
                self.df_trade.loc[stg, '분할진입시간'] = json.dumps(분할진입시간, ensure_ascii=False)
        # print(f"{분할상태=}")
        # print(f"{매입율=}")


        매입율 = int(sum(분할매입금액) / self.df_trade.loc[stg, '배팅금액']*100*증거금률)
        locals_dict_buy = {}
        exec(self.df_trade.loc[stg,'진입전략'], None, locals_dict_buy) #전략연산
        매도전환 = locals_dict_buy.get('매도전환')
        if 매도전환 == True:
            self.df_trade.loc[stg, '매도전환'] = "True"
            print(f"매도전환 == True: {stg= } ,  {ticker= }   {매입율= }  {매도전환= } {상태= }  {분할상태= }")

        if all(x == '대기' for x in 분할상태):  # 전부 대기 일 경우
            상태 = '대기'
        elif '매수주문' in 분할상태 or '시장가매수' in 분할상태 or '부분매수' in 분할상태 :
            if '매수주문' in 분할상태 or '시장가매수' in 분할상태: #상태가 '매수주문', '시장가매수', '대기'로만 되어있을 경우
                상태 = '분할매수주문'
            else:
                # print(f"chegyeol_buy_on_scale  {분할상태= }   {상태= }")
                상태 = '분할부분매수'
        elif all(x == '매수' for x in 분할상태):  # 전부 매수 일 경우
            상태 = '매수'
            self.df_trade.loc[stg, '매도전환'] = "True"
        # elif all(x in ['매수', '대기'] for x in 분할상태):
        elif '대기' in 분할상태:
            상태 = '분할매수대기'
            if self.df_trade.loc[stg, '매도전환'] == 'True':
                상태 = '매수'
                self.df_trade.loc[stg, '매도전환'] = "True"
        else:
            print(f"chegyeol_buy_on_scale - 상태확인 {분할상태=}")


        if sum(분할매입금액) == 0 or sum(분할보유수량) == 0 : #매입금액이 0일 경우
            진입가 = 0
        else:
            sum_price = 0
            for i, qty in enumerate(분할보유수량):
                sum_price = sum_price + (qty * 분할진입가[i])
            진입가 = sum_price / sum(분할보유수량)
            # 진입가 = sum(분할매입금액)/sum(분할보유수량)/거래승수

            if self.market == '국내주식':
                진입가 = self.ex_kis.hogaPriceReturn_per(self.df_stock_info.loc[ticker, '시장구분'],ticker,진입가,0)
            if self.market == '국내선옵':
                진입가 = self.ex_kis.hogaPriceReturn_per(self.market,ticker,진입가,0)
            elif self.market == '코인':
                if np.isnan(진입가):
                    진입가 = 0
                elif not 진입가 == 0:
                    진입가 = float(self.ex_bybit.price_to_precision(ticker+'USDT',진입가))
                else:
                    진입가 = 0
            평가금액 = sum(분할보유수량) * 현재가 * 거래승수

            if 방향 == 'long':
                수익금 = 평가금액 - sum(분할매입금액) - sum(분할진입수수료)
            else:
                수익금 = sum(분할매입금액) - 평가금액 - sum(분할진입수수료)
            수익률 = round((수익금 / (sum(분할매입금액) * 증거금률) * 100), 2)
            self.df_trade.loc[stg, '평가금액'] = 평가금액
            self.df_trade.loc[stg, '수익률'] = 수익률
            self.df_trade.loc[stg, '수익금'] = 수익금
        print(f"chegyeol_buy_on_scale  {stg=}, {ticker=},   매입율: {int(sum(분할매입금액) / self.df_trade.loc[stg, '배팅금액']*100*증거금률)},   {분할매입금액= },   {sum(분할매입금액)= }  {분할보유수량= }, "
              f"  {sum(분할보유수량)= } {거래승수= } {현재가}  {진입가= }  {분할상태= }  |  {상태= } {진입가=}  | {분할진입가=}  {분할주문수량= },   {sum(분할주문수량)= }   {sum(분할진입수수료)= }  {거래승수=}   "
              f"{self.df_trade.loc[stg, '매입금액']= }, {self.df_trade.loc[stg, '배팅금액']= }  {증거금률=}  {self.df_trade.loc[stg, '매도전환']=}")

        self.df_trade.loc[stg, '진입가'] = 진입가
        self.df_trade.loc[stg, '주문수량'] = sum(분할주문수량)
        self.df_trade.loc[stg, '체결수량'] = sum(분할보유수량)
        self.df_trade.loc[stg, '보유수량'] = sum(분할보유수량)
        self.df_trade.loc[stg, '매입금액'] = sum(분할매입금액)
        self.df_trade.loc[stg, '진입수수료'] = sum(분할진입수수료)
        self.df_trade.loc[stg, '상태'] = 상태
        self.df_trade.loc[stg, '분할상태'] = json.dumps(분할상태, ensure_ascii=False)
        # self.df_trade.loc[stg, '분할진입시간'] = json.dumps(분할진입시간, ensure_ascii=False)
        self.df_trade.loc[stg, '분할진입가'] = json.dumps(분할진입가)
        self.df_trade.loc[stg, '분할주문수량'] = json.dumps(분할주문수량)
        self.df_trade.loc[stg, '분할보유수량'] = json.dumps(분할보유수량)
        self.df_trade.loc[stg, '분할매입금액'] = json.dumps(분할매입금액)
        self.df_trade.loc[stg, '분할진입수수료'] = json.dumps(분할진입수수료)

        # con_ex = sqlite3.connect('DB/bt.db')
        # self.df_trade.to_sql('bt',con_ex,if_exists='replace')
        # con_ex.close()
        # quit()
        # return 상태

    def chegyeol_sell_on_scale(self,stg, ticker, 방향, 현재시간, 상태):
        # print('chegyeol_sell_on_scale')
        # 진입수수료 = self.df_trade.loc[stg, '진입수수료']
        trade_market = self.df_trade.loc[stg, 'market']
        분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
        분할주문수량 = json.loads(self.df_trade.loc[stg, '분할주문수량'])
        분할보유수량 = json.loads(self.df_trade.loc[stg, '분할보유수량'])
        분할청산가 = json.loads(self.df_trade.loc[stg, '분할청산가'])
        분할청산금액 = json.loads(self.df_trade.loc[stg, '분할청산금액'])
        분할진입수수료 = json.loads(self.df_trade.loc[stg, '분할진입수수료'])
        분할id = json.loads(self.df_trade.loc[stg, '분할id'])
        분할청산시간 = json.loads(self.df_trade.loc[stg, '분할청산시간'])
        분할평가금액 = json.loads(self.df_trade.loc[stg, '분할평가금액'])
        거래승수 = self.dic_multiplier[ticker[:3]] if self.market == '국내선옵' else 1
        증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1/레버리지 if trade_market == 'bybit' else 1
        # 잔고 = self.df_trade.loc[stg, '잔고']

        # 분할평가금액 = []
        print(f'chegyeol_sell_on_scale - start **************************{stg=} {상태= } {분할보유수량= }')
        for num, 세부상태 in enumerate(분할상태):
            # 세부상태 = 분할상태[num]
            if 세부상태 == '매도주문' or 세부상태 == '시장가매도' or 세부상태 == '부분매도' :
                잔고 = self.df_trade.loc[stg, '잔고']
                # self.df_trade.loc[stg, '주문수량'] = 분할주문수량[num]
                # self.df_trade.loc[stg, '청산금액'] = 분할청산금액[num]
                # self.df_trade.loc[stg, '진입수수료'] = 분할진입수수료[num]
                # self.df_trade.loc[stg, 'id'] = 분할id[num]
                # self.df_trade.loc[stg, '청산가'] = 분할청산가[num]

                분할매입금액 = 분할보유수량[num] * self.df_trade.loc[stg, '진입가'] * 거래승수
                분할상태[num], 누적수익금, 분할보유수량[num], 분할평가금액[num], 분할청산금액[num] = \
                    self.chegyeol_sell(stg, ticker, 방향, 세부상태, 분할보유수량[num], 잔고, 현재가, 현재시간, 분할매입금액,
                                       분할주문수량[num],분할청산금액[num],분할진입수수료[num],분할id[num],분할청산가[num])

                # 분할상태[num] = 분할상태[num]
                # 분할보유수량[num] = 분할보유수량[num]
                # 분할평가금액[num] = 분할평가금액[num]
                # 분할청산금액[num] = 분할청산금액[num]
                print(f"if 세부상태 == '매도주문' or 세부상태 == '시장가매도' or 세부상태 == '부분매도' "
                      f"{num= }  {세부상태= }  {분할상태[num]= }   {분할매입금액= }   ={분할보유수량[num]= }   {분할보유수량[num]= } * {self.df_trade.loc[stg, '진입가']= } * {거래승수= }")
                if 분할상태[num] == '매도':
                    분할청산시간[num] = common_def.datetime_to_str(현재시간)
                    self.df_trade.loc[stg, '분할청산시간'] = json.dumps(분할청산시간, ensure_ascii=False)
                    print(f"if 분할상태[num] == '매도':  {num= }   {self.df_trade.loc[stg, '분할청산시간']}   {분할청산시간[num]= } {분할상태[num]= }"
                          f"   {누적수익금= }, {분할보유수량[num]= }, {분할평가금액[num]= }, {분할보유수량= }  {분할청산금액[num]= } {분할청산금액= }  {분할평가금액= }" )
            elif 세부상태 == '매수' or 세부상태 == '':
                분할평가금액[num] = 분할보유수량[num] * 현재가 * 거래승수
                print(f"elif 세부상태 == '매수' or 세부상태 == '':{stg=} {세부상태= } {분할보유수량= } {분할평가금액= }")
            elif 세부상태 == '매도':
                print(f"elif 세부상태 == '매도':  {num= }  {세부상태= }  {세부상태= } {분할보유수량= } {분할평가금액= }")
                pass
            else:
                print(f"******chegyeol_sell_on_scale::::  확인 요망 {stg= }   {ticker= }    {세부상태=}    {상태}")
        if self.market == '국내주식': fee = self.fee_stock + self.tax_stock #
        elif self.market == '국내선옵': fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 현재가 > 2.47 or 현재가 < 0.42 else self.fee_putopt2 #
        else: fee = self.fee_bybit_market # self.market == '코인':
        평가금액 = sum(분할보유수량) * 현재가 * 거래승수
        남은청산수수료 = 평가금액 * fee / 100
        매입금액 = self.df_trade.loc[stg, '매입금액']

        if 방향 == 'long':
            수익금 = sum(분할평가금액) - 매입금액 - sum(분할진입수수료) - 남은청산수수료   #  - 청산수수료도 빼야되는데 방법이 없음
        elif 방향 == 'short':
            수익금 = 매입금액 - sum(분할평가금액) - sum(분할진입수수료) - 남은청산수수료   #  - 청산수수료도 빼야되는데 방법이 없음
        수익률 = round((수익금 / (매입금액 * 증거금률) * 100), 2)
        self.df_trade.loc[stg, '수익금'] = round(수익금, 2) if self.market == '코인' else round(수익금)
        self.df_trade.loc[stg, '수익률'] = 수익률
        self.df_trade.loc[stg, '최고수익률'] = np.where(수익률 > self.df_trade.loc[stg, '최고수익률'],수익률, self.df_trade.loc[stg, '최고수익률'])
        self.df_trade.loc[stg, '최저수익률'] = np.where(수익률 < self.df_trade.loc[stg, '최저수익률'],수익률, self.df_trade.loc[stg, '최저수익률'])
        print(f"chegyeol_sell_on_scale - end {stg=} {상태= }   {분할상태= }    {분할보유수량= }    {sum(분할보유수량)= }     {현재가= }    {sum(분할진입수수료)=}   {남은청산수수료= }   {수익률=},   {수익금= }   {매입금액= }     {증거금률= }  {sum(분할진입수수료)= } ")
        if '매도주문' in 분할상태 or '시장가매도' in 분할상태 or '부분매도' in 분할상태 :
            if all(x in ['매도주문', '시장가매도', '매수'] for x in 분할상태): #상태가 '매도주문', '시장가매도', '대기'로만 되어있을 경우
                상태 = '분할매도주문'
            else:
                상태 = '분할부분매도' #일정부분 매도가 된 상태
            print(f"if '매도주문' in 분할상태 or '시장가매   {상태= }   {수익금= }")
        elif all(x == '매도' for x in 분할상태):
            상태 = '매도'
            print(f"2 {상태= }")
            self.df_trade.loc[stg, '누적수익금'] = self.df_trade.loc[stg, '누적수익금'] + 수익금
            self.df_trade.loc[stg, '청산시간'] = common_def.datetime_to_str(현재시간)
            win_per = self.df_trade.loc[stg, '승률(win/all)']
            win = win_per[:win_per.index('/')]
            all_game = win_per[win_per.index('/') + 1:win_per.index('(')]
            win = int(win) + 1 if 수익률 > 0 else int(win) + 0
            self.df_trade.loc[stg, '승률(win/all)'] = f'{win}/{int(all_game) + 1}({round(win / (int(all_game) + 1) * 100, 1)})%'
            # 누적수익금 = 0 # 누적수익금을 넣을 수 있는 방법을 생각해볼것
            # self.df_trade.loc[stg, '누적수익금'] = 누적수익금
        elif all(x in ['매수', '매도'] for x in 분할상태):
            # 상태 = '분할매수'
            상태 = '매수'
            print(f"2 {상태= },   {분할상태= }")
        elif '대기' in 분할상태:
            상태 = '분할매수'
            print(f"1 {상태= },   {분할상태= }")
        else:
            print(f"상태 확인 요망 = {분할상태=}")
        # print(self.df_trade)
        # quit()
        # print(분할보유수량)
        self.df_trade.loc[stg, '보유수량'] = sum(분할보유수량)
        self.df_trade.loc[stg, '청산금액'] = sum(분할청산금액)
        self.df_trade.loc[stg, '주문수량'] = sum(분할주문수량)
        self.df_trade.loc[stg, '평가금액'] = sum(분할평가금액)
        self.df_trade.loc[stg, '분할상태'] = json.dumps(분할상태,ensure_ascii=False)
        self.df_trade.loc[stg, '분할보유수량'] = json.dumps(분할보유수량)
        self.df_trade.loc[stg, '분할평가금액'] = json.dumps(분할평가금액)
        self.df_trade.loc[stg, '분할청산금액'] = json.dumps(분할청산금액)
        print(self.df_trade[['보유수량','청산금액','주문수량','보유수량','분할보유수량','상태','분할상태','분할청산금액','분할평가금액']].loc[[stg]])
        # print(self.df_trade)
        # print("==============================================================================")
        return 상태, 수익금

    def order_cancel(self, stg, ticker, 상태, 주문수량, 보유수량, 방향,id, 총체결수량, dict_chegyeol):
        # id = self.df_trade.loc[stg, 'id']
        if 상태 == '매수취소':
            취소수량 = 주문수량-보유수량
            상태 = '매수주문' if 보유수량 == 0 else '부분매수'
        elif 상태 == '매도주문' or 상태 == '매도주문' or 상태 == '매도주문' :
            취소수량 = 보유수량
            pass
        print(f"order_cancel {stg=} {ticker=}, {id=}, {취소수량=}, {상태= }, {총체결수량= }")
        if self.market == '코인':
            if self.simul.isChecked() == False:  # 실매매 시
                self.ex_bybit.cancel_order(id, ticker + 'USDT', params={})
            success = True
        elif self.market == '국내주식' or self.market == '국내선옵':
            output = self.ex_kis.cancel_order(symbol=ticker,order_no=id,quantity=취소수량)
            if output == '모의투자 취소주문이 완료 되었습니다.' or output == '취소주문이 완료 되었습니다.':
                success = True
            elif output == '모의투자 정정/취소할 수량이 없습니다.' or output == '정정/취소할 수량이 없습니다.':
                success = False
                print(f"order_cancel -{output= } {success= } {취소수량= } {주문수량= } {보유수량= }")
            else:
                print(f"def order_cancel(self, stg, 상태, 주문수량, 보유수량): - {output}")

        if success == True:
            if 상태 == '매수주문' or 상태 == '매도주문': # 아직 체결이 되지않은 상태일 경우
                self.color_text(state = 상태, stg=stg, ticker=ticker, 보유수량=취소수량)
                if 상태 == '매수주문':  상태 = '대기'
                elif 상태 == '매도주문':  상태 = '매도취소 시장가매도'
                잔여수량 = self.df_trade.loc[stg, '보유수량']
                print(f"if (상태 == '매수주문' or 상태 == '매도주문') and 주문수량 == 취소수량 : {상태=} {잔여수량= }")
            elif 상태 == '부분매수' or 상태 == '부분매도':
                self.color_text(state = 상태, stg=stg, ticker=ticker, 주문수량=취소수량 , 보유수량=보유수량, 상태=상태)
                상태 = '매수'
                잔여수량 = self.df_trade.loc[stg, '보유수량']
            else:
                print(f"order_cancel {상태= } {주문수량= }, {보유수량= }, {취소수량= }")
                잔여수량 = self.df_trade.loc[stg, '보유수량']
            if self.df_trade.loc[stg, '진입대상'] == '전체':
                self.df_trade.loc[stg, 'ticker'] = ''
        if success == False:
            print('=========================')
            print(self.df_trade)
            print(f"order_cancel 에러 {상태= } {총체결수량= }  {id= }")
            pprint(output)
            print('***************************')
            pprint(dict_chegyeol)
            print('//////////////////////////////')
            if self.market == '국내주식' or self.market == '국내선옵':
                if 방향 == 'long': dict_chegyeol = self.ex_kis.fetch_closed_order(side='buy',ticker=ticker,id=id)
                elif 방향 == 'short': dict_chegyeol = self.ex_kis.fetch_closed_order(side='sell',ticker=ticker,id=id)
                pprint(dict_chegyeol)


            # if 상태 == '매수취소':
            #     if self.market == '국내선옵':
            #         if 방향 == 'long': dict_chegyeol = self.ex_kis.fetch_closed_order(side='buy', ticker=ticker, id=id)
            #         elif 방향 == 'short': dict_chegyeol = self.ex_kis.fetch_closed_order(side='sell', ticker=ticker, id=id)
            #         총체결수량 = int(dict_chegyeol['tot_ccld_qty'])
            #         if 주문수량 == 총체결수량:
            #
            #     상태 == '매수주문'
        time.sleep(1)
        return 상태, 잔여수량

    def order_price(self,ticker, price_in, 현재가, 방향, side): # side = 매수일 경우 '매수주문', 매도 = '매도주문'
        slippage = 0.1 #슬리피지 0.1 %
        if type(price_in) == dict:
            방식 = 'limit'
            hoga_price = list(price_in.keys())[0]
            hoga_rate = price_in[hoga_price]
            if self.market=='코인':
                price_out = float(self.ex_bybit.price_to_precision(ticker+'USDT', hoga_price + (hoga_price * hoga_rate / 100)))
                fee = self.fee_bybit_limit
            elif self.market=='국내주식' :
                price_out = self.ex_kis.hogaPriceReturn(self.df_stock_info.loc[ticker, '시장구분'],ticker, hoga_price, hoga_rate)
                fee = self.fee_stock
            elif self.market == '국내선옵':
                price_out = self.ex_kis.hogaPriceReturn(self.market,ticker, hoga_price, hoga_rate)
                fee = self.fee_future if ticker[:1] == '1' else self.fee_putopt1 if price_out > 2.47 or price_out < 0.42 else self.fee_putopt2
            상태 = side

        elif price_in == 시장가:
            방식 = 'market'
            if 방향 == 'long' and side == '매수주문':
                price_out = 현재가 + (slippage / 100 * 현재가)
                상태 = '시장가매수'
            elif 방향 == 'short' and side == '매수주문':
                price_out = 현재가 - (slippage / 100 * 현재가)
                상태 = '시장가매수'
            elif 방향 == 'long' and side == '매도주문':
                price_out = 현재가 - (slippage / 100 * 현재가)
                상태 = '시장가매도'
            elif 방향 == 'short' and side == '매도주문':
                price_out = 현재가 + (slippage / 100 * 현재가)
                상태 = '시장가매도'
            else:
                print(f"{ticker= }, {현재가= }, {price_in= }")
                raise
            if self.market == '코인':
                price_out = float(self.ex_bybit.price_to_precision(ticker + 'USDT', price_out))
                fee = self.fee_bybit_market
            elif self.market=='국내주식':
                price_out = self.ex_kis.hogaPriceReturn_per(self.df_stock_info.loc[ticker, '시장구분'],ticker, price_out, 0)
                fee = self.fee_stock
            elif self.market=='국내선옵':
                price_out = self.ex_kis.hogaPriceReturn_per(self.market, ticker, price_out, 0)
                fee = self.fee_future if ticker[:1] == '1' else self.fee_putopt1 if price_out > 2.47 or price_out < 0.42 else self.fee_putopt2

        elif type(price_in) == float or type(price_in) == int:
            방식 = 'limit'
            if self.market=='코인':
                price_out = float(self.ex_bybit.price_to_precision(ticker + 'USDT',price_in))
                if self.simul.isChecked() == True:  # 모의매매
                    if 방향 == 'long' and price_out >= 현재가:
                        price_out = 현재가 + (slippage / 100 * 현재가)
                        fee = self.fee_bybit_market
                    elif 방향 == 'long' and price_out < 현재가:
                        fee = self.fee_bybit_limit
                    elif 방향 == 'short' and price_out <= 현재가:
                        price_out = 현재가 - (slippage / 100 * 현재가)
                        fee = self.fee_bybit_market
                    elif 방향 == 'short' and price_out > 현재가:
                        fee = self.fee_bybit_limit
                    else:
                        print(f"{price_out=}, {price_in=}, {self.fee_bybit_limit=}, {self.fee_bybit_market=}")
                        raise
                else: # 실매매
                    fee = self.fee_bybit_market
            elif self.market=='국내주식':
                price_out = self.ex_kis.hogaPriceReturn_per(self.df_stock_info.loc[ticker, '시장구분'],ticker, price_in, 0)
                fee = self.fee_stock
            elif self.market=='국내선옵':
                price_out = self.ex_kis.hogaPriceReturn_per(self.market, ticker, price_in, 0)
                fee = self.fee_future if ticker[:1] == '1' else self.fee_putopt1 if price_out > 2.47 or price_out < 0.42 else self.fee_putopt2
            상태 = side
        else:
            print(f'{ticker= }, {price_in= }, {type(price_in)= }진입주문가 설정 안됨')
            raise
        return price_out, 방식, fee, 상태

    def order_buy(self, stg, 매수, 매수가, 방향, 레버리지, 배팅금액, 상태):
        ticker = self.df_trade.loc[stg, 'ticker']
        거래승수 = self.dic_multiplier[ticker[:3]] if self.market == '국내선옵' else 1
        if self.market=='국내선옵' and 매수가 == 시장가: #선물옵션의경우 시장가 매수 시 잔고만큼 매수가 안되기 때문에 매도수 10호가로 주문
            try:
                매수가 = {현재가:'매수5호가'} if 방향 == 'long' else {현재가:'매도5호가'}
            except:
                print(f"{현재가= }, {self.market= }, {매수가= }, {방향= }")
                raise
        진입가, 진입방식, fee, 상태 = self.order_price(ticker, 매수가, 현재가, 방향, 상태)
        매수가능금액 = 0
        print(f"order_buy {stg= }, {ticker= }, {진입가= }, {현재가= }, {방향= },  {매수가= }, {진입방식= }, {fee= }, {상태= }")
        if 진입가 == 0:
            print(f"진입가 에러 {진입가= }  {현재가= }   {매수가= }")
            quit()
        try:
            if 매수 == True:
                매수 = 100
            금액 = 배팅금액 * (매수 / 100) * 레버리지
        except:
            print(f"{type(배팅금액)= }")
            print(f"{type(매수)= }")
            print(f"{type(레버리지)= }")
            print(f"{stg= }, {ticker= }, 금액= {배팅금액 * (매수 / 100) * 레버리지} = {배팅금액= } * ({매수= } / 100) * {레버리지= } | {진입가= }, {진입방식= }, {fee= }, {상태= }")
        if self.market == '코인':
            #최소주문수량 구하기
            res = self.ex_pybit.get_instruments_info(
                category="linear",  # spot, linear, inverse, option
                symbol=ticker+"USDT",  # BTC, BTCUSDT, BTCUSD
            )['result']['list'][0]
            min_qty = float(res['lotSizeFilter']['minOrderQty'])

            수량 = (100 - (fee * 레버리지)) / 100 * 금액 / 진입가

            if 수량 < min_qty:
                print(f"order_buy - 최소주문수량 미달 주문수량 변경 {수량=},  {min_qty= }")
                수량 = min_qty
            print(f"order_buy   -  {ticker=}  { 수량=}, ")
            수량 = float(self.ex_bybit.amount_to_precision(ticker + 'USDT', 수량))
            # print(f"{ticker= }, {수량= }, {fee= }, {레버리지=}, {금액= }, {진입가= }")
            if 수량 <= 0: raise print(f'수량 이상 {배팅금액= }')

            if self.simul.isChecked() == False: #실매매
                try:
                    self.ex_bybit.set_leverage(leverage=레버리지, symbol=ticker+'USDT')
                except:
                    pass
                if 방향 == 'long':
                    id = self.order_open(ticker=ticker+'USDT' ,price=진입가, qty=수량, side='buy', type=진입방식,leverage=레버리지)
                elif 방향 == 'short':
                    id = self.order_open(ticker=ticker+'USDT' ,price=진입가, qty=수량, side='sell', type=진입방식,leverage=레버리지)
            else: #모의매매
                id = ''

        elif self.market=='국내주식' or self.market=='국내선옵':
            if self.market == '국내주식':
                self.df_trade.loc[stg, 'market'] = self.df_stock_info.loc[ticker,'시장구분']
                수량 = (100 - fee) / 100 * 금액 // 진입가
            elif self.market=='국내선옵':
                if self.df_trade.loc[stg, '진입대상'][0] == '{':
                    trade_market = '조건검색'
                elif ticker[:1] == '1':
                    trade_market = '선물'
                elif ticker[:1] == '2':
                    trade_market = '콜옵션'
                elif ticker[:1] == '3':
                    trade_market = '풋옵션'
                else:
                    trade_market = '스프레드'
                self.df_trade.loc[stg, 'market'] = trade_market
                거래승수 = self.dic_multiplier[ticker[:3]]
                매수가능금액 = round((100 - fee) / 100 * 금액)
                계약가 = 진입가 * 거래승수
                if trade_market == '선물':
                    계약당필요현금 = 계약가 * (self.위탁증거금률 / 100)
                    수량 = int(매수가능금액 // 계약당필요현금)
                else:
                    print(f"{stg= }, {ticker= }, {상태= }, {현재가= }, {매수가= }, {거래승수=}, {진입가=}, {계약가=}, {매수가능금액=}")
                    수량 = int(매수가능금액 // 계약가)
            if 수량 <= 0:
                print(f"order_buy 수량 에러 {stg= }, {ticker= }, {현재가= }, {매수가= }, {진입가= }, {수량= }, {방향= }, {배팅금액= }")
                상태 = '대기'
                수수료 = 0
                id = ''
                return 상태, 수량, 진입가, 수수료, id
            # if self.market == '국내주식':
            #     진입가 =  int(진입가)
            #     if 진입방식 == 'market':
            #         id = self.ex_kis.create_market_buy_order(symbol=ticker, quantity=int(수량), side='buy')
            #     else:
            #         id = self.ex_kis.create_limit_buy_order(symbol=ticker, price=진입가, quantity=int(수량), side='buy')
            # elif self.market == '국내선옵':
            list_state = self.df_trade.loc[(self.df_trade['ticker']==ticker)&(self.df_trade['방향']!=방향),'상태'].tolist() #양방향매매가 안되기 때문에 종목이 역방향 보유중이면 확인 해야함.
            list_state = list(set(list_state))
            # print(f"{stg= }, {ticker= }, {방향= }, {진입방식= }, {진입가= }, {수량= }")
            if not ('매수' in list_state or '매수주문' in list_state or '부분매수' in list_state or '시장가매수' in list_state
                    or '매수취소' in list_state or '매도주문' in list_state or '부분매도' in list_state or '시장가매도' in list_state):
                if 방향 == 'long':
                    if 진입방식 == 'market':
                        id = self.ex_kis.create_market_buy_order(symbol=ticker, quantity=int(수량),side='buy')
                    else:
                        id = self.ex_kis.create_limit_buy_order(symbol=ticker, price=진입가, quantity=int(수량),side='buy')
                elif 방향 == 'short':
                    if 진입방식 == 'market':
                        id = self.ex_kis.create_market_buy_order(symbol=ticker, quantity=int(수량), side='sell')
                    else:
                        id = self.ex_kis.create_limit_buy_order(symbol=ticker, price=진입가, quantity=int(수량),side='sell')
            else:
                order = {}
                order['msg1'] = '기존 반대포지션 보유 중'
                상태 = '매수불가'  # '대기'로할지 '매도'로 해서 종료시점까지 진입 안할지 고민
                수량 = 0
                진입가 = 0
                id = ''
        print(f"order_buy {stg= }, {ticker= }, {현재가= }, {매수가= }, {진입가= }, {수량= }, {방향= }, {배팅금액= } {금액=} {매수가능금액}")

        # self.df_trade.loc[stg, 'ticker'] = ticker

        self.df_trade.loc[stg, '주문수량'] = 수량
        self.df_trade.loc[stg, '진입가'] = 진입가
        # self.df_trade.loc[stg, '기준잔고'] = 잔고
        수수료 = 진입가 * 수량 * fee / 100
        self.df_trade.loc[stg, '수수료'] = 수수료
        self.df_trade.loc[stg, 'id'] = id
        if 상태 == '매수주문' or 상태 == '시장가매수':
            self.color_text(state='open 주문',진입방식=진입방식,stg=stg,ticker=ticker,방향=방향,진입가=진입가,주문수량=수량,레버리지=레버리지,현재봉시간=self.df_trade.loc[stg, '현재봉시간'],
                            상태=상태, id=id, 체결금액=매수가능금액, 매입금액=진입가*수량*거래승수 )
        return 상태, 수량, 진입가, 수수료, id

    def order_sell(self, stg, 청산가, 방향, 수량, 상태): # order sell은 loop_trade 2군데서 주문이 발생하므로 주의
        if 수량 == 0: return '매도'
        ticker = self.df_trade.loc[stg, 'ticker']

        매도가, 청산방식, fee, 상태 = self.order_price(ticker, 청산가, 현재가, 방향, 상태)
        print(f"order_sell {stg= }, {ticker= }, {청산가= }, {현재가= }, {방향= }, {수량= }, {매도가= }, {청산방식= }, {fee= }, {상태= }")
        if self.market == '코인':
            if self.simul.isChecked() == False: #실매매
                if 방향 == 'long':
                    id = self.order_close(ticker=ticker+'USDT' ,price=매도가, qty=수량, side='sell', type=청산방식)
                elif 방향 == 'short':
                    id = self.order_close(ticker=ticker+'USDT' ,price=매도가, qty=수량, side='buy', type=청산방식)
                else:
                    raise print('order_sell 에러')
            else: #모의매매
                id = ''

        elif self.market=='국내주식' or self.market=='국내선옵':
            if self.market=='국내주식':
                매도가 = int(매도가)
                if 청산방식 == 'market':
                    id = self.ex_kis.create_market_sell_order(symbol=ticker, quantity=int(수량))
                else:
                    id = self.ex_kis.create_limit_sell_order(symbol=ticker, price=int(매도가), quantity=int(수량))
            elif self.market == '국내선옵':
                if 방향 == 'long':
                    if 청산방식 == 'market':
                        id = self.ex_kis.create_market_sell_order(symbol=ticker, quantity=int(수량),side='sell')
                    else:
                        id = self.ex_kis.create_limit_sell_order(symbol=ticker, price=매도가, quantity=int(수량),side='sell')
                elif 방향 == 'short':
                    if 청산방식 == 'market':
                        id = self.ex_kis.create_market_sell_order(symbol=ticker, quantity=int(수량),side='buy')
                    else:
                        id = self.ex_kis.create_limit_sell_order(symbol=ticker, price=매도가, quantity=int(수량),side='buy')

        self.df_trade.loc[stg, '청산가'] = 매도가
        self.df_trade.loc[stg, '주문수량'] = 수량
        self.df_trade.loc[stg, '체결수량'] = 0

        self.df_trade.loc[stg, 'id'] = id
        # if 방향 == 'long':
        #     수익률 = round((매도가-self.df_trade.loc[stg, '진입가'])/self.df_trade.loc[stg, '진입가']*100,2)
        # elif 방향 == 'short':
        #     수익률 = round((self.df_trade.loc[stg, '진입가']-매도가)/self.df_trade.loc[stg, '진입가']*100,2)
        print(f"{stg= }, {ticker= }, {방향= }, {청산방식= }, {매도가= }, {수량= }")

        self.color_text(state='close 주문', 청산방식=청산방식, stg=stg, ticker=ticker, 방향=방향, 청산가=매도가, 주문수량=수량 ,잔고=self.df_trade.loc[stg,'잔고'],수익률=self.df_trade.loc[stg, '수익률'], 상태=상태, id=id)
        return 상태, 매도가, id

    def buy_on_scale(self,stg, 매수, 매수가, 방향, 레버리지, 배팅금액, 상태):
        # print('buy_on_scale')
        분할매수 = json.loads(self.df_trade.loc[stg, '분할매수'])
        분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
        분할주문수량 = json.loads(self.df_trade.loc[stg, '분할주문수량'])
        분할진입가 = json.loads(self.df_trade.loc[stg, '분할진입가'])
        분할id = json.loads(self.df_trade.loc[stg, '분할id'])
        for num in 매수:
            if 분할상태[num] == '대기':
                세부상태 = '매수주문'
                세부상태, 진입수량, 진입가, 수수료, id = self.order_buy(stg, int(분할매수[num]), 매수가[num], 방향, 레버리지, 배팅금액,세부상태)  # 시장가 매수 일 경우 '매수'를 받기 때문에 상태를 반환받아야됨
                분할상태[num] = 세부상태
                분할주문수량[num] = 진입수량
                분할진입가[num] = 진입가
                분할id[num] = id

        기존분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])

        # 기존의 분할상태와 주문이 들어간 후의 분할상태를 비교하여 바뀐것만 리스트로 반환
        # order_buy에서 수량이 0으로 나올 경우에는 상태를 '대기'로 반환하기 때문에
        list_compare = [a for a, b in zip(분할상태, 기존분할상태) if a != b]
        if '매수주문'in 분할상태 or '시장가매수' in 분할상태:
            상태 = '분할매수주문'
        elif all(x == '매수' for x in 분할상태):  # 전부 매수 일 경우
            상태 = '매수'
        elif all(x == '대기' for x in 분할상태):  # 전부 대기 일 경우
            상태 = '대기'
        elif all(x in ['매수', '대기'] for x in 분할상태):  # 전부 대기 일 경우
            상태 = '분할매수대기'
        else:
            print(f"buy_on_scale - {list_compare= },  {분할상태= },  {기존분할상태= }  {상태= }")
        self.df_trade.loc[stg, '분할상태'] = json.dumps(분할상태,ensure_ascii=False)
        self.df_trade.loc[stg, '분할주문수량'] = json.dumps(분할주문수량)
        self.df_trade.loc[stg, '분할진입가'] = json.dumps(분할진입가) # 코인 모의매매를 위해 필요
        self.df_trade.loc[stg, '분할id'] = json.dumps(분할id,ensure_ascii=False)
        return 상태

    def sell_on_scale(self,stg, 매도, 매도가, 방향):
        분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
        분할주문수량 = json.loads(self.df_trade.loc[stg, '분할주문수량'])
        # 분할청산금액 = json.loads(self.df_trade.loc[stg, '분할청산금액'])
        분할청산가 = json.loads(self.df_trade.loc[stg, '분할청산가'])
        분할id = json.loads(self.df_trade.loc[stg, '분할id'])
        # 분할보유수량 = json.loads(self.df_trade.loc[stg, '분할보유수량'])
        # 분할청산시간 = json.loads(self.df_trade.loc[stg, '분할청산시간'])
        for num in 매도:
            if 분할상태[num] == '매수':
                세부상태 = '매도주문'
                세부상태, 청산가, id = self.order_sell(stg, 매도가[num], 방향, 분할주문수량[num], 세부상태)  # 시장가 매수 일 경우 '매수'를 받기 때문에 상태를 반환받아야됨
                분할상태[num] = 세부상태
                분할청산가[num] = 청산가
                분할id[num] = id
                print(f"sell_on_scale - {stg= }, {매도가[num]= }, {방향= }, {분할주문수량[num]= }, {세부상태= } {청산가= }  {id=}")
        self.df_trade.loc[stg, '분할상태'] = json.dumps(분할상태,ensure_ascii=False)
        self.df_trade.loc[stg, '분할주문수량'] = json.dumps(분할주문수량)
        self.df_trade.loc[stg, '분할보유수량'] = json.dumps(분할주문수량)
        # self.df_trade.loc[stg, '분할청산금액'] = json.dumps(분할청산금액)
        self.df_trade.loc[stg, '분할청산가'] = json.dumps(분할청산가) # 코인 모의매매를 위해 필요
        self.df_trade.loc[stg, '분할id'] = json.dumps(분할id,ensure_ascii=False)
        self.df_trade.loc[stg, '주문수량'] = sum(분할주문수량)
        상태 = '분할매도주문'
        return 상태

    def cal_ror(self, stg, 현재가, 방향): # 나중에 balance_account랑 합쳐야 됨
        보유수량 = self.df_trade.loc[stg, '보유수량']
        매입금액 = self.df_trade.loc[stg, '매입금액']
        레버리지 = self.df_trade.loc[stg, '레버리지']
        진입수수료 = self.df_trade.loc[stg, '진입수수료']
        진입가 = self.df_trade.loc[stg, '진입가']
        청산금액 = self.df_trade.loc[stg, '청산금액']
        ticker = self.df_trade.loc[stg, 'ticker']
        trade_market = self.df_trade.loc[stg, 'market']
        증거금률 = self.위탁증거금률 / 100 if trade_market == '선물' else 1/레버리지 if trade_market == 'bybit' else 1

        if self.market == '코인':
            fee = self.fee_bybit_market #매도수수료
            # 체결금액 = 진입가 * 보유수량
            평가금액 = 보유수량 * 현재가
            청산수수료 = round(평가금액 * fee / 100, 4)
        elif self.market=='국내주식':
            fee = self.fee_stock + self.tax_stock
            # 체결금액 = 진입가 * 보유수량
            평가금액 = round(보유수량 * 현재가)
            청산수수료 = 평가금액 * fee // 100
        elif self.market == '국내선옵':
            fee = self.fee_future if trade_market == '선물' else self.fee_putopt1 if 진입가 > 2.47 or 진입가 < 0.42 else self.fee_putopt2
            거래승수 = self.dic_multiplier[ticker[:3]]
            평가금액 = round(보유수량 * 현재가 * 거래승수)
            청산수수료 = 평가금액 * fee // 100

        if 방향 == 'long':
            수익금 = (평가금액+청산금액) - 매입금액 - 진입수수료 - 청산수수료
        elif 방향 == 'short':
            수익금 = 매입금액 - (평가금액+청산금액) - 진입수수료 - 청산수수료

        self.df_trade.loc[stg, '평가금액'] = round(평가금액)
        self.df_trade.loc[stg, '수익금'] = round(수익금)
        self.df_trade.loc[stg, '수수료'] = 진입수수료 + 청산수수료

        if 매입금액 == 0 or 수익금 == 0:
            수익률 = 0
        else:
            수익률 = round((수익금 / (매입금액*증거금률) * 100) , 2)

        # if 수익률 < -10 or 수익률 > 20:
        # print(f"cal_ror: {stg= }, {수익률= },{평가금액= }, {청산금액= }  {수익금= } / {매입금액= }, {레버리지= }, {보유수량= }, {현재가= }, {증거금률=} {진입수수료= }  {청산수수료= }")

        self.df_trade.loc[stg, '수익률'] = 수익률
        self.df_trade.loc[stg, '최고수익률'] = np.where(수익률 > self.df_trade.loc[stg, '최고수익률'],
                                                수익률, self.df_trade.loc[stg, '최고수익률'])
        self.df_trade.loc[stg, '최저수익률'] = np.where(수익률 < self.df_trade.loc[stg, '최저수익률'],
                                            수익률, self.df_trade.loc[stg, '최저수익률'])
        누적수익금 = self.df_trade.loc[stg, '누적수익금'] + 수익금
        # print(f"cal_ror - {누적수익금= }    {self.df_trade.loc[stg, '누적수익금']= }     {수익금= },  {수익률= }")
        return 누적수익금

    def make_df(self,ticker, bong, bong_detail, bong_since, check_compare):
        ticker_full_name = f"{ticker}_{bong}_{bong_detail}"
        if self.market =='국내주식':
            if ticker_full_name in globals():  # 만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
                ohlcv = globals()[ticker_full_name]
                if bong == '일봉':
                    if not ohlcv.empty:
                        df = common_def.convert_df(ohlcv)
                        dict_output = self.ex_kis.fetch_price(ticker)
                        today = pd.to_datetime(datetime.datetime.now().date())
                        df.loc[today,'시가'] = int(dict_output['stck_oprc'])
                        df.loc[today,'고가'] = int(dict_output['stck_hgpr'])
                        df.loc[today,'저가'] = int(dict_output['stck_lwpr'])
                        df.loc[today,'종가'] = int(dict_output['stck_prpr'])
                        df.loc[today,'거래대금'] = int(dict_output['acml_tr_pbmn'])
                        df.loc[today,'거래량'] = int(dict_output['acml_vol'])
                        df.loc[today,'전일대비거래량비율'] = float(dict_output['prdy_vrss_vol_rate'])
                        df.loc[today,'외국인순매수수량'] = int(dict_output['frgn_ntby_qty'])
                        df.loc[today,'프로그램매매순매수수량'] = int(dict_output['pgtr_ntby_qty'])
                        df.loc[today,'PER'] = float(dict_output['per'])
                        df.loc[today,'PBR'] = float(dict_output['pbr'])
                        df.loc[today,'EPS'] = float(dict_output['eps'])
                        df.loc[today,'BPS'] = float(dict_output['bps'])
                        df.loc[today,'52주최고가'] = int(dict_output['w52_hgpr'])
                    else:
                        df = ohlcv
                else:
                    to = ohlcv[0]['stck_cntg_hour']
                    output = self.ex_kis._fetch_futopt_today_1m_ohlcv(symbol=ticker,to=datetime.datetime.now().strftime("%H%M%S"),fake_tick=True)  # to = 현재시간, 허봉 포함
                    output = output['output2']
                    list_cntg_hour = [item['stck_cntg_hour'] for item in output]  # 딕셔너리의 시간을 리스트로 변환
                    if to in list_cntg_hour:
                        output = output[:list_cntg_hour.index(to) + 1]
                        del ohlcv[0]  # 마지막행은 불완전했던 행 이였으므로 삭제
                        output.extend(ohlcv)
                        ohlcv = output
                        globals()[ticker_full_name] = ohlcv
            else:  # 최초 생성 시
                if bong == '일봉':
                    date_old = datetime.datetime.now().date() - datetime.timedelta(days=int(bong_since))
                    date_old = datetime.datetime.strftime(date_old,'%Y%m%d')
                    df = self.ex_kis.fetch_ohlcv(symbol=ticker,early_day=date_old)
                    if not df.empty:
                        globals()[ticker_full_name] = df.copy()
                        df = common_def.convert_df(df)
                else:
                    df = common_def.get_kis_ohlcv(self.market,ohlcv)
                    if ticker_full_name.count('_') == 2:  # 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
                        df_standard, df = common_def.detail_to_spread(df, bong, bong_detail)
                    else:  # 비교대상의 경우 'BTC_5분봉'
                        df = common_def.detail_to_compare(df, bong, ticker_full_name)
            return df
        elif self.market == '국내선옵':
            if ticker_full_name in globals():  # 만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
                ohlcv = globals()[ticker_full_name]
                to = ohlcv[0]['stck_cntg_hour']
                output = self.ex_kis._fetch_futopt_today_1m_ohlcv(symbol=ticker,to=datetime.datetime.now().strftime("%H%M%S"),fake_tick=True)  # to = 현재시간, 허봉 포함
                output = output['output2']
                list_cntg_hour = [item['stck_cntg_hour'] for item in output]  # 딕셔너리의 시간을 리스트로 변환
                if to in list_cntg_hour:
                    output = output[:list_cntg_hour.index(to)+1]
                    del ohlcv[0]  # 마지막행은 불완전했던 행 이였으므로 삭제
                    output.extend(ohlcv)
                    ohlcv = output
                    globals()[ticker_full_name] = ohlcv
            else: # 최초 생성 시
                ohlcv = self.ex_kis.fetch_futopt_1m_ohlcv(symbol=ticker,limit=bong_since)
                globals()[ticker_full_name] = ohlcv


                # 시간 단축을 위해 데이터프레임에서 필요없는 팩터 지우기
                # df_check = common_def.get_kis_ohlcv(self.market,ohlcv)
                # df_standard, df_check = common_def.detail_to_spread(df_check, dict_stg['봉'], dict_stg['상세봉'])
                # li_factor = []
                # for factor in df_check.columns.tolist():
                #     if not factor in str(dict_stg['진입전략'] + dict_stg['청산전략']):  # 실제 전략에 필요한 팩터만 남기고 데이터프레임에서 삭제
                #         if not factor in ['상세시가', '상세고가', '상세저가', '상세종가', '시가', '고가', '저가', '종가', '종료시간',
                #                           '현재시간', '장시작시간', '장종료시간']:  # 삭제에서 제외
                #             df_check.drop(factor, axis=1, inplace=True)
                #             li_factor.append(factor)

            df = common_def.get_kis_ohlcv(self.market,ohlcv)
            if not check_compare:  # 진입대상인지 비교대상인지 확인 - 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
                df_standard, df = common_def.detail_to_spread(df, bong, bong_detail, False)
            else:  # 비교대상의 경우 'BTC_5분봉'
                # print(ticker)
                # print(bong)
                # print(df)
                df = common_def.detail_to_compare(df, ticker, bong)

            return df

        elif self.market =='코인':
            if f'{ticker_full_name}' in globals(): #만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
                ohlcv = globals()[f'{ticker_full_name}']
                stamp_date_old = ohlcv[-1][0]/1000
                # del globals()[f'{ticker_full_name}'][-1]  # 마지막행은 불완전했던 행 이였으므로 삭제
                # pprint(ohlcv)
                # print('=============================')
                del ohlcv[-1]  # 마지막행은 불완전했던 행 이였으므로 삭제
                # pprint(ohlcv)
                # quit()
            else: #만들어진 df가 없을 경우 (최초 DF생성 시)
                ohlcv = []
                date_old = datetime.datetime.now().date() - datetime.timedelta(days=int(bong_since))
                stamp_date_old = common_def.datetime_to_stamp(date_old)
            ohlcv = common_def.get_bybit_ohlcv(self.ex_bybit, ohlcv, stamp_date_old, ticker_full_name, ticker, bong, bong_detail)
            globals()[ticker_full_name] = ohlcv
            df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
            df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
            df['날짜'] = df['날짜'].dt.tz_localize(None)
            df.set_index('날짜', inplace=True)
            df.index = df.index - pd.Timedelta(hours=9)
            if not check_compare: # 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
                df_standard, df = common_def.detail_to_spread(df, bong, bong_detail, False)
            else: # 비교대상의 경우 'BTC_5분봉'
                df = common_def.detail_to_compare(df, ticker, bong)
            df.index = df.index + pd.Timedelta(hours=9)
            return df
    def check_compare_ticker(self,stg,ticker,dict_stg_stg):
        stg_buy = self.df_trade.loc[stg, '진입전략']
        # 첫 번째 줄 진입대상 삭제
        lines = stg_buy.splitlines()  # 줄로 나누기
        stg_buy = "\n".join(lines[1:])  # 첫 줄 제외하고 다시 합치기
        stg_sell = self.df_trade.loc[stg, '청산전략']
        stg_sum = stg_buy + stg_sell
        list_compare = []
        # print(stg_sum)
        # print('===========')
        if self.market == '국내선옵':
            if '선물' in stg_sum:
#                 print('선물')
                # stg_sum = stg_sum.replace('선물', self.list_tickers[0])
                list_compare.append('선물')
            if '풋옵션' in stg_sum and ticker[:1] == '2':
#                 print('풋옵션')
                # symbol = '3' + ticker[1:]
#                 stg_sum = stg_sum.replace('풋옵션', symbol)
                list_compare.append('풋옵션')
            if '콜옵션' in stg_sum and ticker[:1] == '3':
#                 print('콜옵션')
                # symbol = '2' + ticker[1:]
#                 stg_sum = stg_sum.replace('콜옵션', symbol)
                list_compare.append('콜옵션')
#             print(list_compare)
            for symbol in list_compare:
#                 print(f"{symbol= }")
                if symbol in stg_sum:
#                 #     print(f"--------in--------")
                    stg_sum_copy = stg_sum
                    list_bong = []
                    while symbol in stg_sum_copy:
#                         print(stg_sum_copy)
#                         print('***************')
                        stg_sum_copy = stg_sum_copy[stg_sum_copy.index(symbol):]
#                         print(stg_sum_copy)
#                         print('***************')
                        if '봉' in stg_sum_copy:
                            ticker_full_name = stg_sum_copy[:stg_sum_copy.index('봉')+1]
                            stg_sum_copy = stg_sum_copy.replace(ticker_full_name,'')
                            bong = ticker_full_name[ticker_full_name.index('_')+1:]
                            list_bong.append(bong)
#                             print(f"{dict_stg_stg['비교대상']=}")
                        else:
                            break
#                         print('----------------------')
                    dict_stg_stg['비교대상'][symbol] = list_bong
            if '외인' in stg_sum or '개인' in stg_sum or '기관' in stg_sum:
                dict_stg_stg['비교대상']['수급동향'] = True
            # dict_stg_stg['비교대상']['301W01337'] = '5분봉'
        return dict_stg_stg
    def add_compare_df(self, ticker, df, dict_stg_stg,bong_detail,bong_since):
        list_idx = df.index.tolist()
        # print(dict_stg_stg['비교대상'].items())
        for symbol,list_bong in dict_stg_stg['비교대상'].items():
            # symbol = {'3AF75W332':'5분봉'}
            if symbol=='수급동향':
                if list_bong == True:
                    # if '코스피_외인' in df.columns.tolist():
                    #     df.drop(
                    #         ['코스피_외인', '코스피_개인', '코스피_기관', '선물_외인', '선물_개인', '선물_기관', '주식선물_외인', '주식선물_개인', '주식선물_기관',
                    #          '콜옵션_외인', '콜옵션_개인', '콜옵션_기관', '풋옵션_외인', '풋옵션_개인', '풋옵션_기관', '콜_위클리_외인', '콜_위클리_개인',
                    #          '콜_위클리_기관', '풋_위클리_외인', '풋_위클리_개인', '풋_위클리_기관'], inplace=True, axis=1)
                    df = pd.concat([df, self.df_trend], axis=1)
                else:
                    pass
            else:
                symbol_orgin = symbol # 전략에는 시가_선물_일봉 이런식으로 들어가지만 조회할 때는 선물 ticker를 찾아야해서
                if symbol == '선물':
                    symbol = self.list_tickers[0]
                elif symbol == '콜옵션':
                    symbol = '2' + ticker[1:]
                elif symbol == '풋옵션':
                    symbol = '3' + ticker[1:]
                for bong in list_bong:
                    df_compare = self.make_df(symbol, bong, bong_detail, bong_since, True)
#                     print(f"{symbol= }")
#                     print(df_compare)
                    df_compare.columns = [f"{col}_{symbol_orgin}_{bong}" for col in df_compare.columns]
#                     print(df)
#                     print(df_compare)
                    if bong != '일봉' and bong != '주봉': #분봉일 경우
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
#                     print(df)
#                     quit()
                    if [x for x in df.columns.tolist() if '_y' in x]:
                        print('add_compare_df _y 들어가있음')
                        quit()
                    df.ffill(inplace=True)
                    try:
                        df.index = list_idx
                    except:
                        print(list_idx)
                        print(df)
                        df.index = list_idx
                        raise Exception('Exception')
        # print(df)
        # quit()
        return df

    def sorting_make_df(self, dict_stg):
        # list_cntg_hour = [item['진입대상'] for item in dict_stg]  # 딕셔너리의 시간을 리스트로 변환
        # print(list_cntg_hour)
        today = datetime.datetime.now().replace(second=0, microsecond=0)
        li_obj_type = []
        for val in dict_stg.values():
            if type(val['진입대상']) == dict:
                li_obj_type.append(list(val['진입대상'].keys())[0])
        if li_obj_type:
            if self.market == '코인':
                fetch_tickers = self.ex_bybit.fetch_tickers()
                df = self.bybit_set_tickers(fetch_tickers)
                if '거래대금급등' in li_obj_type:  # 옵션_월물
                    se_vol = self.se_vol - df['quoteVolume']
                    se_vol.sort_values(ascending=False, inplace=True)  # 거래대금 급등 순 정렬
                    self.se_vol = df['quoteVolume']
                    se_vol = se_vol.dropna()
                    list_increase_vol = se_vol.tolist()[:50]  # 거래대금 급등 상위 20위만 거래
                    se_top = self.se_vol.copy()
                if '거래대금상위' in li_obj_type:  # 옵션_월물
                    self.df_quotevolum = df['quoteVolume'].copy()
                    self.df_quotevolum.sort_values(ascending=False, inplace=True)  # 거래대금 상위 순 정렬

                    # self.dict_sorting_obj = list(set(list_increase_vol) & set(list_top_vol))  # 거래대금 급등, 거래대금 상위 교집합
                    # self.dict_sorting_obj = [x[:-10] for x in list_tickers if x[-4:] == 'USDT' and x[:6] != 'GASDAO']  #GASDAO 종목 삭제
                    # list_tickers = list(set(list_tickers) - set(self.list_stg_tickers))  # 전체 대상에서 전략에 종목이 지정된 종목은 제외
            elif self.market == '국내선옵':
                if '콜옵션' in li_obj_type or '풋옵션' in li_obj_type:  # 옵션_월물
                    # print('콜풋')
                    QTest.qWait(500)
                    df_c, df_p = self.ex_kis.display_opt(today)
                    self.df_c = common_def.convert_column_types(df_c)
                    self.df_p = common_def.convert_column_types(df_p)
#                     print(self.df_c)
#                     print(self.df_p)
                if '콜옵션_위클리' in li_obj_type or '풋옵션_위클리' in li_obj_type: #옵션_주간
#                     print('위클리')
                    QTest.qWait(500)
                    df_c_weekly, df_p_weekly,cond_mrkt = self.ex_kis.display_opt_weekly(today)
                    self.df_c_weekly = common_def.convert_column_types(df_c_weekly)
                    self.df_p_weekly = common_def.convert_column_types(df_p_weekly)
                # if week == 4 or week == 5 or week == 6 or week == 0: #위클리 월요일일 경우

                # else: #목요일 만기 옵션일 경우
                #     first_day_of_month = datetime.datetime.today().replace(day=1)
                #
                #     # 첫 번째 주의 목요일 찾기
                #     first_week_start = first_day_of_month - datetime.timedelta(
                #         days=first_day_of_month.weekday())  # 첫 주의 월요일
                #     second_week_start = first_week_start + datetime.timedelta(weeks=1)  # 두 번째 주의 월요일
                #     second_thursday = second_week_start + datetime.timedelta(days=3)  # 두 번째 주의 목요일
                #
                #     # 오늘이 두 번째 주의 목요일인지 확인
                #     if datetime.datetime.today().date() == second_thursday.date(): #만기주 일 경우
                #         df_c, df_p = self.ex_kis.display_opt()
                #     elif week == 1 or week == 2 or week == 3:
                #         df_c, df_p = self.ex_kis.display_opt_weekly_thur()

    def sorting_tickers(self,dict_stg_stg,obj):
        key = list(obj.keys())[0]
        value = obj[key]
        upper = float(value[value.index('~') + 1:])
        lower = float(value[:value.index('~')])
        if self.market == '코인':
            if type(obj) == dict:
                if key == '거래대금상위':
                    list_idx = self.df_quotevolum.index.tolist()
                    list_idx = [x[:x.index('/')] for x in list_idx]
                    list_sorting = list_idx[int(lower)-1:int(upper)]
                else:
                    raise
        elif self.market == '국내주식':
            self.dict_sorting_obj = []
            for content in obj:
                self.dict_sorting_obj.extend(self.ex_kis.ranking(content))
            return self.dict_sorting_obj
        elif self.market == '국내선옵':
            # pd.set_option('display.max_rows', None)
            if type(obj) == dict:
                if key == '콜옵션':
                    df = self.df_c.loc[(lower <= self.df_c['현재가']) & (self.df_c['현재가'] <= upper)]
                elif key == '풋옵션':
                    df = self.df_p.loc[(lower <= self.df_p['현재가']) & (self.df_p['현재가'] <= upper)]
                elif key == '콜옵션_위클리':
                    df = self.df_c_weekly.loc[(lower <= self.df_c_weekly['현재가']) & (self.df_c_weekly['현재가'] <= upper)]
                elif key == '풋옵션_위클리':
                    df = self.df_p_weekly.loc[(lower <= self.df_p_weekly['현재가']) & (self.df_p_weekly['현재가'] <= upper)]
                else:
                    raise
                list_sorting = df.index.tolist()
            else:
                print(obj)
                raise
            if '' in list_sorting:
                print(f"{key= }   {value= }   {upper= }   {lower= }")
                print(df)
                raise
        return list_sorting

    def market_finish(self):
        print(f'장 마감 {datetime.datetime.now()=}')
        for stg in self.df_trade.index:
            print('===============================')
            상태 = self.df_trade.loc[stg, '상태']
            print(상태)
            ticker = self.df_trade.loc[stg, 'ticker']
            분할상태 = json.loads(self.df_trade.loc[stg, '분할상태'])
            if 상태 == '매수주문' or 상태 == '매도' or 상태 == '청산' or '매수불가':
                if '매수' in 분할상태:
                    상태 = '매수'
                    self.df_trade.loc[stg, '매도전환'] = 'True'
                else:
                    상태 = '대기'
                print(f"1 {stg= }, {ticker= } | {self.df_trade.loc[stg, '상태']} → {상태= }")
                self.df_trade.loc[stg, '상태'] = 상태
            elif 상태 == '매도주문' or ('매수' in 분할상태) or ('매도주문' in 분할상태):
                상태 = '매수'
                print(f"2 {stg= }, {ticker= } | {self.df_trade.loc[stg, '상태']} → {상태= }")
                self.df_trade.loc[stg, '상태'] = 상태
            else:
                print(f"3 {stg= }, {ticker= } | {self.df_trade.loc[stg, '상태']} → {상태= }   {분할상태}")
        self.qt_open.emit(self.df_trade)
        if self.market == '국내주식':
            quit()
        elif self.market == '국내선옵':
            export_sql(self.df_trend,datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d_investor"))
            quit()

    def order_open(self, ticker, price, qty, side, type, leverage):
        try:
            if side == 'buy':  # 지정가 open long
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                #type = 'limit', side = 'buy'
                res = self.ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty,
                                                 price=price, params=params)
            elif side == 'sell':  # 지정가 open short
                params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                res = self.ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty,
                                                 price=price, params=params)
            else:
                print('에라 오픈')
                raise
        except:
            print(f"에러 order_open  -  {ticker= }, {price= }, {qty= }, {side= }, {type= }, {leverage= }")
            if side == 'buy':  # 지정가 open long
                params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                res = self.ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty,
                                                 price=price, params=params)
            elif side == 'sell':  # 지정가 open short
                params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
                res = self.ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty,
                                                 price=price, params=params)
            else:
                print('에라 오픈')
                raise
            quit()

        # print(f"{self.yellow(f'{type} open 주문')} [{res['id']}] [{side}] - 진입가:{price}, 수량:{qty}, 레버리지: {leverage}, 배팅금액: {round(price * qty, 4)}")
        return res['id']

    def order_close(self,ticker, price, qty, side, type):
        if side == 'buy':  # 지정가 close long
            params = {'positionIdx': 2}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            res = self.ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty, price=price,
                                             params=params)
        elif side == 'sell':  # 지정가 close short
            params = {'positionIdx': 1}  # 0 One-Way Mode, 1 Buy-side, 2 Sell-side
            res = self.ex_bybit.create_order(symbol=ticker, type=type, side=side, amount=qty, price=price,
                                             params=params)
        else:
            print('에라 close')
            raise

        return res['id']

    def fetch_open_orders(self,id,ticker):  # 미체결주문 조회
        params = {}
        try:
            res = self.ex_bybit.fetch_open_orders(symbol=ticker+'USDT', params=params)
            for order in res:
                if order['id'] == id:
                    return order
            # return res
        except:
            print('open 조회 에러')
            order={'id':None,'info':{'orderStatus':None}}
            return order

    def fetch_closed_orders(self,id,ticker):  # 체결주문 조회
        params = {}
        try:
            # order = self.exchange.fetch_closed_orders(self.ticker, params=params)
            res = self.ex_bybit.fetch_closed_orders(symbol=ticker+'USDT', params=params)
            for order in res:
                if order['id'] == id:
                    return order
        except:
            print('close 조회 에러')
            order={'id':None,'info':{'orderStatus':None}}
            # order = []
            return order

    def fetch_order_cancel(self,id,ticker):  # 체결주문 조회
        params = {}
        try:
            res = self.ex_bybit.fetch_canceled_orders(symbol=ticker+'USDT', params=params)
            for order in res:
                if order['id'] == id:
                    return order
            # return res
        except:
            print('close 조회 에러')
            order={'id':None,'info':{'orderStatus':None}}
            return order

    def add_investor_trend(self, 현재시간):
        dict_trend = {}
        dict_trend.update(self.ex_kis.investor_trend_time('코스피'))
        dict_trend.update(self.ex_kis.investor_trend_time('선물'))
        dict_trend.update(self.ex_kis.investor_trend_time('주식선물'))
        dict_trend.update(self.ex_kis.investor_trend_time('콜옵션'))
        dict_trend.update(self.ex_kis.investor_trend_time('풋옵션'))
        if self.COND_MRKT == "WKM":
            dict_trend.update(self.ex_kis.investor_trend_time('콜_위클리_월'))
            dict_trend.update(self.ex_kis.investor_trend_time('풋_위클리_월'))
        elif self.COND_MRKT == "WKI":
            dict_trend.update(self.ex_kis.investor_trend_time('콜_위클리_목'))
            dict_trend.update(self.ex_kis.investor_trend_time('풋_위클리_목'))

        df = pd.DataFrame([dict_trend], index=[현재시간])
        if not self.df_trend.empty:
            self.df_trend = pd.concat([self.df_trend, df],axis=0)
        else:
            self.df_trend = df

    def divide_by_ratio(self, number, ratio_list, decimal_places=0):  #  차이점은 divide_by_ratio(10, [30,30,30], 0)  # [3,3,4]
        total_ratio = sum(ratio_list)
        # 각 비율에 따라 값을 소수점 자리수로 나눠서 계산
        raw_values = [(number * ratio / total_ratio) for ratio in ratio_list]

        # 소수점 자리수에 맞게 반올림
        rounded_values = [round(value, decimal_places) for value in raw_values]
        diff = round(number - sum(rounded_values), decimal_places)  # 남은 차이를 계산합니다.

        # 남은 차이를 마지막 요소에 반영해 합을 맞춥니다.
        for i in range(len(rounded_values)):
            if diff != 0:
                adjust = round(diff, decimal_places)
                rounded_values[i] += adjust
                break
        return rounded_values

    def distribute_by_ratio(self, number, ratios, decimal_places=0):  #  distribute_by_ratio(10, [30,30,30], 0)  # [3,3,3]
        # 비율 합계를 100으로 보정하여 계산할 비율을 구함
        total_ratio = sum(ratios)
        effective_number = number * (total_ratio / 100)

        # 각 비율에 따른 분배값 계산
        results = [(effective_number * (ratio / total_ratio)) for ratio in ratios]

        # 소숫점 자릿수에 맞게 반올림
        results = [round(result, decimal_places) for result in results]

        # 반올림 후 합이 달라졌을 수 있으므로 보정
        rounded_total = sum(results)
        difference = round(effective_number - rounded_total, decimal_places)

        # 보정이 필요한 경우 첫 번째 원소에 차이 추가
        if difference != 0:
            results[0] = round(results[0] + difference, decimal_places)

        return results

    def decimal_places(self, number):
        # 정수인지 확인하여 0을 반환합니다.
        if isinstance(number, int) or number.is_integer():
            return 0
        # 소수점 이하 자리수를 계산합니다.
        decimal_str = str(number).split('.')[1]
        return len(decimal_str)

    def bybit_set_tickers(self,fetch_tickers):
        for ticker in fetch_tickers.keys():
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
            del fetch_tickers[ticker]['info']
        df = pd.DataFrame.from_dict(data=fetch_tickers, orient='index')  # 딕셔너리로 데이터프레임  만들기 키값으로 행이름을 사용
        return df

    def color_text(self,state:str,stg:str,ticker:str,방향:str="long",진입가=0,주문수량=0,체결수량=0,보유수량=0,진입방식:str="",청산가=0,청산방식:str="",수익금=0,레버리지=1,체결금액=0,매입금액=0,잔고=0,수익률:float=0.0,상태="",현재봉시간='',수수료=0,id=''):
        진입가 = 진입가
        청산가 = format(청산가,',')
        수익금 = format(수익금,',')
        체결금액 = format(체결금액,',')
        잔고 = format(잔고,',')
        매입금액 = format(매입금액,',')
        수수료 = format(수수료,',')
        if state == 'open 주문':
            print(f"[{stg} - {ticker}] {self.yellow(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}, {진입방식= }, {방향= }, {진입가= }, {주문수량= }, {레버리지= }, {현재봉시간= }, {상태= }, {id=}, 금액={매입금액}, 매수가능금액={체결금액}")
            txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}  {진입방식= }, {방향= }, {진입가= }, {주문수량= }, {레버리지= }, {상태= }")
        elif state == 'close 주문':
            print(f"[{stg} - {ticker}] {self.cyan(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}  {청산방식= }, {방향= }, {청산가= }, {주문수량= }, {잔고= }, {수익률= }, {상태= }, {id=}")
            txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}  {청산방식= }, {방향= }, {청산가= }, {주문수량= }, {잔고= }, {수익률= }, {상태= }")
        elif state == 'open 체결' or state == 'open 부분체결':
            print(f"[{stg} - {ticker}] {self.blue(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}  {방향= }, {진입가= }, {주문수량= }, {체결수량= }, {보유수량= }, {체결금액= }, {매입금액= }, {잔고= }, {수수료= }, {상태= }")
            txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}  {방향= }, {진입가= }, {체결수량= }, {보유수량= }, {체결금액= }, {매입금액= }, {잔고= }")
        elif state == 'close 체결' or state == 'close 부분체결':
            print(f"[{stg} - {ticker}] {self.fie(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}  {방향= }, {청산가= }, {주문수량= }, {체결수량= }, {보유수량= }, {체결금액= }, {매입금액= }, {수익금= }, {수익률= }, {잔고= }, {수수료= }, {상태= }")
            txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}  {방향= }, {청산가= }, {체결수량= }, {보유수량= }, {체결금액= }, {수익금= }, {수익률= }, {잔고= }")
        elif state == '매수주문' or state == '매도주문': #취소주문일 경우
            print(f"[{stg} - {ticker}] {self.red(f'{state} 취소')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')} 취소수량= {보유수량}")
            txt = (f"[{stg} - {ticker}] {state} 취소| {common_def.datetime_to_str(datetime.datetime.now())} | 취소수량= {보유수량}")
        elif state == '부분매수':
            state = '부분체결(open) 나머지 취소'
            print(f"[{stg} - {ticker}] {self.red(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}, {보유수량= }, 취소수량: {주문수량}, {상태= }")
            txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}, {보유수량= }, 취소수량: {주문수량}")
        elif state == '부분매도':
            state = '부분체결(close) 나머지 시장가매도 전환'
            print(f"[{stg} - {ticker}] {self.red(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}, {보유수량= }, 취소수량: {주문수량}, {상태= }")
            txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}, {보유수량= }, 취소수량: {주문수량}")
        # elif state == '매수 부분 체결 나머지 취소' or state == '매도 부분 체결 나머지 취소':
        #     print(f"[{stg} - {ticker}] {self.red(f'{state}')} | {self.green(f'{common_def.datetime_to_str(datetime.datetime.now())}')}, 취소수량: {체결수량}")
        #     txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(datetime.datetime.now())}, 취소수량: {체결수량}")
        # elif state == 'close 주문 미 체결':
        #     print(f"[{stg} - {ticker}] {self.purple(f'{state}')} | {self.green(f'{common_def.datetime_to_str(현재시간)}')}, {방향= }, {진입가= }, 청산가= {체결금액}, 현재가= {레버리지= }  , {체결수량=}")
        #     txt = (f"[{stg} - {ticker}] {state} | {common_def.datetime_to_str(현재시간)}, {방향= }, {진입가= }, 청산가= {체결금액}, 현재가= {레버리지= }  , {체결수량=}")
        else:
            print('텍스트 조건 확인')
            print(f'{state}')
            txt = ('텍스트 조건 확인')
        if self.tele == True:
            if state != 'open 부분체결' or state != 'close 부분체결':
                self.bot = telegram.Bot(token=self.TOKEN)
                try:
                    asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=txt))
                except:
                    print('텔레그램 오류')
                # asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=txt))

    def fetch_bal(self):  # 지갑 조회
        # self.ex_bybit.set_sandbox_mode(False)
        # balanceSpot = self.ex_bybit.fetch_balance()['total']
        # print(balanceSpot)
        balanceSpot = self.ex_bybit.fetch_balance()
        # pprint(balanceSpot)
        # balanceSpot = self.ex_bybit.fetch_balance()
        # pprint(balanceSpot)
        return balanceSpot

    def test_sql(self,df,text):
        df.to_sql(text, sqlite3.connect('DB/bt.db'), if_exists='replace')

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
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)



    class simul_QCB():
        def isChecked(self):
            return True
    simul = simul_QCB()

    # market = '국내주식'
    # market = '국내선옵'
    market = '코인'
    list_tickers = []
    if market == '국내주식':
        conn_stg = sqlite3.connect('DB/stg_stock.db')
    elif market == '국내선옵':
        def convert_column_types(df):
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='raise')
                except ValueError:
                    pass
            return df
        conn_stg = sqlite3.connect('DB/stg_futopt.db')
        ex_kis = common_def.make_exchange_kis('모의선옵')
        date=datetime.datetime.now().replace(second=0, microsecond=0)

        df_f = ex_kis.display_fut()
        df_f = convert_column_types(df_f)
        현재가 = df_f.loc[df_f.index[0], '현재가']
        time.sleep(1)

        df_c,df_p = ex_kis.display_opt(date)
        df_c = convert_column_types(df_c)
        df_p = convert_column_types(df_p)
        df_c = df_c[df_c['행사가'] > 현재가 - 25]
        df_c = df_c[df_c['행사가'] < 현재가 + 25]
        df_c['종목명'] = '콜옵션'
        df_p = df_p[df_p['행사가'] > 현재가 - 25]
        df_p = df_p[df_p['행사가'] < 현재가 + 25]
        df_p['종목명'] = '풋옵션'
        time.sleep(1)
        df_c_w,df_p_w,COND_MRKT = ex_kis.display_opt_weekly(date)
        df_c_w = convert_column_types(df_c_w)
        df_p_w = convert_column_types(df_p_w)
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

        if not df_c_w.empty and not df_p_w.empty:
            if COND_MRKT == "WKM":
                yoil = '월'
            elif COND_MRKT == "WKI":
                yoil = '목'
            else:
                yoil = '만기'

            df_c_w = df_c_w[df_c_w['행사가'] > 현재가 - 25]
            df_c_w = df_c_w[df_c_w['행사가'] < 현재가 + 25]
            df_c_w['종목명'] = '콜'+'_위클리_'+yoil

            df_p_w = df_p_w[df_p_w['행사가'] > 현재가 - 25]
            df_p_w = df_p_w[df_p_w['행사가'] < 현재가 + 25]
            df_p_w['종목명'] = '풋'+'_위클리_'+yoil

            df_c_w.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
            df_p_w.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
            df_c_w_common = df_c_w[common_columns]
            df_p_w_common = df_p_w[common_columns]
            df4_with_separator = pd.concat([df_c_w_common, create_separator_row(common_columns)], ignore_index=True)
            df5_with_separator = pd.concat([df_p_w_common, create_separator_row(common_columns)], ignore_index=True)
            df_combined = pd.concat([df_combined, df4_with_separator, df5_with_separator], ignore_index=True)


        # 결과 출력
        # df_combined['종목코드_시장'] = df_combined['종목코드'] + df_combined['종목명']

        list_tickers = df_combined['종목코드'].tolist()
        # list_tickers = dict(zip(df_combined['종목코드'].tolist(),df_combined['종목명'].tolist()))
        # pd.set_option('display.max_rows',None)
        # print(df_combined)
        # pd.set_option('display.max_rows',False)
    elif market == '코인':
        conn_stg = sqlite3.connect('DB/stg_bybit.db')
        list_tickers = ['BTC','ETH','XRP']
        COND_MRKT = "WKM"
    df_stg = pd.read_sql(f"SELECT * FROM 'stg'", conn_stg).set_index('index')
    # df_instock = pd.DataFrame()
    tele = True
    duration = 30
    trade = Trade_np(None,market,simul,df_stg,duration,tele,list_tickers,COND_MRKT)

    # stg = '시가_풋'
    # ticker = '201W01337'
    # dict_stg_stg = {'진입대상': {'풋옵션': '1~2'}, 'ticker': '301W01332', '봉': '5분봉', '상세봉': '1분봉', '봉제한': np.int64(3), '팩터': [], '비교대상': {'수급동향': False}}
    # df = trade.make_df(ticker,dict_stg_stg['봉'],dict_stg_stg['상세봉'],dict_stg_stg['봉제한'],False)
    # print(df)
    # trade.run()
    # dict_stg_stg = trade.check_compare_ticker(stg,ticker, dict_stg_stg)
    # print(f"{dict_stg_stg['비교대상']=}")

    # quit()
    # print(trade.fie('asdf'))
    trade.run()