#import ATOM_chart
import tab_chart_table
import sqlite3
import pandas as pd
import math
import numpy as np
from pprint import pprint
#import inspect
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
from collections import defaultdict
# import ATOM_stg_numpy
# np.set_printoptions(threshold=784,linewidth=np.inf)
np.set_printoptions(threshold=np.inf, linewidth=np.inf) #넘파이 행렬 전체 다 보기
# 현재가=1
# 시가=1
# 고가=1
# 저가=1
# 등락율=1
# 당일거래대금=1
# 체결강도=1
# 거래대금증감=1
# 전일비=1
# 회전율=1
# 전일동시간비=1
# 시가총액=1
# 라운드피겨위5호가이내=1
# 초당매수수량=1
# 초당매도수량=1
# VI해제시간=1
# VI가격=1
# VI호가단위=1
# 초당거래대금=1
# 고저평균대비등락율=1
# 매도총잔량=1
# 매수총잔량=1
# 매도호가5=1
# 매도호가4=1
# 매도호가3=1
# 매도호가2=1
# 매도호가1=1
# 매수호가1=1
# 매수호가2=1
# 매수호가3=1
# 매수호가4=1
# 매수호가5=1
# 매도잔량5=1
# 매도잔량4=1
# 매도잔량3=1
# 매도잔량2=1
# 매도잔량1=1
# 매수잔량1=1
# 매수잔량2=1
# 매수잔량3=1
# 매수잔량4=1
# 매수잔량5=1
# 매도수5호가잔량합=1
# 이평=1
# 이평60=1
# 이평300=1
# 이평600=1
# 이평1200=1
# 체결강도평균=1
# 최고체결강도=1
# 최저체결강도=1
# 초당거래대금평균=1
# # 전일비각도=1
# VI아래5호가=1
# 초당순매수금액=1
# 초당순매도금액=1
# 수익률 =1
# 최고수익률 =1
# 최저수익률 =1


def 누적초당매수수량(pre):
    np_tik = np_tik_ar[:, list_columns.index('초당매수수량')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.sum(rolling, axis=1)
    return np.append(np.zeros(pre-1) + np.nan, np_arr[:])

def 누적초당매도수량(pre):
    np_tik = np_tik_ar[:, list_columns.index('초당매도수량')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.sum(rolling, axis=1)
    return np.append(np.zeros(pre-1) + np.nan, np_arr[:])

def 전일비각도(pre):
    n_jvp=np.concatenate((np.full(pre-1, np.nan),np_tik_ar[: - pre+1, list_columns.index('전일비')]))
    jvp=np_tik_ar[:, list_columns.index('전일비')]
    jvp_gap = (jvp) - (n_jvp)
    jvp = lambda x: round(math.atan2(x, pre) / (2 * math.pi) * 360, 2)
    cal_jvp = np.vectorize(jvp)
    return cal_jvp(jvp_gap)

def 당일거래대금각도(pre):
    n_jvp=np.concatenate((np.full(pre-1, np.nan),np_tik_ar[: - pre+1, list_columns.index('당일거래대금')]))
    # jvp_gap = 당일거래대금 - np_tik_ar[-(pre), list_columns.index('당일거래대금')]
    jvp_gap = (np_tik_ar[:, list_columns.index('당일거래대금')]) - n_jvp
    jvp = lambda x: round(math.atan2(x, pre) / (2 * math.pi) * 360, 2)
    cal_jvp = np.vectorize(jvp)
    return cal_jvp(jvp_gap)

def 구간최고시가(pre):
    np_tik = np_tik_ar[:, list_columns.index('시가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저시가(pre):
    np_tik = np_tik_ar[:, list_columns.index('시가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최고고가(pre):
    np_tik = np_tik_ar[:, list_columns.index('고가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저고가(pre):
    np_tik = np_tik_ar[:, list_columns.index('고가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최고저가(pre):
    np_tik = np_tik_ar[:, list_columns.index('저가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저저가(pre):
    np_tik = np_tik_ar[:, list_columns.index('저가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최고종가(pre):
    try:
        np_tik = np_tik_ar[:, list_columns.index('종가')]
        shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
        strides = np_tik.strides + (np_tik.strides[-1],)
        rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
        np_arr = np.max(rolling,axis=1)
        return np.append(np.zeros(pre-1)+np.nan,np_arr[:])
    except:
        return np.array([np.nan for x in range(len(np_tik))])

def 구간최저종가(pre):
    try:
        np_tik = np_tik_ar[:, list_columns.index('종가')]
        shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
        strides = np_tik.strides + (np_tik.strides[-1],)
        rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
        np_arr = np.min(rolling, axis=1)
        return np.append(np.zeros(pre-1)+np.nan,np_arr[:])
    except:
        return np.array([np.nan for x in range(len(np_tik))])

def 구간최고시가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('시가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저시가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('시가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최고고가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('고가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저고가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('고가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최고저가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('저가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저저가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('저가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최고종가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('종가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 구간최저종가N(pre,N):
    np_tik = np_tik_ar[:, list_columns.index('종가')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.min(rolling, axis=1)
    np_arr = np.roll(np_arr,shift=N,axis=None)
    np_arr[:N] = np_arr[N]
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 최고초당매수수량(pre):
    np_tik = np_tik_ar[:, list_columns.index('초당매수수량')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])
    # return np_tik_ar[-(pre):, list_columns.index('초당매수수량')].max()

def 최고초당매도수량(pre):
    np_tik = np_tik_ar[:, list_columns.index('초당매도수량')]
    shape = np_tik.shape[:-1] + (np_tik.shape[-1] - pre + 1, pre)
    strides = np_tik.strides + (np_tik.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(np_tik, shape=shape, strides=strides)
    np_arr = np.max(rolling,axis=1)
    return np.append(np.zeros(pre-1)+np.nan,np_arr[:])

def 누적초당매수수량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('누적초당매수수량_avg')]))

def 누적초당매도수량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('누적초당매도수량_avg')]))

def 전일비각도N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('전일비각도_avg')]))

def 당일거래대금각도N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('당일거래대금각도_avg')]))

def 등락율N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('등락율')]))

def 고저평균대비등락율N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('고저평균대비등락율')]))

def 초당거래대금N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('초당거래대금')]))

