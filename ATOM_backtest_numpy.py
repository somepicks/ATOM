import sqlite3
import pandas as pd
import numpy as np
import datetime
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
import time
import talib
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
import ccxt
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex,pyqtSlot
from PyQt5.QtWidgets import QMessageBox

import KIS
from pprint import pprint
import common_def



def 구간최고시가(pre):
    if market == '코인':
        pp = row_tik - int(pre * bong_stamp/bong_detail_stamp)
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('시가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('시가')].max()
def 구간최저시가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('시가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('시가')].max()
def 구간최고고가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('고가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('고가')].max()
def 구간최저고가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('고가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('고가')].max()
def 구간최고저가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('저가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('저가')].max()
def 구간최저저가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('저가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('저가')].max()
def 구간최고종가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('조가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('종가')].max()
def 구간최저종가(pre):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp/bong_detail_stamp):,list_columns.index('조가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        idx = np.where(np_tik[:,list_columns.index('데이터길이')]==num-pre)[0][0] #데이터길이가 num-pre인 인덱스 추출
        return np_tik[idx:,list_columns.index('종가')].max()
def 구간최고시가N(pre,N): #이거는 다시 한번 봐야 됨
    if market == '코인':
        pre_len = row_tik - int(pre * bong_stamp / bong_detail_stamp)
        div = int(bong_stamp / bong_detail_stamp*N)
        return np_tik[pre_len-div:row_tik-div, list_columns.index('시가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('시가')].max()
def 구간최저시가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('시가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx = np.argmax(np_tik[:, list_columns.index('데이터길이')] == num - pre - N)
        end_idx = np.argmax(np_tik[:, list_columns.index('데이터길이')] == num - N+1)
        return np_tik[first_idx:end_idx, list_columns.index('시가')].min()
def 구간최고고가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('고가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('고가')].max()
def 구간최저고가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('고가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('고가')].min()
def 구간최고저가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('저가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('저가')].max()
def 구간최저저가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('저가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('저가')].min()
def 구간최고종가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('종가')].max()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('종가')].max()
def 구간최저종가N(pre,N):
    if market == '코인':
        return np_tik[row_tik - int(pre * bong_stamp / bong_detail_stamp)-int(bong_stamp / bong_detail_stamp*N):row_tik-int(bong_stamp / bong_detail_stamp*N), list_columns.index('종가')].min()
    else:
        num = np_tik[row_tik, list_columns.index('데이터길이')]  # 현재 데이터길이 값 갖고오기
        first_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-pre-N)
        end_idx=np.argmax(np_tik[:,list_columns.index('데이터길이')]==num-N+1)
        return np_tik[first_idx:end_idx,list_columns.index('종가')].min()

def 시가CN(bong,pre):
    if market == '코인':
        return np_tik_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), list_columns.index(f'시가_{bong}')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, list_columns.index(f'데이터길이_{bong}')] == num - pre][0][list_columns.index(f'시가_{bong}')]

def 고가CN(bong,pre):
    if market == '코인':
        return np_tik_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), list_columns.index(f'고가_{bong}')]
    else:
        num = np_tik[row_tik, list_columns.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, list_columns.index(f'데이터길이_{bong}')] == num - pre][0][list_columns.index(f'고가_{bong}')]
def 저가CN(bong,pre):
    if market == '코인':
        return np_tik_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), list_columns.index(f'저가_{bong}')]
    else:
        num = np_tik[row_tik, list_columns.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, list_columns.index(f'데이터길이_{bong}')] == num - pre][0][list_columns.index(f'저가_{bong}')]
def 종가CN(bong,pre):
    if market == '코인':
        return np_tik_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), list_columns.index(f'종가_{bong}')]
    else:
        num = np_tik[row_tik, list_columns.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, list_columns.index(f'데이터길이_{bong}')] == num - pre][0][list_columns.index(f'종가_{bong}')]
def 이평20CN(bong,pre):
    if market == '코인':
        return np_tik_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), list_columns.index(f'이평20_{bong}')]
    else:
        num = np_tik[row_tik, list_columns.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, list_columns.index(f'데이터길이_{bong}')] == num - pre][0][list_columns.index(f'이평20_{bong}')]
def 이평60CN(bong,pre):
    if market == '코인':
        return np_tik_ar[row_tik - int(dict_bong_stamp[bong]/bong_detail_stamp*pre), list_columns.index(f'이평60_{bong}')]
    else:
        num = np_tik[row_tik, list_columns.index(f'데이터길이_{bong}')]  # df에서 인덱스순서를 갖고오기
        return np_tik[np_tik[:, list_columns.index(f'데이터길이_{bong}')] == num - pre][0][list_columns.index(f'이평60_{bong}')]


# np_tik이나 np_tik_ar로 돌리는거보다 np_df_tik이 더 빠름
def 시가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('시가')]
    else: #국내시장일 경우(일봉)
        # 빠름
        # np_date = np_tik_idx[row_tik].astype('datetime64[D]')  # 디테일에서 날짜를 추출하기
        # num = np.argmax(np_df_idx_date == np_tik_idx[row_tik].astype('datetime64[D]') )  # df에서 인덱스순서를 갖고오기
        # return np_df_tik[num - pre, np.argmax(np_df_col == '시가')]  # df에서 데이터를 갖고오기

        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'시가')]

def 고가N(pre):
    if 데이터길이 <= pre: return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('고가')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'시가')]
def 저가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('저가')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'저가')]
def 종가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('종가')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'종가')]
def 이평5N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('이평5')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'이평5')]
def 이평20N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('이평20')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'이평20')]
def 이평60N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('이평60')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'이평60')]
def 이평120N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('이평120')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'이평120')]
def 이평240N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('이평240')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'이평240')]
def 거래량N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'거래량')]
def 거래량이평3N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량이평3')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'거래량이평3')]
def 거래량이평20N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량이평20')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'거래량이평20')]
def 거래량이평60N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('거래량이평60')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'거래량이평60')]
def RSI14N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('RSI14')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'RSI14')]
def RSI18N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('RSI18')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'RSI18')]
def RSI30N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('RSI30')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'RSI30')]
def ATRN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('ATR')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'ATR')]
def TRANGEN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('TRANGE')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'TRANGE')]
def 이격도20이평N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('이격도20이평')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'이격도20이평')]
def 밴드상N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('밴드상')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'밴드상')]
def 밴드중N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('밴드중')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'밴드중')]
def 밴드하N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('밴드하')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'밴드하')]
def MACDN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('MACD')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'MACD')]
def MACD_SIGNALN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('MACD_SIGNAL')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'MACD_SIGNAL')]
def MACD_HISTN(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('MACD_HIST')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'MACD_HIST')]
def 등락율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('등락율')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'등락율')]
def 변화율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('변화율')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'변화율')]
def 수익율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('수익율')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'수익율')]
def 고저평균대비등락율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('고저평균대비등락율')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'고저평균대비등락율')]
def 당일거래대금N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('당일거래대금')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'당일거래대금')]
def 종료시간N(pre):
    if 데이터길이 <= pre:
        return np.nan
    if market == '코인':
        return np_tik_ar[row_tik - int(pre * bong_stamp/bong_detail_stamp), list_columns.index('종료시간')]
    else:
        num = np_tik[row_tik,list_columns.index(f'데이터길이')]
        return np_tik[np.argmax(np_tik_length == num-pre), list_columns.index(f'종료시간')]

def moving_average(np_arry, w):
    return np.convolve(np_arry, np.ones(w), 'valid') / w

def 이평(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('종가')]/pre
# def 전일비각도(pre):
#     print('전일비각도')
#     try:
#         jvp_gap = 전일비 - np_tik[-(pre), list_columns.index('전일비')]
#         return round(math.atan2(jvp_gap, pre) / (2 * math.pi) * 360, 2)
#     except:
#         print('에러')
#         return 0
#
#
# def 거래대금각도(pre):
#     print('당일거래대금각도')
#     try:
#         dmp_gap = 당일거래대금 - np_tik[-(pre), list_columns.index('당일거래대금')]
#         return round(math.atan2(dmp_gap, pre) / (2 * math.pi) * 360, 2)
#     except:
#         return 0

