import sqlite3
import pandas as pd
import math
import numpy as np
from datetime import datetime,timedelta,date
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
import KIS
# import cal_krx
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex
from pprint import pprint
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


def 구간최고시가(pre):
    return np_tik[-(pre+1):, list_columns.index('시가')].max()
def 구간최저시가(pre):
    return np_tik[-(pre+1):, list_columns.index('시가')].min()
def 구간최고고가(pre):
    return np_tik[-(pre+1):, list_columns.index('고가')].max()
def 구간최저고가(pre):
    return np_tik[-(pre+1):, list_columns.index('고가')].min()
def 구간최고저가(pre):
    return np_tik[-(pre+1):, list_columns.index('저가')].max()
def 구간최저저가(pre):
    return np_tik[-(pre+1):, list_columns.index('저가')].min()
def 구간최고종가(pre):
    return np_tik[-(pre+1):, list_columns.index('종가')].max()
def 구간최저종가(pre):
    return np_tik[-(pre+1):, list_columns.index('종가')].min()
def 구간최고시가N(pre,N): #N칸만큼 쉬프트 시킨거에 pre구간 최고값
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('시가')].max()
def 구간최저시가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('시가')].min()
def 구간최고고가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('고가')].max()
def 구간최저고가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('고가')].min()
def 구간최고저가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('저가')].max()
def 구간최저저가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('저가')].min()
def 구간최고종가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('종가')].max()
def 구간최저종가N(pre,N):
    return np_tik[-(pre+1+N):row_tik-N, list_columns.index('종가')].min()
def 시가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('시가')]
def 고가N(pre):
    if 데이터길이 <= pre:
        return np.nan
    return np_tik_ar[row_tik - pre, list_columns.index('고가')]
def 저가N(pre):
    if 데이터길이 <= pre:
        return np.nan
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
# def 수익률N(pre):
#     if 데이터길이 <= pre:
#         return np.nan
#     # print(ror[:row_tik])
#     # print(ror[row_tik])
#     # print(pre)
#     return ror[row_tik - pre]
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