def 초당거래대금평균N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('초당거래대금평균')]))

def 당일거래대금N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('당일거래대금')]))

def 종가N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('종가')]))
def 고가N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('고가')]))
def 저가N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('저가')]))
def 시가N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('시가')]))
def 초당매수수량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('초당매수수량')]))

def 초당매도수량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('초당매도수량')]))

def 매수총잔량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('매수총잔량')]))

def 매도총잔량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('매도총잔량')]))

def 매수잔량1N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('매수잔량1')]))

def 매도잔량1N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('매도잔량1')]))

def 매도수5호가잔량합N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('매도수5호가잔량합')]))
def 이평20N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('이평20')]))
def 이평60N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('이평60')]))

def 이평300N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('이평300')]))

def 이평600N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('이평600')]))

def 이평1200N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('이평1200')]))

def 거래대금증감N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('거래대금증감')]))

def 전일비N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('전일비')]))

def 회전율N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('회전율')]))

def 전일동시간비N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('전일동시간비')]))

def 이평5N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('이평5')]))
def 거래량N(pre):
    return np.concatenate((np.full(pre, np.nan),np_tik_ar[: - pre, list_columns.index('거래량')]))
# def 일봉(candle):
#     df = pd.DataFrame(index=list_idx, data=candle, columns=['상세시가'])
#     print(df)
#     df_daily = resample_df(df, 'D')
#     print(df_daily)
#     quit()
# def MA(pre):
#     np_tik = np_tik_ar[:, list_columns.index('현재가')]
#     np_tik = np.convolve(np_tik, np.ones(pre), 'valid') / pre
#     return np.append( np.zeros(pre-1)+np.nan,np_tik[:])


# def resample_df(df, rule):
#     ohlc_dict = {'상세시가': 'first',
#         '상세고가': 'max',
#         '상세저가': 'min',
#         '상세종가': 'last',
#         '상세거래량': 'sum',
#         # '상세거래대금': 'sum'
#     }
#     df = df.resample(rule).apply(ohlc_dict).dropna()
#     return df