class backtest_np(QThread):
    val_df = pyqtSignal(pd.DataFrame)
    # val_dict_result = pyqtSignal(dict)
    val_bar = pyqtSignal(int)
    val_state = pyqtSignal(dict)

    def __init__(self, parent, df, df_detail, dict_info):
        super().__init__(parent)
    # def __init__(self,df,df_detail,dict_info):
    #     super().__init__()

        # self.mutex = QMutex()
        self.market = dict_info['market']
        self.exchange = dict_info['exchange']
        self.stg_buy = dict_info['stg_buy']
        self.stg_sell = dict_info['stg_sell']
        self.bet = dict_info['bet']
        self.bong = dict_info['bong']
        self.bong_detail = dict_info['bong_detail']
        # self.conn_DB = dict_info['connect']
        self.dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                           '주봉': 10080}
        # self.dic_multiplier = {'101':250000,'201':250000,'301':250000, #코스피200
        #                        '105':50000,'205':50000,'305':50000, #미니코스피200
        #                        '106': 10000, '206': 10000, '306': 10000, #코스닥150
        #                        }

        self.trade_market = dict_info['trade_market']
        self.direction = dict_info['direction']
        self.거래승수 = dict_info['거래승수']
        self.레버리지 = dict_info['증거금률']
        if self.trade_market == 'bybit':
            self.ticker = dict_info['ticker']+'USDT'
            self.exchange.fetch_tickers() #바이비트의 경우 한번 해줘야 에러가 안남
        else:
            self.ticker = dict_info['ticker']
        self.fee_krx = 0.015
        self.tax_krx = 0.018
        self.fee_limit = 0.02
        self.fee_market = 0.055
        self.fee_furure = 0.01
        self.위탁증거금률 = 10    # 선물 위탁증거금률 = 10%
        self.df = df
        df_detail = self.reset_data_lenth(df_detail)
        self.df_detail = df_detail
        self.count = 0
        self._status = True

    def run(self):
        global np_tik_ar
        global row_tik
        global list_columns
        global np_tik
        global np_tik_idx
        global np_df_tik
        global np_df_idx_date
        global np_df_col
        global np_tik_length
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
        global bong_detail_stamp
        global 롱, long, 숏, short
        global 시가, 고가, 저가, 종가
        global 분봉1, 분봉3, 분봉5, 분봉15, 분봉30, 시간봉4, 일봉, 주봉, 월봉
        # 분봉1 = '1분봉'
        # 분봉3 = '3분봉' # 시가CN(bong,pre) bong자리에 넣기 위함 변수로 숫자가 앞에 올 수는 없기 때문
        # 분봉5 = '5분봉'
        # 분봉15 = '15분봉'
        # 분봉30 = '30분봉'
        # 시간봉4 = '4시간봉'
        # 일봉 = '일봉'
        # 주봉 = '주봉'
        # 월봉 = '월봉'
        롱 = 'long'
        long = 'long'
        숏 = 'short'
        short = 'short'
        시장가 = '시장가'

        bong_stamp = self.dict_bong_stamp[self.bong]
        bong_detail_stamp = self.dict_bong_stamp[self.bong_detail]
        start_time = time.time()

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
        self.ror_strategy = [np.nan for x in range(len(self.df_detail.index))]  # 전략수익률
        self.benefit = [np.nan for x in range(len(self.df_detail.index))]  # 수익금
        self.wallet = [np.nan for x in range(len(self.df_detail.index))]  # 잔고
        self.asset = [np.nan for x in range(len(self.df_detail.index))]  # 잔고
        self.qty = [np.nan for x in range(len(self.df_detail.index))]  # 보유수량
        self.fee_sum = [np.nan for x in range(len(self.df_detail.index))]  # 수수료
        self.price_buy = [np.nan for x in range(len(self.df_detail.index))]  # 총매수금액
        self.price_sell = [np.nan for x in range(len(self.df_detail.index))]  # 총매도금액
        self.numbers = [np.nan for x in range(len(self.df_detail.index))]  # 총매도금액
        self.val = [np.nan for x in range(len(self.df_detail.index))]  # test
        self.val_k = [np.nan for x in range(len(self.df_detail.index))]  # test
        잔고 = self.bet
        자산 = self.bet
        self.df.loc[self.df['데이터길이'] == 1, '잔고'] = 잔고
        self.df.loc[self.df['데이터길이'] == 1, '자산'] = 자산
        market = self.market

        np_df_tik = self.df.to_numpy()
        np_df_idx_date = self.df.index.normalize().to_numpy() #시간무시하고 날짜만 갖고오기
        np_df_col = self.df.columns.to_numpy()

        np_tik_ar = self.df_detail.to_numpy()  # 전체 데이터를 np로 저장
        np_tik_idx = self.df_detail.index.to_numpy()  # 인덱스를 np로 저장
        np_tik_length = self.df_detail['데이터길이'].to_numpy()  # 전체 데이터를 np로 저장
        list_columns = self.df_detail.columns.tolist()  # 컬럼명을 리스트로 저장
        # self.df_detail.drop('종료시간',axis=1,inplace=True)
        length_index = len(self.df_detail.index)
        row_tik = 0
        old_row_tik = 0
        numbers = 0
        bong_stamp = self.dict_bong_stamp[self.bong]
        bong_detail_stamp = self.dict_bong_stamp[self.bong_detail]
        dict_state = {'상태':'대기','잔고':잔고,'수익률':0,'수익금':0}
        self.val_state.emit(dict_state)

        while self._status and row_tik < length_index:
            # for row_tik in range(len(self.df_detail.index)):
            # np_tik = np_tik_ar[:row_tik + 1]
            # for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
            #     globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
            # 현재가 = 상세시가
            if 상태 == '대기': #미 보유 시 진입 주문
                while row_tik < length_index :
                    self.wallet[row_tik] = 잔고
                    self.asset[row_tik] = 자산
                    self.state[row_tik] = 상태
                    # print(f"{상태=}   {row_tik= }  {데이터길이= }   {종가N(1)= }")
                    np_tik = np_tik_ar[:row_tik + 1]
                    for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                        globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
                    현재가 = 상세시가
                    # 매수 = False
                    locals_dict_buy = {}
                    exec(self.stg_buy, None, locals_dict_buy)
                    매수 = locals_dict_buy.get('매수')
                    # if 현재시간.date() == date(2019,3,27):
                    # if 현재시간 == datetime(2024,7,2,15,20,0):
                    #     print(f"{현재시간= } | {시가= }, {시가N(2)= }")
                    #     quit()
                    if not 매수 == False:  # 매수 일 경우 None을 반환하기 때문에(매수신호 떳을 때)
                        # print(f"{현재시간}  {구간최고시가N(10, 1)} <= {종가N(1)}")
                        상태 = '매수주문'
                        진입주문가 = locals_dict_buy.get('매수가')
                        매수가 = self.order_price(진입주문가,상세시가,'매수주문')
                        self.buy_order[row_tik] = 매수가
                        self.state[row_tik] = 상태
                        break
                    row_tik += 1
                    self.val_bar.emit(round(row_tik / length_index * 100))
            if 상태 == '매수주문':  # 매수 체결 확인
                if (self.direction == 'long' and 매수가 >= 저가) or (self.direction == 'short' and 매수가 <= 고가):
                    # while self.minute_check.isChecked():
                    while True:
                        np_tik = np_tik_ar[:row_tik + 1]
                        for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                            globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
                        # print(f"{종료시간= }")
                        # print(f"{현재시간= }")
                        # print(f"{매수= }")
                        if 상세저가 <= 매수가 and 매수가 <= 상세고가: #롱이던 숏이던 상세 진입구간을 알고싶은거기 때문에 무관함,
                            slippage = 0.1  # 슬리피지 0.1 %
                            if self.direction == 'long' and 매수가 > 상세고가 : #롱일경우 매수가가 저가보다 낮을 수 없음 (시장가 슬리피지일 경우 감안하여 저가로)
                                매수가 = 상세고가
                                # 가격 = 상세고가 + (slippage / 100 * 상세고가)
                                # if self.trade_market == 'bybit':
                                #     매수가 = float(self.exchange.price_to_precision(self.ticker, 가격))
                                # elif self.trade_market == '선물':
                                #     매수가 = self.exchange.hogaPriceReturn_per(가격, 0, self.ticker)
                            elif self.direction == 'short' and 매수가 < 상세저가 :
                                매수가 = 상세저가
                                # 가격 = 상세저가 - (slippage / 100 * 상세저가)
                                # if self.trade_market == 'bybit':
                                #     매수가 = float(self.exchange.price_to_precision(self.ticker, 가격))
                                # elif self.trade_market == '선물':
                                #     매수가 = self.exchange.hogaPriceReturn_per(가격, 0, self.ticker)
                            매수수량, 매수금액, 잔고, 자산, 매수금액, 매수수수료, 최고수익률, 최저수익률, 상태 = \
                                self.chegyeol_buy(매수, 매수가, 잔고, row_tik)
                            numbers += 1
                            self.numbers[row_tik] = numbers
                            break
                        elif 현재시간 >= 종료시간: #long일경우 매수가>저가 이지만 상세로 보면 이미 지나버린 시점일 수 있음에 유의
                            상태 = '대기'
                            self.wallet[row_tik] = 잔고
                            self.asset[row_tik] = 자산
                            self.buy_order[row_tik] = 매수가
                            self.state[row_tik] = '매수 안됨 상태 매도 전환'
                            row_tik += 1
                            break
                        self.wallet[row_tik] = 잔고
                        self.asset[row_tik] = 자산
                        self.buy_order[row_tik] = 매수가
                        self.state[row_tik] = '매수 대기'
                        row_tik += 1
                    # if self.minute_check.isChecked() == False:
                    #     매수수량, 매수금액, 잔고, 자산, 매수금액, 매수수수료, 최고수익률, 최저수익률, 상태 = self.chegyeol_buy(매수, 매수가, 레버리지, 잔고, row_tik)

                else: # 미체결 시
                    # if self.minute_check.isChecked() == True:
                    # pprint(np_tik_idx)
                    # print(f"{종료시간=}    {type(종료시간)=}   {type(장시작시간)=}   {type(장종료시간)=}   {type(현재시간)=}     {type(np_tik_idx[0])=}     {type(np_tik_idx[0])=}")
                    row_tik_old = row_tik
                    idx_num = np.where(np_tik_idx==종료시간)  #idx_num[0].size      np.argmax로 해도 됨
                    # idx_num = np.argmax(np_tik_idx==종료시간)
                    if idx_num[0].size == 0 : #넘파이가 비어있을 경우(row_tik이 마지막행까지 갔을 경우)
                        상태 = '종료'
                        self.wallet[row_tik_old:length_index] = [잔고 for x in range(length_index - row_tik_old)]
                        self.asset[row_tik_old:length_index] = [자산 for x in range(length_index - row_tik_old)]
                        self.state[row_tik_old:length_index] = ['종료' for x in range(length_index - row_tik_old)]
                        break
                    row_tik = (idx_num[0][0])    #시간절약을위해 매수주문 후 큰 범위에서 매수가 안되면 건너뛰기
                    self.wallet[row_tik_old:row_tik+1] = [잔고 for x in range(row_tik+1-row_tik_old)]
                    self.asset[row_tik_old:row_tik+1] = [자산 for x in range(row_tik+1-row_tik_old)]
                    self.buy_order[row_tik_old:row_tik+1] = [매수가 for x in range(row_tik+1-row_tik_old)]
                    self.state[row_tik_old:row_tik+1] = ['매수 미 체결' for x in range(row_tik+1-row_tik_old)]
                    self.buy[row_tik_old] = '매수주문'
                    상태 = '대기'
                    row_tik += 1

                    # else:
                    #     self.wallet[row_tik] = 잔고
                    #     self.asset[row_tik] = 자산
                    #     self.state[row_tik] = '매수 미 체결'
                    #     상태 = '대기'
                    #     row_tik += 1


            while 상태 == '매수':  # 매수상태일 때
                # st = time.time()
                np_tik = np_tik_ar[:row_tik + 1]
                for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                    try:
                        globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
                    except:
                        print(f"{row_tik= }")
                        globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
                수익률, 최고수익률, 최저수익률 = self.cal_ror(상세고가, 상세저가, 상세종가, 매수수량, 매수금액, 잔고, 최고수익률, 최저수익률, row_tik)
                locals_dict_sell = {}
                exec(self.stg_sell, None, locals_dict_sell)
                매도 = locals_dict_sell.get('매도')

                self.wallet[row_tik] = 잔고
                self.asset[row_tik] = 자산
                # if 현재시간.date() == date(2022, 8, 22):  # <class 'pandas._libs.tslibs.timestamps.Timestamp'> 타입 비교
                #     print(f'{현재시간} {상태=}')
                if 매도 == True:
                    상태 = '매도주문'
                    청산주문가 = locals_dict_sell.get('매도가')
                    매도가 = self.order_price(청산주문가,상세시가,'매도주문')
                    self.sell_order[row_tik] = 매도가
                    self.state[row_tik] = 상태
                    # if 현재시간.date() == date(2022, 8,22):  # <class 'pandas._libs.tslibs.timestamps.Timestamp'> 타입 비교
                    #     print(현재시간.date(), '-', 매도)
                    break
                else:
                    self.state[row_tik] = 상태
                    row_tik += 1

            if 상태 == '매도주문':
                # if (self.direction == 'long' and 매도가 <= 고가) or (self.direction == 'short' and 매도가 >= 저가):
                # while self.minute_check.isChecked():
                while True:
                    np_tik = np_tik_ar[:row_tik + 1]
                    for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                        globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
                    # 상세시가, 상세고가, 상세저가, 상세종가, 상세거래량, 상세거래대금, 종료시간, 시작시간, 시가, 고가, 저가, 종가, 거래량, 거래대금, \
                    #     등락율, 변화율, 이평5, 이평20, 이평60, 이평120, 이평200, 거래량이평3, 거래량이평20, 거래량이평60, RSI14, RSI18, \
                    #     RSI30, ATR10, TRANGE, 이격도20이평, 밴드20상, 밴드20중, 밴드20하, 고저평균대비등락율, 데이터길이, 현재시간 = self.factors()

                    수익률, 최고수익률, 최저수익률 = self.cal_ror(상세고가, 상세저가, 상세종가, 매수수량, 매수금액, 잔고, 최고수익률, 최저수익률, row_tik)
                    if (self.direction == 'long' and 매도가 <= 상세고가) or (self.direction == 'short' and 매도가 >= 상세저가):
                        slippage = 0.1  # 슬리피지 0.1 %
                        # if 현재시간.date() == date(2022, 8, 22):  # <class 'pandas._libs.tslibs.timestamps.Timestamp'> 타입 비교
                        #     print('매도진입', 매도가)
                        if self.direction == 'long' and 매도가 < 상세저가 : #롱일경우 매도가가 저가보다 낮을 수 없음 (시장가 슬리피지일 경우 감안하여 저가로)
                            매도가 = 상세저가
                            # 가격 = 상세저가 - (slippage / 100 * 상세저가)
                            # if self.trade_market == 'bybit':
                            #     매도가 = float(self.exchange.price_to_precision(self.ticker, 가격))
                            # elif self.trade_market == '선물':
                            #     매도가 = self.exchange.hogaPriceReturn_per(가격, 0, self.ticker)
                        elif self.direction == 'short' and 매도가 > 상세고가 :
                            매도가 = 상세고가
                            # 가격 = 상세고가 + (slippage / 100 * 상세고가)
                            # if self.trade_market == 'bybit':
                            #     매도가 = float(self.exchange.price_to_precision(self.ticker, 가격))
                            # elif self.trade_market == '선물':
                            #     매도가 = self.exchange.hogaPriceReturn_per(가격, 0, self.ticker)
                        수익률, 잔고, 자산 = self.chegyeol_sell(매도가, 매수수량, 매수금액, 잔고, row_tik)
                        상태 = '대기'
                        row_tik_old = row_tik
                        idx_num = np.argmax(np_tik_idx == 종료시간)
                        self.wallet[row_tik_old+1:idx_num+1] = [잔고 for x in range(idx_num - row_tik_old)]
                        self.asset[row_tik_old+1:idx_num+1] = [자산 for x in range(idx_num - row_tik_old)]
                        self.state[row_tik_old+1:idx_num+1] = ['청산- 추가 매수 X' for x in range(idx_num - row_tik_old)]
                        row_tik = idx_num+1  # 시간절약을위해 매수주문 후 큰 범위에서 매수가 안되면 건너뛰기
                        break
                    elif 현재시간 >= 종료시간: #long일경우 매도가 < 고가 여도 상세로 보면 이미 지나버린 시점일 수 있음에 유의
                        상태 = '매수'
                        self.wallet[row_tik] = 잔고
                        self.asset[row_tik] = 자산
                        self.sell_order[row_tik] = 매도가
                        self.state[row_tik] = '종료시간까지 매도 안됨 상태 매수 전환'
                        # print(f"매도안됨 {row_tik=}, {현재시간=}, {종료시간=}, {type(현재시간)=}, {type(종료시간)=}")
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
                            수익률, 잔고, 자산 = self.chegyeol_sell(매도가, 매수수량, 매수금액, 잔고, row_tik)
                            상태 = '대기'
                            print(f"{상태= }   {잔고= }   {row_tik=} {old_row_tik=}  |  {np_tik_idx[row_tik]=},")
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

                # if self.minute_check.isChecked() == False:
                #     if (self.direction == 'long' and 매도가 <= 고가) or (방향 == 'short' and 매도가 >= 저가):
                #         수익률, 잔고, 자산 = self.chegyeol_sell(매도가, 매수수량, 매수금액, 레버리지, 잔고, row_tik)
                #         상태 = '대기'
                #         self.state[row_tik] = 상태

            if 상태 == '종료':
                print('상태 종료')
                break

            if np.isnan(self.wallet[row_tik-1]):
                self.check_db(row_tik)
                print(f"{self.df_detail.index[row_tik]} : {row_tik + 1} ,'- 잔고 엥꼬' | 상태: {상태},   잔고: {self.wallet[row_tik]}")
                # self.check_db(row_tik)
                break

            if row_tik >= length_index:
                row_tik -= 1 # row_tik은 0부터 시작 length_index는 1부터 시작 때문에
                print('정상종료')
                self.ror_strategy[row_tik] = round((자산 - self.bet) / self.bet * 100, 1)  # 최초 배팅 금액 대비 수익률 계산용
                break

            self.ror_strategy[row_tik] = round((자산 - self.bet) / self.bet * 100, 1)  # 최초 배팅 금액 대비 수익률 계산용
            # print(f"{np_tik_idx[row_tik]=} :  {round((자산 - self.bet) / self.bet * 100, 1)} ")
            # 상태 = 상태
            if self.ror_strategy[row_tik] < -80 or (self.ror_min[row_tik] < -80 and np.isnan(self.sell[row_tik])):  # 자산이 베팅금액의 80프로 미만일 경우 청산
                print(f'****** 청산: {현재시간=}')
                break

            # print(row_tik)
            # print(row_tik)
            self.val_bar.emit(round(row_tik / length_index * 100))
            if not old_row_tik == row_tik:
                old_row_tik = row_tik
                # print(f"if not old_row_tik == row_tik:   {old_row_tik=}")
            elif old_row_tik == row_tik :
                print(f'******* row_tik 변화 없음 | {row_tik=} {old_row_tik=}  |  {np_tik_idx[row_tik]=},  - {상태=}')
                self.check_db(row_tik)
                break
            elif old_row_tik > row_tik:
                print(f"******* row_tik 동일 : {row_tik=} {old_row_tik=}  |  {np_tik_idx[row_tik]=},  - {상태=}")
            else:
                print(f'에러 -- while self._status and row_tik < length_index:')
                raise
        #################################### 여기까지가 while loop

        print(f'backtest 걸린시간: {(time.time() - start_time)}   {row_tik= } < {length_index= } {상태= }  {self._status= }')
        # st = time.time()
        self.df_detail['매수주문가'] = self.buy_order
        self.df_detail['매수가'] = self.buy
        self.df_detail['매도주문가'] = self.sell_order
        self.df_detail['매도가'] = self.sell
        self.df_detail['수량'] = self.qty
        self.df_detail['수수료'] = self.fee_sum
        self.df_detail['수익률'] = self.ror
        self.df_detail['최고수익률'] = self.ror_max
        self.df_detail['최저수익률'] = self.ror_min
        self.df_detail['상태'] = self.state
        self.df_detail['수익금'] = self.benefit
        self.df_detail['잔고'] = self.wallet
        self.df_detail['전략수익률'] = self.ror_strategy
        self.df_detail['매수금액'] = self.price_buy
        self.df_detail['매도금액'] = self.price_sell
        self.df_detail['자산'] = self.asset
        self.df_detail['횟수'] = self.numbers #a매수 횟수
        self.df_detail['val'] = self.val
        self.df_detail['val_k'] = self.val_k

        # common_def.export_sql(self.df_detail,'bt_detail')
        if np.nan in self.df_detail['잔고'].tolist():
            print('잔고')
            print(self.df_detail['잔고'].tolist())
        # ddf = self.df_detail[['상세시가','상세고가','상세저가','상세종가','상세거래량','시가','고가','저가','종가','이평5','이평20','이평60','거래량이평3','거래량','매수주문가','매수가',
        #                       '매도주문가','매도가','수익률','수익금','최고수익률','최저수익률','상태','잔고','자산','횟수',
        #                       '데이터길이','이격도20이평']]
        # ddf.to_sql('numpy_detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
        # ddf = ddf[~np.isnan(ddf['매수가'])]
        # self.df['잔고'].fillna(method='ffill', inplace=True)
        # self.df['자산'].fillna(method='ffill', inplace=True)
        self.df['잔고'] = self.df['잔고'].ffill()
        self.df['자산'] = self.df['자산'].ffill()
        # common_def.export_sql(self.df_detail,'complete_backtest')
        # if self.market == '코인':
        #     ddf = self.df[['시가','고가','저가','종가','거래량','매수가','매도가','수량','수익률',
        #                           '최고수익률','최저수익률','수익금','매수금액','매도금액','잔고','자산','수수료']]
        # if self.market == '국내시장':
        #     ddf = self.df[['시가','고가','저가','종가','거래량','거래대금','매수가','매도가','수량','수익률',
        #                           '최고수익률','최저수익률','수익금','매수금액','매도금액','잔고','자산','수수료']]
        # ddf.to_sql('numpy', sqlite3.connect('DB/bt.db'), if_exists='replace')

        # print(f"{상태= }")
        # print(f"{row_tik= }")
        # print(f"{length_index= }")
        if self._status and length_index != row_tik+1:  # 백테스트가 다 돌아가지 않고 중간에 종료될 경우
            self.df_detail = self.df_detail[~np.isnan(self.df_detail['잔고'])] #조건 행 삭제 (잔고가 nan이 아닌행만 갖고오기)
            # self.df_detail['잔고'].fillna(method='ffill', inplace=True)
            # self.df_detail['자산'].fillna(method='ffill', inplace=True)
            print(f"{row_tik= }")
            print(f"{length_index= }")
            print('중간에 종료')
            # ddf = self.df_detail[['상세시가', '상세고가', '상세저가', '상세종가', '상세거래량', '시가','고가','저가','종가','이평5', '이평20', '매수주문가', '매수가', '매도주문가', '매도가', '수익률', '수익금',
            #      '최고수익률', '최저수익률', '상태', '잔고', '자산']]
            # ddf.to_sql('bt_numpy_detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
            # idx_end = self.df_detail.index[row_tik]
            # self.df_detail = self.df_detail[:row_tik + 1]
            # self.df_detail = self.df_detail.loc[self.df_detail.index[0]:idx_end]
            # raise

        # self.df_detail.drop(['종료시간','현재시간','상태','val','val_k'],axis=1,inplace=True)
        self.df.rename(columns={'자산': 'strategy'},inplace=True)
        self.df['매수가'] = self.df['매수가'].astype(float)
        self.df['매도가'] = self.df['매도가'].astype(float)
        self.df['수량'] = self.df['수량'].astype(float)
        self.df['수익률'] = self.df['수익률'].astype(float)
        self.df['최고수익률'] = self.df['최고수익률'].astype(float)
        self.df['최저수익률'] = self.df['최저수익률'].astype(float)
        self.df['수익금'] = self.df['수익금'].astype(float)
        self.df['전략수익률'] = self.df['전략수익률'].astype(float)
        self.df['매수금액'] = self.df['매수금액'].astype(float)
        self.df['매도금액'] = self.df['매도금액'].astype(float)
        self.df['수수료'] = self.df['수수료'].astype(float)
        # df.index.rename('index', inplace=True)  # 인덱스명 변경

        self.val_df.emit(self.df)


        # self.check_db(row_tik)
        # df = self.df
        # return df
    # def run(self):
    #     print('asdf')
    #     self.val_df.emit(self.df)


    def check_db(self,row_tik):
        print('*************************************** check_db ***************************************')
        self.df_detail['매수주문가'] = self.buy_order
        self.df_detail['매수가'] = self.buy
        self.df_detail['매도주문가'] = self.sell_order
        self.df_detail['매도가'] = self.sell
        self.df_detail['수량'] = self.qty
        self.df_detail['수수료'] = self.fee_sum
        self.df_detail['수익률'] = self.ror
        self.df_detail['최고수익률'] = self.ror_max
        self.df_detail['최저수익률'] = self.ror_min
        self.df_detail['상태'] = self.state
        self.df_detail['수익금'] = self.benefit
        self.df_detail['잔고'] = self.wallet
        self.df_detail['전략수익률'] = self.ror_strategy
        self.df_detail['매수금액'] = self.price_buy
        self.df_detail['매도금액'] = self.price_sell
        self.df_detail['자산'] = self.asset
        self.df_detail['횟수'] = self.numbers
        self.df_detail['val'] = self.val
        self.df_detail['val_k'] = self.val_k

        ddf = self.df_detail[:row_tik+5]
        print(ddf.tail())
        # ddf = ddf[['상세시가','상세고가','상세저가','상세종가','상세거래량','이평5','이평20','종료시간',
        #            '매수주문가','매수가','매도주문가','매도가','수익률','수익금','최고수익률','최저수익률','상태','잔고','자산','횟수',
        #                       '데이터길이','이격도20이평']]
        # ddf.to_sql('bt', sqlite3.connect('DB/bt.db'), if_exists='replace')
        common_def.export_sql(ddf,'check_db')

    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self._status = False
        print(f"def stop(self):   {self._status=}")
        self.quit()
        self.wait(3000)  # 3초 대기 (바로 안꺼질수도)

    def order_price(self,price_in,시가,side):
        slippage = 0.1  # 슬리피지 0.1 %
        # print(self.trade_market)
        if type(price_in) == dict:
            hoga_price = list(price_in.keys())[0]
            hoga_rate = price_in[hoga_price]
            if self.trade_market == 'bybit':
                price_out = float(self.exchange.price_to_precision(self.ticker, hoga_price + (hoga_price * hoga_rate / 100)))
            elif self.trade_market == 'KOSPI' or self.trade_market == 'KOSDAQ' or self.trade_market == 'ETF' or self.trade_market == 'ETF':
                price_out = self.exchange.hogaPriceReturn(self.trade_market,self.ticker, hoga_price, hoga_rate)
            elif self.trade_market == '선물' or self.trade_market == '옵션':
                price_out = self.exchange.hogaPriceReturn(self.trade_market,self.ticker, hoga_price, hoga_rate)
        elif price_in == 시장가 :  # 슬리피지 반영
            if self.trade_market == 'bybit' or self.trade_market == '선물' or self.trade_market == '옵션':
                if self.direction == 'long' and side == '매수주문': 가격 = 시가 + (slippage / 100 * 시가)
                elif self.direction == 'long' and side == '매도주문': 가격 = 시가 - (slippage / 100 * 시가)
                elif self.direction == 'short' and side == '매수주문': 가격 = 시가 - (slippage / 100 * 시가)
                elif self.direction == 'short' and side == '매도주문': 가격 = 시가 + (slippage / 100 * 시가)
                else: raise
                if self.trade_market == 'bybit':
                    price_out = float(self.exchange.price_to_precision(self.ticker, 가격))
                elif self.trade_market == '선물' or self.trade_market == '옵션':
                    price_out = self.exchange.hogaPriceReturn_per(self.trade_market, self.ticker, 가격, 0)
            elif self.trade_market == 'KOSPI' or self.trade_market == 'KOSDAQ' or self.trade_market == 'ETF' or self.trade_market == 'ETF':
                if side == '매수주문':
                    가격 = 시가 + (slippage / 100 * 시가)
                elif side == '매도주문':
                    가격 = 시가 - (slippage / 100 * 시가)
                price_out = self.exchange.hogaPriceReturn_per(self.trade_market,self.ticker, 가격, 0)
        else:
            if self.trade_market == 'bybit':  # 슬리피지 반영 해야함
                price_out = float(self.exchange.price_to_precision(self.ticker, price_in))
            elif self.trade_market == 'KOSPI' or self.trade_market == 'KOSDAQ' or self.trade_market == 'ETF' or self.trade_market == 'ETF':
                price_out = self.exchange.hogaPriceReturn_per(self.trade_market,self.ticker, price_in, 0)
            elif self.trade_market == '선물' or self.trade_market == '옵션':
                price_out = self.exchange.hogaPriceReturn_per(self.trade_market,self.ticker, price_in, 0)
        if price_out == None:
            raise print('가격 확인')
        return price_out

    def chegyeol_buy(self, 매수, 매수가, 잔고, row_tik):
        상태 = '매수'
        if self.trade_market == '선물':
            self.거래승수 = self.dic_multiplier[self.ticker[:3]]
            배팅금액 = 잔고 * (매수 / 100)
            매수가능금액 = (100 - (self.fee_furure)) / 100 * 배팅금액
            계약가 = 매수가 * self.거래승수
            계약당필요현금 = 계약가 * (self.위탁증거금률 / 100)
            매수수량 = 매수가능금액 // 계약당필요현금
            매수금액 = 매수수량 * 계약당필요현금
            self.매수계약금액 = 계약가 * 매수수량
            매수수수료 = self.매수계약금액 * self.fee_furure // 100
            잔고 = 잔고 - 매수금액 - 매수수수료
            자산 = 잔고 + 매수금액
            최고수익률 = 0
            최저수익률 = 0
            if 매수수량 == 0:
                print('(선물) 매수 할 자금 부족')
                상태 = '종료'
        else:
            # print(f"{잔고} * ({매수} / 100) * {레버리지}")
            배팅금액 = 잔고 * (매수 / 100) * self.레버리지
            매수수량 = (100 - (self.fee_market * self.레버리지)) / 100 * 배팅금액 / 매수가
            매수수량 = float(self.exchange.amount_to_precision(self.ticker, 매수수량))
            매수금액 = round(매수수량 * 매수가,4)
            매수수수료 = round(매수금액 * self.fee_market / 100, 4)
            잔고 = round(잔고 - (매수금액 / self.레버리지) - 매수수수료, 4)
            자산 = round(잔고 + (매수금액 / self.레버리지),4)
            최고수익률 = 0
            최저수익률 = 0

        self.buy[row_tik] = 매수가
        self.wallet[row_tik] = 잔고
        self.asset[row_tik] = 자산
        self.state[row_tik] = 상태
        self.qty[row_tik] = 매수수량
        self.price_buy[row_tik] = 매수금액
        self.fee_sum[row_tik] = 매수수수료
        self.df.loc[self.df['데이터길이'] == 데이터길이, '매수가'] = 매수가
        self.df.loc[self.df['데이터길이'] == 데이터길이, '수량'] = 매수수량
        self.df.loc[self.df['데이터길이'] == 데이터길이, '매수금액'] = 매수금액
        self.df.loc[self.df['데이터길이'] == 데이터길이, '잔고'] = 잔고
        self.df.loc[self.df['데이터길이'] == 데이터길이, '자산'] = 자산

        # print(f"{매수=}, {레버리지=}, {잔고=}, {자산=}, {배팅금액=}, {매수가=}, {매수수량=}, {매수금액=}, {매수수수료=}")
        return 매수수량, 매수금액, 잔고, 자산, 매수금액, 매수수수료, 최고수익률, 최저수익률, 상태

    def chegyeol_sell(self, 매도가,매수수량,매수금액,잔고,row_tik):
        if self.direction == 'long':
            if self.trade_market == '선물':
                매도계약금액 = 매수수량 * 매도가 * self.거래승수
                매수수수료 = self.매수계약금액 * self.fee_furure // 100
                매도수수료 = 매도계약금액 * self.fee_furure // 100
                수익금 = 매도계약금액 - self.매수계약금액 - 매도수수료
                수익률 = round(((수익금 - 매수수수료) / 매수금액 * 100) * self.레버리지, 2)
                잔고 = 잔고 + 매수금액 + 수익금  ##매수수수료는 매수하면서 이미 냈음
                매도금액 = 매수수량 * (매도가 * self.거래승수 * (self.위탁증거금률/100))

            else:
                매도금액 = 매도가 * 매수수량
                매수수수료 = round(매수금액 * self.fee_market / 100, 4)
                매도수수료 = round(매도금액 * self.fee_market / 100, 4)
                수익금 = round(매도금액 - 매수금액 - 매도수수료, 4)
                수익률 = round(((수익금 - 매수수수료) / 매수금액 * 100) * self.레버리지, 2)
                잔고 = round(잔고 + (매수금액 / self.레버리지) + 수익금,4)  ##매수수수료는 매수하면서 이미 냈음
        elif self.direction == 'short':
            if self.trade_market == '선물':
                매도계약금액 = 매수수량 * 매도가 * self.거래승수
                매수수수료 = self.매수계약금액 * self.fee_furure // 100
                매도수수료 = 매도계약금액 * self.fee_furure // 100
                수익금 = self.매수계약금액 - 매도계약금액 - 매도수수료
                수익률 = round(((수익금 - 매수수수료) / 매수금액 * 100) * self.레버리지, 2)
                잔고 = 잔고 + 매수금액 + 수익금  ##매수수수료는 매수하면서 이미 냈음
                매도금액 = 매수수량 * (매도가 * self.거래승수 * (self.위탁증거금률/100))

            else:
                매도금액 = 매도가 * 매수수량
                매수수수료 = round(매수금액 * self.fee_market / 100, 4)
                매도수수료 = round(매도금액 * self.fee_market / 100, 4)
                수익금 = round(매수금액 - 매도금액 - 매도수수료, 4)
                수익률 = round(((수익금 - 매수수수료) / 매수금액 * 100) * self.레버리지, 2)
                잔고 = round(잔고 + (매수금액 / self.레버리지) + 수익금,4)  ##매수수수료는 매수하면서 이미 냈음

        self.sell[row_tik] = 매도가
        self.wallet[row_tik] = 잔고
        자산 = 잔고
        self.asset[row_tik] = 자산
        self.state[row_tik] = '매도'
        self.ror[row_tik] = 수익률
        self.price_sell[row_tik] = 매도금액
        self.benefit[row_tik] = 수익금 - 매수수수료
        self.fee_sum[row_tik] = 매도수수료
        self.df.loc[self.df['데이터길이'] == 데이터길이, '매도가'] = 매도가
        self.df.loc[self.df['데이터길이'] == 데이터길이, '매도금액'] = 매도금액
        self.df.loc[self.df['데이터길이'] == 데이터길이, '수익률'] = 수익률
        self.df.loc[self.df['데이터길이'] == 데이터길이, '수수료'] = 매수수수료 + 매도수수료
        self.df.loc[self.df['데이터길이'] == 데이터길이, '수익금'] = 수익금 - 매수수수료
        self.df.loc[self.df['데이터길이'] == 데이터길이, '잔고'] = 잔고
        self.df.loc[self.df['데이터길이'] == 데이터길이, '자산'] = 자산
        return 수익률, 잔고, 자산

    def cal_ror(self, 상세고가, 상세저가, 상세종가, 매수수량, 매수금액, 잔고, 현최고수익률, 현최저수익률, row_tik):
        # print('==================')
        # print(f"{np_tik_idx[row_tik]= }, {레버리지= }, {상세고가= }, {상세저가= }, {상세종가= }, {매수수량= }, {매수금액= }, {잔고= }, {현최고수익률= }, {현최저수익률= }")

        if self.direction == 'long':
            if self.trade_market == '선물':
                매수수수료 = self.매수계약금액 * self.fee_furure // 100
                매도수수료 = 매수수량 * 상세종가 * self.거래승수 * self.fee_furure // 100
                평가금액 = 매수수량 * 상세종가 * self.거래승수 - 매도수수료
                최고평가금액 = 매수수량 * 상세고가 * self.거래승수 - 매도수수료
                최저평가금액 = 매수수량 * 상세저가 * self.거래승수 - 매도수수료
                수익금 = 평가금액 - self.매수계약금액 - 매도수수료
                최고수익금 = 최고평가금액 - self.매수계약금액 - 매도수수료
                최저수익금 = 최저평가금액 - self.매수계약금액 - 매도수수료
            else:
                매수수수료 = round(매수금액 * self.fee_market / 100, 0)
                매도수수료 = round(매수수량 * 상세종가 * self.fee_market / 100, 0)
                평가금액 = 매수수량 * 상세종가 - 매도수수료
                최고평가금액 = 매수수량 * 상세고가 - 매도수수료
                최저평가금액 = 매수수량 * 상세저가 - 매도수수료
                수익금 = round(평가금액 - 매수금액 - 매도수수료, 4)
                최고수익금 = 최고평가금액 - 매수금액 - 매도수수료
                최저수익금 = 최저평가금액 - 매수금액 - 매도수수료
        elif self.direction == 'short':
            if self.trade_market == '선물':
                매수수수료 = self.매수계약금액 * self.fee_furure // 100
                매도수수료 = 매수수량 * 상세종가 * self.거래승수 * self.fee_furure // 100
                평가금액 = 매수수량 * 상세종가 * self.거래승수 - 매도수수료
                최고평가금액 = 매수수량 * 상세저가 * self.거래승수 - 매도수수료
                최저평가금액 = 매수수량 * 상세고가 * self.거래승수 - 매도수수료
                수익금 = self.매수계약금액 - 평가금액 - 매도수수료
                최고수익금 = self.매수계약금액 - 최고평가금액 - 매도수수료
                최저수익금 = self.매수계약금액 - 최저평가금액 - 매도수수료
            else:
                매수수수료 = round(매수금액 * self.fee_market / 100, 0)
                매도수수료 = round(매수수량 * 상세종가 * self.fee_market / 100, 0)
                평가금액 = 매수수량 * 상세종가 - 매도수수료
                수익금 = round(매수금액 - 평가금액 - 매도수수료, 4)
                최고평가금액 = 매수수량 * 상세저가 - 매도수수료
                최저평가금액 = 매수수량 * 상세고가 - 매도수수료
                최고수익금 = 매수금액 - 최고평가금액 - 매도수수료
                최저수익금 = 매수금액 - 최저평가금액 - 매도수수료
        # try:
        # print(f"{np_tik_idx[row_tik]= }, {잔고= }, {수익금= }, {매수수수료= }) / {매수금액= } * 100)*{레버리지= }")
        수익률 = round(((수익금-매수수수료) / 매수금액 * 100)*self.레버리지, 2)
        # except:
        #     raise '배팅금액 확인'
        최고수익률 = round(((최고수익금 - 매수수수료) / 매수금액 * 100)*self.레버리지, 2)
        최저수익률 = round(((최저수익금 - 매수수수료) / 매수금액 * 100)*self.레버리지, 2)
        self.ror_max[row_tik] = float(np.where(최고수익률 > 현최고수익률, 최고수익률, 현최고수익률))
        self.ror_min[row_tik] = float(np.where(최저수익률 < 현최저수익률, 최저수익률, 현최저수익률))
        자산 = round(잔고 + (매수금액/self.레버리지) + 수익금,4)
        self.ror[row_tik] = 수익률
        self.asset[row_tik] = 자산
        if 현재시간 == 종료시간:
            self.df.loc[self.df['데이터길이'] == 데이터길이, '잔고'] = 잔고
            self.df.loc[self.df['데이터길이'] == 데이터길이, '자산'] = 자산
            self.df.loc[self.df['데이터길이'] == 데이터길이, '수익률'] = 수익률
            self.df.loc[self.df['데이터길이'] == 데이터길이, '최고수익률'] = 최고수익률
            self.df.loc[self.df['데이터길이'] == 데이터길이, '최저수익률'] = 최저수익률

        return 수익률, self.ror_max[row_tik], self.ror_min[row_tik]

    # 백테스트용 DF를 만들때는 전체 날짜를 만들지만 나중에 잘라서 쓸 수 있음
    # 때문에 날짜를 처음부터 테스트 하는게 아니라면 데이터길이가 들어가는 변수의 경우 데이터길이 값을 변경해줘야 함.
    def reset_data_lenth(self,df):
        list_columns = df.columns.tolist()
        # print('==============='*5)
        for col in list_columns:
            if '데이터길이' in col:
                # num = df[col][0]
                # print(df[col][0])
                num = df[col].tolist()[0]
                # print(df[col].tolist()[0])
                if num != 1:
                    df[col] = df[col]-(num-1)
                    # print(df)
                    # quit()
        return df

