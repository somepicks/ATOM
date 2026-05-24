import sqlite3
import pandas as pd
import numpy as np
import datetime
import time
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex,pyqtSlot
import common_def
from matplotlib.gridspec import GridSpec
import KIS
from pprint import pprint


pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
import ccxt
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex,pyqtSlot
from PyQt5.QtWidgets import QMessageBox

import KIS
from pprint import pprint
import common_def



def 구간최고시가(pre):
    if market == 'bybit':
        # pp = row_tik - int(pre * bong_stamp/bong_detail_stamp)
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('시가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('시가')].max()
def 구간최저시가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('시가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('시가')].max()
def 구간최고고가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('고가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('고가')].max()
def 구간최저고가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('고가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('고가')].max()
def 구간최고저가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('저가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('저가')].max()
def 구간최저저가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('저가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('저가')].max()
def 구간최고종가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('조가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('종가')].max()
def 구간최저종가(pre):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,li_detail_col.index('조가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,li_detail_col.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,li_detail_col.index('종가')].max()
def 구간최고시가N(pre,N): #이거는 다시 한번 봐야 됨
    if market == 'bybit':
        pre_len = row_tik - int(pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        # print(np_tik[pre_len-div:row_tik-div])
        return np_tik[pre_len-div:row_tik-div, li_detail_col.index('시가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('시가')].max()
def 구간최저시가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('시가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx = np.argmax(np_tik[:, li_detail_col.index('데이터길이')] == num - pre - N)
        end_idx = np.argmax(np_tik[:, li_detail_col.index('데이터길이')] == num - N+1)
        return np_tik[first_idx:end_idx, li_detail_col.index('시가')].min()
def 구간최고고가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('고가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('고가')].max()
def 구간최저고가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('고가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('고가')].min()
def 구간최고저가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('저가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('저가')].max()
def 구간최저저가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('저가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('저가')].min()
def 구간최고종가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('종가')].max()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('종가')].max()
def 구간최저종가N(pre,N):
    if market == 'bybit':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), li_detail_col.index('종가')].min()
    else:
        num = np_tik[row_tik, li_detail_col.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,li_detail_col.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,li_detail_col.index('종가')].min()

def 시가CN(bong,pre):
    if market == 'bybit':
        return np_detail_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), li_detail_col.index(f'시가_{bong}')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, li_detail_col.index(f'데이터길이_{bong}')] == num - pre][0][li_detail_col.index(f'시가_{bong}')]

def 고가CN(bong,pre):
    if market == 'bybit':
        return np_detail_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), li_detail_col.index(f'고가_{bong}')]
    else:
        num = np_tik[row_tik, li_detail_col.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, li_detail_col.index(f'데이터길이_{bong}')] == num - pre][0][li_detail_col.index(f'고가_{bong}')]
def 저가CN(bong,pre):
    if market == 'bybit':
        return np_detail_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), li_detail_col.index(f'저가_{bong}')]
    else:
        num = np_tik[row_tik, li_detail_col.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, li_detail_col.index(f'데이터길이_{bong}')] == num - pre][0][li_detail_col.index(f'저가_{bong}')]
def 종가CN(bong,pre):
    if market == 'bybit':
        return np_detail_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), li_detail_col.index(f'종가_{bong}')]
    else:
        num = np_tik[row_tik, li_detail_col.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, li_detail_col.index(f'데이터길이_{bong}')] == num - pre][0][li_detail_col.index(f'종가_{bong}')]
def 이평20CN(bong,pre):
    if market == 'bybit':
        return np_detail_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), li_detail_col.index(f'이평20_{bong}')]
    else:
        num = np_tik[row_tik, li_detail_col.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, li_detail_col.index(f'데이터길이_{bong}')] == num - pre][0][li_detail_col.index(f'이평20_{bong}')]
def 이평60CN(bong,pre):
    if market == 'bybit':
        return np_detail_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), li_detail_col.index(f'이평60_{bong}')]
    else:
        num = np_tik[row_tik, li_detail_col.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, li_detail_col.index(f'데이터길이_{bong}')] == num - pre][0][li_detail_col.index(f'이평60_{bong}')]


# np_tik이나 np_detail_ar로 돌리는거보다 np_df_ar 이 더 빠름


def 고가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('고가')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'고가')]

def 시가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('시가')]
    else: #국내시장일 경우(일봉)
        # 빠름
        # num = np.argmax(np_df_idx_date == np_detail_idx[row_tik].astype('datetime64[D]') )  # df에서 인덱스순서를 갖고오기
        # return np_df_ar[num - pre, np.argmax(np_df_col == '시가')]  # df에서 데이터를 갖고오기


        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'시가')]

        # mask = np_detail_ar[:, globals()['데이터길이_num']] == 데이터길이
        # last_idx = len(mask) - 1 - np.argmax(mask[::-1])
        # return np_detail_ar[last_idx, globals()['시가_num']]

def 저가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('저가')]
    else:
        # num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        # if 현재시간.date() == datetime.date(2025, 10, 15):
        #     print(num)
        return np_tik[np.argmax(np_detail_data_length == 데이터길이-pre), li_detail_col.index(f'저가')]

        # mask = np_detail_ar[:, globals()['데이터길이_num']] == 데이터길이
        # last_idx = len(mask) - 1 - np.argmax(mask[::-1])
        # return np_detail_ar[last_idx, globals()['저가_num']]
def 종가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('종가')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'종가')]

        # mask = np_detail_ar[:, globals()['데이터길이_num']] == 데이터길이
        # last_idx = len(mask) - 1 - np.argmax(mask[::-1])
        # return np_detail_ar[last_idx, globals()['종가_num']]

def 거래량N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('거래량')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'거래량')]

        # mask = np_detail_ar[:, globals()['데이터길이_num']] == 데이터길이
        # last_idx = len(mask) - 1 - np.argmax(mask[::-1])
        # return np_detail_ar[last_idx, globals()['거래량_num']]
def 이평20N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평20')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평20')]

        # mask = np_detail_ar[:, globals()['데이터길이_num']] == 데이터길이
        # last_idx = len(mask) - 1 - np.argmax(mask[::-1])
        # return np_detail_ar[last_idx, globals()['이평20_num']]
def 거래량이평3N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('거래량이평3')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'거래량이평3')]

        # mask = np_detail_ar[:, globals()['데이터길이_num']] == 데이터길이
        # last_idx = len(mask) - 1 - np.argmax(mask[::-1])
        # return np_detail_ar[last_idx, globals()['거래량이평3_num']]
def 이평5N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평5')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평5')]


def 이평60N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평60')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평60')]
def 이평100N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평100')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평100')]
def 이평120N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평120')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평120')]
def 이평200N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평200')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평200')]
def 이평240N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이평240')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이평240')]


def 거래량이평20N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('거래량이평20')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'거래량이평20')]
def 거래량이평60N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('거래량이평60')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'거래량이평60')]
def RSI14N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('RSI14')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'RSI14')]
def RSI18N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('RSI18')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'RSI18')]
def RSI30N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('RSI30')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'RSI30')]
def ATRN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('ATR')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'ATR')]
def TRANGEN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('TRANGE')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'TRANGE')]
def 이격도20이평N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('이격도20이평')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'이격도20이평')]
def 밴드상N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('밴드상')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'밴드상')]
def 밴드중N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('밴드중')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'밴드중')]
def 밴드하N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('밴드하')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'밴드하')]
def MACDN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('MACD')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'MACD')]
def MACD_SIGNALN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('MACD_SIGNAL')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'MACD_SIGNAL')]
def MACD_HISTN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('MACD_HIST')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'MACD_HIST')]
def 등락율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('등락율')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'등락율')]
def 변화율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('변화율')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'변화율')]
def 수익율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('수익율')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'수익율')]
def 고저평균대비등락율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('고저평균대비등락율')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'고저평균대비등락율')]
def 당일거래대금N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == 'bybit':
        return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('당일거래대금')]
    else:
        num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
        return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'당일거래대금')]
# def 종료시간N(pre):
#     if 데이터길이 <= pre:
#         return np.nan
#     if market == 'bybit':
#         return np_detail_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), li_detail_col.index('종료시간')]
#     else:
#         num = np_tik[row_tik,li_detail_col.index(f'데이터길이')]
#         return np_tik[np.argmax(np_detail_data_length == num-pre), li_detail_col.index(f'종료시간')]

def moving_average(np_arry, w):
    return np.convolve(np_arry, np.ones(w), 'valid') / w