# def chart_get(df,factor):
#     global list_columns
#     global np_tik_ar
#
#     np_tik_ar = df.to_numpy() #전체 데이터를 np로 저장
#     list_columns = df.columns.tolist() #컬럼명을 리스트로 저장
#     # print(np_tik_ar)
#     # print(list_columns)
#     if factor in list_columns:
#         val = np_tik_ar[:, list_columns.index(factor)]
#     elif not factor in list_columns and factor[:2] != '부호' and factor[:2] != '비교':  # 비교, 부호가 아닐경우
#         factor_val = 'val=' + factor  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
#         locals_dict_vars = {}
#         exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
#         val = locals_dict_vars.get('val')
#     elif factor[:2] == '비교' or factor[:2] == '부호':
#         mark = factor[:2]
#         factor_split = factor[3:]
#         factor1 = factor_split[:factor_split.index('_')]  # factor 값 얻기 (ex:현재가)
#         factor2 = factor_split[factor_split.index('_') + 1:]  # 위치 값 얻기 (ex:매수가)
#         if factor1 in list_columns:
#             val1 = np_tik_ar[:, list_columns.index(factor1)]
#         else:
#             factor_val = 'val=' + factor1  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
#             locals_dict_vars = {}
#             exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
#             val1 = locals_dict_vars.get('val')
#         if factor2 in list_columns:
#             val2 = np_tik_ar[:, list_columns.index(factor2)]
#         else:
#             factor_val = 'val=' + factor2  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
#             locals_dict_vars = {}
#             exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
#             val2 = locals_dict_vars.get('val')
#         if mark == '비교':
#             i_min = np.nanmin(val1)  # nan을 제외한 넘파이 최소값
#             i_max = np.nanmax(val1)
#             o_min = np.nanmin(val2)
#             o_max = np.nanmax(val2)
#             lfunc = lambda x: (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # map()함수 정의.
#             val = lfunc(val1)
#         elif mark == '부호':
#             val = np.where(~np.isnan(val2), val1, val2)  # val2에서 nan이 아닌 인데스를 val1로 채움
#     return val