class backtest_np(QThread):
    val_df = pyqtSignal(pd.DataFrame)
    # val_dict_result = pyqtSignal(dict)
    val_bar = pyqtSignal(int)

    # def __init__(self,**kwargs):
    # def __init__(self,parent,df,df_detail, dict_info):
    #     super().__init__(parent)
    def __init__(self,df,df_detail, dict_info):
        super().__init__()

        # self.mutex = QMutex()
        self.market = dict_info['market']

        self.trade_market = dict_info['trade_market']
        if self.trade_market == 'bybit':
            self.ticker = dict_info['ticker']+'USDT'
        else:
            self.ticker = dict_info['ticker']
        self.stg_buy = dict_info['stg_buy']
        self.stg_sell = dict_info['stg_sell']
        self.bet = dict_info['bet']
        self.minute_check = dict_info['minute_check']
        self.fee_krx = 0.015
        self.tax = 0.018
        self.fee_limit = 0.02
        self.fee_market = 0.055
        self.df = df
        self.df_detail = df_detail
        self.count = 0
        self._status = True
        if self.trade_market == 'bybit':
            # self.exchange = self.make_exchange_bybit()
            self.exchange = dict_info['exchange']
            self.exchange.fetch_tickers() #바이비트의 경우 한번 해줘야 에러가 안남
        else:
            self.exchange = dict_info['exchange']
            # balanceSpot = self.exchange.fetch_balance()
            # pprint(balanceSpot)
        # elif self.trade_market == '코스피' or self.trade_market == '코스닥' or self.trade_market == 'etf':
        #     self.exchange = cal_krx.cal_krx()
        # elif self.trade_market == '선물':
        #     print(self.trade_market)
    def run(self):

        global np_tik_ar
        global row_tik
        global list_columns
        global np_tik
        global np_tik_idx
        global 데이터길이
        global 상태
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
        global 롱
        global long
        global 숏
        global short
        start_time = time.time()

        for i in range(20):
            globals()[f'매도{i}호가'] = f'매도{i}호가'
        for i in range(20):
            globals()[f'매수{i}호가'] = f'매수{i}호가'

        상태 = '매도'
        self.buy = [np.nan for x in range(len(self.df.index))]  # 매수가
        self.sell = [np.nan for x in range(len(self.df.index))]  # 매도가
        self.buy_order = [np.nan for x in range(len(self.df.index))]  # 매수주문가
        self.sell_order = [np.nan for x in range(len(self.df.index))]  # 매도주문가
        self.ror = [np.nan for x in range(len(self.df.index))]  # 수익률
        self.ror_max = [np.nan for x in range(len(self.df.index))]  # 최고수익률
        self.ror_min = [np.nan for x in range(len(self.df.index))]  # 최저수익률
        self.ror_strategy = [np.nan for x in range(len(self.df.index))]  # 최저수익률
        self.benefit = [np.nan for x in range(len(self.df.index))]  # 수익금
        self.wallet = [np.nan for x in range(len(self.df.index))]  # 잔고
        self.asset = [np.nan for x in range(len(self.df.index))]  # 잔고
        self.qty = [np.nan for x in range(len(self.df.index))]  # 보유수량
        self.fee_sum = [np.nan for x in range(len(self.df.index))]  # 수수료
        self.price_buy = [np.nan for x in range(len(self.df.index))]  # 총매수금액
        self.price_sell = [np.nan for x in range(len(self.df.index))]  # 총매도금액
        self.val = [np.nan for x in range(len(self.df.index))]  # test
        self.val_k = [np.nan for x in range(len(self.df.index))]  # test
        self.wallet[-1] = self.bet
        self.asset[-1] = self.bet

        self.df['데이터길이'] = np.arange(1, len(self.df.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
        self.df['데이터길이'] = self.df['데이터길이'].fillna(0)
        np_tik_ar = self.df.to_numpy()  # 전체 데이터를 np로 저장
        np_tik_idx = self.df.index.to_numpy()  # 전체 데이터를 np로 저장
        list_columns = self.df.columns.tolist()  # 컬럼명을 리스트로 저장
        # list_idx = df['인덱스'].tolist()
        # if self.trade_market =='코인':
        self.df_detail['매수주문가'] = np.nan
        self.df_detail['매수가'] = np.nan
        self.df_detail['매도주문가'] = np.nan
        self.df_detail['매도가'] = np.nan
        self.df_detail['수익률'] = np.nan
        self.df_detail['수익금'] = np.nan
        self.df_detail['최고수익률'] = np.nan
        self.df_detail['최저수익률'] = np.nan
        self.df_detail['상태'] = np.nan
        self.df_detail['잔고'] = np.nan
        self.df_detail['자산'] = np.nan
        self.df_detail['매수수수료'] = np.nan
        self.df_detail['매도수수료'] = np.nan
        self.df_detail['횟수'] = np.nan
        numbers = 0
        length_index=len(self.df.index)
        row_tik = 0
        # print('데이터변환 완료..')
        slippage = 0.1  # 슬리피지 0.1 %
        old_row_tik = 0

        롱 = 'long'
        long = 'long'
        숏 = 'short'
        short = 'short'

        while self._status and row_tik  < length_index:
        # for row_tik in range(len(self.df.index)):
            np_tik = np_tik_ar[:row_tik + 1]
            self.wallet[row_tik] = self.wallet[row_tik - 1]
            self.asset[row_tik] = self.asset[row_tik - 1]

            for col in list_columns:  # 연산을 위해 컬럼의 값을 행별로 돌아가며 변수로 선언
                globals()[f'{col}'] = np_tik[row_tik, list_columns.index(f'{col}')]
            # 데이터길이 = row_tik + 1
            locals_dict_buy = {}
            locals_dict_sell = {}
            # print(f"{row_tik + 1} | {상태=} - {self.minute_check.isChecked()} | {저가=}")
            if 상태 == '매도':  # 미 보유 시 매수 주문
                exec(self.stg_buy, None, locals_dict_buy)
                매수 = locals_dict_buy.get('매수')
                if self.trade_market == 'bybit' or self.trade_market == '선물':
                    레버리지 = locals_dict_buy.get('레버리지')
                    방향 = locals_dict_buy.get('방향')
                    if 레버리지 == None or 방향 == None:
                        레버리지 = 1
                        방향 = 'long'
                    self.direction = 방향
                elif self.trade_market == '코스피' or self.trade_market == '코스닥' or self.trade_market == 'etf':
                    방향 = 'long'
                    self.direction = 방향
                    레버리지 = 1
                if self.df.index[row_tik].date() == date(2024,7,2):
                    print(f"{구간최고시가(5)=}")
                    print(f"{구간최고시가N(5,2)=}")
                    print(f"{구간최저시가N(7,2)=}")
                    quit()
                if not 매수 == False:  # 매수 일 경우 None을 반환하기 때문에(매수신호 떳을 때)
                    # print(f"{row_tik} | {상태=} - {asset[row_tik]=}")
                    상태 = '매수주문'
                    진입주문가 = locals_dict_buy.get('매수가')
                    매수가 = self.order_price(진입주문가, 시가, '매수주문')

            if 상태 == '매수주문':  # 매수 체결 확인
                if self.minute_check.isChecked() == True:
                    # if row_tik == 144:
                    #     quit()
                    list_open, list_high, list_low, list_close, list_now, df_check = self.get_list(self.df, self.df_detail, row_tik)
                    if (방향 == 'long' and 매수가 >= 저가) or (방향 == 'short' and 매수가 <= 고가):
                        for i, close in enumerate(list_close):
                            self.df_detail.loc[list_now[i], '매수주문가'] = 매수가
                            self.df_detail.loc[list_now[i], '상태'] = 상태
                            if list_low[i] <= 매수가 and 매수가 <= list_high[i]:
                                # 매수가 = list_close[i]  ##### 슬리피지 감안하여 종가가 매수가보다 높을경우 진입하며 매수가난 종가로 대입

                                상태 = '매수'
                                self.buy[row_tik] = 매수가
                                row_tik_buy = row_tik
                                매수시간 = df_check.index[i].to_pydatetime()
                                종료시간 = list_now[-1]
                                self.df_detail.loc[list_now[i], '매수가'] = 매수가
                                self.df_detail.loc[list_now[i], '상태'] = 상태
                                매수수량, 매수금액, 잔고 = self.chegyeol_buy(매수, 매수가, 레버리지)
                                self.df_detail.loc[list_now[i], '잔고'] = 잔고
                                numbers += 1
                                self.df_detail.loc[list_now[i], '횟수'] = numbers

                                # print(f"{list_now[i]=}, {매수가=}, , {상태=}")
                                list_open = list_open[i:]  # 체결되는 1분봉부터 마지막까지
                                list_high = list_high[i:]
                                list_low = list_low[i:]
                                list_close = list_close[i:]
                                list_now = list_now[i:]
                                self.ror_max[row_tik] = 0
                                self.ror_min[row_tik] = 0
                                # print(f"{row_tik=}, {self.df.index[row_tik]}, {이평5=}, {이평20=}, | {이평5N(1)=}, {이평20N(1)=},  | {이평5N(2)=}, {이평20N(2)=}")
                                break
                            elif list_now[i] == list_now[-1]:#long일경우 매수가>저가 이지만 상세로 보면 이미 지나버린 시점일 수 있음에 유의
                                상태 = '매도'
                                self.df_detail.loc[list_now[i], '상태'] = '매수 안됨 상태 매도 전환'

                    else:
                        # print(f"{list_idx[row_tik]} | {상태=} - 매수가 미달로 미 체결")
                        상태 = '매도'


                elif self.minute_check.isChecked() == False:
                    # print(f"{row_tik + 1} | {상태=} - {매수가=},{저가=}")
                    if (방향 == 'long' and 매수가 >= 저가) or (방향 == 'short' and 매수가 <= 고가):
                        상태 = '매수'
                        self.buy[row_tik] = 매수가
                        row_tik_buy = row_tik
                        매수수량, 매수금액 = self.chegyeol_buy(매수, 매수가, 레버리지)
                        self.ror_max[row_tik] = 0
                        self.ror_min[row_tik] = 0
                    else:
                        # print(f"{list_idx[row_tik]} | {상태=} - 매수가 미달로 미 체결")
                        상태 = '매도'


            if 상태 == '매수':  # 매수상태일 때
                if self.minute_check.isChecked() == True:
                    if row_tik_buy == row_tik:
                        잔고 = self.wallet[row_tik]
                        self.ror_max[row_tik] = 0
                        self.ror_min[row_tik] = 0

                    else:
                        list_open, list_high, list_low, list_close, list_now, df_check = self.get_list(self.df, self.df_detail,row_tik)
                        잔고 = self.wallet[row_tik - 1]
                        self.price_buy[row_tik] = self.price_buy[row_tik - 1]
                        self.ror_max[row_tik] = self.ror_max[row_tik - 1]
                        self.ror_min[row_tik] = self.ror_min[row_tik - 1]
                    for i, close in enumerate(list_close):
                        수익률, 최고수익률, 최저수익률, = self.cal_ror(레버리지, list_high[i], list_low[i], close, 매수수량, 매수금액, 잔고)
                        현재시간 = list_now[i]
                        self.df_detail.loc[현재시간, '수익률'] = 수익률
                        self.df_detail.loc[현재시간, '최고수익률'] = 최고수익률
                        self.df_detail.loc[현재시간, '최저수익률'] = 최저수익률
                        self.df_detail.loc[현재시간, '상태'] = 상태
                        # print(f"{row_tik + 1} {현재시간} | {상태=} - ")

                        exec(self.stg_sell, None, locals_dict_sell)
                        매도 = locals_dict_sell.get('매도')
                        # if 현재시간.date() == date(2019, 5, 9): # <class 'pandas._libs.tslibs.timestamps.Timestamp'> 타입 비교
                        #     print(현재시간)
                        #     print('=======================')
                        #     print(not(((저가N(1) > 저가N(2)) or (거래량N(1) < 거래량이평3N(1))) and
                        #               ((이격도20이평 < 99) or (이격도20이평 > 103))))
                        #     print('***********************')
                        #     print((((저가N(1) > 저가N(2)) or (거래량N(1) < 거래량이평3N(1)))))
                        #     print((저가N(1) > 저가N(2)))
                        #     print((거래량N(1) < 거래량이평3N(1)))
                        #     quit()
                        if 매도 == True:


                            상태 = '매도주문'
                            self.df_detail.loc[list_now[i], '상태'] = 상태

                            청산주문가 = locals_dict_sell.get('매도가')
                            매도가 = self.order_price(청산주문가, list_open[i], '매도주문')
                            if 현재시간.date() == date(2019, 5,9):  # <class 'pandas._libs.tslibs.timestamps.Timestamp'> 타입 비교
                                print(f"{현재시간=}, {매도=}, {매도가=}")
                                # print(현재시간)
                                # print('=======================')
                                # print(not(((저가N(1) > 저가N(2)) or (거래량N(1) < 거래량이평3N(1))) and
                                #           ((이격도20이평 < 99) or (이격도20이평 > 103))))
                                # print('***********************')
                                # print((((저가N(1) > 저가N(2)) or (거래량N(1) < 거래량이평3N(1)))),end='=')
                                # print((저가N(1) > 저가N(2)),end='')
                                # print((거래량N(1) < 거래량이평3N(1)))
                                # print(((이격도20이평 < 99) or (이격도20이평 > 103)),end='=')
                                # print((이격도20이평 < 99),end='')
                                # print((이격도20이평 > 103))
                                # quit()
                            self.sell_order[row_tik] = 매도가
                            list_open = list_open[i:]  # 신호가 발생되는 다음 1분봉부터 마지막까지
                            list_high = list_high[i:]
                            list_low = list_low[i:]
                            list_close = list_close[i:]
                            list_now = list_now[i:]
                            row_tik_sell = row_tik
                            break
                elif self.minute_check.isChecked() == False:
                    if not row_tik_buy == row_tik:
                        잔고 = self.wallet[row_tik - 1]
                        수익률, 최고수익률, 최저수익률, = self.cal_ror(레버리지, 고가, 저가, 종가, 매수수량, 매수금액, 잔고)
                        # print(f"{row_tik + 1} | {상태=} - {수익률=}, {최고수익률=}, {최저수익률=}")
                        exec(self.stg_sell, None, locals_dict_sell)
                        매도 = locals_dict_sell.get('매도')
                        if 매도 == True:

                            # print(f'{현재시간=}============={매도=}, {수익률=}, {상태=}')
                            상태 = '매도주문'
                            # self.df_detail.loc[list_now[i], '상태'] = 상태
                            청산주문가 = locals_dict_sell.get('매도가')
                            매도가 = self.order_price(청산주문가, list_open[i], '매도주문')


            if 상태 == '매도주문':
                if self.minute_check.isChecked() == True:
                    if row_tik_sell == row_tik:
                        잔고 = self.wallet[row_tik]
                    else:
                        list_open, list_high, list_low, list_close, list_now, df_check = self.get_list(self.df, self.df_detail,row_tik)
                        잔고 = self.wallet[row_tik - 1]
                        self.price_buy[row_tik] = self.price_buy[row_tik - 1]
                        self.ror_max[row_tik] = self.ror_max[row_tik - 1]
                        self.ror_min[row_tik] = self.ror_min[row_tik - 1]

                    for i, close in enumerate(list_close):
                        수익률, 최고수익률, 최저수익률 = self.cal_ror(레버리지, list_high[i], list_low[i], close, 매수수량, 매수금액,잔고)
                        현재시간 = list_now[i]
                        self.df_detail.loc[현재시간, '매도주문가'] = 매도가
                        self.df_detail.loc[현재시간, '수익률'] = 수익률
                        self.df_detail.loc[현재시간, '최고수익률'] = 최고수익률
                        self.df_detail.loc[현재시간, '최저수익률'] = 최저수익률
                        self.df_detail.loc[현재시간, '상태'] = 상태

                        exec(self.stg_sell, None,locals_dict_sell)  # 매도신호가 나와있는 와중에 손절등으로 추가 매도 신호가 나올 수 있기 때문에 다시한번 매도 신호를 받음
                        매도 = locals_dict_sell.get('매도')

                        if 매도 == True:
                            상태 = '매도주문'
                            청산주문가 = locals_dict_sell.get('매도가')
                            매도가 = self.order_price(청산주문가, list_open[i], '매도주문')

                            if (방향 == 'long' and 매도가 <= list_high[i]) or (방향 == 'short' and 매도가 >= list_low[i]):
                                # if 매도가 <= list_high[i]:
                                상태 = '매도'
                                if 매도가 < list_low[i]:
                                    매도가 = list_low[i]
                                수익률, 수익금 = self.chegyeol_sell(매도가, 매수수량, 매수금액, 레버리지, 잔고)
                                self.df_detail.loc[현재시간, '수익률'] = 수익률
                                self.df_detail.loc[현재시간, '수익금'] = 수익금
                                self.df_detail.loc[현재시간, '매도가'] = 매도가
                                self.df_detail.loc[현재시간, '상태'] = 상태
                                break

                    if 상태 == '매도주문':
                        상태 = '매수'


                elif self.minute_check.isChecked() == False:
                    잔고 = self.wallet[row_tik - 1]
                    수익률, 최고수익률, 최저수익률 = self.cal_ror(레버리지, 고가, 저가, 종가, 매수수량, 매수금액, 잔고)

                    exec(self.stg_sell, None,locals_dict_sell)  # 매도신호가 나와있는 와중에 손절등으로 추가 매도 신호가 나올 수 있기 때문에 다시한번 매도 신호를 받음
                    매도 = locals_dict_sell.get('매도')

                    if 매도 == True:
                        상태 = '매도주문'
                        청산주문가 = locals_dict_sell.get('매도가')
                        매도가 = self.order_price(청산주문가, 시가, '매도주문')


                        if (방향 == 'long' and 매도가 <= 고가) or (방향 == 'short' and 매도가 >= 저가):
                            상태 = '매도'
                            if 매도가 < 저가: 매도가 = 저가
                            수익률, 수익금 = self.chegyeol_sell(매도가, 매수수량, 매수금액, 레버리지, 잔고)
                            상태 = '매도'


                if 상태 == '매도주문':
                    상태 = '매수'

            if 상태 == '종료':
                break

            if np.isnan(self.wallet[row_tik]):
                print(f"{self.df.index[row_tik]} : {row_tik + 1} ,'- 잔고 엥꼬' | 상태: {상태},   잔고: {self.wallet[row_tik]}")
                raise

            # print(f"{현재시간=}, {type(현재시간)}")
            # print(np.datetime64('2024-05-01T09:00:00'))
            # if 현재시간 == np.datetime64('2024-05-01T09:00:00'): #<class 'pandas._libs.tslibs.timestamps.Timestamp'> 타입 비교
            #     print('break')
            #     break
            self.ror_strategy[row_tik] = round((self.asset[row_tik] - self.bet) / self.bet * 100,1)  # 배팅 금액 대비 수익률 계산용
            if self.ror_strategy[row_tik] < -80 or (
                    self.ror_min[row_tik] < -80 and np.isnan(self.sell[row_tik])):  # 자산이 베팅금액의 85프로 미만일 경우 청산
                print(f'****** 청산: {현재시간=}')
                break
            # print(row_tik)
            # print(round(row_tik / length_index * 100))
            row_tik += 1
            if old_row_tik == row_tik:
                print('old_row_tik')
                print(row_tik)
                break
            else:
                old_row_tik = row_tik
            self.count = (round(row_tik / len(self.df.index) * 100))
            self.val_bar.emit(self.count)

        self.df['매수주문가'] = self.buy_order
        self.df['매수가'] = self.buy
        self.df['매도주문가'] = self.sell_order
        self.df['매도가'] = self.sell
        self.df['수량'] = self.qty
        self.df['수수료'] = self.fee_sum
        self.df['수익률'] = self.ror
        self.df['최고수익률'] = self.ror_max
        self.df['최저수익률'] = self.ror_min
        self.df['수익금'] = self.benefit
        self.df['잔고'] = self.wallet
        self.df['전략수익률'] = self.ror_strategy
        self.df['매수금액'] = self.price_buy
        self.df['매도금액'] = self.price_sell
        self.df['자산'] = self.asset
        self.df['val'] = self.val
        self.df['val_k'] = self.val_k

        if self._status and length_index  != row_tik:  # 백테스트가 다 돌아가지 않고 중간에 종료될 경우
            idx_end = self.df.index[row_tik + 1]
            self.df = self.df[:row_tik + 1]
            self.df_detail = self.df_detail.loc[self.df.index[0]:idx_end]


        for i, idx in enumerate(self.df_detail['매수가'].tolist()):
            if not np.isnan(idx):
                print(f"{idx=}, {i=}, {self.df_detail.index[i]}")
                break
        self.df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가', '거래량': '상세거래량'},inplace=True)
        # self.df = ['시가', '고가', '저가', '종가', '거래량', '등락율', '변화율', '이평5', '이평20', '이평60', '이평120', '이평200',
        # '거래량이평3', '거래량이평20', '거래량이평60', 'RSI14', 'RSI18', 'RSI30', 'ATR10', 'TRANGE', '이격도20이평',
        # '밴드20상', '밴드20중', '밴드20하', '고저평균대비등락율', '데이터길이', '매수주문가', '매수가', '매도주문가', '매도가',
        # '수량', '수수료', '수익률', '최고수익률', '최저수익률', '수익금', '잔고', '전략수익률', '매수금액', '매도금액', 'strategy', 'val', 'val_k']
        # self.df_detail = ['상세시가', '상세고가', '상세저가', '상세종가', '상세거래량', '매수주문가', '매수가', '매도주문가', '매도가', '수익률', '최고수익률', '최저수익률', '상태']

        self.df_ohlcv = self.df[['시가','고가','저가','종가','거래량','이평5','이평20','이평60','거래량이평3']]
        self.df_detail_ohlcv =self.df_detail[['상세시가','상세고가','상세저가','상세종가','상세거래량']]
        self.df_detail_stg =self.df_detail[['매수주문가', '매수가', '매도주문가', '매도가', '수익률', '수익금', '최고수익률', '최저수익률', '상태','횟수']]
        self.df_result = pd.merge(self.df_detail_ohlcv, self.df_ohlcv, left_index=True, right_index=True, how='left')
        self.df_result.fillna(method='ffill', inplace=True)
        self.df_result = pd.merge(self.df_result, self.df_detail_stg, left_index=True, right_index=True, how='left')
        self.df_result = self.df_result[['상세시가','상세고가','상세저가','상세종가','상세거래량','시가','고가','저가','종가','이평5','이평20','이평60','거래량이평3','거래량','매수주문가','매수가','매도주문가','매도가','수익률','최고수익률','최저수익률','상태','횟수']]
        self.df_result.to_sql('thread_detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
        # self.df_result = self.df_result[~np.isnan(self.df_result['매수가'])]
        if self.market == '코인':
            ddf = self.df[['시가', '고가', '저가', '종가', '거래량', '매수가', '매도가', '수량', '수익률',
                                  '최고수익률', '최저수익률', '수익금', '매수금액', '매도금액', '잔고', '자산', '수수료']]
        elif self.market == '국내시장':
            ddf = self.df[['시가','고가','저가','종가','거래량','거래대금','매수가','매도가','수량','수익률',
                                  '최고수익률','최저수익률','수익금','매수금액','매도금액','잔고','자산','수수료']]
        self.df.rename(columns={'자산': 'strategy'}, inplace=True)
        ddf.to_sql('thread', sqlite3.connect('DB/bt.db'), if_exists='replace')
        self.val_df.emit(self.df)
        # print(self.df_result)
        # print(self.df_result)
        # quit()
        # print(self.df)
        # df = self.df[['시가', '고가', '저가', '종가', '이평5', '이평20', '이평60', '매수주문가', '매수가', '매도주문가',
        #          '매도가', '수익률', '최고수익률', '최저수익률', '수익금', '잔고','strategy']]
        # df.to_sql('bt_thread', sqlite3.connect('DB/bt.db'), if_exists='replace')
        print(f'tab backtest 걸린시간: {(time.time() - start_time)}')

        return self.df



    def stop(self):
        # 멀티쓰레드를 종료하는 메소드
        self._status = False
        self.quit()
        self.wait(3000)  # 3초 대기 (바로 안꺼질수도)



    def chegyeol_buy(self, 매수, 매수가, 레버리지):
        잔고 = self.wallet[row_tik - 1]
        배팅금액 = 잔고 * (매수 / 100) * 레버리지
        매수수량 = (100 - (self.fee_market * 레버리지)) / 100 * 배팅금액 / 매수가
        매수수량 = float(self.exchange.amount_to_precision(self.ticker, 매수수량))
        매수금액 = 매수수량 * 매수가
        매수수수료 = round(매수금액 * self.fee_market / 100, 4)
        잔고 = round(잔고 - (매수금액 / 레버리지) - 매수수수료, 4)

        self.qty[row_tik] = 매수수량
        self.price_buy[row_tik] = 매수금액
        self.fee_sum[row_tik] = 매수수수료
        self.wallet[row_tik] = 잔고

        return 매수수량, 매수금액, 잔고

    def chegyeol_sell(self, 매도가,매수수량,매수금액, 레버리지,잔고):
        매도금액 = 매도가 * 매수수량
        매수수수료 = round(매수금액 * self.fee_market / 100, 4)
        매도수수료 = round(매도금액 * self.fee_market / 100, 4)

        수익금 = round(매도금액 - 매수금액 - 매도수수료, 4)

        수익률 = round(((수익금 - 매수수수료) / 매수금액 * 100) * 레버리지, 2)
        잔고 = round(잔고 + (매수금액 / 레버리지) + 수익금,4)  ##매수수수료는 매수하면서 이미 냈음
        self.sell[row_tik] = 매도가
        self.wallet[row_tik] = 잔고
        자산 = 잔고
        self.asset[row_tik] = 자산
        self.ror[row_tik] = 수익률
        self.price_sell[row_tik] = 매도금액
        self.benefit[row_tik] = 수익금-매수수수료
        수수료 = 매수수수료+매도수수료
        self.fee_sum[row_tik] = 수수료
        return 수익률, 수익금

    def order_price(self,price_in,시가,side):
        slippage = 0.1  # 슬리피지 0.1 %
        # print(f"{현재시간=}, {시가}")
        if type(price_in) == dict:
            # print(f"{현재시간=},1 1{시가}")
            hoga_price = list(price_in.keys())[0]
            hoga_rate = price_in[hoga_price]
            if self.trade_market == 'bybit':
                price_out = float(self.exchange.price_to_precision(self.ticker, hoga_price + (hoga_price * hoga_rate / 100)))
            elif self.trade_market == '코스피' or self.trade_market == '코스닥' or self.trade_market == 'etf' or self.trade_market == 'ETF':
                price_out = self.exchange.hogaPriceReturn(hoga_price, hoga_rate, self.trade_market)
            elif self.trade_market == '선물':
                price_out = self.exchange.hogaPriceReturn(hoga_price, hoga_rate, self.ticker)
        elif price_in == 시장가 :  # 슬리피지 반영
            # print(f"{현재시간=},2 {시가}")
            if self.trade_market == 'bybit' or self.trade_market == '선물':
                if self.direction == 'long' and side == '매수주문': 가격 = 시가 + (slippage / 100 * 시가)
                elif self.direction == 'long' and side == '매도주문': 가격 = 시가 - (slippage / 100 * 시가)
                elif self.direction == 'short' and side == '매수주문': 가격 = 시가 - (slippage / 100 * 시가)
                elif self.direction == 'short' and side == '매도주문': 가격 = 시가 + (slippage / 100 * 시가)
                else: raise
                # print(f"{현재시간=},2 {가격=}")
                if self.trade_market == 'bybit':
                    price_out = float(self.exchange.price_to_precision(self.ticker, 가격))
                elif self.trade_market == '선물':
                    price_out = self.exchange.hogaPriceReturn_per(가격, 0, self.ticker)
                # print(f"{가격=}, {price_out=}")
            elif self.trade_market == '코스피' or self.trade_market == '코스닥' or self.trade_market == 'etf' or self.trade_market == 'ETF':
                if side == '매수주문':
                    가격 = 시가 + (slippage / 100 * 시가)
                elif side == '매도주문':
                    가격 = 시가 - (slippage / 100 * 시가)
                price_out = self.exchange.hogaPriceReturn_per(가격, 0, self.trade_market)
        else:
            # print(f"{현재시간=},3 {시가}")
            if self.trade_market == 'bybit':  # 슬리피지 반영 해야함
                price_out = float(self.exchange.price_to_precision(self.ticker, price_in))
            elif self.trade_market == '코스피' or self.trade_market == '코스닥' or self.trade_market == 'etf' or self.trade_market == 'ETF':
                price_out = self.exchange.hogaPriceReturn_per(price_in, 0, self.trade_market)
            elif self.trade_market == '선물':
                price_out = self.exchange.hogaPriceReturn_per(price_in, 0, self.ticker)
        if price_out == None:
            raise '가격 확인'
        return price_out

    def cal_ror(self, 레버리지, 상세고가, 상세저가, 상세종가, 매수수량, 매수금액, 잔고):
        if self.direction == 'long':
            매수수수료 = round(매수금액 * self.fee_market / 100, 0)
            매도수수료 = round(매수수량 * 상세종가 * self.fee_market / 100, 0)
            평가금액 = 매수수량 * 상세종가 - 매도수수료
            최고평가금액 = 매수수량 * 상세고가 - 매도수수료
            최저평가금액 = 매수수량 * 상세저가 - 매도수수료
            수익금 = round(평가금액 - 매수금액 - 매도수수료, 4)
            최고수익금 = 최고평가금액 - 매수금액 - 매도수수료
            최저수익금 = 최저평가금액 - 매수금액 - 매도수수료
        elif self.direction == 'short':
            매수수수료 = round(매수금액 * self.fee_market / 100, 0)
            매도수수료 = round(매수수량 * 상세종가 * self.fee_market / 100, 0)
            평가금액 = 매수수량 * 상세종가 - 매도수수료
            수익금 = round(매수금액 - 평가금액 - 매도수수료, 4)
            최고평가금액 = 매수수량 * 상세저가 - 매도수수료
            최저평가금액 = 매수수량 * 상세고가 - 매도수수료
            최고수익금 = 매수금액 - 최고평가금액 - 매도수수료
            최저수익금 = 매수금액 - 최저평가금액 - 매도수수료

        # try:
        수익률 = round(((수익금-매수수수료) / 매수금액 * 100)*레버리지, 2)
        # except:
        #     raise '배팅금액 확인'
        최고수익률 = round(((최고수익금 - 매수수수료) / 매수금액 * 100)*레버리지, 2)
        최저수익률 = round(((최저수익금 - 매수수수료) / 매수금액 * 100)*레버리지, 2)
        self.ror_max[row_tik] = float(np.where(최고수익률 > self.ror_max[row_tik], 최고수익률, self.ror_max[row_tik]))
        self.ror_min[row_tik] = float(np.where(최저수익률 < self.ror_min[row_tik], 최저수익률, self.ror_min[row_tik]))
        자산 = round(잔고 + (매수금액/레버리지) + 수익금,4)
        self.ror[row_tik] = 수익률
        self.asset[row_tik] = 자산
        최고수익률 = self.ror_max[row_tik]
        최저수익률 = self.ror_min[row_tik]
        return 수익률, 최고수익률, 최저수익률


    def get_list(self, df,df_detail,row_tik):
        idx_start = df.index[row_tik]
        # if row_tik == 144:
        #     idx_start = df.index[row_tik]
        if not row_tik == len(df) - 1:  # 마지막행이 아닐 경우
            if self.market == '국내시장':
                df_check = df_detail[(df_detail.index >= idx_start) & (df_detail.index < df.index[row_tik + 1])]
            elif self.market == '코인':
                df_check = df_detail[idx_start:df.index[row_tik + 1]]
        else:
            start = df.index[row_tik]
            pre = df.index[row_tik - 1]
            cha = start - pre
            if start + cha <= df_detail.index[-1]:  # 1분봉 데이터가 더 최근 데이터를 포함하고 있을 경우
                df_check = df_detail[start:start + cha]
            else:
                df_check = df_detail[start:]
        if self.market == '국내시장':
            list_open = df_check['시가'].tolist()
            list_high = df_check['고가'].tolist()
            list_low = df_check['저가'].tolist()
            list_close = df_check['종가'].tolist()
            list_now = df_check.index.tolist()
        elif self.market == '코인':
            list_open = df_check['시가'].tolist()[:-1]
            list_high = df_check['고가'].tolist()[:-1]
            list_low = df_check['저가'].tolist()[:-1]
            list_close = df_check['종가'].tolist()[:-1]
            list_now = df_check.index.tolist()[:-1]
        return list_open, list_high, list_low, list_close, list_now, df_check



    def convert_df(self,df):

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

        return df


    def make_exchange_bybit(self):
        exchange = ccxt.bybit(config={
            'apiKey': 'ZFEksBSBjIHk7drUou',
            'secret': 'MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI',
            'enableRateLimit': True,
            'options': {
                'position_mode': True,
            }, })
        return exchange


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

    def make_exchange_bybit():
        exchange = ccxt.bybit(config={
            'apiKey': 'ZFEksBSBjIHk7drUou',
            'secret': 'MXWVVshe71hnKR4SZEoUH4XqYxLLeV3uFIAI',
            'enableRateLimit': True,
            'options': {
                'position_mode': True,
            }, })
        return exchange
    def make_exchange_kis():
        key= 'test'
        secret= 'Hxx/vqG/010MOcgYo6j1fss7EtSPAAHGxBGAETgqsARRJLEt7ELVLcLRjzKeoW6hpRMPJRdiY42tNV+ulQxw+3Gpen7s0HIeyvms1azMepOE1KSFjfmIFheM6ApCbRTauh+jtun/+2tN8OWANevTk9MiLqXwcKe2DNFI7FnptAS84hoXAIU='
        acc_no = "63761517-01"
        # broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no)
        exchange = KIS.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, trade_market='')
        return exchange
    def convert_df(df):
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
        return df


    start_time = time.time()
    dict_bong = {'1분봉': '1m', '3분봉': '3m', '5분봉': '5m', '30분봉': '30m', '4시간봉': '4h', '일봉': 'd', '주봉': 'w'}

    # ticker = 'BTC'
    # market = '코인'
    ticker = '122630'
    market = '국내시장'
    # ticker = '코스피200선물'

    bong = '일봉'

    frdate = '2010-01-01'
    todate = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('DB/strategy.db')
    if market == '코인':
        bet = 100
        df = pd.read_sql(f"SELECT * FROM 'coin_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_buy_text = df.loc['변돌','전략코드']
        print(stg_buy_text)
        df = pd.read_sql(f"SELECT * FROM 'coin_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_sell_text = df.loc['변돌_트레일링','전략코드']
        print(stg_sell_text)
        print('======================================')
        conn.close()
        db_file = 'DB/DB_bybit.db'
        con_db = sqlite3.connect(db_file)
        ticker_bong = ticker+'_'+dict_bong[bong]
        ticker_bong_detail = ticker+'_5m'
        trade_market = 'bybit'
        exchange = make_exchange_bybit()


    elif market == '국내시장':
        bet = 1_000_000
        df = pd.read_sql(f"SELECT * FROM 'stock_buy'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_buy_text = df.loc['매수','전략코드']
        df = pd.read_sql(f"SELECT * FROM 'stock_sell'", conn).set_index('index')  # 머니탑 테이블 갖고오기
        stg_sell_text = df.loc['매도','전략코드']
        print(stg_buy_text)
        print(stg_sell_text)
        print('======================================')

        conn.close()

        db_file = 'DB/DB_krx.db'
        con_db = sqlite3.connect(db_file)
        ticker_bong = ticker+'_'+dict_bong[bong]
        ticker_bong_detail = ticker+'_5m'

        list_ksp = []
        list_ksq = []
        list_etf = ['122630']
        list_future = ['코스피200선물']
        if ticker in list_etf:
            trade_market = 'etf'
        elif ticker in list_ksp:
            trade_market = '코스피'
        elif ticker in list_ksq:
            trade_market = '코스닥'
        elif ticker in list_future:
            trade_market = '선물'
        exchange = make_exchange_kis()

    def replace_tabs_with_spaces(text): #스페이스랑 탭 혼용 시 에러 방지용
        space_count = 4
        return text.replace('\t', ' ' * space_count)
    stg_buy_text = replace_tabs_with_spaces(stg_buy_text)
    stg_sell_text = replace_tabs_with_spaces(stg_sell_text)

    df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", con_db).set_index('날짜')
    df_detail = pd.read_sql(f"SELECT * FROM '{ticker_bong_detail}'", con_db).set_index('날짜')
    df.index = pd.to_datetime(df.index)  # datime형태로 변환
    df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환

    if trade_market == 'bybit':
        df['종료시간'] = df.index
        df['종료시간'] = df['종료시간'].shift(-1)
        df['종료시간'] = df['종료시간'] - timedelta(hours=0, minutes=1)
        df_detail = pd.merge(df_detail, df['종료시간'], left_index=True, right_index=True, how='left')
        df_detail['종료시간'].fillna(method='ffill', inplace=True)
        df.drop(['종료시간'], axis=1, inplace=True)  # 중간에 float이나 int형태가 아닌 다른타입이 섞이면 차트 표시 에러남(코인은 종료시간 구하는 코드가 다름)
    elif trade_market == '선물':
        if bong == '일봉':
            df_detail['종료시간'] = np.nan
            serise_end_t = df_detail.groupby(df_detail.index.date).transform(
                lambda x: x.index[-1]).종료시간  # 날짜별 마지막 시간을 같은행에 넣기
            df_detail['종료시간'] = serise_end_t
            df_detail['시작시간'] = np.nan
            serise_start_t = df_detail.groupby(df_detail.index.date).transform(
                lambda x: x.index[0]).시작시간  # 날짜별 마지막 시간을 같은행에 넣기
            df_detail['시작시간'] = serise_start_t
            group = serise_start_t.groupby(serise_start_t)
            list_start_t = group.size().index.tolist()
            df.index = df.index + timedelta(hours=9)  # 일봉일 경우 날짜만 나오기때문에 앞에 우선 시간을 넣어줘야 됨
            list_date = df.index.date.tolist()
            list_idx = df.index.tolist()
            for new_idx in list_start_t:
                if new_idx.date() in list_date:
                    list_idx[list_date.index(new_idx.date())] = new_idx
            df.index = list_idx
            df.index.rename('날짜', inplace=True)  # 인덱스명 변경

    elif trade_market == '코스피' or trade_market == '코스닥' or trade_market == 'etf':
        if bong == '일봉':
            df_detail['종료시간'] = np.nan
            serise_end_t = df_detail.groupby(df_detail.index.date).transform(
                lambda x: x.index[-1]).종료시간  # 날짜별 마지막 시간을 같은행에 넣기
            df_detail['종료시간'] = serise_end_t
            df_detail['시작시간'] = np.nan
            serise_start_t = df_detail.groupby(df_detail.index.date).transform(
                lambda x: x.index[0]).시작시간  # 날짜별 마지막 시간을 같은행에 넣기
            df_detail['시작시간'] = serise_start_t
            group = serise_start_t.groupby(serise_start_t)
            list_start_t = group.size().index.tolist()
            df.index = df.index + timedelta(hours=9)  # 일봉일 경우 날짜만 나오기때문에 앞에 우선 시간을 넣어줘야 됨
            list_date = df.index.date.tolist()
            list_idx = df.index.tolist()
            for new_idx in list_start_t:
                if new_idx.date() in list_date:
                    list_idx[list_date.index(new_idx.date())] = new_idx
            df.index = list_idx
            df.index.rename('날짜', inplace=True)  # 인덱스명 변경
    # df = df[1400:]
    if df.index[0] < df_detail.index[0]:
        df = df[df.index >= df_detail.index[0]]
        df_detail = df_detail[df_detail.index >= df.index[0]]
    elif df.index[0] > df_detail.index[0]:
        df_detail = df_detail[df_detail.index >= df.index[0]]

    if df.index[-1] > df_detail.index[-1]:
        df = df[df.index <= df_detail.index[-1]]
        df_detail = df_detail[df_detail.index < df.index[-1]]
        df = df[df.index < df_detail.index[-1]]
    elif df.index[-1] < df_detail.index[-1]:
        df_detail = df_detail[df_detail.index < df.index[-1]]
        df = df[df.index < df_detail.index[-1]]
    # print(df)
    # print(len(df))
    # print(df_detail)
    df = convert_df(df)
    class min_QCB():
        def isChecked(self):
            return True
    min = min_QCB()
    dict_info = {'market': market, 'trade_market': trade_market, 'exchange': exchange, 'ticker': ticker,
                 'stg_buy': stg_buy_text,
                 'stg_sell': stg_sell_text, 'bet': bet, 'minute_check': min}


    # df = df[:600]
    backtest = backtest_np(df, df_detail, dict_info)
    df = backtest.run()

    # df = pd.read_sql(f"SELECT * FROM 'bt_thread'", sqlite3.connect('DB/bt.db')).set_index('날짜')
    # df=df[:23]

    df['index'] = compare_price(df['종가'],df['strategy'])
    # df.index = df.index.astype(str).str[:10]
    conn.close()

    # df['holding'] = np.log1p(df['holding'])
    df['ror'] = (df['종가']-df['시가'][0])/df['시가'][0]

    df['holding'] = bet+(df['ror']*bet)
    amount = round(df['수익금'].sum(),4)
    games = df['수익금'].count()

    # plt.xlabel('date')
    # plt.ylabel('수익금')
    # plt.plot(df.index,df['asset'])
    df.plot(y=['strategy','index','holding'],
            # logy=True,
            # ylim=(30000000, 100000000),
            figsize=(16, 9),
            grid=True, xlabel=f'종목명: {ticker}, 총 수익금: {amount}, 거래횟수: {games}', ylabel=f'가격',)
    plt.text(200,500,f'종목명: {ticker}, 총 수익금:{amount}, 거래횟수: {games}')
    plt.title('thread')
    plt.legend()
    print(f'총 수익금:{amount}')
    print(f'걸린시간: {(time.time()-start_time)}')

    plt.show()

    # df = df.drop(['이평5',  '이평20',  '이평60', '이평120', '이평200',
    #               # '거래량이평3',
    #               '거래량이평20',
    #               '거래량이평60', 'RSI14', 'RSI18', 'RSI30', 'ATR10', 'TRANGE', '이격도20이평', '밴드20상', '밴드20중',
    #               '밴드20하', '고저평균대비등락율'], axis=1)
    # df.to_sql(ticker, sqlite3.connect('DB/bt.db'), if_exists='replace')