def 이평(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_detail_ar[row_tik - pre, li_detail_col.index('종가')]/pre
# def 전일비각도(pre):
#     print('전일비각도')
#     try:
#         jvp_gap = 전일비 - np_tik[-(pre), li_detail_col.index('전일비')]
#         return round(math.atan2(jvp_gap, pre) / (2 * math.pi) * 360, 2)
#     except:
#         print('에러')
#         return 0
#
#
# def 거래대금각도(pre):
#     print('당일거래대금각도')
#     try:
#         dmp_gap = 당일거래대금 - np_tik[-(pre), li_detail_col.index('당일거래대금')]
#         return round(math.atan2(dmp_gap, pre) / (2 * math.pi) * 360, 2)
#     except:
#         return 0

class backtest_np(QThread):
    signal_df = pyqtSignal(pd.DataFrame,pd.DataFrame)
    signal_bar = pyqtSignal(int)
    signal_state = pyqtSignal(dict)
    signal_light = pyqtSignal(bool)
    signal_message = pyqtSignal(str,str)
    signal_stop = pyqtSignal()

    def __init__(self, parent, df, df_detail, dict_info):
        super().__init__(parent)
    # def __init__(self,df,df_detail,dict_info):
    #     super().__init__()

        # self.mutex = QMutex()
        # pprint(dict_info)
        self.market = dict_info['market']
        self.stg_buy = dict_info['stg_buy']
        self.stg_sell = dict_info['stg_sell']
        self.bet = dict_info['bet']
        self.bong = dict_info['봉']
        self.bong_detail = dict_info['상세봉']
        self.exchange = dict_info['exchange']
        self.fee = dict_info['fee']
        self.dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '1시간봉': 60, '4시간봉': 240, '일봉': 1440,
                           '주봉': 10080}
        self.dic_multiplier = {'101':250000,'201':250000,'301':250000, #코스피200
                               '105':50000,'205':50000,'305':50000, #미니코스피200
                               '106': 10000, '206': 10000, '306': 10000, #코스닥150
                               '선물': 250000, '콜옵션': 250000, '풋옵션': 250000,
                               '미니선물': 50000,'코스닥선물': 10000}
        self.bool_light = False
        self.trade_market = dict_info['trade_market']
        self.direction = dict_info['direction']
        self.거래승수 = dict_info['거래승수']
        self.leverage = dict_info['증거금률']
        self.buy_scale = dict_info['분할매수']
        self.sell_scale = dict_info['분할매도']
        if self.market == 'bybit':
            # self.exchange = dict_info['exchange']
            self.ticker = dict_info['ticker']+'USDT'
            self.exchange.fetch_tickers() #바이비트의 경우 한번 해줘야 에러가 안남
            self.leverage = dict_info['증거금률']
            self.ror_leverage = self.leverage
        elif self.market == '국내선옵':
            self.ticker = dict_info['ticker']
            if self.ticker.endswith('선물'):
                self.trade_market = '선물'
                self.leverage = 100/self.leverage
            else:
                self.trade_market = '옵션'
            self.ror_leverage =1
        elif self.market == '국내주식': #국내주식
            self.ticker = dict_info['ticker']
            self.ror_leverage =1
        # self.fee_krx = 0.015
        # self.tax_krx = 0.018
        # self.fee_limit = 0.02
        # self.fee_market = 0.055
        # self.fee = 0.01  # 0.01% -> 0.0001
        # self.위탁증거금률 = 10    # 선물 위탁증거금률 = 10%
        self.df = df
        self.df_detail = self.reset_data_lenth(df_detail)
        self._status = True


    def run(self):
        global np_detail_ar
        global row_tik
        global li_detail_col
        global np_tik
        global np_detail_idx
        global np_df_ar
        global np_df_idx_date
        global np_df_col
        global np_detail_data_length
        global 데이터길이
        global 상태
        global 수익률, 최고수익률, 최저수익률
        global 매수가, 매도가, 시장가
        global 현재시간, 매수시간, 종료시간
        global 자산
        global 상세시가, 상세고가, 상세저가, 상세종가
        global 현재가
        global market
        global bong_stamp
        global dict_bong_stamp
        global bong_detail_stamp
        global 롱, long, 숏, short
        global 시가, 고가, 저가, 종가
        global 분봉1, 분봉3, 분봉5, 분봉15, 분봉30, 시간봉4, 일봉, 주봉, 월봉
        global 재진입금지
        재진입금지 = False
        # 분봉3 = '3분봉' # 시가CN(bong,pre) bong자리에 넣기 위함 변수로 숫자가 앞에 올 수는 없기 때문
        # 분봉5 = '5분봉'
        # 분봉15 = '15분봉'
        롱 = 'long'
        long = 'long'
        숏 = 'short'
        short = 'short'
        시장가 = '시장가'


        start_time = time.time()
        dict_bong_stamp = self.dict_bong_stamp
        for i in range(20):
            globals()[f'매도{i}호가'] = f'매도{i}호가'
        for i in range(20):
            globals()[f'매수{i}호가'] = f'매수{i}호가'

        상태 = '대기'

        # if not len(self.df_detail) == len(self.df_detail):
        #     print(f'{len(self.df_detail)}, {len(self.df_detail)}')
        #     raise '데이터길이 다름 확인 필요'
        self.buy = [np.nan for x in range(len(self.df_detail.index))]  # 매수가
        self.sell = [np.nan for x in range(len(self.df_detail.index))]  # 매도가
        self.buy_order = [np.nan for x in range(len(self.df_detail.index))]  # 매수주문가
        self.sell_order = [np.nan for x in range(len(self.df_detail.index))]  # 매도주문가
        self.state = [np.nan for x in range(len(self.df_detail.index))]  # 상태
        self.ror = [np.nan for x in range(len(self.df_detail.index))]  # 수익률
        self.ror_max = [np.nan for x in range(len(self.df_detail.index))]  # 최고수익률
        self.ror_min = [np.nan for x in range(len(self.df_detail.index))]  # 최저수익률
        # self.ror_strategy = [np.nan for x in range(len(self.df_detail.index))]  # 전략수익률
        self.benefit = [np.nan for x in range(len(self.df_detail.index))]  # 수익금
        self.wallet = [np.nan for x in range(len(self.df_detail.index))]  # 잔고
        self.asset = [np.nan for x in range(len(self.df_detail.index))]  # 잔고
        self.hold_qty = [np.nan for x in range(len(self.df_detail.index))]  # 보유수량
        self.fee_paid = [np.nan for x in range(len(self.df_detail.index))]  # 수수료
        self.price_buy = [np.nan for x in range(len(self.df_detail.index))]  # 총매수금액
        self.price_sell = [np.nan for x in range(len(self.df_detail.index))]  # 총매도금액
        # self.buy_count = [np.nan for x in range(len(self.df_detail.index))]  # 총매수횟수
        self.val = [np.nan for x in range(len(self.df_detail.index))]  # test
        self.val_k = [np.nan for x in range(len(self.df_detail.index))]  # test
        잔고 = self.bet
        자산 = self.bet
        self.df.loc[self.df['데이터길이'] == 1, '잔고'] = 잔고
        self.df.loc[self.df['데이터길이'] == 1, '자산'] = 자산
        market = self.market
        np_df_ar = self.df.to_numpy()
        np_df_idx_date = self.df.index.normalize().to_numpy() #시간무시하고 날짜만 갖고오기
        np_df_col = self.df.columns.to_numpy()
        np_detail_ar = self.df_detail.to_numpy()  # 전체 데이터를 np로 저장
        np_detail_idx = self.df_detail.index.to_numpy()  # 인덱스를 np로 저장
        np_detail_data_length = self.df_detail['데이터길이'].to_numpy()  # 전체 데이터를 np로 저장
        # np_detail_now = self.df_detail['현재시간'].to_numpy()  # 전체 데이터를 np로 저장
        li_detail_col = self.df_detail.columns.tolist()  # 컬럼명을 리스트로 저장
        for i,col in enumerate(li_detail_col):  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
            globals()[f'{col}_num'] = i
        # self.df_detail.drop('종료시간',axis=1,inplace=True)
        length_index = len(self.df_detail.index)
        row_tik = 0
        old_row_tik = 0
        bong_stamp = self.dict_bong_stamp[self.bong]
        bong_detail_stamp = self.dict_bong_stamp[self.bong_detail]
        self.dict_state = {'현재시간':'','상태':'대기','잔고':잔고,'수익률':0,'수익금':0}
        '''sqlite=1 == row_tik=0 , length_index=1'''

        # common_def.export_sql(self.df,"DB/bt.db","df")
        # if 현재시간.date() == datetime.date(2019,3,27):
        # if 현재시간 == datetime.datetime(2020,11,2,9,0,0):
        st = time.time()
        while self._status and row_tik < length_index:
            if 상태 == '대기': #미 보유 시 진입 주문
                while row_tik < length_index :
                    self.wallet[row_tik] = 잔고
                    self.asset[row_tik] = 자산
                    self.state[row_tik] = 상태

                    # 밑에 명령처럼 넘파이를 자르면서 하는게 빠른지 확인 필요
                    np_tik = np_detail_ar[:row_tik + 1]
                    # for col in li_detail_col:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                    #     globals()[f'{col}'] = np_tik[row_tik, li_detail_col.index(f'{col}')]

                    self.make_vars(row_tik)
                    현재가 = 상세시가
                    # 매수 = False
                    locals_dict_buy_signal = {}
                    exec(self.stg_buy, None, locals_dict_buy_signal)
                    매수 = locals_dict_buy_signal.get('매수')
                    self.active_light()
                    self.signal_dict_state(현재시간)
                    # print(f"+ {현재시간= }  {상세시가=}     {현재가=}  {시가_일봉=}  {MACDN(1)=}   {MACD_SIGNALN(1)=}  {RSI14N(1)=}")

                    if (not 매수 == False) and (not 매수 == None):  # 매수 일 경우 None을 반환하기 때문에(매수신호 떳을 때)
                        상태 = '매수주문'
                        진입주문가 = locals_dict_buy_signal.get('매수가')
                        매수가 = self.order_price(진입주문가,상세시가,'매수주문')
                        self.buy_order[row_tik] = 매수가
                        print(f"-매수주문 {현재시간=}   {매수가=}   {진입주문가= }    {매수= }  {상세시가=}     {현재가=}   ")
                        break
                    row_tik += 1
                    self.signal_bar.emit(round(row_tik / length_index * 100))
            if 상태 == '매수주문':  # 매수 체결 확인
                print(f"if 상태 == '매수주문':{현재시간}   {self.direction}   {매수가=}   {저가=}   {self.direction == 'long' and 매수가 >= 저가}")
                self.state[row_tik] = 상태
                self.dict_state['상태'] = 상태
                # if 현재시간 > datetime.datetime(2025, 10, 15, 15, 29, 0):
                #     print(f"{현재시간=}  {매수=}  {상태= }    {저가=}   {저가N(1)= }    {저가N(2)=}  {데이터길이=} {row_tik=}")
                #     self.check_db(row_tik)
                #     quit()
                if (self.direction == 'long' and 매수가 >= 저가) or (self.direction == 'short' and 매수가 <= 고가):
                    print(f"{매수가=}  |  {저가=}")
                    while True:
                        np_tik = np_detail_ar[:row_tik + 1]
                        self.signal_dict_state(현재시간)
                        print(f"상태 == '매수주문' === :{현재시간=}   {row_tik= }   {상세저가}   {매수가=}   {상세고가=}   {상세저가 <= 매수가}    {매수가 <= 상세고가}")
                        # for col in li_detail_col:  # 첫 매수주문 후에 상세가격 확인을 위해
                        #     globals()[f'{col}'] = np_tik[row_tik, li_detail_col.index(f'{col}')]
                        self.make_vars(row_tik)

                        if (self.direction == 'long' and 매수가 >= 상세저가) or (self.direction == 'short' and 매수가 <= 상세고가): #롱이던 숏이던 상세 진입구간을 알고싶은거기 때문에 무관함,
                            print(f"매수주문1 {row_tik= } {매수= }, {매수가= }, {잔고= }, ")
                            보유수량, 매수금액, 잔고, 자산, 최고수익률, 최저수익률, 상태 = \
                                self.chegyeol_buy(매수, 매수가, 잔고, row_tik)
                            print(f"*매수주문2 {row_tik= }  {현재시간=}  {보유수량=}, {매수금액=}, {잔고=}, {자산=}, {매수금액=}, {self.매수수수료=}, {최고수익률=}, {최저수익률=}, {상태=},")
                            break
                        print(f"{row_tik= }  {잔고=}")
                        self.wallet[row_tik] = 잔고
                        self.asset[row_tik] = 자산
                        self.buy_order[row_tik] = 매수가
                        self.state[row_tik] = '매수 대기'
                        self.signal_bar.emit(round(row_tik / length_index * 100))
                        row_tik += 1
                        if row_tik == length_index:
                            self._status == False
                            상태 = '종료'
                            break
                        print(f"{row_tik= }  {잔고=}")
                        # else:
                        #     self.check_db(row_tik)
                        #     quit()
                        # elif 현재시간 >= 종료시간: #long일경우 매수가>저가 이지만 상세로 보면 이미 지나버린 시점일 수 있음에 유의
                        #     print("미체결 시")
                        #     상태 = '대기'
                        #     self.wallet[row_tik] = 잔고
                        #     self.asset[row_tik] = 자산
                        #     self.buy_order[row_tik] = 매수가
                        #     self.state[row_tik] = '매수 안됨 상태 매도 전환'
                        #     break

                else: # 미체결 시
                    print(f"미체결 시  {row_tik=} {현재시간=}  ")
                    row_tik_old = row_tik
                    # idx_num = np.where(np_detail_idx>종료시간)  #idx_num[0].size      np.argmax로 해도 됨
                    # print(f"1 {idx_num=} {종료시간= }   {time.time() - st}")
                    st = time.time()
                    idx_num = np.argmax(np_detail_idx > 종료시간)-1  #idx_num[0].size      np.argmax로 해도 됨
                    print(f"미체결 시  1 {idx_num=} {종료시간= }   {np_detail_data_length[idx_num]}   {np_detail_data_length[-1]} {time.time() - st}")
                    # idx_num = np.argmax(np_detail_idx==종료시간)
                    if np_detail_data_length[idx_num] == np_detail_data_length[-1] : #넘파이가 비어있을 경우(row_tik이 마지막행까지 갔을 경우)
                        self.wallet[row_tik_old:length_index] = [잔고 for x in range(length_index - row_tik_old)]
                        self.asset[row_tik_old:length_index] = [자산 for x in range(length_index - row_tik_old)]
                        self.state[row_tik_old:length_index] = ['종료' for x in range(length_index - row_tik_old)]
                        상태 = {'종료':'백테스트 종료'}
                        self._status = False
                    row_tik = idx_num   #시간절약을위해 매수주문 후 큰 범위에서 매수가 안되면 건너뛰기
                    print(f"미체결 시  2 {idx_num=} {종료시간= }   {time.time() - st}")
                    print(f"{잔고= }")
                    print(f"{자산= }")
                    print(f"{매수가= }")
                    print(f"{row_tik= }")
                    print(f"{row_tik_old= }")
                    count = int(row_tik + 1 - row_tik_old)
                    self.wallet[row_tik_old:row_tik+1] = [잔고 for x in range(count)]
                    self.asset[row_tik_old:row_tik+1] = [자산 for x in range(count)]
                    self.buy_order[row_tik_old:row_tik+1] = [매수가 for x in range(count)]
                    self.state[row_tik_old:row_tik+1] = ['매수 미 체결' for x in range(count)]
                    # self.buy[row_tik_old] = '매수주문'
                    상태 = '대기'
                row_tik += 1

            while 상태 == '매수':  # 매수상태일 때
                np_tik = np_detail_ar[:row_tik + 1]
                # for col in li_detail_col:  # 수익률 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                #     globals()[f'{col}'] = np_tik[row_tik, li_detail_col.index(f'{col}')]
                self.make_vars(row_tik)

                수익률, 최고수익률, 최저수익률 = (
                    self.cal_ror(상세고가, 상세저가, 상세종가,보유수량, 매수금액, 잔고, 최고수익률, 최저수익률, row_tik))
                locals_dict_sell = {}
                exec(self.stg_sell, None, locals_dict_sell)
                매도 = locals_dict_sell.get('매도')

                if 매도 == True:
                    상태 = '매도주문'
                    청산주문가 = locals_dict_sell.get('매도가')
                    매도가 = self.order_price(청산주문가,상세시가,'매도주문')
                    self.sell_order[row_tik] = 매도가
                    self.state[row_tik] = 상태
                    self.dict_state['상태'] = 상태
                    break
                else:
                    self.state[row_tik] = 상태
                    self.dict_state['상태'] = 상태
                    row_tik += 1
                    if row_tik == length_index:
                        self._status = False
                        상태 = '종료'
                        break

            if 상태 == '매도주문':
                while True:
                    print(f"{row_tik= }")
                    np_tik = np_detail_ar[:row_tik + 1]
                    # for col in li_detail_col:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                    #     globals()[f'{col}'] = np_tik[row_tik, li_detail_col.index(f'{col}')]
                    self.make_vars(row_tik)

                    print(f"if 상태 == '매도주문' {현재시간=}   {매수가=}   {진입주문가= }    {매수= }  {상세시가=}     {현재가=}    {MACDN(1)=}   {MACD_SIGNALN(1)=} {RSI14N(1)=}")
                    # if (self.direction == 'long' and 매수가 >= 고가) or (self.direction == 'short' and 매수가 <= 저가):
                    수익률, 최고수익률, 최저수익률 = self.cal_ror(상세고가, 상세저가, 상세종가, 보유수량, 매수금액, 잔고, 최고수익률, 최저수익률, row_tik)
                    if (self.direction == 'long' and 매도가 <= 상세고가) or (self.direction == 'short' and 매도가 >= 상세저가):
                        # if self.direction == 'long' and 매도가 < 상세저가 : #롱일경우 매도가가 저가보다 낮을 수 없음 (시장가 슬리피지일 경우 감안하여 저가로)
                        #     매도가 = 상세저가
                        # elif self.direction == 'short' and 매도가 > 상세고가 :
                        #     매도가 = 상세고가
                        수익률, 잔고, 자산 = self.chegyeol_sell(매도가, 보유수량, 매수금액, 잔고, row_tik)
                        상태 = '대기'
                        row_tik_old = row_tik
                        # idx_num = np.argmax(np_detail_idx == 종료시간)
                        idx_num = np.argmax(np_detail_idx > 종료시간)-1
                        # print(f"2 {np_detail_idx=}")
                        # print(f"2 {idx_num=} {np_detail_idx[idx_num]}   {종료시간= }")
                        # quit()
                        self.wallet[row_tik_old+1:idx_num+1] = [잔고 for x in range(idx_num - row_tik_old)]
                        self.asset[row_tik_old+1:idx_num+1] = [자산 for x in range(idx_num - row_tik_old)]
                        self.state[row_tik_old+1:idx_num+1] = ['청산- 추가 매수 X' for x in range(idx_num - row_tik_old)]
                        row_tik = idx_num+1  # 시간절약을위해 매수주문 후 큰 범위에서 매수가 안되면 건너뛰기
                        np_tik = np_detail_ar[:row_tik + 1]

                        print(f"{row_tik=}    {idx_num= }     {length_index=}    {len(np_tik)= }")
                        print(f"if 상태 == '매도주문'2 {현재시간=}   {매수가=}   {진입주문가= }    {매수= }  {상세시가=}     {현재가=}    {MACDN(1)=}   {MACD_SIGNALN(1)=} {RSI14N(1)=}")
                        # self.check_db(row_tik)
                        # quit()
                        break
                    elif 현재시간 >= 종료시간: #long일경우 매도가 < 고가 여도 상세로 보면 이미 지나버린 시점일 수 있음에 유의
                        상태 = '매수'
                        self.wallet[row_tik] = 잔고
                        self.asset[row_tik] = 자산
                        self.sell_order[row_tik] = 매도가
                        self.state[row_tik] = '종료시간까지 매도 안됨 상태 매수 전환'
                        row_tik += 1
                        break
                    else:
                        locals_dict_sell = {}
                        # 매도신호가 나와있는 와중에 손절등으로 추가 매도 신호가 나올 수 있기 때문에 다시한번 매도 신호를 받음
                        exec(self.stg_sell, None,locals_dict_sell)
                        매도 = locals_dict_sell.get('매도')
                        # 매도 진입 확인이 먼지인지 매도신호가 나와있는 와중에 손절등으로 추가매도 신호가 나으는걸 확인하는게 먼저인지 고민해볼 필요
                        청산주문가 = locals_dict_sell.get('매도가')
                        if 매도 == True and 청산주문가 == 시장가: # 기존에 지정가로 매도가 나가있는 상태에서 다른조건에의한 지정가 매도는 수정 안됨 (시장가만 수정하여 매도)
                            # print(f"중간에 시장가 매도 {row_tik=}, {현재시간=}, {매도가=}")
                            매도가 = self.order_price(청산주문가, 상세시가,'매도주문')
                            self.sell_order[row_tik] = 매도가
                            수익률, 잔고, 자산 = self.chegyeol_sell(매도가, 보유수량, 매수금액, 잔고, row_tik)
                            상태 = '대기'
                            print(f"{상태= }   {잔고= }   {row_tik=} {old_row_tik=}  |  {np_detail_idx[row_tik]=},")
                            self.wallet[row_tik] = 잔고
                            self.asset[row_tik] = 자산
                            self.state[row_tik] = '시장가 매도'
                            # self.check_db(row_tik)
                            row_tik += 1
                            break
                        self.wallet[row_tik] = 잔고
                        self.asset[row_tik] = 자산
                        self.sell_order[row_tik] = 매도가
                        self.state[row_tik] = '매도 대기'
                        row_tik += 1
            # print(f"{length_index= } | {row_tik= } | {상태=} | {np_detail_now[row_tik]=}")
            # self.ror_strategy[row_tik] = round((자산 - self.bet) / self.bet * 100, 1)  # 최초 배팅 금액 대비 수익률 계산용
            self.signal_bar.emit(round(row_tik / length_index * 100))
            if row_tik >= length_index:
                row_tik -= 1 # row_tik은 0부터 시작 length_index는 1부터 시작 때문에
                print('정상종료')
                # self.ror_strategy[row_tik] = round((자산 - self.bet) / self.bet * 100, 1)  # 최초 배팅 금액 대비 수익률 계산용
                break
            elif self.wallet[row_tik-1] is None:
                print('자금 None')
                raise
            elif np.isnan(self.wallet[row_tik-1]):
                self.check_db(row_tik)
                print(f"{self.df_detail.index[row_tik]} : {row_tik + 1} ,'- 잔고 엥꼬' | 상태: {상태},   잔고: {self.wallet[row_tik]}")
                break

        self.finish_df(length_index,start_time,상태)


    def order_price(self,price_in,시가,side):
        slippage = 0.1  # 슬리피지 0.1 %
        if type(price_in) == dict:
            hoga_price = list(price_in.keys())[0]
            hoga_rate = price_in[hoga_price]
            # try:
            if self.market == 'bybit':
                매수가 = float(self.exchange.price_to_precision(self.ticker, hoga_price + (hoga_price * hoga_rate / 100)))
            elif self.trade_market == 'KOSPI' or self.trade_market == 'KOSDAQ' or self.trade_market == 'ETF' or self.trade_market == 'ETF':
                매수가 = self.exchange.hogaPriceReturn(self.trade_market,self.ticker, hoga_price, hoga_rate)
            elif self.trade_market == '선물' or self.trade_market == '옵션':
                매수가 = self.exchange.hogaPriceReturn(self.trade_market,self.ticker, hoga_price, hoga_rate)
            # except: f"{self.ticker= }   {hoga_price= }  {hoga_rate= }    "
        elif price_in == 시장가 :  # 슬리피지 반영
            if self.market == 'bybit' or self.trade_market == '선물' or self.trade_market == '옵션':
                if self.direction == 'long' and side == '매수주문': 가격 = 시가 + (slippage / 100 * 시가)
                elif self.direction == 'long' and side == '매도주문': 가격 = 시가 - (slippage / 100 * 시가)
                elif self.direction == 'short' and side == '매수주문': 가격 = 시가 - (slippage / 100 * 시가)
                elif self.direction == 'short' and side == '매도주문': 가격 = 시가 + (slippage / 100 * 시가)
                else: raise
                if self.trade_market == 'bybit':
                    매수가 = float(self.exchange.price_to_precision(self.ticker, 가격))
                elif self.trade_market == '선물' or self.trade_market == '옵션':
                    매수가 = self.exchange.hogaPriceReturn_per(self.trade_market, self.ticker, 가격, 0)
            elif self.trade_market == 'KOSPI' or self.trade_market == 'KOSDAQ' or self.trade_market == 'ETF' or self.trade_market == 'ETF':
                if side == '매수주문':
                    가격 = 시가 + (slippage / 100 * 시가)
                elif side == '매도주문':
                    가격 = 시가 - (slippage / 100 * 시가)
                매수가 = self.exchange.hogaPriceReturn_per(self.trade_market,self.ticker, 가격, 0)
        else:
            if self.market == 'bybit':  # 슬리피지 반영 해야함
                매수가 = float(self.exchange.price_to_precision(self.ticker, price_in))
            elif self.trade_market == 'KOSPI' or self.trade_market == 'KOSDAQ' or self.trade_market == 'ETF' or self.trade_market == 'ETF':
                매수가 = self.exchange.hogaPriceReturn_per(self.trade_market,self.ticker, price_in, 0)
            elif self.trade_market == '선물' or self.trade_market == '옵션':
                매수가 = self.exchange.hogaPriceReturn_per(self.trade_market,self.ticker, price_in, 0)
        if 매수가 == None:
            raise print('가격 확인')
        return 매수가
    # def order_buy(self):

    def chegyeol_buy(self, 매수, 매수가, 잔고, row_tik):
        상태 = '매수'
        if 매수 == None:
            raise f'chegyeol_buy: {매수= }'
        # 매수가 = 매수가 * self.거래승수
        if type(매수) == str:
            # 배팅금액 = 잔고 * (100 / 100) * self.leverage
            매수수량 = int(매수.replace('개', ''))
            매수금액 = 매수수량 * (매수가* self.거래승수)
            배팅금액 = 매수금액
            if 잔고*self.leverage < 매수금액:
                err = True
            else:
                err = False
        else:
            배팅금액 = 잔고 * (매수 / 100) * self.leverage
            매수수량 = 배팅금액 // (매수가* self.거래승수)
            매수금액 = 매수수량 * (매수가* self.거래승수)
            if self.trade_market == '선물' or self.market == '국내주식':
                if 매수수량 < 1:
                    err = True
                else:
                    err = False
            else:
                if 매수수량 * 매수가 < 50: #bybit 인데 50불 이하일 경우 에러
                    err = True
                else:
                    err = False
        # print(f"chegyeol_buy {매수수량=}   {매수금액=}   {매수가=}   {잔고=}  {배팅금액=}")
        if err:
#             print(f'(선물) 매수 할 자금 부족: {잔고=}  {매수=}   {매수수량=}   {매수가=}  '
#                   f'{self.leverage=}  {매수가=}  {self.거래승수=}')
            자산 = 잔고
            상태 = {"종료":"매수자금부족","자산":자산,"매수":매수,"매수가":매수가,"매수수량":매수수량, "idx":row_tik}
            self.매수수수료 = 0
            self.asset[row_tik] = 자산
            self._status = False

        else:
            # 매수금액 = 매수수량 * 계약당필요현금
            self.매수수수료 = round((매수금액 * self.fee) / 100, 2)
            # self.매수수수료 = 매수금액 * self.fee // 100
            잔고 = 잔고 - (매수금액/self.leverage) - self.매수수수료
            자산 = 잔고 + (매수금액/self.leverage)
#             print(f"chegyeol_buy: {row_tik= }  {잔고=}  {자산=}  {매수금액=}    {매수=}   {매수수량=}  {self.매수수수료=}  {매수가= } * "
#                   f"{self.leverage=}  {배팅금액=} {self.거래승수=}")

        최고수익률 = 0
        최저수익률 = 0

        self.buy[row_tik] = 매수가
        self.wallet[row_tik] = 잔고
        self.asset[row_tik] = 자산
        self.state[row_tik] = 상태
        self.hold_qty[row_tik] = 매수수량
        self.price_buy[row_tik] = 매수금액
        self.fee_paid[row_tik] = self.매수수수료

        # self.df.loc[self.df['데이터길이'] == 데이터길이, '매수가'] = 매수가
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '보유수량'] = 매수수량
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '매수금액'] = 매수금액
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '수수료'] = self.매수수수료

        # self.df.loc[self.df['데이터길이'] == 데이터길이, '매수수량'] = 매수수량
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '잔고'] = 잔고
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '자산'] = 자산
        print(f"chegyeol_buy  {현재시간=}  {매수=},  {잔고=}, {자산=}, {배팅금액=}, {매수가=}, {매수수량=}, {매수금액=}, {self.매수수수료=}")
        return 매수수량, 매수금액, 잔고, 자산, 최고수익률, 최저수익률, 상태

    def chegyeol_sell(self, 매도가,보유수량,매수금액,잔고,row_tik):
        매도금액 = (매도가 * self.거래승수) * 보유수량
        매도수수료 = round(매도금액 * self.fee / 100,1)
        if self.direction == 'long':
            수익금 = round(매도금액 - 매수금액 - self.매수수수료 - 매도수수료, 4)
            # 수익률 = round(((수익금 - self.매수수수료) / 매수금액 * 100) * self.leverage, 2)
        else:
            수익금 = round(매수금액 - 매도금액 - self.매수수수료 - 매도수수료, 4)
        수익률 = round((수익금 / 매수금액 * 100) * self.ror_leverage, 2)
        # print(f"chegyeol_sell {잔고= } {매도금액= } {수익금=} {self.매수수수료=} {매도수수료=} {매수금액/self.leverage=}")
        잔고 = round(잔고 + (매수금액/self.leverage) + 수익금,1)  ##매수수수료는 매수하면서 이미 냈음
        자산 = 잔고
        # if 현재시간 == datetime.datetime(2025,11,21,8,45,0):

            # 잔고 = round(잔고 + (매수금액 / self.leverage) + 수익금,4)  ##매수수수료는 매수하면서 이미 냈음
            # print(f"chegyeol_sell {자산= }   {매수금액=}   {self.매수수수료=}    {self.leverage= }   {(매수금액/self.leverage)}  {수익금=} {매도수수료=}")
            # quit()
        self.sell[row_tik] = 매도가
        self.wallet[row_tik] = 잔고
        self.asset[row_tik] = 자산
        self.state[row_tik] = '매도'
        self.ror[row_tik] = 수익률
        self.price_sell[row_tik] = 매도금액
        self.benefit[row_tik] = 수익금
        self.fee_paid[row_tik] = 매도수수료