def chart_np(df,df_chart_table):  #차트 연상용

    # global np_tik
    global list_columns
    global list_idx
    global np_tik_ar
    # print(df)
    # print(df.dtypes)
    # 데이터타입이 object 이거나 전부 nan으로 되어있는열이 있으면 에러발생하기 때문에 그런열은 삭제 해줘야 됨
    # df.drop('date',axis=1,inplace=True)
    # df.drop('전략수익률',axis=1,inplace=True)
    # print(df)


    np_tik_ar = df.to_numpy() #전체 데이터를 np로 저장
    list_columns = df.columns.tolist() #컬럼명을 리스트로 저장
    list_idx = df.index.tolist()
    # print(np_tik_ar)
    # print(list_columns)
    for factor in list_columns:
        globals()[f'{factor}'] = np_tik_ar[:,list_columns.index(str(factor))]

    dict_plot = defaultdict(dict)
    # print(dict_plot)
    for plot in df_chart_table.index:    # p0_0, 0_1
        chart_factor = df_chart_table.loc[plot,'chart']  #chart_factor = 현재가, 시가, 고가
        # chart_factor = chart_factor.replace(' ','')
        list_factor = chart_factor.splitlines()    #리스트로 나누기
        for i in range(len(list_factor)):
            if ',' in list_factor[i]:
                list_factor = list_factor + list_factor[i].split(',') #팩터가 쉼표로 구분되어있으면 원소로 나눠서 추가
                list_factor = [x for x in list_factor if str(x) != ' ']  # ''이 아닌 원소 없애기
                del list_factor[i]
        # for i in range(len(list_factor)):
        #     if '틱수' in list_factor[i]:
        #         list_factor[i]=list_factor[i].replace('틱수','30')
        # try:
        list_factor = [x for x in list_factor if str(x) != '']  # ''이 아닌 원소 없애기
        list_factors = [x for x in list_factor if str(x)[0] != '#']  # 첫번째 행이 '#'이 아닌 원소 없애기
        # except:
        dict_factor = defaultdict(lambda: np.zeros(len(df.index))) #딕셔녀리 생성을 위한 초기화
        for fac in list_factors: # 최종적으로 딕셔너리에 저장하는건 원래이름으로 하기위해 fac 과 factor을 구분
            if '.cl'in fac:
                factor = fac[:fac.rindex('.cl')]
            elif '.fill' in fac:
                factor = fac[:fac.rindex('.fill')]
            else:
                factor = fac

            # print(list_columns)
            if (factor in list_columns) and factor!='매수가' and factor !='매도가' and factor !='전략매수' and \
                    factor !='전략매도' and factor !='맥점매수' and factor !='맥점매도':
                # print(f'1 - {factor}')
                dict_factor[fac] = np_tik_ar[:, list_columns.index(factor)]
            elif (not '_종가' in factor) and factor!='매수가' and factor!='매도가' and factor!='전략매수' and factor!='전략매도' and factor!='맥점매수' and factor!='맥점매도':  # 비교, 부호가 아닐경우
                # print(f'2 - {factor}')
                factor_val = 'val=' + factor  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
                locals_dict_vars = {}
                # print(factor_val)
                # print(f"elif (not '_' in factor) and factor!='매수nd factor! {fac}")
                try:
                    exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
                except:
                    print('에라_',factor_val)
                dict_factor[fac] = locals_dict_vars.get('val')
            # elif '_' in factor: #비교 compare 차트 현재 시가_30분봉 같이 언더바 들어가는 팩터가있기 때문에 사용 안됨
            #     # print(f'3 - {factor}')
            #     # mark = factor[:2]
            #     # if factor[:2] == '비교':
            #     # if '_' in factor:
            #     # factor_split = factor[3:]
            #     factor1 = factor[:factor.index('_')]  # factor 값 얻기 (ex:체결강도)
            #     factor2 = factor[factor.index('_') + 1:]  # 비교 값 얻기 (ex:현재가)
            #     if factor1 in list_columns:
            #         val1 = np_tik_ar[:, list_columns.index(factor1)]
            #
            #     else:
            #         factor_val = 'val=' + factor1  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
            #         locals_dict_vars = {}
            #         exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
            #         val1 = locals_dict_vars.get('val')
            #         if True in val1: #데이터가 True 또는 False 로 이루어져 있을 경우 1, 0 으로 변환
            #             val1 = np.where(val1==True,1,0)
            #     if factor2 in list_columns:
            #         val2 = np_tik_ar[:, list_columns.index(factor2)]
            #     else:
            #         factor_val = 'val=' + factor2  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
            #         locals_dict_vars = {}
            #         exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
            #
            #         val2 = locals_dict_vars.get('val')
            #     # print(factor1,' | ',val1)
            #     # print(factor2, ' | ', val2)
            #
            #     o_min = np.nanmin(val1)
            #     o_max = np.nanmax(val1)
            #     i_min = np.nanmin(val2)  # nan을 제외한 넘파이 최소값
            #     i_max = np.nanmax(val2)
            #     # print(f'{o_min}, {o_max}, {i_min}, {i_max}')
            #     # print(dict_factor)
            #     # print(fac)
            #     # print(val2)
            #     lfunc = lambda x: (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # map()함수 정의.
            #     dict_factor[fac] = lfunc(val2)
            elif factor =='매수가' or factor =='매도가' or factor =='청산신호' or factor =='진입신호' \
                or factor =='맥점매수' or factor =='맥점매도':
                # np.isnan(np.array([np.nan, 0], dtype=object))
                # print(f'4 - {factor}')
                if factor in list_columns:
                    # print('if')
                    factor_val = np_tik_ar[:, list_columns.index(factor)]
                    # print('---------')
                    # print(factor_val)
                    # print(type(factor_val))
                else:
                    # print('else')
                    factor_val = 'val=' + factor  # 나중에 locals_dict_vars.get('val') 으로 값을 가져오기 위해 'val' 추가
                    locals_dict_vars = {}
                    # try:
                    exec(factor_val, None, locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
                    factor_val = locals_dict_vars.get('val')
                    # print(f"{factor_val= }")
                    # except:
                    #     pass
                if dict_factor: #테이블이 비어있지 않을 때만 진행
                    first_key = list(dict_factor.keys())[0]
                    compare_val=dict_factor[first_key]
                    # print(len(factor_val))
                    # print(len(compare_val))
                    if not first_key == '종가':
                        dict_factor[fac] = np.where(~np.isnan(factor_val), compare_val, factor_val)  # factor_val에서 nan이 아닌 인덱스를 compare_val로 채움(매수가에있는 가격을 종가로 채운다는 얘기임)
                    else:
                        dict_factor[fac] = factor_val
                    # dict_factor[fac] = np.where(np.isnan == factor_val, compare_val, factor_val)  # factor_val에서 nan이 아닌 인덱스를 compare_val로 채움
                    # print(dict_factor[fac])
                # print(val2)
                # print(val1)
                # df_val = pd.DataFrame()
                # df_val['1'] = val2
                # df_val['2'] = val1
                # print(df_val)
                # df_val['3'] = dict_factor[fac]
                # table_PYQT_2.df_check1(df_val,fac)
            else:
                print(f'5 - {factor}    이상허다     {plot}')
        dict_plot[plot] = dict_factor
    return dict_plot


if __name__ == '__main__':
    from PyQt5.QtWidgets import *
    import sys
    app = QApplication(sys.argv)
    conn = sqlite3.connect('DB/bt.db')
    df = pd.read_sql(f"SELECT * FROM 'bt'", conn).set_index('날짜')
    conn.close()
    df.index = pd.to_datetime(df.index)  # datime형태로 변환

    conn = sqlite3.connect('DB/chart_table.db')
    df_chart_table = pd.read_sql(f"SELECT * FROM '국내주식'", conn).set_index('index')
    conn.close()
    dict_plot = chart_np(df, df_chart_table)
    print(dict_plot)
    tab_chart = tab_chart_table.Window()
    tab_chart.chart_show(df, dict_plot)
    print('asdf')
    sys.exit(app.exec_())