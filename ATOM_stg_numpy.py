#import numba
#import sys
import sqlite3
import pandas as pd
import math
import numpy as np
from datetime import datetime,timedelta
# import edit_stg
#import inspect
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
#import getpass
#import pyupbit
#import re
import time
import talib
#from pykrx import stock
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
#from pprint import pprint
import ccxt
# import cal_krx
class Bong():
    def __init__(self,df):
        # print(df)
        self.df = df
        self.df['이평20'] = talib.MA(self.df['종가'],20)
    def 이평(self):
        print('이평')
        print(self.df)

현재가=1
현재시간 = 1
시가=1
고가=1
저가=1
종가=1
거래량=1
거래대금=1
종료시간 = datetime.now().strftime('%Y-%m-%d')
NAV=1
거래량이평3=1
등락율=1
시가총액=1
이평=1
수익률 =1
최고수익률 =1
최저수익률 =1
이격도20이평 = 1
시장가 = '시장가'
# 매수1 = np.nan
# 매수2 = np.nan
# 매수3 = np.nan
# 매수4 = np.nan
# 매수5 = np.nan
# 분할매수 = [0,0,0,0,0]


def 구간최고시가(pre):
    return np_tik[-(pre):, list_columns.index('시가')].max()
def 구간최저시가(pre):
    return np_tik[-(pre):, list_columns.index('시가')].min()
def 구간최고고가(pre):
    return np_tik[-(pre):, list_columns.index('고가')].max()
def 구간최저고가(pre):
    return np_tik[-(pre):, list_columns.index('고가')].min()
def 구간최고저가(pre):
    return np_tik[-(pre):, list_columns.index('저가')].max()
def 구간최저저가(pre):
    return np_tik[-(pre):, list_columns.index('저가')].min()
def 구간최고종가(pre):
    return np_tik[-(pre):, list_columns.index('종가')].max()
def 구간최저종가(pre):
    return np_tik[-(pre):, list_columns.index('종가')].min()
def 구간최고시가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('시가')].max()
def 구간최저시가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('시가')].min()
def 구간최고고가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('고가')].max()
def 구간최저고가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('고가')].min()
def 구간최고저가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('저가')].max()
def 구간최저저가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('저가')].min()
def 구간최고종가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('종가')].max()
def 구간최저종가N(pre,N):
    return np_tik[-(pre):row_tik-N, list_columns.index('종가')].min()
def 시가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('시가')]
def 고가N(pre):
    if 데이터길이 <= pre:
        return np.nan
        # return np_tik_ar[row_tik, list_columns.index('고가')]
    return np_tik_ar[row_tik - pre, list_columns.index('고가')]
def 저가N(pre):
    if 데이터길이 <= pre:
        return np.nan
        # return np_tik_ar[row_tik, list_columns.index('저가')]
    return np_tik_ar[row_tik - pre, list_columns.index('저가')]
def 종가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('종가')]
def 이평5N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('이평5')]
def 이평20N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('이평20')]
def 이평60N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('이평60')]
def 거래량N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('거래량')]
def 거래량이평3N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('거래량이평3')]
def 거래량이평20N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('거래량이평20')]
def 거래량이평60N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('거래량이평60')]
def RSI14N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('RSI14')]
def RSI18N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('RSI18')]
def RSI30N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('RSI30')]
def ATR10N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('ATR10')]
def TRANGEN(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('TRANGE')]
def 이격도20이평N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('이격도20이평')]
def 밴드20상N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('밴드20상')]
def 밴드20중N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('밴드20중')]
def 밴드20하N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('밴드20하')]
# def 인덱스F(fore):
#     if len(np_tik_ar) == 데이터길이:
#         return np.nan
#     return np_tik_ar[row_tik + fore, list_columns.index('인덱스')]

# def 전일비각도(pre):
#     print('전일비각도')
#     try:
#         jvp_gap = 전일비 - np_tik[-(pre), list_columns.index('전일비')]
#         return round(math.atan2(jvp_gap, pre) / (2 * math.pi) * 360, 2)
#     except:
#         print('에러')
#         return 0
#
# def 당일거래대금각도(pre):
#     print('당일거래대금각도')
#     try:
#         dmp_gap = 당일거래대금 - np_tik[-(pre), list_columns.index('당일거래대금')]
#         return round(math.atan2(dmp_gap, pre) / (2 * math.pi) * 360, 2)
#     except:
#         return 0


def 등락율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('등락율')]
def 변화율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('변화율')]
def 수익률N(pre):
    if 데이터길이 <= pre:
        return np.nan
    # print(ror[:row_tik])
    # print(ror[row_tik])
    # print(pre)
    return ror[row_tik - pre]