if __name__ == '__main__':
    import tab_backtest
    def make_start_stop(df_detail, detail_stamp):
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
        return df_detail

    def make_df(dict_info):
        dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                           '주봉': 10080}
        market = dict_info['market']
        ticker = dict_info['ticker']
        bong = dict_info['bong']
        bong_detail = dict_info['bong_detail']
        start_day = dict_info['start_day']
        end_day = dict_info['end_day']
        conn_DB = dict_info['connect']
        table_list_DB = dict_info['table_list_DB']
        trade_market = dict_info['trade_market']
        dict_bong = dict_info['dict_bong']
        dict_bong_reverse = dict_info['dict_bong_reverse']
        ticker_detail = ticker+'_'+dict_bong[bong_detail]
        df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", conn_DB).set_index('날짜')
        df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
        if market == '코인':
            df_detail.index = df_detail.index - pd.Timedelta(hours=9)
            df, df_detail = common_def.detail_to_spread(df_detail,bong,bong_detail)
            df_detail.index = df_detail.index + pd.Timedelta(hours=9)
            df.index = df.index + pd.Timedelta(hours=9)
            for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
                start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
                end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
                df_detail.loc[start_time:end_time, '장시작시간'] = start_time
                df_detail.loc[start_time:end_time, '장종료시간'] = end_time
            df_detail['현재시간'] = df_detail.index
            if bong == '일봉':
                df_detail['종료시간'] = df_detail['장종료시간'].copy()
            elif bong != '일봉' and bong != '주봉' and bong != '월봉':
                df_detail_end_time = df_detail['현재시간'].resample(f'{dict_bong_stamp[bong]}min').last()
                df_detail_end_time = pd.Series(df_detail_end_time,name='종료시간')
                df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
            # print(df_detail.head(20))
            df_detail.ffill(inplace=True)
            # print(df_detail)
            # conn = sqlite3.connect('DB/bt.db')
            # df_detail.to_sql('bt',conn,if_exists='replace')
        else:
            df_detail.index = df_detail.index - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
            # df_detail = df_detail[df_detail.index >= datetime.strptime("20200326","%Y%m%d")]
            df, df_detail = common_def.detail_to_spread(df_detail,bong,bong_detail)
            df_detail = make_start_stop(df_detail, dict_bong_stamp[bong_detail])
            df_detail['현재시간'] = df_detail.index
            if bong == '일봉':
                df_detail['종료시간'] = df_detail['장종료시간'].copy()
            elif bong != '일봉' and bong != '주봉' and bong != '월봉':
                # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
                df_detail_end_time = df_detail['현재시간'].resample(f'{dict_bong_stamp[bong]}min').last()
                df_detail_end_time = pd.Series(df_detail_end_time,name='종료시간') #추출한 시리즈의 이름을 종료시간으로 변경
                df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
                # df_detail.fillna(method='ffill', inplace=True)
                df_detail.ffill(inplace=True)
        save = True
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
        return df, df_detail, save

    def mapping(x, i_min, i_max, o_min, o_max):
        return (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # mapping()함수 정의.

    def compare_price(price, vars):
        i_min = price.min()  # 현재가.min
        i_max = price.max()
        return price.apply(mapping, args=(i_min, i_max, vars.min(), vars.max()))

    def leak_to_fill(df_detail,detail_stamp):
        # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
        df_detail['장시작시간'] = np.nan
        serise_start_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
        df_detail['장시작시간'] = serise_start_t
        df_detail['장종료시간'] = np.nan
        serise_end_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
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
        # 슬라이싱된 데이터프레임들을 하나로 결합
        df_detail = pd.concat(dfs)
        # if 현재시간 == 장종료시간: False 조건이 먹히기 위해서는 장종료시간에서 bong_detail만큼 빼줘야됨
        # df_detail['장종료시간'] = df_detail['장종료시간'] - timedelta(minutes=detail_stamp)  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨

        # 누락되는 데이터 메꾸기 용 (다른방법)
        # serise_day = df_detail.groupby(df_detail.index.date)
        # serise_day = serise_day.size()
        # mode_val = serise_day.mode()[0] #각 일자별 통계 (최빈값)
        # condition = serise_day != mode_val #최빈값이 아닌 행들 추출
        # filtered_data = serise_day[condition]
        # for idx in filtered_data.index:
        #     df_split = df_detail[df_detail.index.date==idx]
        #     for i,idx_split in enumerate(df_split.index):
        #         if idx_split == df_split['종료시간'][0]:
        #             break
        #         elif idx_split+timedelta(minutes=5) != df_split.index[i+1]: #현재 인덱스에서 5분을 더한게 다음 인덱스랑 다를경우
        #             cha = df_split.index[i+1] - idx_split
        #             several = int((cha-timedelta(minutes=5))/timedelta(minutes=5))
        #             list_split = [idx_split+timedelta(minutes=(x+1)*5) for x in range(several)]
        #             nan_row = pd.DataFrame([[np.nan] * len(df_detail.columns)], columns=df_detail.columns, index=list_split)
        #             nan_row.index = pd.to_datetime(nan_row.index)  # datime형태로 변환
        #             insert_index = df_detail.index.tolist().index(idx_split) #인덱스를 번호로 추출
        #             insert_index += 1
        #             top_df = df_detail.iloc[:insert_index]
        #             bottom_df = df_detail.iloc[insert_index:]
        #             df_detail = pd.concat([top_df, nan_row, bottom_df])

        return df_detail

    def get_df_multi(dict_info):

        market = dict_info['market']
        ticker = dict_info['ticker']
        bong = dict_info['bong']
        bong_detail = dict_info['bong_detail']
        QLE_start = dict_info['start_day']
        QLE_end = dict_info['end_day']
        conn_DB = dict_info['connect']
        # table_list_DB = dict_info['table_list_DB']
        trade_market = dict_info['trade_market']
        dict_bong = dict_info['dict_bong']
        dict_bong_reverse = dict_info['dict_bong_reverse']

        st = time.time()
        print(market)
        if market == '전체':
            print('******************전체에 대한 백테스트 아직 정의 안됨******************')
            return 0
        elif market == '국내주식' or market == '국내선옵':
            market = '국내시장'
            db_file = 'DB/DB_stock.db'
            if ticker in stocks_info.index.tolist():
                trade_market = stocks_info.loc[ticker,'시장구분']
            elif ticker in ['10100','코스피200선물', '미니코스피200선물','코스닥150선물','미국달러선물','3년국채선물','10년국채선물', '금연결선물']:
                trade_market = '선물'
            else:
                raise
        elif market == '코인':
            db_file = 'DB/DB_bybit.db'
        else:
            db_file = ''
            raise

        dict_bong = {'1분봉': '1m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}


        ticker_bong = ticker + '_' + dict_bong[bong]
        ticker_detail = ticker + '_' + dict_bong[bong_detail]


        # print(f"{market}, {ticker}  기준봉: {ticker} = {bong}  |  상세봉: {ticker} = {bong_detail}  |  ", end='')
        con_db = sqlite3.connect(db_file)
        cursor = con_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = np.concatenate(cursor.fetchall()).tolist()

        list_bong = [x[x.index('_')+1:] for x in table_list if x[:x.index('_')]==ticker] # 해당 ticker가 갖고있는 db를 리스트화 [1m,3m,5m...]
        dict_bong = {key: value for key, value in dict_bong.items() if value in list_bong} #리스트에있는 원소만 딕셔너리에 남기기

        if ticker_bong in table_list:
            df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", con_db).set_index('날짜')

            df.index = pd.to_datetime(df.index)  # datime형태로 변환
            if market =='국내시장' and bong != '일봉' and bong != '주봉' and bong != '월봉': #국내시장의 기준이 분봉일 경우
                df.index = df.index - datetime.timedelta(minutes=dict_bong_stamp[bong]) # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨

            # 입력받은 날짜로 자르기
            start_day = datetime.datetime.strptime(QLE_start, '%Y-%m-%d')
            end_day = datetime.datetime.strptime(QLE_end, '%Y-%m-%d')
            df = df[df.index >= start_day]
            df = df[df.index < end_day + datetime.timedelta(days=1)]

            if bong != bong_detail:
                print(' 디테일 사용')
                df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", con_db).set_index('날짜')
                df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
                st = time.time()
                del dict_bong[bong] # 기준봉은 삭제
                del dict_bong[bong_detail]  # 디테일 사용 시 디테일봉 삭제

                if market == '국내시장':
                    if bong_detail != '일봉' and bong_detail != '주봉' and bong_detail != '월봉':
                        df_detail.index = df_detail.index - datetime.timedelta(minutes=dict_bong_stamp[bong_detail]) # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨
                    df_detail = leak_to_fill(df_detail,dict_bong_stamp[bong_detail]) #누락되는 분봉 채우기
                elif market == '코인':
                    pass
                # df_detail.to_sql('detail',sqlite3.connect('DB/bt.db'), if_exists='replace')
                # quit()
                df_detail = df_detail[df_detail.index >= start_day]
                df_detail = df_detail[df_detail.index < end_day + datetime.timedelta(days=1)]
                if df_detail.empty:
                    print(f"df_detail 데이터 없음 DB 시간 확인 요망")
                    quit()


                # # df와 df_detail에 있는 날짜로만 자르기
                if df.index[0] < df_detail.index[0] and bong == '일봉' and market == '국내시장': # 일봉의 경우 인덱스의 시간이 0시 기준이기 때문에 -1일 해줘야됨
                    df = df[df.index >= df_detail.index[0] - datetime.timedelta(days=1)]
                    df_detail = df_detail[df_detail.index >= df.index[0]]
                elif df.index[0] < df_detail.index[0]:
                    df = df[df.index >= df_detail.index[0]]
                    df_detail = df_detail[df_detail.index >= df.index[0]]
                elif df.index[0] > df_detail.index[0]:
                    df_detail = df_detail[df_detail.index >= df.index[0]]
                if df.index[-1] > df_detail.index[-1]:
                    df = df[df.index <= df_detail.index[-1]]
                    df_detail = df_detail[df_detail.index < df.index[-1]]
                    df = df[df.index <df_detail.index[-1]]
                elif df.index[-1] < df_detail.index[-1] and bong == '일봉' and market == '국내시장': # 일봉의 경우 인덱스의 시간이 0시 기준이기 때문에 +1일 해줘야됨
                    df_detail = df_detail[df_detail.index < df.index[-1] + datetime.timedelta(days=1)]
                    df = df[df.index <= df_detail.index[-1]]
                elif df.index[-1] < df_detail.index[-1]:
                    df_detail = df_detail[df_detail.index <= df.index[-1]]
                    df = df[df.index <= df_detail.index[-1]]

            elif bong == bong_detail:
                print(' 디테일 사용 X')
                df_detail = df.copy()
                del dict_bong[bong] # 기준봉은 삭제
                if market == '국내시장' and bong != '일봉' and bong != '주봉' and bong != '월봉':
                    df_detail['장종료시간'] = np.nan
                    serise_end_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
                    df_detail['장종료시간'] = serise_end_t
                    # df.loc[df.index < datetime.strptime('2016-08-01', '%Y-%m-%d'),'종료시간'] = df['장종료시간'] + timedelta(hours=15, minutes=10)
                    # df.loc[df.index >= datetime.strptime('2016-08-01', '%Y-%m-%d'),'종료시간'] = df['장종료시간'] + timedelta(hours=15, minutes=40)
                    df_detail['장시작시간'] = np.nan
                    serise_start_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
                    df_detail['장시작시간'] = serise_start_t
                    # if 현재시간 == 장종료시간: False 조건이 먹히기 위해서는 장종료시간에서 bong_detail만큼 빼줘야됨
                    df_detail['장종료시간'] = df_detail['장종료시간'] - datetime.timedelta(minutes=dict_bong_stamp[bong])
                elif market == '국내시장' and (bong == '일봉' or bong == '주봉' or bong == '월봉'):
                    df_detail['장종료시간'] = df_detail.index
                    df_detail['장시작시간'] = df_detail.index
            st = time.time()
            if market == '국내시장':
                if trade_market == '선물':
                    if bong_detail == '일봉':
                        df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                                  '전일대비':'상세전일대비','거래량': '상세거래량', '거래대금': '상세거래대금',
                                                  '선물이론가': '상세선물이론가', '베이시스': '상세베이시스', },inplace=True)
                    elif bong_detail == '주봉' or bong_detail == '월봉':
                        df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                                  '거래량': '상세거래량', '거래대금': '상세거래대금'},inplace=True)
                    else: #분봉
                        df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                                  '거래량': '상세거래량', '거래대금': '상세거래대금','누적체결매도수량':'상세누적체결매도수량',
                                                  '누적체결매수수량':'상세누적체결매수수량'},inplace=True)

                else: #주식
                    if bong_detail == '일봉':
                        df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                                  '전일대비': '상세전일대비', '거래량': '상세거래량', '거래대금': '상세거래대금',
                                                  '상장주식수':'상세상장주식수', '시가총액':'상세시가총액', '외국인현보유수량':'상세외국인현보유수량',
                                                  '외국인현보유비율':'상세외국인현보유비율', '기관순매수량':'상세기관순매수량', '기관누적순매수량':'상세기관누적순매수량'}, inplace=True)
                    elif bong_detail == '주봉' or bong_detail == '월봉':
                        df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                                  '거래량': '상세거래량', '거래대금': '상세거래대금'}, inplace=True)
                    else: #분봉
                        df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                                  '거래량': '상세거래량', '거래대금': '상세거래대금','누적체결매도수량':'상세누적체결매도수량',
                                                  '누적체결매수수량':'상세누적체결매수수량'}, inplace=True)
                if bong == '일봉':
                    #기준봉이 일봉일 경우 detail봉에서 장 시작시간을 가져와 일봉에 넣기 위함
                    df_detail['장시작시간'] = np.nan
                    # serise_start_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[0]).장시작시간 #날짜별 시간을 같은행에 넣기
                    serise_start_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[0]).장시작시간 #날짜별 시간을 같은행에 넣기
                    df_detail['장시작시간'] = serise_start_t
                    group = serise_start_t.groupby(serise_start_t)
                    list_start_t = group.size().index.tolist()
                    df.index = df.index + datetime.timedelta(hours=9)  # 일봉일 경우 날짜만 나오기때문에 앞에 우선 시간을 넣어줘야 됨
                    list_date = df.index.date.tolist()
                    list_idx = df.index.tolist()
                    for new_idx in list_start_t:
                        if new_idx.date() in list_date:
                            list_idx[list_date.index(new_idx.date())]=new_idx
                    df.index = list_idx
                    df.index.rename('날짜', inplace=True)  # 인덱스명 변경

                    df_detail['종료시간'] = df_detail['장종료시간'].copy()

                elif bong != '일봉' and bong != '주봉' and bong != '월봉':
                    # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
                    df_detail['종료시간'] = df_detail.index
                    df_detail_end_time = df_detail['종료시간'].resample(f'{dict_bong_stamp[bong]}T').last()
                    del df_detail['종료시간']
                    df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')


                if set(df.index.tolist()) - set(df_detail.index.tolist()):  # 머지 적용이 안되고 남은 idx가 있을 경우 예) 장 시작시간이 10시일 경우
                    print('set(df.index.tolist()) - set(df_detail.index.tolist())')
                    pprint(set(df.index.tolist()) - set(df_detail.index.tolist()))
                    extra = set(df.index.tolist()) - set(df_detail.index.tolist())
                    extra = list(extra)
                    for ix in extra:
                        df_extra = df.loc[df.index == ix]  # 날짜 조건으로 데이터 추출
                        export_date = ix.date()  # <class 'pandas._libs.tslibs.timestamps.Timestamp'>에서 날짜만 추출
                        df_date = df_detail.loc[df_detail.index.date == export_date]  # 같은날짜 조건으로 데이터 추출
                        df_extra = df_extra.assign(날짜=[df_date.index[0]]).set_index('날짜')
                        df_detail = df_detail.combine_first(df_extra)


            elif market == '코인':
                df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가', '거래량': '상세거래량'},inplace=True)


                # datetime 형태의 start_time 컬럼 추가
                # df_detail['장시작시간'] = pd.NaT

                for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
                    start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
                    end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
                    df_detail.loc[start_time:end_time, '장시작시간'] = start_time
                    df_detail.loc[start_time:end_time, '장종료시간'] = end_time

                if bong == '일봉':
                    df_detail['종료시간'] = df_detail['장종료시간'].copy()

                elif bong != '일봉' and bong != '주봉' and bong != '월봉':
                    df_detail['종료시간'] = df_detail.index
                    df_detail_end_time = df_detail['종료시간'].resample(f'{dict_bong_stamp[bong]}T').last()
                    del df_detail['종료시간']
                    df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')

            st = time.time()
            df = common_def.convert_df(df)
            df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
            df_detail = pd.merge(df_detail, df, left_index=True, right_index=True, how='left')

            # df_detail.fillna(method='ffill', inplace=True)
            df_detail.ffill(inplace=True)
            # df_detail.to_sql('detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
            df_detail['데이터길이'] = df_detail['데이터길이'].fillna(0) # nan을 0으로 채우기

            df_detail['현재시간'] = df_detail.index
            dict_bong_reverse = dict(zip(dict_bong.values(), dict_bong.keys()))

            start_day = df_detail.index[0]
            end_day = df_detail.index[-1]
            st = time.time()
            print('멀티봉 생성 중..')
            for bong_add in dict_bong_reverse.keys():
                if market == '코인': # bybit일 경우
                    df_add = pd.read_sql(f"SELECT * FROM '{ticker}_{bong_add}'", con_db).set_index('날짜')
                    df_add.index = pd.to_datetime(df_add.index)  # datime형태로 변환
                    df_add = df_add[df_add.index >= start_day]
                    df_add = df_add[df_add.index < end_day + datetime.timedelta(days=1)]
                    if df_add.empty:
                        print(f"** {dict_bong_reverse[bong_add]} '데이터는 없음'")
                        del dict_bong[dict_bong_reverse[bong_add]]
                        pass
                    else:
                        df_add[f'데이터길이_{dict_bong_reverse[bong_add]}'] = np.arange(1, len(df_add.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1

                        df_add.rename(columns={'시가': f'시가_{dict_bong_reverse[bong_add]}', '고가': f'고가_{dict_bong_reverse[bong_add]}',
                                               '저가': f'저가_{dict_bong_reverse[bong_add]}', '종가': f'종가_{dict_bong_reverse[bong_add]}',
                                               '거래량': f'거래량_{dict_bong_reverse[bong_add]}'}, inplace=True)  # 컬럼명 변경

                        df_add[f'이평20_{dict_bong_reverse[bong_add]}'] = talib.MA(df_add[f'종가_{dict_bong_reverse[bong_add]}'], 20)
                        df_add[f'이평60_{dict_bong_reverse[bong_add]}'] = talib.MA(df_add[f'종가_{dict_bong_reverse[bong_add]}'], 60)
                        df_detail = pd.merge(df_detail, df_add, left_index=True, right_index=True, how='left')
                elif market == '국내시장': # 국내시장일 경우
                    df_add = pd.read_sql(f"SELECT * FROM '{ticker}_{bong_add}'", con_db).set_index('날짜')
                    df_add.index = pd.to_datetime(df_add.index)  # datime형태로 변환
                    df_add = df_add[df_add.index >= start_day]
                    df_add = df_add[df_add.index < end_day + datetime.timedelta(days=1)]
                    if df_add.empty:
                        print(f"** {dict_bong_reverse[bong_add]} '데이터는 없음'")
                        del dict_bong[dict_bong_reverse[bong_add]]
                        pass
                    else:
                        if dict_bong_reverse[bong_add] in ['1분봉','3분봉','5분봉','15분봉','30분봉','60분봉']:
                            df_add.index = df_add.index - datetime.timedelta(minutes=dict_bong_stamp[dict_bong_reverse[bong_add]]) # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 5분 빼줘야됨

                        elif dict_bong_reverse[bong_add] == '주봉' or dict_bong_reverse[bong_add] == '월봉':  # 일봉일 경우 제외
                            # 주봉과 월봉의 경우 장 시간을 찾아서 인덱스를 맞추기 (나중에 인덱스에 맞춰 merge 시키기 위해)
                            # 주봉과 월봉의 경우 대신증권에서 주봉은 주의 첫번째, 두번째, 월은 단순 월을 넘겨주기 때문에 가공해서
                            # 주봉은 주의 월요일날짜 월요일은 월의 첫번째 요일을 받음 때문에 해당일이 휴일일경우도 있어서 추가 가공해줘야됨
                            # df_add = df_add[df_add.index.date >= df_detail.index[0].date()]
                            serise_day = df_detail.groupby(df_detail.index.date)
                            list_detail_day = serise_day.size().index.tolist()
                            list_add_day = df_add.index.date.tolist()
                            list_extra_day = set(list_add_day) - set(list_detail_day) # df_add에는 있지만 df_detail에는 없는날(휴일)을 리스트화

                            for extra_day in list_extra_day: # 휴일을 돌아가면서 +1일 씩 함
                                cha_day = extra_day
                                # quit()
                                while not cha_day in list_detail_day:
                                    cha_day = cha_day + datetime.timedelta(days=1)
                                    if cha_day in list_detail_day: # + 1일 씩 하면서 df_detail에 날짜가 있으면
                                        list_add_day[list_add_day.index(extra_day)]=cha_day #원래 있던 자리에 저장
                                        break
                                    elif cha_day - extra_day > datetime.timedelta(days=7): # 7일 이상 더했는데도 저장이 안된다면 휴일이 7일 이상이거나 데이터 날짜가 서로 안맞는거임
                                        print(f"{dict_bong_reverse[bong_add]=}")
                                        print(f"{extra_day=}")
                                        print(f"{cha_day=}")
                                        raise
                            df_add.index = list_add_day
                            # df_detail 각 날짜의 마지막 시간을 찾기
                            last_times = df_detail.groupby(df_detail.index.date).apply(lambda x: x.index.min())
                            # 날짜 인덱스를 마지막 시간으로 매핑
                            new_index = df_add.index.map(lambda x: last_times[x])

                            # df2의 인덱스를 새로운 인덱스로 설정
                            df_add.index = new_index
                            ########################## 마지막날짜가 detail에 포함되지 않으면 에러가 날 수 있음에 유의
                            # 인덱스가 NaT인 행 삭제
                            df_add = df_add[df_add.index.notna()]
                            # df_add.to_sql('w', sqlite3.connect('DB/bt.db'), if_exists='replace')


                        df_add[f'데이터길이_{dict_bong_reverse[bong_add]}'] = np.arange(1, len(df_add.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
                        df_add.rename(columns={'시가': f'시가_{dict_bong_reverse[bong_add]}', '고가': f'고가_{dict_bong_reverse[bong_add]}',
                                               '저가': f'저가_{dict_bong_reverse[bong_add]}', '종가': f'종가_{dict_bong_reverse[bong_add]}',
                                               '거래량': f'거래량_{dict_bong_reverse[bong_add]}', '거래대금': f'거래대금_{dict_bong_reverse[bong_add]}',
                                               '누적체결매도수량': f'누적체결매도수량_{dict_bong_reverse[bong_add]}', '누적체결매수수량': f'누적체결매수수량_{dict_bong_reverse[bong_add]}',},inplace=True)  # 컬럼명 변경
                        df_add[f'이평20_{dict_bong_reverse[bong_add]}'] = talib.MA(df_add[f'종가_{dict_bong_reverse[bong_add]}'], 20)
                        df_add[f'이평60_{dict_bong_reverse[bong_add]}'] = talib.MA(df_add[f'종가_{dict_bong_reverse[bong_add]}'], 60)


                        df_detail = pd.merge(df_detail, df_add, left_index=True, right_index=True, how='left')
            print(f"4 걸린시간{time.time()-st}")
            st = time.time()
            print(f'사용가능한 캔들 {dict_bong.keys()}')
            cursor.close()
            con_db.close()

            # df_detail.fillna(method='ffill', inplace=True)
            df_detail.ffill(inplace=True)
            # df_detail.to_sql('detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
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
            # quit()
            save = True
            return df, df_detail, save

        else:
            print(f"{ticker_bong=}")
            print(f"{table_list=}")
            raise print('데이터 확인 요망')

    def replace_tabs_with_spaces(text): #스페이스랑 탭 혼용 시 에러 방지용
        space_count = 4
        return text.replace('\t', ' ' * space_count)

    class min_QCB():
        def __init__(self,signal:bool):
            self.signal = signal
        def isChecked(self):
            return self.signal

    from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
        QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, \
        QAbstractItemView, QProgressBar

    class Window(QMainWindow): #별도로 실행하고자 할 때
        def __init__(self,dict_info):
            super().__init__()
            self.QL_state = QLabel()
            self.QL_wallet = QLabel()
            self.QL_ror = QLabel()
            self.QL_benefit = QLabel()
            QW_main = QWidget()
            self.setCentralWidget(QW_main)
            self.QPB_bar = QProgressBar(self)

            QGL = QGridLayout()
            QGL.addWidget(QLabel('상태'), 0, 0)
            QGL.addWidget(self.QL_state, 0, 1)
            QGL.addWidget(QLabel('잔고'), 1, 0)
            QGL.addWidget(self.QL_wallet, 1, 1)
            QGL.addWidget(QLabel('수익률'), 2, 0)
            QGL.addWidget(self.QL_ror, 2, 1)
            QGL.addWidget(QLabel('수익금'), 3, 0)
            QGL.addWidget(self.QL_benefit, 3, 1)
            QGL.addWidget(self.QPB_bar, 4, 0,1,2)

            QVB_main = QVBoxLayout()
            QVB_main.addLayout(QGL)
            QW_main.setLayout(QVB_main)

            self.thread_make = tab_backtest.make_data(self,dict_info)
            self.thread_make.start()
            self.thread_make.val.connect(self.run_backtest)

        def run_backtest(self,df,df_detail):
            for factor in df_detail.columns.tolist():
                if not factor in str(stg_buy+stg_sell): #실제 전략에 필요한 팩터만 남기고 데이터프레임에서 삭제
                    if not factor in ['상세시가','상세고가','상세저가','상세종가','시가','고가','저가','종가','종료시간',
                                      '현재시간','장시작시간','장종료시간']: #삭제에서 제외
                        df_detail.drop(factor,axis=1,inplace=True)

            print(df_detail)

            self.length_index = len(df_detail.index)
            if sys.maxsize > self.length_index: # df_detail.index의 값이 int형의 최대값보다 작을 경우만 백테스트 진행
                self.thread = backtest_np(self, df, df_detail, dict_info)
                self.thread.start()
                self.thread.val_bar.connect(self.progress_loading)
                self.thread.val_state.connect(self.mark_state)
                self.thread.val_df.connect(self.view_chart)
            else:
                print(f"데이터 최대값 초과    {sys.maxsize=}    {self.length_index=}")
        #     self.thread.val_df.connect(self.view_chart)
        def progress_loading(self, val):
            self.QPB_bar.setValue(val)
            # if self.length_index == val: self.thread.stop()
        @pyqtSlot(dict)
        def mark_state(self,dict_state):
            self.QL_state.setText(dict_state['상태'])
            self.QL_wallet.setText(str(dict_state['잔고']))
            self.QL_ror.setText(str(dict_state['수익률']))
            self.QL_benefit.setText(str(dict_state['수익금']))
        def view_chart(self, df):
            if (df['잔고'] == df.loc[df.index[0], '잔고']).all():
                print('잔고 변함 없음 매수 0 회')
                QMessageBox.about(self, '알람', '잔고 변함 없음 매수 0 회')

            else:
                df['index'] = compare_price(df['종가'], df['strategy'])
                # df.index = df.index.astype(str).str[:10]

                # df['holding'] = np.log1p(df['holding'])
                df['ror'] = (df['종가'] - df['시가'][0]) / df['시가'][0]
                df['holding'] = bet + (df['ror'] * bet)
                amount = round(df['수익금'].sum(), 4)
                games = df['수익금'].count()

                # plt.xlabel('date')
                # plt.ylabel('수익금')
                # plt.plot(df.index,df['asset'])rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
                df.plot(y=['strategy', 'index', 'holding'],
                        # logy=True,
                        # ylim=(30000000, 100000000),
                        figsize=(16, 9),
                        grid=True, xlabel=f'종목명: {ticker}, 총 수익금: {amount}, 거래횟수: {games}', ylabel=f'가격', )
                plt.text(200, 500, f'종목명: {ticker}, 총 수익금:{amount}, 거래횟수: {games}')
                plt.title('numpy')
                plt.legend()
                print(f'총 수익금:{amount}')
                print(f'총 걸린시간: {(time.time() - start_time)}')

                plt.show()
        # def closeEvent(self, event):
        #     # 창을 닫으려 할 때, 닫지 않고 무시
        #     event.ignore()
        #     print("창을 닫을 수 없습니다. 창을 닫으려면 다른 방법을 사용하세요.")


    start_time = time.time()

    # market = '코인'
    # ticker = 'BTC'
    market = '국내주식'
    ticker = '122630'
    # market = '국내선옵'
    # ticker = '201VA355'
    # ticker = '코스피200선물'

    bong = '일봉'
    bong_detail = '5분봉'
    min = min_QCB(True)

    frdate = '2010-01-01'
    todate = datetime.datetime.now().strftime('%Y-%m-%d')
    # frdate = '2022-06-28'
    # todate = '2024-01-03'
    long = 'long'
    conn = sqlite3.connect('DB/strategy.db')
    locals_dict_buy = {}
    if market == '코인':
        bet = 100
        df_stg = pd.read_sql(f"SELECT * FROM 'coin_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_buy_text = df_stg.loc['매수','전략코드']
        df_stg = pd.read_sql(f"SELECT * FROM 'coin_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        conn.close()
        stg_sell_text = df_stg.loc['매도','전략코드']
        conn_DB = sqlite3.connect('DB/DB_bybit.db')
        exchange,exchange_pybit = common_def.make_exchange_bybit(False)
        stocks_info = pd.DataFrame()
        trade_market = 'bybit'
        증거금률 = stg_buy_text.split("\n", 3)[2]  # 첫줄 읽기 추출
        exec(증거금률, None, locals_dict_buy)
        증거금률 = locals_dict_buy.get('레버리지')
        direction = stg_buy_text.split("\n", 4)[3]  # 첫줄 읽기 추출
        exec(direction, None, locals_dict_buy)
        direction = locals_dict_buy.get('방향')
        거래승수 = 1

    elif market == '국내주식' or market == '국내선옵':
        bet = 1_000_000
        df_stg = pd.read_sql(f"SELECT * FROM 'stock_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_buy_text = df_stg.loc['매수','전략코드']
        df_stg = pd.read_sql(f"SELECT * FROM 'stock_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        conn.close()
        stg_sell_text = df_stg.loc['매도','전략코드']
        exchange = common_def.make_exchange_kis(f"모의{market[-2:]}")

        if market == '국내주식':
            conn_DB = sqlite3.connect('DB/DB_stock.db')
            stocks_info = pd.read_sql(f"SELECT * FROM 'stocks_info'", conn_DB).set_index('종목코드')
            trade_market = stocks_info.loc[ticker, '시장구분']
            거래승수 = 1
        elif market == '국내선옵':
            conn_DB = sqlite3.connect('DB/DB_futopt.db')
            trade_market = '선물' if ticker[:1] == '1' else '옵션'
            dic_multiplier = {'101': 250000, '201': 250000, '301': 250000, '209': 250000, '309': 250000,
                              '2AF': 250000, '3AF': 250000,  # 코스피200
                              '105': 50000, '205': 50000, '305': 50000,  # 미니코스피200
                              '106': 10000, '206': 10000, '306': 10000,  # 코스닥150
                              }
            거래승수 = dic_multiplier[ticker[:3]]

    else:
        conn_DB = ''
        stocks_info = pd.DataFrame()
        stg_buy_text = ''
        stg_sell_text = ''
    print(stg_buy_text)
    print(stg_sell_text)
    print('============' * 5)

    stg_buy = replace_tabs_with_spaces(stg_buy_text)
    stg_sell = replace_tabs_with_spaces(stg_sell_text)

    dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                       '주봉': 10080}
    dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉': '4h',
                      '일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
    dict_bong_reverse = dict(zip(dict_bong.values(), dict_bong.keys()))

    st = time.time()

    division_buy = stg_buy_text.split("\n", 1)[0]  # 첫줄 읽기 추출
    exec(division_buy, None, locals_dict_buy)
    division_buy = locals_dict_buy.get('분할매수')
    division_sell = stg_buy_text.split("\n", 2)[1]  # 첫줄 읽기 추출
    exec(division_sell, None, locals_dict_buy)
    division_sell = locals_dict_buy.get('분할매도')

    dict_info = {'market': market, 'ticker': ticker, 'bong': bong, 'bong_detail': bong_detail, 'bet': bet,
                 'start_day': frdate, 'end_day': todate, 'connect': conn_DB, 'dict_bong': dict_bong,'stg_buy': stg_buy,'stg_sell': stg_sell,
                 'dict_bong_reverse': dict_bong_reverse, 'trade_market':trade_market, 'exchange':exchange,
                 'division_buy': division_buy, 'division_sell': division_sell, 'direction':direction,'거래승수':거래승수,
                 '증거금률':증거금률}


    # df, df_detail, save = get_df_multi(dict_info)
    # df, df_detail, save = make_df(dict_info)

    # df = common_def.import_sql('DB/bt.db','df')
    # df_detail = common_def.import_sql('DB/bt.db','df_detail')
    # df.index = pd.to_datetime(df.index)
    # df_detail.index = pd.to_datetime(df_detail.index)
    # df_detail['장시작시간'] = pd.to_datetime(df_detail['장시작시간'])
    # df_detail['장종료시간'] = pd.to_datetime(df_detail['장종료시간'])
    # df_detail['현재시간'] = pd.to_datetime(df_detail['현재시간'])
    # df_detail['종료시간'] = pd.to_datetime(df_detail['종료시간'])

    # df = pd.DataFrame()
    # df_detail = pd.DataFrame()

    # df = df[df.index >= datetime.datetime.strptime("20240101","%Y%m%d")]
    # common_def.export_sql(df,'df')

    # print(df_detail)
    # print(f"데이터로딩 걸린시간{time.time()-st}")
    # if '시가_x' in df_detail.columns.tolist():
    #     print('데이터프레임 확인')
    #     quit()
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    # app = QApplication(sys.argv)
    app = QApplication([])

    main_table = Window(dict_info)
    main_table.show()
    sys.exit(app.exec_())

    # df_detail.to_sql('get_df_multi', sqlite3.connect('DB/bt.db'), if_exists='replace')