#         self.df.loc[self.df['데이터길이'] == 데이터길이, '매도가'] = 매도가
#         self.df.loc[self.df['데이터길이'] == 데이터길이, '보유수량'] = 0
#         self.df.loc[self.df['데이터길이'] == 데이터길이, '매도금액'] = 매도금액
#         self.df.loc[self.df['데이터길이'] == 데이터길이, '수수료'] = 매도수수료

        # self.df.loc[self.df['데이터길이'] == 데이터길이, '수익률'] = 수익률
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '수수료'] = self.매수수수료 + 매도수수료
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '수익금'] = 수익금
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '잔고'] = 잔고
        # self.df.loc[self.df['데이터길이'] == 데이터길이, '자산'] = 자산
        return 수익률, 잔고, 자산

    def cal_ror(self, 상세고가, 상세저가, 상세종가, 매수수량, 매수금액, 잔고, 현최고수익률, 현최저수익률, row_tik):
        매도수수료 = 매수수량 * (상세종가 * self.거래승수) * self.fee / 100
        평가금액 = 매수수량 * (상세종가 * self.거래승수)
        최고평가금액 = 매수수량 * (상세고가 * self.거래승수)
        최저평가금액 = 매수수량 * (상세저가 * self.거래승수)
        if self.direction == 'long':
            수익금 = 평가금액 - 매수금액 - self.매수수수료 - 매도수수료
            최고수익금 = 최고평가금액 - 매수금액 - self.매수수수료 - 매도수수료
            최저수익금 = 최저평가금액 - 매수금액 - self.매수수수료 - 매도수수료
        else:
            수익금 = 매수금액 - 평가금액 - self.매수수수료 - 매도수수료
            최고수익금 = 매수금액 - 최고평가금액 - self.매수수수료 - 매도수수료
            최저수익금 = 매수금액 - 최저평가금액 - self.매수수수료 - 매도수수료

        수익률 = round((수익금 / 매수금액 * 100) * self.ror_leverage, 2) #레버리지를 곱해야하나
        최고수익률 = round((최고수익금/ 매수금액 * 100) * self.ror_leverage, 2)
        최저수익률 = round((최저수익금 / 매수금액 * 100) * self.ror_leverage, 2)

        self.ror_max[row_tik] = float(np.where(최고수익률 > 현최고수익률, 최고수익률, 현최고수익률))
        self.ror_min[row_tik] = float(np.where(최저수익률 < 현최저수익률, 최저수익률, 현최저수익률))
        자산 = round(잔고 + (매수금액/self.leverage) + 수익금,4)
        self.ror[row_tik] = 수익률
        self.wallet[row_tik] = 잔고
        self.asset[row_tik] = 자산
        self.benefit[row_tik] = 수익금
        # print(f"cal_ror: {현재시간} {row_tik= }| {수익률= } | {수익금= } | {매수금액=} | {평가금액=} | {self.매수수수료=} | {매도수수료}  | {잔고=}  {자산=} {이평100N(1)}{이평200N(1)}")
        # quit()
        # if 현재시간 == 종료시간: #종료시간은 장 종료시간이 아닌 분봉에대한 종료시간
        #     self.df.loc[self.df['데이터길이'] == 데이터길이, '잔고'] = 잔고
        #     self.df.loc[self.df['데이터길이'] == 데이터길이, '자산'] = 자산
        #     self.df.loc[self.df['데이터길이'] == 데이터길이, '수익률'] = 수익률
        #     self.df.loc[self.df['데이터길이'] == 데이터길이, '수익금'] = 수익금
        #     self.df.loc[self.df['데이터길이'] == 데이터길이, '최고수익률'] = 최고수익률
        #     self.df.loc[self.df['데이터길이'] == 데이터길이, '최저수익률'] = 최저수익률

        return 수익률, self.ror_max[row_tik], self.ror_min[row_tik]

    # 백테스트용 DF를 만들때는 전체 날짜를 만들지만 나중에 잘라서 쓸 수 있음
    # 때문에 날짜를 처음부터 테스트 하는게 아니라면 데이터길이가 들어가는 변수의 경우 데이터길이 값을 변경해줘야 함.
    def reset_data_lenth(self,df):
        li_col = df.columns.tolist()
        # print('==============='*5)
        for col in li_col:
            if '데이터길이' in col:
                # num = df[col][0]
                # print(df[col][0])
                num = df[col].tolist()[0]
                # print(df[col].tolist()[0])
                if num != 1:
                    df[col] = df[col]-(num-1)
                    # print(df)
        return df
    def make_vars(self,row_tik):
        for i,col in enumerate(li_detail_col):  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
            globals()[f'{col}'] = np_detail_ar[row_tik][i]  #아래보다 이게 약간 빠름
            # globals()[f'{col}'] = np_tik[row_tik][li_detail_col.index(f'{col}')]

    def active_light(self):
        self.signal_light.emit(self.bool_light)
        self.bool_light = not self.bool_light
    def signal_dict_state(self,현재시간):
        self.dict_state['현재시간'] = 현재시간
        self.signal_state.emit(self.dict_state)
    def cal_df(self, df):
        # df['매수가'] = df['매수가'].astype(float)
        # df['매도가'] = df['매도가'].astype(float)
        # df['보유수량'] = df['보유수량'].astype(float)

        # 방법 1: groupby + last() 사용
        grouped_last = self.df_detail.groupby('데이터길이')['매수가'].last()
        df['매수가'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['매도가'].last()
        df['매도가'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['매수금액'].last()
        df['매수금액'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['매도금액'].last()
        df['매도금액'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['수익금'].last()
        df['수익금'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['보유수량'].last()
        df['보유수량'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['수익률'].last()
        df['수익률'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['최고수익률'].last()
        df['최고수익률'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['최저수익률'].last()
        df['최저수익률'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['수익금'].last()
        df['수익금'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['잔고'].last()
        df['잔고'] = df['데이터길이'].map(grouped_last)
        grouped_last = self.df_detail.groupby('데이터길이')['자산'].last()
        df['자산'] = df['데이터길이'].map(grouped_last)
        df['자산'][-1] = self.df_detail['자산'][-1]
        df['잔고'][-1] = self.df_detail['잔고'][-1]

        df['holding'] = (df['종가'] - df['시가'][0]) / df['시가'][0] * 100
        # df['holding'] = int(self.bet) + (df['ror'] * int(self.bet))
        # df['holding'] = df['holding'] / df['holding'][0]
        df['DD'] = round(df['자산'] / df['자산'].cummax() - 1, 2)
        df['MDD'] = round(df['DD'].cummin(), 2)
        df['전략수익률'] = (df['자산'] - self.bet) / self.bet * 100
        return df
    def finish_df(self,length_index,start_time,상태):
        self._status = False
        print(f'backtest 걸린시간: {(time.time() - start_time)}   {상태= }  {self._status= }')
        # self.df['잔고'] = self.df['잔고'].ffill()
        # self.df['자산'] = self.df['자산'].ffill()
        buy_count = np.count_nonzero(~np.isnan(self.buy)) #넘파이에서 nan이 아닌 갯수를 확인해서 매수횟수로
        if buy_count == 0:
            print('잔고 변함 없음 매수 0 회')
            self.signal_message.emit('알람', '잔고 변함 없음 매수 0 회')
        else:
            if type(상태) == dict:
                if 상태['종료'] == '매수자금부족':
                    self.signal_message.emit('에러', '매수 할 자금이 부족 합니다.')
                else:
                    self.signal_message.emit('에러', f'매수 할 수 없습니다. {상태=}')
            elif self._status and length_index != row_tik+1:  # 백테스트가 다 돌아가지 않고 중간에 종료될 경우
                print(f"{row_tik= }")
                print(f"{length_index= }")
                print('중간에 종료')
                self.check_db(row_tik)
            else:
                pprint(f"{상태= }")
                if type(상태) == dict:
                    if 상태['종료'] == '매수자금부족':
                        self.dict_state['상태'] = "매수자금부족."
                        self.signal_state.emit(self.dict_state)
            ################################################################# self.df_detail
            st = time.time()
            self.df_detail['매수주문가'] = self.buy_order
            self.df_detail['매수가'] = self.buy
            self.df_detail['매도주문가'] = self.sell_order
            self.df_detail['매도가'] = self.sell
            self.df_detail['보유수량'] = self.hold_qty
            self.df_detail['수수료'] = self.fee_paid
            self.df_detail['수익률'] = self.ror
            self.df_detail['최고수익률'] = self.ror_max
            self.df_detail['최저수익률'] = self.ror_min
            self.df_detail['상태'] = self.state
            self.df_detail['수익금'] = self.benefit
            self.df_detail['잔고'] = self.wallet
            # self.df_detail['전략수익률'] = self.ror_strategy
            self.df_detail['매수금액'] = self.price_buy
            self.df_detail['매도금액'] = self.price_sell
            self.df_detail['자산'] = self.asset
            # self.df_detail['매수횟수'] = self.buy_count
            self.df_detail['val'] = self.val
            self.df_detail['val_k'] = self.val_k
            if type(상태) == dict:
                if 상태['종료'] == '매수자금부족':
                    self.df_detail = self.df_detail[:상태['idx']]
            #################################################################

            # self.df.rename(columns={'자산': 'strategy'},inplace=True)

            df = self.cal_df(self.df)
            # common_def.export_sql(df,'DB/bt.db','df')
            # common_def.export_sql(self.df_detail,'DB/bt.db','detail')

            idx_final = self.df_detail.index[-1]
            df = df.loc[:idx_final]


            # df.index.rename('index', inplace=True)  # 인덱스명 변경
            self.signal_df.emit(df,self.df_detail)
    def check_db(self,row_tik):
        print('*************************************** check_db ***************************************')
        self.df_detail['매수주문가'] = self.buy_order
        self.df_detail['매수가'] = self.buy
        self.df_detail['매도주문가'] = self.sell_order
        self.df_detail['매도가'] = self.sell
        self.df_detail['보유수량'] = self.hold_qty
        self.df_detail['수수료'] = self.fee_paid
        self.df_detail['수익률'] = self.ror
        self.df_detail['최고수익률'] = self.ror_max
        self.df_detail['최저수익률'] = self.ror_min
        self.df_detail['상태'] = self.state
        self.df_detail['수익금'] = self.benefit
        self.df_detail['잔고'] = self.wallet
        self.df_detail['매수금액'] = self.price_buy
        self.df_detail['매도금액'] = self.price_sell
        self.df_detail['자산'] = self.asset
        self.df_detail['val'] = self.val
        self.df_detail['val_k'] = self.val_k
        ddf = self.df_detail[:row_tik+10] #데이터가 너무 많기 때문에 입력받은 row_tik의 +5 까지만 저장하거나 잔고가 nan이 아니행만 갖고와서 저장
        # ddf = self.df_detail[~np.isnan(self.df_detail['잔고'])]  # 조건 행 삭제 (잔고가 nan이 아닌행만 갖고오기)
        if np.nan in ddf['잔고'].tolist():
            print(f"{ddf['잔고'].tolist()= }")
        # ddf['잔고'].fillna(method='ffill', inplace=True)
        # ddf['자산'].fillna(method='ffill', inplace=True)
        li = ['상세시가', '상세고가', '상세저가', '상세종가', '시가', '고가', '저가', '종가', '거래량',
              '데이터길이', '장시작시간', '장종료시간', '현재시간', '종료시간', '시분초']
        li_vars = ['매수주문가','매수가','매도주문가','매도가','상태']
        ddf = ddf[li + li_vars]
        common_def.export_sql(ddf,'DB/bt.db','df_detail')

        df = self.cal_df(self.df)
        li = ['시가', '고가', '저가', '종가', '거래량', '데이터길이', '매수가', '매도가', '보유수량', '수익률', '최고수익률',
              '최저수익률', '수익금', '전략수익률', '매수금액', '매도금액', '자산','잔고', '수수료', 'holding', 'DD', 'MDD']
        li_vars = ['이평20','거래량이평3','이격도20이평'] # 기준컬럼에서 추가되는 컬럼 (해당컬럼만 저장되도록)
        li_del_vars = ['보유수량', '수익률', '최고수익률','최저수익률','이격도20이평','holding', 'DD', 'MDD'] # 기준컬럼에서 추가되는 컬럼 (해당컬럼만 저장되도록)
        df = df[list(set(li + li_vars) - set(li_del_vars))]
        idx_final = self.df_detail.index[-1]
        df = df.loc[:idx_final]
        common_def.export_sql(df,'DB/bt.db','df')

    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self._status = False
        print(f"def stop(self):   {self._status=}")
        self.quit()
        # self.wait(3000)  # 3초 대기 (바로 안꺼질수도)
        self.signal_stop.emit()

import sys
import tab_chart_table
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QApplication, QTextEdit, QProgressBar, QMessageBox
class Window(QMainWindow): #별도로 실행하고자 할 때
    def __init__(self,df,df_detail,dict_info,chart_table):
        super().__init__()
        self.chart_table = chart_table
        self.QPB_start = QPushButton('시작')
        self.QTE_state = QTextEdit()
        self.QPB_bar = QProgressBar(self)
        self.df = df
        self.df_detail = df_detail
        self.dict_info = dict_info

        QW_main = QWidget()
        self.setCentralWidget(QW_main)
        StyleSheet_Qtextedit = "color: #B4B4B4; background-color: NightRider; selection-background-color: #B4B4B4;" \
                               "border-color: black; font: 14pt 나눔고딕; "
        self.QTE_state.setStyleSheet(StyleSheet_Qtextedit)
        QVB_main = QVBoxLayout()
        QVB_main.addWidget(self.QPB_start)
        QVB_main.addWidget(self.QTE_state)
        QVB_main.addWidget(self.QPB_bar)
        QW_main.setLayout(QVB_main)

        self.QPB_start.clicked.connect(self.do_backtest)
        self.do_backtest()
    def do_backtest(self):
        self.thread_make = backtest_np(self,self.df,self.df_detail,self.dict_info)
        self.thread_make.start()
        self.thread_make.signal_bar.connect(self.progress_loading)
        self.thread_make.signal_state.connect(self.state_bt)
        self.thread_make.signal_light.connect(self.effect_start)
        self.thread_make.signal_df.connect(self.show_chart)
        self.thread_make.signal_message.connect(self.put_message)

    def progress_loading(self, val):
        self.QPB_bar.setValue(val)
    def state_bt(self, state):
        txt = ''
        for key, value in state.items():
            txt += f'{key}: {value}, '
            # txt += f'{key}: {value}\n'
        self.QTE_state.setText(txt)
    def effect_start(self, light):
        if light == True:
            self.QPB_start.setStyleSheet("background-color: #fa3232;")
        if light == False:
            self.QPB_start.setStyleSheet("background-color: #cccccc;")
    def put_message(self,title,txt):
        QMessageBox.about(self, title, txt)
    def mapping(self, x, i_min, i_max, o_min, o_max):
        return (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # mapping()함수 정의.

    def compare_price(self, price, vars):
        i_min = price.min()  # 현재가.min
        i_max = price.max()
        return price.apply(self.mapping, args=(i_min, i_max, vars.min(), vars.max()))
    def result_chart(self, df):
        기간수익률 = df['자산'][-1] / df['자산'][0]
        delta = df.index[-1] - df.index[0]
        N = delta.days / 365
        연복리수익률 =  (기간수익률 ** (1 / N)) - 1

        # df['index'] = round(self.compare_price(df['종가'], df['전략수익률']), 2)
        # df_benefit = df[['MDD','DD']]
        buy_count = df['매수가'].count()
        df_profit = df.loc[df['매도금액'].notna()] #매도가열과 매도금액 열이 nan이 아닌행만
        common_def.export_sql(df,'DB/bt.db','df')
        common_def.export_sql(df_profit,'DB/bt.db','df_profit')
        win = len(df_profit.loc[df_profit['수익금'] > 0])  # 횟수
        lose = len(df_profit.loc[df_profit['수익금'] < 0])
        win_sum = df_profit.loc[df_profit['수익금'] > 0].수익금.sum()  # 금액
        loss_sum = df_profit.loc[df_profit['수익금'] < 0].수익금.sum()
        avg_profit = win_sum / win
        print(f"{loss_sum= }")
        print(f"{lose= }")
        if lose == 0:
            avg_loss = 0
        else:
            avg_loss = loss_sum / lose
        pov = win / buy_count * 100


        grid = GridSpec(4, 1, wspace=0.3, hspace=0.5)
        fig = plt.figure(figsize=(16, 9))

        ax1 = fig.add_subplot(grid[0:3, 0:1])
        ax2 = fig.add_subplot(grid[3:4, 0:1], sharex=ax1)

        market = self.dict_info['market']
        if market == 'bybit':
            x_range = df.index
        else:
            x_range = range(len(df))

        # 좌측 y축 (ax1) - index
        ax1.plot(x_range, df['종가'], label=f"{self.dict_info['ticker']} 종가", color='red')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.set_ylabel(f"'{self.dict_info['ticker']}'", color='red')
        ax1.legend(loc='upper right', shadow=True)  # 좌측 상단


        # 우측 y축 (ax1_right) - 전략수익률, holding
        ax1_right = ax1.twinx()
        ax1_right.plot(x_range, df['전략수익률'], label='전략수익률 %', color='orange')
        ax1_right.plot(x_range, df['holding'], label='holding %', color='green')
        ax1_right.set_ylabel('전략수익률 / Holding', color='red')
        ax1_right.tick_params(axis='y', labelcolor='black')
        ax1_right.legend(loc='upper right', shadow=True)  # 우측 상단

        # lines2, labels2 = ax1_right.get_legend_handles_labels()
        # ax1_right.legend(lines2, labels2, loc='upper right', ncol=1, shadow=True)

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
        self.배팅금액 = format(int(self.dict_info['bet']), ',')
        수익금 = round(df['자산'][-1]-int(self.dict_info['bet']))
        self.수익금 = format(수익금, ',')
        self.수익률 = round(수익금 / int(self.dict_info['bet']) * 100)
        self.연복리수익률 = round(연복리수익률*100, 1)
        self.거래횟수 = buy_count
        idx_day = df.index.astype(str).str[:10]
        거래일 = len(df.groupby(idx_day).size().index)
        self.일평균거래횟수 = round(buy_count / 거래일, 1)
        self.승률 = round(pov, 1)
        self.MDD = df['MDD'][-1].round(1)
        import math
        gcd = math.gcd(int(avg_profit), avg_loss) #최소공배수
        # 손익비 = f"{avg_profit // gcd}:{avg_loss // gcd}"

        low_nem = min(int(avg_profit), int(abs(avg_loss)))
        leng = len(str(low_nem)) - 1
        print(f"{leng}")
        leng = 10 ** leng
        손익비 = f"[ {round((int(avg_profit) // gcd) / leng, 1)} : {round(int(abs(avg_loss)) // gcd / leng, 1)} ]"

        # try:
        # plt.title(
        #     f"종목명: {self.dict_info['ticker']},  배팅금액{self.배팅금액},  매매기간: {self.dict_info['시작일']} ~ {self.dict_info['종료일']},  "
        #     f"봉: {self.dict_info['봉']},  총 수익금: {self.수익금} 원,  수익률: {self.수익률} %, 연복리수익률(CAGR): {self.연복리수익률} %,\n"
        #     f"거래횟수: {self.거래횟수},  일평균 거래횟수: {self.일평균거래횟수},  거래일: {거래일}  승률: {self.승률}%,  손익비: {손익비}%, "
        #     f"MDD: {self.MDD*100} %,  "
        #     f"TradingEdge: {round(pov * avg_profit - (1 - pov) * avg_loss)},  "
        #     f"P&L ration: {round((1 - pov) / pov, 1)} ")
        # except:
        plt.title(
            f"종목명: {self.dict_info['ticker']},  배팅금액{self.배팅금액},  매매기간: {self.dict_info['시작일'] + '~' + self.dict_info['종료일']},  "
            f"봉: {self.dict_info['봉']},  총 수익금: {self.수익금} 원,  수익률: {self.수익률} %, 연복리수익률(CAGR): {self.연복리수익률} %,\n"
            f"거래횟수: {self.거래횟수},  일평균 거래횟수: {self.일평균거래횟수},  거래일: {거래일}  승률: {self.승률}%,  손익비: {손익비}, "
            f"MDD: {self.MDD*100} %,  "
            f"TradingEdge: {round(pov * avg_profit - (1 - pov) * avg_loss)},  "
            f"P&L ration: {round((1 - pov) / pov, 1)} ")
        # df_nan = df.loc[np.isnan(df['strategy'])]
        # plt.title(
        #     f"배팅금액{format(int(self.dict_info['bet']), ',')}  총 수익금: 청산  거래횟수: {buy_count}  승률: {round(pov, 1)}%,"
        #     # f"청산일: {df_nan.index[0]}"
        #     )
        plt.legend()
        plt.show()
        self.plt = plt
    def show_chart(self,df,df_detail):
        # 데이터타입이 object 이거나 전부 nan으로 되어있는열이 있으면 에러발생하기 때문에 그런열은 삭제 해줘야 됨
        # dtype이 object인 열 이름 추출
        object_columns = df.select_dtypes(include='object').columns.tolist()
        if object_columns:
            for del_col in object_columns:
                df.drop(del_col, axis=1, inplace=True)
        # start_day = datetime.datetime.strftime(df.index[0], '%Y-%m-%d')
        # df_chart_table = self.chart_table.input(df, self.dict_info['market'])
        self.chart_table.impo_table(df,self.dict_info['market'])
        self.chart_table.chart_show(self.dict_info['market'], self.dict_info['ticker'])
        self.result_chart(df)

        li = ['시가', '고가', '저가', '종가', '거래량', '데이터길이', '매수가', '매도가', '보유수량', '수익률', '최고수익률',
              '최저수익률', '수익금', '전략수익률', '매수금액', '매도금액', '자산','잔고', '수수료', 'holding', 'DD', 'MDD']
        li_vars = ['이평100','이평200'] # 기준컬럼에서 추가되는 컬럼 (해당컬럼만 저장되도록)
        df = df[li+li_vars]
        # common_def.export_sql(df,'DB/bt.db','backtest')
        li = ['상세시가', '상세고가', '상세저가', '상세종가',
              '시가', '고가', '저가', '종가', '거래량', '데이터길이', '장시작시간', '장종료시간', '현재시간', '종료시간',
              '시분초','매수주문가', '매수가', '매도주문가', '매도가', '보유수량', '수수료', '수익률', '최고수익률', '최저수익률',
              '상태', '수익금', '잔고','매수금액','매도금액','자산','val','val_k']
        li_vars = []
        df_detail = df_detail[li+li_vars]
#         common_def.export_sql(df_detail,'DB/bt.db','backtest_detail')

if __name__ == '__main__':
    import KIS
    market = '국내주식'
    stg_name_buy = '퀀트'
    stg_name_sell = '퀀트'
    conn = sqlite3.connect('DB/strategy.db')
    df_stg_buy = pd.read_sql(f"SELECT * FROM '{market}_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
    df_stg_sell = pd.read_sql(f"SELECT * FROM '{market}_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
    conn.close()
    try:
        stg_buy_text = df_stg_buy.loc[f'{stg_name_buy}','전략코드']
    except KeyError:
        print(f'매수 전략명 확인 {df_stg_buy.index.tolist()}')
        quit()
    try:
        stg_sell_text = df_stg_sell.loc[f'{stg_name_sell}','전략코드']
    except KeyError:
        print(f'매도 전략명 확인 {df_stg_sell.index.tolist()}')
        quit()
    stg_buy = common_def.replace_tabs_with_spaces(stg_buy_text)
    stg_sell = common_def.replace_tabs_with_spaces(stg_sell_text)
    print(stg_buy)
    print('============' * 5)
    locals_dict_buy = {}
    obj = stg_buy.split("\n", 1)[0]  # 첫줄 읽기 추출
    exec(obj, None, locals_dict_buy)
    obj = locals_dict_buy.get('진입대상')

    bong = stg_buy.split("\n", 2)[1]
    exec(bong, None, locals_dict_buy)
    bong = locals_dict_buy.get('봉')

    bet = stg_buy.split("\n", 3)[2]
    exec(bet, None, locals_dict_buy)
    bet = locals_dict_buy.get('초기자금')

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
    else:
        direction = 'long'
        증거금률 = 1
    locals_dict_sell = {}
    division_sell = stg_sell.split("\n", 1)[0]  # 첫줄 읽기 추출
    exec(division_sell, None, locals_dict_sell)
    division_sell = locals_dict_sell.get('분할매도')

    bong = list(bong.keys())[0]
    if type(obj) == dict:
        ticker = list(obj.keys())[0]
        val_range = list(obj.values())[0]
    else:
        ticker = obj
        val_range = None


    st = time.time()

    거래승수 = 1

    if market == 'bybit':
        trade_market = 'bybit'
        거래승수 = 1
        exchange,_ = common_def.make_exchange_bybit()
        fee = 0.055
    elif market == '국내주식':
        conn_DB = sqlite3.connect('DB/DB_stock.db')
        # stocks_info = pd.read_sql(f"SELECT * FROM 'stocks_info'", conn_DB).set_index('종목코드')
        trade_market = "KOSPI"
        거래승수 = 1
        fee = 0.018
        # fee_limit = 0.02
        exchange = KIS.KoreaInvestment(market='test')

    elif market == '국내선옵':
        conn_DB = sqlite3.connect('DB/DB_futopt.db')
        dic_multiplier = {'선물': 250000, '콜옵션': 250000, '풋옵션': 250000, '위클리_콜옵션': 250000, '위클리_풋옵션': 250000,
                          '2AF': 250000, '3AF': 250000,  # 코스피200
                          '미니선물': 50000, '205': 50000, '305': 50000,  # 미니코스피200
                          '코스닥선물': 10000, '206': 10000, '306': 10000,  # 코스닥150
                          }
        거래승수 = dic_multiplier[ticker]
        trade_market = '선물' if ticker.endswith('선물') else '옵션'
        fee = 0.01
        if trade_market == '선물':
            증거금률 = 10
        else:
            증거금률 = 100
        exchange = KIS.KoreaInvestment(market='test')
    else:
        conn_DB = ''
        stocks_info = pd.DataFrame()
        stg_buy_text = ''
        stg_sell_text = ''
        fee = 0.1


    frdate = '2025-09-01'
    todate = '2026-05-31'

    if obj == None or bong == None or bet == None:
        print('에러', f"전략확인 | {obj=} | {bong=} | {bet=}")
        quit()
    dict_DB_info = {'market': market, 'ticker': ticker, '봉': bong, '상세봉': '1분봉', 'bet': bet,
                 '시작일': frdate, '종료일': todate, 'stg_buy': stg_buy,'stg_sell': stg_sell,
                 'trade_market':trade_market, 'val_range':None,
                 '분할매수': division_buy, '분할매도': division_sell, 'direction':direction,'거래승수':거래승수,
                 '증거금률':증거금률,'exchange':exchange,'fee':fee}
    market,df,df_detail=common_def.get_df_detail(ticker,frdate,todate,bong)
    print(f"{bong= }")
    print(f"{bong= }")
    # common_def.export_sql(df,'DB/bt.db','df')
    # common_def.export_sql(df_detail[['상세시가','상세저가','시가','고가','저가','종가','데이터길이','종료시간']],'DB/bt.db','df_detail')
    # common_def.export_sql(df_detail,'DB/bt.db','df_detail')
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    # app = QApplication(sys.argv)
    app = QApplication([])

    main_table = Window(df,df_detail,dict_DB_info,tab_chart_table.Window())
    main_table.show()
    sys.exit(app.exec_())