def 고저평균대비등락율N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('고저평균대비등락율')]


def 당일거래대금N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('당일거래대금')]


def 현재가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('현재가')]


def moving_average(np_arry, w):
    return np.convolve(np_arry, np.ones(w), 'valid') / w

def 이평(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('종가')]/pre




# class get_db:
#     def __init__(self, ticker,idx):
#         conn = sqlite3.connect('DB_krx.db')
#         self.df = pd.read_sql(f"SELECT * FROM '{ticker}'", conn).set_index('날짜')
#         self.df.index = pd.to_datetime(self.df.index)  # datime형태로 변환
#         self.idx = idx
#     def 종가(self):
#         return self.df.loc[self.idx,'종가']



def strategy_np(market,exchange, ticker, bong, stg_buy, stg_sell, bet, start_day, end_day,QPB_bar):
    def chegyeol_buy_bybit(매수, 매수가, 레버리지):
        잔고 = wallet[row_tik - 1]
        배팅금액 = 잔고 * (매수 / 100) * 레버리지
        매수수량 = (100 - (fee_market * 레버리지)) / 100 * 배팅금액 / 매수가
        매수수량 = float(exchange.amount_to_precision(ticker, 매수수량))

        매수금액 = 매수수량 * 매수가
        매수수수료 = round(매수금액 * fee_market / 100, 4)
        잔고 = round(잔고 - (매수금액 / 레버리지) - 매수수수료, 4)

        qty[row_tik] = 매수수량
        price_buy[row_tik] = 매수금액
        fee_sum[row_tik] = 매수수수료
        wallet[row_tik] = 잔고
        # print(f'{잔고= }, {매수금액= }')

        return 매수수량, 매수금액

    def chegyeol_sell_bybit(매도가,매수수량,매수금액, 레버리지,잔고):
        매도금액 = 매도가 * 매수수량
        매수수수료 = round(매수금액 * fee_market / 100, 4)
        매도수수료 = round(매도금액 * fee_market / 100, 4)
        수익금 = round(매도금액 - 매수금액 - 매도수수료, 4)
        수익률 = round(((수익금 - 매수수수료) / 매수금액 * 100) * 레버리지, 2)
        잔고 = round(잔고 + (매수금액 / 레버리지) + 수익금,4)  ##매수수수료는 매수하면서 이미 냈음
        wallet[row_tik] = 잔고
        자산 = 잔고
        asset[row_tik] = 자산
        ror[row_tik] = 수익률
        price_sell[row_tik] = 매도금액
        benefit[row_tik] = 수익금
        수수료 = 매수수수료+매도수수료
        fee_sum[row_tik] = 수수료
        return 수익률



    def cal_ror_bybit(레버리지, 분봉1_고가, 분봉1_저가, 분봉1_종가, 매수수량, 매수금액, 잔고):
        if 방향 == 'long':
            매수수수료 = round(매수금액 * fee_market / 100, 0)
            매도수수료 = round(매수수량 * 분봉1_종가 * fee_market / 100, 0)
            평가금액 = 매수수량 * 분봉1_종가 - 매도수수료
            수익금 = round(평가금액 - 매수금액 - 매도수수료, 4)
            최고평가금액 = 매수수량 * 분봉1_고가 - 매도수수료
            최저평가금액 = 매수수량 * 분봉1_저가 - 매도수수료
        try:
            수익률 = round(((수익금-매수수수료) / 매수금액 * 100)*레버리지, 2)
        except: '배팅금액 확인'
        최고수익률 = round(((최고평가금액 - 매수금액) / 매수금액 * 100)*레버리지, 2)
        최저수익률 = round(((최저평가금액 - 매수금액) / 매수금액 * 100)*레버리지, 2)
        ror_max[row_tik] = float(np.where(최고수익률 > ror_max[row_tik], 최고수익률, ror_max[row_tik]))
        ror_min[row_tik] = float(np.where(최저수익률 < ror_min[row_tik], 최저수익률, ror_min[row_tik]))
        자산 = round(잔고 + (매수금액/레버리지) + 수익금,4)
        # print(f'{잔고}, {매수금액/레버리지}, {수익금}, {자산}')
        ror[row_tik] = 수익률
        asset[row_tik] = 자산
        최고수익률 = ror_max[row_tik]
        최저수익률 = ror_min[row_tik]
        list_ror.append(수익률)
        list_ror_max.append(최고수익률)
        list_ror_min.append(최저수익률)
        return 수익률, 최고수익률, 최저수익률




    def get_list(df,df_1m,row_tik):
        idx_start = df.index[row_tik]
        if not row_tik == len(df) - 1:  # 마지막행이 아닐 경우
            idx_end = df.index[row_tik + 1]  # 이 부분은 확인해봐야 될 부분
            df_check = df_1m[idx_start:idx_end]
        else:
            start = df.index[row_tik]
            pre = df.index[row_tik - 1]
            cha = start - pre
            if start + cha <= df_1m.index[-1]:  # 1분봉 데이터가 더 최근 데이터를 포함하고 있을 경우
                df_check = df_1m[start:start + cha]
            else:
                df_check = df_1m[start:]
        list_open = df_check['시가'].tolist()[:-1]
        list_high = df_check['고가'].tolist()[:-1]
        list_low = df_check['저가'].tolist()[:-1]
        list_close = df_check['종가'].tolist()[:-1]
        list_now = df_check.index.tolist()[:-1]

        return list_open, list_high, list_low, list_close, list_now, df_check


    """                            여기서부터 코드 시작                             """

    # if market == '코스피' or market == '코스닥' or market == 'etf' or market == 'ETF':
    dict_bong = {'1분봉':'1m','3분봉':'3m','5분봉':'5m','30분봉':'30m','4시간봉':'4h','일봉':'d','주봉':'w'}

    if market == '코스피' or market == '코스닥' or market == 'etf' :
        fee_market = 0.015
        tax = 0.018

        db_file = 'DB/DB_krx.db'
        con_db = sqlite3.connect(db_file)
        cursor = con_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
        table_list = np.concatenate(table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
        if ticker == '전체':
            print('전체에 대한 백테스트 적용 안됨')
        ticker_bong = ticker + '_' + dict_bong[bong]
        ticker_1m = ticker + '_' + dict_bong['5분봉']
        ticker = ticker + 'USDT'
        print(f"{datetime.fromtimestamp(time.time())} - {ticker} {ticker_bong}")
        if ticker_bong in table_list:
            df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", con_db).set_index('날짜')
            df.index = pd.to_datetime(df.index)  # datime형태로 변환
            df['인덱스'] = df.index  # 차트에서 이상하게 나오기 때문에 나중에 없애야 됨
            print('DF 읽어오기 완료..')
            df_1m = pd.read_sql(f"SELECT * FROM '{ticker_1m}'", con_db).set_index('날짜')
            df_1m.index = pd.to_datetime(df_1m.index)  # datime형태로 변환
            df_1m.index = df_1m.index - timedelta(minutes=5)
            print('5분봉 읽어오기 완료..')
        else:
            print('데이터 확인 요망')
            raise

        length = len(df.index)
        if ticker == '122630':
            market = 'etf'

    elif market == '코인':
        fee_limit = 0.02
        fee_market = 0.055

        # start_time = exchange.parse8601(f'{start_day}T00:00:00Z')
        # end_time = exchange.milliseconds()  # 현재 시간
        # total_data = []

        db_file = 'DB/DB_bybit.db'
        con_db = sqlite3.connect(db_file)
        cursor = con_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()  # fetchall 한번에 모든 로우 데이터 읽기 (종목코드 읽기)
        table_list = np.concatenate(table_list).tolist()  # 모든테이블을 리스트로변환 https://codechacha.com/ko/python-flatten-list/
        if ticker == '전체':
            print('전체에 대한 백테스트 적용 안됨')
        # symbol = str(ticker)[:ticker.index('_')]
        ticker_bong = ticker + '_' + dict_bong[bong]
        ticker_1m = ticker + '_' + dict_bong['1분봉']
        ticker_3m = ticker + '_' + dict_bong['3분봉']
        ticker_5m = ticker + '_' + dict_bong['5분봉']
        ticker_30m = ticker + '_' + dict_bong['30분봉']
        ticker = ticker + 'USDT'
        print(f"{datetime.fromtimestamp(time.time())} - {ticker} {ticker_bong}")
        if ticker_bong in table_list:
            df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", con_db).set_index('날짜')
            print('DF 읽어오기 완료..')
            df_1m = pd.read_sql(f"SELECT * FROM '{ticker_1m}'", con_db).set_index('날짜')
            print('1분봉 읽어오기 완료..')
            # print('1m')
            # df_3m = pd.read_sql(f"SELECT * FROM '{ticker_3m}'", con_db).set_index('날짜')
            # print('3m')
            # df_5m = pd.read_sql(f"SELECT * FROM '{ticker_5m}'", con_db).set_index('날짜')
            # print('5m')
            # df_30m = pd.read_sql(f"SELECT * FROM '{ticker_30m}'", con_db).set_index('날짜')
            # print('30m')
        else:
            print('데이터 확인 요망')
            raise
        exchange.fetch_tickers()

        df.index = pd.to_datetime(df.index)  # datime형태로 변환
        length = len(df.index)
        df['인덱스'] = df.index #차트에서 이상하게 나오기 때문에 나중에 없애야 됨
        df_1m.index = pd.to_datetime(df_1m.index)  # datime형태로 변환


    # 체크용 DF의 시작날짜와 마지막날짜로 자르기
    df = df[df.index >= df_1m.index[0]]
    df = df[df.index <= df_1m.index[-1]]


    start_day = datetime.strptime(start_day,'%Y-%m-%d')
    end_day = datetime.strptime(end_day,'%Y-%m-%d')
    df = df[df.index >= start_day]
    df = df[df.index <= end_day]
    # df = df[:23]
    # 분봉30 = Bong(df_30m)

    df['등락율'] = round((df['종가']-df['종가'].shift(1))/df['종가'].shift(1)*100,2)
    df['변화율'] = round((df['종가']-df['시가'])/df['시가']*100,2)
    df['이평5' ] = talib.MA(df['종가'],5)
    df['이평20'] = talib.MA(df['종가'],20)
    df['이평60'] = talib.MA(df['종가'],60)
    df['이평120'] = talib.MA(df['종가'],120)
    df['이평200'] = talib.MA(df['종가'],200)
    df['거래량이평3'] = talib.MA(df['거래량'],3)
    df['거래량이평20'] = talib.MA(df['거래량'],20)
    df['거래량이평60'] = talib.MA(df['거래량'],60)
    df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
    df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
    df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
    df['ATR10'] = talib.ATR(df['고가'],df['저가'],df['종가'], timeperiod=10)
    df['TRANGE'] = talib.TRANGE(df['고가'],df['저가'],df['종가'])
    df['이격도20이평'] = df['종가'].shift(1)/df['이평20'].shift(1)*100
    df['밴드20상'],df['밴드20중'],df['밴드20하'] = talib.BBANDS(df['종가'].shift(1),20,2)
    df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    # df['cnt'] = (df['고가'].shift(1).pct_change() > 0) & (df['저가'].shift(1).pct_change() > 0)
    # df['cnt_ma'] = df['cnt'].rolling(10).sum()
    # df['val_k'] = df['cnt_ma'] / 10


    global np_tik_ar
    global row_tik
    global list_columns
    global np_tik
    global 데이터길이
    global ror
    global state
    global 수익률
    global 최고수익률
    global 최저수익률
    global 매수가
    global 매도가
    global 시장가
    global 레버리지
    global 현재시간
    global 매수시간
    global 종료시간
    global 자산
    global list_ror
    global list_idx
    global list_ror_max
    global list_ror_min
    global val
    global val_k
    for i in range(20):
        globals()[f'매도{i}호가'] = f'매도{i}호가'
    for i in range(20):
        globals()[f'매수{i}호가'] = f'매수{i}호가'

    매도4호가='매도4호가'
    buy = [np.nan for x in range(len(df.index))]    #매수가
    sell = [np.nan for x in range(len(df.index))]   #매도가
    buy_order = [np.nan for x in range(len(df.index))]    #매수가
    sell_order = [np.nan for x in range(len(df.index))]   #매도가
    ror = [np.nan for x in range(len(df.index))]    #수익률
    ror_max = [np.nan for x in range(len(df.index))]    #최고수익률
    ror_min = [np.nan for x in range(len(df.index))]    #최저수익률
    ror_strategy = [np.nan for x in range(len(df.index))]    #최저수익률
    benefit = [np.nan for x in range(len(df.index))]    #수익금
    wallet = [np.nan for x in range(len(df.index))]    #잔고
    asset = [np.nan for x in range(len(df.index))]  #잔고
    qty = [np.nan for x in range(len(df.index))]    #보유수량
    fee_sum = [np.nan for x in range(len(df.index))]    #수수료
    price_buy = [np.nan for x in range(len(df.index))]  #총매수금액
    price_sell = [np.nan for x in range(len(df.index))] #총매도금액
    val = [np.nan for x in range(len(df.index))] #test
    val_k = [np.nan for x in range(len(df.index))] #test
    # total_hold = [np.nan for x in range(len(df.index))] #누적보유수량
    # total_buy_qty = [np.nan for x in range(len(df.index))] #누적매수수량
    # total_buy = [np.nan for x in range(len(df.index))]  #누적매수금액
    # total_sell = [np.nan for x in range(len(df.index))]  #누적매수금액
    # total_buy_per = [np.nan for x in range(len(df.index))]  #누적매수per

    # value_p = [np.nan for x in range(len(df.index))]
    분할매도수량 = []

    state = '매도'
    wallet[-1] = bet
    asset[-1] = bet
    np_tik_ar = df.to_numpy() #전체 데이터를 np로 저장
    list_columns = df.columns.tolist() #컬럼명을 리스트로 저장
    list_idx = df['인덱스'].tolist()
    # if market =='코인':
    df_1m['매수가'] = np.nan
    df_1m['매도가'] = np.nan
    df_1m['수익률'] = np.nan
    df_1m['최고수익률'] = np.nan
    df_1m['최저수익률'] = np.nan
    df_1m['state'] = np.nan
    print('데이터변환 완료..')
    for row_tik in range(len(df.index)):
        np_tik = np_tik_ar[:row_tik+1]
        wallet[row_tik] = wallet[row_tik - 1]
        asset[row_tik] = asset[row_tik - 1]


        for col in list_columns: #연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
            globals()[f'{col}'] = np_tik[row_tik,list_columns.index(f'{col}')]
        데이터길이 = row_tik+1
        # locals_dict_vars = {}
        locals_dict_buy = {}
        locals_dict_sell = {}



        ###################
        if state == '매도': # 미 보유 시 매수 주문
            exec(stg_buy,None,locals_dict_buy)
            매수 = locals_dict_buy.get('매수')
            if market == '코인':
                레버리지 = locals_dict_buy.get('레버리지')
                방향 = locals_dict_buy.get('방향')
            elif market == '코스피' or market == '코스닥' or market == 'etf' :
                방향 = 'long'
                레버리지 = 1
            if not 매수 == False: #매수 일 경우 None을 반환하기 때문에(매수신호 떳을 때)
                # print(f"{row_tik + 1} | {state=} - {asset[row_tik]=}")
                매수가 = locals_dict_buy.get('매수가')
                state = '매수주문'
                if type(매수가) == dict:
                    hoga_price = list(매수가.keys())[0]
                    hoga_rate = 매수가[hoga_price]
                    if market == '코인':
                        매수가 = float(exchange.price_to_precision(ticker, hoga_price + (hoga_price * hoga_rate / 100)))
                    elif market == '코스피' or market == '코스닥' or market == 'etf' or market == 'ETF':
                        매수가 = exchange.hogaPriceReturn(hoga_price, hoga_rate, market)
                elif 매수가 == 시장가:
                    매수가 = 시가
                else:
                    if market == '코인':
                        매수가 = float(exchange.price_to_precision(ticker, 매수가 ))
                    elif market == '코스피' or market == '코스닥' or market == 'etf' or market == 'ETF':
                        매수가 = exchange.hogaPriceReturn_per(매수가, 0, market)
                buy_order[row_tik] = 매수가


        ###################
        if state == '매수주문': #매수 체결 확인
            # print(f"{row_tik + 1} | {state=} - {asset[row_tik]=}")
            list_open, list_high, list_low, list_close, list_now, df_check = get_list(df,df_1m,row_tik)

            if 방향 == 'long' and 매수가 >= 저가:
                for i,close in enumerate(list_close):
                    if 매수가 >= list_low[i] and 매수가 <= list_high[i]:
                        # print(list_close[-1])
                        # 매수가 = list_close[i]  ##### 슬리피지 감안하여 종가가 매수가보다 높을경우 진입하며 매수가난 종가로 대입
                        state = '매수'
                        buy[row_tik] = 매수가
                        # print(f'{list_high[i]= }, {list_low[i]= }, {list_close[i]= }')
                        row_tik_buy = row_tik
                        매수시간 = df_check.index[i].to_pydatetime()
                        종료시간 = list_now[-1]
                        df_1m.loc[list_now[i],'매수가'] = 매수가
                        df_1m.loc[list_now[i],'state'] = state
                        # print(asset[row_tik])
                        매수수량, 매수금액 = chegyeol_buy_bybit(매수,매수가,레버리지)
                        list_open = list_open[i:] #체결되는 1분봉부터 마지막까지
                        list_high = list_high[i:]
                        list_low = list_low[i:]
                        list_close = list_close[i:]
                        list_now = list_now[i:]
                        ror_max[row_tik] = 0
                        ror_min[row_tik] = 0
                        list_ror = []
                        list_ror_max = []
                        list_ror_min = []
                        break
            else :
                # print(f"{list_idx[row_tik]} | {state=} - 매수가 미달로 미 체결")
                state = '매도'


        ###################
        if state == '매수': # 매수상태일 때
            # if market == '코인':
            if row_tik_buy == row_tik:
                잔고 = wallet[row_tik]
                ror_max[row_tik] = 0
                ror_min[row_tik] = 0
                list_ror = []
                list_ror_max = []
                list_ror_min = []
            else:
                list_open, list_high, list_low, list_close, list_now, df_check = get_list(df,df_1m,row_tik)
                잔고 = wallet[row_tik -1]
                price_buy[row_tik] = price_buy[row_tik -1]
                ror_max[row_tik] = ror_max[row_tik -1]
                ror_min[row_tik] = ror_min[row_tik -1]

            # print(f"{row_tik + 1} | {state=} - {asset[row_tik]=}")
            for i, close in enumerate(list_close):
                수익률, 최고수익률, 최저수익률, = cal_ror_bybit(레버리지, list_high[i], list_low[i], close, 매수수량, 매수금액, 잔고)

                현재시간 = list_now[i]
                df_1m.loc[현재시간, '수익률'] = 수익률
                df_1m.loc[현재시간, '최고수익률'] = 최고수익률
                df_1m.loc[현재시간, '최저수익률'] = 최저수익률
                df_1m.loc[현재시간, 'state'] = state

                exec(stg_sell, None, locals_dict_sell)
                매도 = locals_dict_sell.get('매도')
                if 매도 == True:
                    # print(f'{현재시간=}============={매도=}, {수익률=}, {state=}')
                    state = '매도주문'
                    df_1m.loc[list_now[i], 'state'] = state
                    매도가 = locals_dict_sell.get('매도가')
                    if type(매도가) == dict:
                        hoga_price = list(매도가.keys())[0]
                        hoga_rate = 매도가[hoga_price]
                        if market == '코인':
                            매도가 = float(exchange.price_to_precision(ticker, hoga_price + (hoga_price * hoga_rate / 100)))
                        if market == '코스피' or market == '코스닥' or market == 'etf' :
                            매도가 = exchange.hogaPriceReturn(hoga_price, hoga_rate, market)
                    elif 매도가 == 시장가:
                        매도가 = list_open[i]
                    else:
                        if market == '코인':
                            매도가 = float(exchange.price_to_precision(ticker, 매도가))
                        elif market == '코스피' or market == '코스닥' or market == 'etf' :
                            매도가 = exchange.hogaPriceReturn_per(매도가, 0, market)
                    sell_order[row_tik] = 매도가
                    list_open = list_open[i:] #신호가 발생되는 다음 1분봉부터 마지막까지
                    list_high = list_high[i:]
                    list_low = list_low[i:]
                    list_close = list_close[i:]
                    list_now = list_now[i:]
                    row_tik_sell = row_tik
                    break



        ###################
        if state == '매도주문':
            # print(f"{row_tik + 1} | {state= } - {asset[row_tik]= }")
                if row_tik_sell == row_tik:
                    잔고 = wallet[row_tik]
                else:
                    list_open, list_high, list_low, list_close, list_now, df_check = get_list(df,df_1m,row_tik)
                    잔고 = wallet[row_tik - 1]
                    price_buy[row_tik] = price_buy[row_tik - 1]
                    ror_max[row_tik] = ror_max[row_tik-1]
                    ror_min[row_tik] = ror_min[row_tik-1]
                if 방향 == 'long' :
                    for i,close in enumerate(list_close):
                        # print(f'{현재시간=}============={매도=}, {수익률=}, {state=}')
                        수익률, 최고수익률, 최저수익률 = cal_ror_bybit(레버리지, list_high[i], list_low[i], close, 매수수량, 매수금액, 잔고)
                        현재시간 = list_now[i]
                        df_1m.loc[현재시간, '수익률'] = 수익률
                        df_1m.loc[현재시간, '최고수익률'] = 최고수익률
                        df_1m.loc[현재시간, '최저수익률'] = 최저수익률
                        df_1m.loc[현재시간, 'state'] = state
                        exec(stg_sell, None, locals_dict_sell) #매도신호가 나와있는 와중에 손절등으로 추가 매도 신호가 나올 수 있기 때문에 다시한번 매도 신호를 받음
                        매도 = locals_dict_sell.get('매도')

                        if 매도 == True:
                            # print(f'{row_tik=}==================={매도=}')
                            state = '매도주문'
                            매도가 = locals_dict_sell.get('매도가')
                            if type(매도가) == dict:
                                hoga_price = list(매도가.keys())[0]
                                hoga_rate = 매도가[hoga_price]
                                if market == '코인':
                                    매도가 = float(exchange.price_to_precision(ticker, hoga_price + (hoga_price * hoga_rate / 100)))
                                elif market == '코스피' or market == '코스닥' or market == 'etf':
                                    매도가 = exchange.hogaPriceReturn(hoga_price, hoga_rate, market)
                            elif 매도가 == 시장가:
                                매도가 = list_open[i]
                                # print(f'시장가 : {매도가=}')
                            else:
                                if market == '코인':
                                    매도가 = float(exchange.price_to_precision(ticker, 매도가))
                                elif market == '코스피' or market == '코스닥' or market == 'etf':
                                    매도가 = exchange.hogaPriceReturn_per(매도가, 0, market)
                            if 매도가 <= list_high[i]:
                                if 매도가 < list_low[i]:
                                    매도가 = list_low[i]
                                sell[row_tik] = 매도가
                                수익률 = chegyeol_sell_bybit(매도가,매수수량,매수금액, 레버리지, 잔고)
                                state = '매도'
                                df_1m.loc[현재시간, '매도가'] = 매도가
                                df_1m.loc[현재시간, 'state'] = state
                                break
                    if state == '매도주문':
                        state = '매수'
                elif 방향 == 'short':
                    state = '매도'


        if state == '종료':
            break


        if np.isnan(wallet[row_tik]):
            print(f"{df.index[row_tik]} : {row_tik + 1} ,'- 잔고 엥꼬' | state: {state},   잔고: {wallet[row_tik]}")
            raise
        # else:   #전량 매도에 매수시그널 없을 때
        #     else:
        #         print(f"아무튼 에러 {row_tik + 1} ,'- 잔고 엥꼬' {state}")
        #         raise
        # print(f'[{row_tik= }] | {asset[row_tik]= }, {bet= },')
        ror_strategy[row_tik] = round((asset[row_tik]-bet)/bet*100,1) #배팅 금액 대비 수익률 계산용
        if ror_strategy[row_tik] < -80 or (ror_min[row_tik] < -80 and np.isnan(sell[row_tik])):  # 자산이 베팅금액의 85프로 미만일 경우 청산
            print(f'****** 청산: {현재시간=}')
            break

        # if row_tik == 35:
        #     print(f'break, {close= }')
        #     break
        # print('=========================================================================================================')
        # if 종료시간 == 현재시간:
        #     print(f'{종료시간=}, {현재시간=}')
        #     break
        # QPB_bar.setValue(round(row_tik/length*100))

    df['매수주문가'] = buy_order
    df['매수가'] = buy
    df['매도주문가'] = sell_order
    df['매도가'] = sell
    df['수량'] = qty
    df['수수료'] = fee_sum
    df['수익률'] = ror
    df['최고수익률'] = ror_max
    df['최저수익률'] = ror_min
    df['수익금'] = benefit
    df['잔고'] = wallet
    df['전략수익률'] = ror_strategy
    df['매수금액'] = price_buy
    df['매도금액'] = price_sell
    df['strategy'] = asset
    df['val'] = val
    df['val_k'] = val_k


    df = df.drop('인덱스',axis=1)

    if len(df)-1 != row_tik: #백테스트가 다 돌아가지 않고 중간에 종료될 경우
        idx_end = df.index[row_tik+1]
        df = df[:row_tik+1]
        df_1m = df_1m.loc[df.index[0]:idx_end]
    if market == '코인':
        df_1m.to_sql('df_check',sqlite3.connect('DB/bt.db'),if_exists='replace')
    return df


def df_sql(df,db_file,table):
    try:
        # df = df[:end_idx+1]
        conn = sqlite3.connect(db_file)
        df.to_sql(table, conn, if_exists='replace')
    except:
        print(df)
        print('에러')
        raise

def mapping(x, i_min, i_max, o_min, o_max):
    return (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # mapping()함수 정의.
def compare_price(price,vars):
    i_min = price.min() # 현재가.min
    i_max = price.max()
    return price.apply(mapping, args=(i_min, i_max, vars.min(), vars.max()))


if __name__ == '__main__':
    start_time = time.time()

    ticker = '122630'
    # ticker = 'BTC'
    bong = '일봉'
    market = 'etf'
    frdate = '2023-01-01'
    todate = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('DB/strategy.db')
    if market == '코인':
        bet = 100
        df = pd.read_sql(f"SELECT * FROM 'coin_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_buy_text = df.loc['퀀택_변돌','전략코드']
        print(stg_buy_text)
        df = pd.read_sql(f"SELECT * FROM 'coin_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_sell_text = df.loc['변돌','전략코드']
        print(stg_sell_text)
        print('======================================')
        conn.close()
        ex = ccxt.bybit(config={
            'apiKey': 'ZFEksBSBjIHk7drUou',
            'secret': 'MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI',
            # 'timeout': 3000,
            'enableRateLimit': True,
            'options': {
                'position_mode': True,
            }, })
    elif market == 'etf':
        bet = 1_000_000
        df = pd.read_sql(f"SELECT * FROM 'stock_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_buy_text = df.loc['코덱스','전략코드']
        df = pd.read_sql(f"SELECT * FROM 'stock_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_sell_text = df.loc['코덱스','전략코드']
        conn.close()

        frdate = '2010-01-01'
        todate = '2023-12-31'
        ex = cal_krx.cal_krx()

        # stock_tick='DB/DB_krx.db'
        # conn = sqlite3.connect(stock_tick)
        # df = pd.read_sql(f"SELECT * FROM '{ticker}'", conn).set_index('날짜')  # 머니탑 테이블 갖고오기
        import os
        import pandas_datareader.data as web
        from pandas import to_numeric


        # if not os.path.isfile(stock_tick):
        #     print('db데이터 없음')
        #     conn = sqlite3.connect(stock_tick)
        #     # df = stock.get_etf_ohlcv_by_date(fromdate=frdate, todate= todate, ticker = ticker)
        #     data = web.DataReader(ticker, 'naver', start='2000-01-01', end='2023-12-31')
        #     df = data.apply(to_numeric)
        #     df.rename(columns={'Open':'시가','High':'고가','Low':'저가','Close':'종가','Volume':'거래량'}, inplace=True)  # 컬럼명 변경
        #     df.index.rename('날짜',inplace = True)
        #     df.to_sql(ticker,conn,if_exists='replace')
        # else:
        #     conn = sqlite3.connect(stock_tick)
        #     try:
        #         df = pd.read_sql(f"SELECT * FROM '{ticker}'", conn).set_index('날짜')  # 머니탑 테이블 갖고오기
        #     except:
        #         data = web.DataReader(ticker, 'naver', start='2000-01-01', end='2023-12-31')
        #         df = data.apply(to_numeric)
        #         df.rename(columns={'Open':'시가','High':'고가','Low':'저가','Close':'종가','Volume':'거래량'}, inplace=True)  # 컬럼명 변경
        #         df.index.rename('날짜',inplace = True)
        #         df.to_sql(ticker,conn,if_exists='replace')
        # conn.close()

    df = strategy_np(market,ex,ticker,bong, stg_buy_text, stg_sell_text, bet,frdate,todate,'')
    # df.to_sql(ticker, sqlite3.connect('DB/bt.db'), if_exists='replace')

    # import ATOM_chart_numpy
    # conn = sqlite3.connect('DB/ATOM_chart_table.db')
    # df_chart_table = pd.read_sql(f"SELECT * FROM 'chart_table'", conn).set_index('index')  # 머니탑 테이블 갖고오기
    # dict_plot = ATOM_chart_numpy.chart_np(df,df_chart_table)

    # import ATOM_chart
    # asdf = ATOM_chart.Window(df,dict_plot,universe,'1415')
    # print(asdf)
    # print('asdf')
    # asdf.setGeometry(0, 30, 3840, 2100)
    # asdf.show()
    df['index'] = compare_price(df['종가'],df['strategy'])
    # df.index = df.index.astype(str).str[:10]
    conn.close()

    # df['holding'] = np.log1p(df['holding'])
    df['ror'] = (df['종가']-df['시가'][0])/df['시가'][0]
    df['holding'] = bet+(df['ror']*bet)
    amount = df['수익금'].sum()

    # plt.xlabel('date')
    # plt.ylabel('수익금')
    # plt.plot(df.index,df['asset'])
    df.plot(y=['strategy','index','holding'],
            # logy=True,
            # ylim=(30000000, 100000000),
            figsize=(16, 9),
            grid=True, xlabel=f'총 수익금: {amount}', ylabel=f'가격',)
    plt.text(200,500,f'총 수익금:{amount}')
    plt.legend()
    print(f'총 수익금:{amount}')
    print(f'걸린시간: {(time.time()-start_time)}')

    plt.show()

    df = df.drop(['이평5', '이평7', '이평20', '이평25', '이평60', '이평120', '이평200',
                  # '거래량이평3',
                  '거래량이평20',
                  '거래량이평60', 'RSI14', 'RSI18', 'RSI30', 'ATR10', 'TRANGE', '이격도20이평', '밴드20상', '밴드20중',
                  '밴드20하', '고저평균대비등락율'], axis=1)
    df.to_sql(ticker, sqlite3.connect('DB/bt.db'), if_exists='replace')
