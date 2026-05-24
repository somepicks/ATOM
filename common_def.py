from turtledemo.forest import doit1
import math
import talib
import numpy as np
import subprocess
import pandas as pd
import sqlite3
import ccxt
import KIS
from pandas import to_numeric
import time
from pybit.unified_trading import HTTP

from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, QAbstractItemView
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QTimer, QRegExp,Qt,QThread,pyqtSignal,QWaitCondition,QMutex,QTimer,QObject
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics, QFont, QColor, QSyntaxHighlighter, QTextCharFormat
import datetime
import re
from pprint import pprint
import ccxt.pro as ccxtpro

import pickle
def convert_df(df):
    df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
    df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
    df['이평5'] = talib.MA(df['종가'], 5)
    df['이평20'] = talib.MA(df['종가'], 20)
    df['이평60'] = talib.MA(df['종가'], 60)
    df['이평100'] = talib.MA(df['종가'], 100)
    df['이평120'] = talib.MA(df['종가'], 120)
    df['이평200'] = talib.MA(df['종가'], 200)
    df['이평240'] = talib.MA(df['종가'], 240)
    df['거래량이평3'] = talib.MA(df['거래량'], 3)
    df['거래량이평20'] = talib.MA(df['거래량'], 20)
    df['거래량이평60'] = talib.MA(df['거래량'], 60)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(df['종가'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI'] = talib.RSI(df["종가"], timeperiod=14).round(1)
    df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
    df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
    df['ATR'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
    # df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
    df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
    df['이격도60이평'] = df['종가'].shift(1) / df['이평60'].shift(1) * 100
    df['밴드상'], df['밴드중'], df['밴드하'] = talib.BBANDS(df['종가'], 20, 2)
    df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df
def convert_df_compare(df):
    df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
    df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
    df['이평5'] = talib.MA(df['종가'], 5)
    df['이평20'] = talib.MA(df['종가'], 20)
    df['이평60'] = talib.MA(df['종가'], 60)
    df['이평120'] = talib.MA(df['종가'], 120)
    # df['이평240'] = talib.MA(df['종가'], 200)
    # df['거래량이평3'] = talib.MA(df['거래량'], 3)
    # df['거래량이평20'] = talib.MA(df['거래량'], 20)
    # df['거래량이평60'] = talib.MA(df['거래량'], 60)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(df['종가'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
    # df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
    # df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
    # df['ATR'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
    # df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
    # df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
    # df['이격도60이평'] = df['종가'].shift(1) / df['이평60'].shift(1) * 100
    df['밴드상'], df['밴드중'], df['밴드하'] = talib.BBANDS(df['종가'], 20, 2)
    # df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df
def futopt_set_tickers(df_f,df_f_mini,df_c,df_p,df_c_weekly,df_p_weekly,COND_MRKT):
    # 조건에 '시가_풋옵션_5분봉' 과같은 팩터가 올 수 있으니 비율을 똑같이 해줘야 함
    현재가 = df_f.loc[df_f.index[0], '현재가']
    df_c = df_c[df_c['행사가'] > 현재가 - 30]
    df_c = df_c[df_c['행사가'] < 현재가 + 30]
    df_c['종목명'] = '콜옵션'
    df_p = df_p[df_p['행사가'] > 현재가 - 30]
    df_p = df_p[df_p['행사가'] < 현재가 + 30]
    df_p['종목명'] = '풋옵션'
    df_f.rename(columns={'이론가': '이론가/행사가'}, inplace=True)
    df_f_mini.rename(columns={'이론가': '이론가/행사가'}, inplace=True)
    df_c.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
    df_p.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
    # df = ex.fetch_closed_roder(side='매수',ticker='005930')
    #옵션은 시가를 종목별로 조회해야 나오므로 그냥 0으로 표기
    df_c['시가'] = 0
    df_p['시가'] = 0
    df_c_weekly['시가'] = 0
    df_p_weekly['시가'] = 0
    # 공통된 컬럼명 찾기
    common_columns = list(set(df_f.columns).intersection(df_c.columns).intersection(df_p.columns))
    # 공통된 컬럼명만 추출하여 새로운 데이터프레임 생성
    df_f_common = df_f[common_columns]
    df_f_mini_common = df_f_mini[common_columns]
    df_c_common = df_c[common_columns]
    df_p_common = df_p[common_columns]
    # 구분 표시 행 생성 함수
    def create_separator_row(columns):
        return pd.DataFrame({col: '===' for col in columns}, index=[0])
    # 각 데이터프레임에 구분 행 추가
    df1_with_separator = pd.concat([df_f_common, create_separator_row(common_columns)], ignore_index=True)
    df2_with_separator = pd.concat([df_f_mini_common, create_separator_row(common_columns)], ignore_index=True)
    df3_with_separator = pd.concat([df_c_common, create_separator_row(common_columns)], ignore_index=True)
    df4_with_separator = pd.concat([df_p_common, create_separator_row(common_columns)], ignore_index=True)

    # 모든 데이터프레임을 합치기
    df_combined = pd.concat([df1_with_separator, df2_with_separator, df3_with_separator, df4_with_separator], ignore_index=True)

    if not df_c_weekly.empty and not df_p_weekly.empty:
        if COND_MRKT == "WKM":
            yoil = '월'
        elif COND_MRKT == "WKI":
            yoil = '목'
        else:
            yoil = '만기'

        df_c_weekly = df_c_weekly[df_c_weekly['행사가'] > 현재가 - 30]
        df_c_weekly = df_c_weekly[df_c_weekly['행사가'] < 현재가 + 30]
        df_c_weekly['종목명'] = '콜' + '_위클리_' + yoil

        df_p_weekly = df_p_weekly[df_p_weekly['행사가'] > 현재가 - 30]
        df_p_weekly = df_p_weekly[df_p_weekly['행사가'] < 현재가 + 30]
        df_p_weekly['종목명'] = '풋' + '_위클리_' + yoil

        df_c_weekly.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
        df_p_weekly.rename(columns={'행사가': '이론가/행사가'}, inplace=True)
        df_c_weekly_common = df_c_weekly[common_columns]
        df_p_weekly_common = df_p_weekly[common_columns]
        df4_with_separator = pd.concat([df_c_weekly_common, create_separator_row(common_columns)], ignore_index=True)
        df5_with_separator = pd.concat([df_p_weekly_common, create_separator_row(common_columns)], ignore_index=True)
        df_combined = pd.concat([df_combined, df4_with_separator, df5_with_separator], ignore_index=True)

    df_combined = df_combined[['종목코드', '현재가','시가',  '이론가/행사가', '거래량', '거래대금', '전일대비','종목명','만기일','지난만기일']]
    return df_combined

def stamp_to_df(df):
    # df = pd.DataFrame(list_data, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
    df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
    df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
    df['날짜'] = df['날짜'].dt.tz_localize(None)
    df.set_index('날짜', inplace=True)
    return df

def get_coin_initial_data(market, dict_option, ohlcv, since, ticker, limit, bong_detail):
    i = 0
    err_i = 0
    dict_bong_stamp = {'1분봉': 1 * 60, '3분봉': 3 * 60, '5분봉': 5 * 60, '15분봉': 15 * 60, '30분봉': 30 * 60, '1시간봉': 60 * 60,
                       '4시간봉': 240 * 60, '일봉': 1440 * 60,
                       '주봉': 10080 * 60}
    print(f"{ticker=}   {limit= }    {since= }")
    while True:
        i += 1
        # try:
        QTest.qWait(200)
        if market == 'bybit':
            new_ohlcv = dict_option['bybit'].fetch_ohlcv(symbol=ticker + 'USDT', timeframe="1m",
                                                          limit=limit, since=int(since * 1000))  # 밀리초로 전달
        elif market == 'binance':
            new_ohlcv = dict_option['linear'].fetch_ohlcv(symbol=ticker + 'USDT', timeframe="1m",
                                                           limit=limit, since=int(since * 1000))  # 밀리초로 전달
        elif market == '업비트':
            new_ohlcv = dict_option['exchange'].fetch_ohlcv(symbol=ticker + '/KRW', timeframe="1m",
                                                             limit=limit, since=int(since * 1000))  # 밀리초로 전달
        else:
            new_ohlcv = []
        QTest.qWait(500)
        # print(new_ohlcv[-1][0]) #최근 가까운
        # print(new_ohlcv[0][0]) #멀리 오래된
        ohlcv = ohlcv+new_ohlcv  # 순서만 바꾸면 됨

        try:
            print(f"{cyan(ticker) + 'USDT'} DB 저장 중...start time - 조회 {stamp_to_datetime(since)}:" , end="")
            since = (new_ohlcv[-1][0] / 1000) + dict_bong_stamp[bong_detail]  # 다음봉 시간 계산
            print(f" 결과 값{stamp_to_datetime(new_ohlcv[0][0])}   {stamp_to_datetime(new_ohlcv[-1][0])}   다음조회: {datetime.datetime.fromtimestamp(math.trunc(since))}[{i}]")
        except:
            err_i += 1
            pprint(new_ohlcv)
            print(datetime.datetime.now())
            print(stamp_to_datetime(since))
            print(f"{limit=} {since=}   ")
            print(f'error get_coin_initial_data {err_i=}')
            QTest.qWait(500)
            if err_i >10:
                return ohlcv
            return ohlcv
        if since > time.time():
            # print(end="저장 완료")
            return ohlcv
def get_coin_ohlcv_real(dict_option, ohlcv, since, ticker, limit, bong_detail):
    def fill_missing_candles(ohlcv, new_data):
        """  인터넷 끊김 등으로 빠진 구간 채우기 + 마지막 현재봉 업데이트 """
        if not ohlcv or not new_data:
            return ohlcv
        # 새 데이터를 dict로 변환 {timestamp: candle}
        new_dict = {candle[0]: candle for candle in new_data}
        # 기존 데이터를 dict로 변환
        ohlcv_dict = {candle[0]: candle for candle in ohlcv}
        # 새 데이터로 업데이트 (빠진 구간 + 마지막봉 갱신 모두 처리)
        ohlcv_dict.update(new_dict)
        # 정렬 후 리스트로 반환
        result = sorted(ohlcv_dict.values(), key=lambda x: x[0])
        return result
    def update_latest(ohlcv, new_candles):
        """
        현재 진행중인 마지막 봉 업데이트 + 끊긴 구간 보완
        new_candles: 최근 fetch한 소량의 데이터
        """
        if not new_candles:
            return ohlcv

        last_ohlcv_ts = ohlcv[-1][0] if ohlcv else 0
        new_last_ts = new_candles[-1][0]

        # 마지막 타임스탬프 차이 (분 단위)
        gap_minutes = (new_last_ts - last_ohlcv_ts) // 60000

        if gap_minutes > 1:
            # 1분 이상 차이나면 끊김 발생 → 빠진 구간 채우기
            print(f"[!] {gap_minutes}분 데이터 누락 감지, 보완 중...")
            ohlcv = fill_missing_candles(ohlcv, new_candles)
        else:
            # 정상: 마지막 봉만 교체 (진행중인 봉 갱신)
            if ohlcv[-1][0] == new_candles[-1][0]:
                ohlcv[-1] = new_candles[-1]  # 현재봉 업데이트
            else:
                ohlcv.append(new_candles[-1])  # 새 봉 추가

        return ohlcv
    dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '1시간봉': '1h', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
    try:
        if dict_option['market'] == 'bybit':
            new_candles = dict_option['bybit'].fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong_detail],
                                                   limit=limit, since=int(since*1000)) #밀리초로 전달
        elif dict_option['market'] == 'binance':
            new_candles = dict_option['linear'].fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong_detail],
                                                   limit=limit, since=int(since*1000)) #밀리초로 전달
        elif dict_option['market'] == '업비트':
            new_candles = dict_option['exchange'].fetch_ohlcv(symbol=ticker + '/KRW', timeframe=dict_bong[bong_detail], limit=5) #밀리초로 전달
        else:
            new_candles = []
        if new_candles:
            ohlcv = update_latest(ohlcv, new_candles)
            consecutive_errors = 0
            return ohlcv

    except ccxt.RateLimitExceeded:
        print("[!] Rate limit, 5초 대기...")

    except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
        consecutive_errors += 1
        wait = min(60, 5 * consecutive_errors)
        print(f"[!] 네트워크 오류 ({consecutive_errors}회 연속), {wait}초 후 재시도: {e}")

    except Exception as e:
        print(f"[!] 오류 발생: {e}")


def get_funding_rates(market, dict_ex, list_inverse):
    if market == 'bybit':
        list_res_btc = dict_ex['bybit'].fetch_funding_rate_history(symbol='BTCUSD', since=None )
    elif market == 'binance':
        list_res_btc = dict_ex['spot'].fetch_funding_rate_history(symbol='BTCUSD_PERP', since=None, params={'type': 'delivery'})
    else:
        print(f"market 확인 필요")
    std_len = len(list_res_btc)
    btc_date_end = (list_res_btc[-1]['timestamp']//1000)*1000
    btc_date_from = (list_res_btc[0]['timestamp']//1000)*1000
    df_funding = pd.DataFrame()
    print(f"{btc_date_from=}    {stamp_to_datetime(btc_date_from - 32400000)}   {btc_date_end=}    {stamp_to_datetime(btc_date_end - 32400000)}   ")

    for i, ticker in enumerate(list_inverse):
        print(ticker)
        i=0
        list_res_total = []
        from_time = btc_date_from
        while True:
            if market == 'bybit':
                symbol = ticker + 'USD'
                list_res = dict_ex['bybit'].fetch_funding_rate_history(symbol=symbol, since=from_time)
            elif market == 'binance':
                symbol = ticker + 'USD_PERP'
                list_res = dict_ex['spot'].fetch_funding_rate_history(symbol=symbol, since=from_time,params={'type': 'delivery'})
            else:
                list_res = []

            for item in list_res:
                del item['info']
                # del item['fundingRate']
                del item['symbol']
            # pprint(list_res)
            # print('===========================================')
            if not list_res:
                break
            else:
                list_timestamp = []
                for item in list_res:
                    item['timestamp'] = item['timestamp'] // 1000 *1000 # 데이터 시간이 1000/1 초정도 잘못 찍히는 경우가 있어서 변환
                    list_timestamp.append(item['timestamp'])

                if len(list_res) < std_len or not from_time in list_timestamp:
                    list_res.extend(list_res_total)
                    list_res_total = list_res
                    break

                else:
                    get_time = list_res[0]['timestamp']
                    from_time = get_time - (8 * 3600 * 1000 * len(list_res))
                    # print(f"{get_time=}    {stamp_to_datetime(get_time-32400000)}    | {len(list_res)} |    {from_time=}    {stamp_to_datetime(from_time-32400000)}   ") # utc+0 기준으로 표시하기위해 -32400000
                    list_res.extend(list_res_total)
                    list_res_total = list_res
                # i += 1
                # if i == 2:
                #     quit()

        data = [x['fundingRate'] for x in list_res_total]
        timestamps = [x['timestamp'] for x in list_res_total]
        df = pd.DataFrame({
            f'{ticker}': data,
            '날짜': timestamps
        })
        # df[f'{ticker}_d'] = df['날짜'].apply(stamp_to_str)

        df = df[~df.날짜.duplicated(keep='last')]
        df.set_index('날짜', inplace=True)


        if df.index[-1] == btc_date_end:
            if not df_funding.empty:
                if df_funding.index[0] <= df.index[0]:
                    df_funding = pd.concat([df_funding, df], axis=1) #오래된 데이터가 앞으로 오도록해야 날짜가 뒤죽박죽 안됨
                else:
                    df_funding = pd.concat([df, df_funding], axis=1)
            else: #df_funding이 비어있을 경우
                df_funding = df
    return df_funding
class common(QObject):
    send_make_df = pyqtSignal(pd.DataFrame,dict)
    send_trend_df = pyqtSignal(pd.DataFrame)
    df_real_chart = pyqtSignal(pd.DataFrame)
    def __init__(self, market,dict_option):
        super().__init__()
        self.market = market
        self.dict_option = dict_option
        self.dict_bong_int_reverse = {1:'1분봉' , 3:'3분봉', 5:'5분봉' , 15:'15분봉' ,30 :'30분봉' ,
        60:'1시간봉' ,4 * 60:'4시간봉', 24 * 60 :'일봉' }
        self.dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '1시간봉': 60, '4시간봉': 240, '일봉': 1440,
                           '주봉': 10080}
        self.dict_bong_time_datetime = {1: datetime.timedelta(minutes=1), 3: datetime.timedelta(minutes=3),
                                        5: datetime.timedelta(minutes=5), 15: datetime.timedelta(minutes=15),
                                        30: datetime.timedelta(minutes=30),60: datetime.timedelta(minutes=60),
                                        240: datetime.timedelta(minutes=240), 1440: datetime.timedelta(days=1)}
        self.df_trend = pd.DataFrame()

    def make_df(self, dict_info, ohlcv):
        if self.market == '국내주식':
            if ticker_full_name in globals():  # 만들어진 df가 있을 경우 데이터는 종목_봉_생성봉에 따라 다름에 유의
                ohlcv = globals()[ticker_full_name]
                if bong == '일봉':
                    if not ohlcv.empty:
                        df = common_def.convert_df(ohlcv)
                        dict_output = ex_kis.fetch_price(ticker)
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
                    output = ex_kis._fetch_1m_ohlcv(symbol=ticker,to=datetime.datetime.now().strftime("%H%M%S"),fake_tick=True)  # to = 현재시간, 허봉 포함
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
                    df = ex_kis.fetch_ohlcv(symbol=ticker,early_day=date_old)
                    if not df.empty:
                        globals()[ticker_full_name] = df.copy()
                        df = common_def.convert_df(df)
                else:
                    # df = common_def.get_kis_ohlcv(market,ohlcv)
                    if ticker_full_name.count('_') == 2:  # 진입대상의 경우 'BTC_5분봉_1분봉'으로 표시되기 때문에
                        df_standard, df = common_def.detail_to_spread(df, bong, bong_detail)
                    else:  # 비교대상의 경우 'BTC_5분봉'
                        df = common_def.detail_to_compare(df, cker_full_name)
        elif self.market == '국내선옵':
                # 시간 단축을 위해 데이터프레임에서 필요없는 팩터 지우기
                # df_check = common_def.get_kis_ohlcv(market,ohlcv)
                # df_standard, df_check = common_def.detail_to_spread(df_check, dict_stg['봉'], dict_stg['상세봉'])
                # li_factor = []
                # for factor in df_check.columns.tolist():
                #     if not factor in str(dict_stg['진입전략'] + dict_stg['청산전략']):  # 실제 전략에 필요한 팩터만 남기고 데이터프레임에서 삭제
                #         if not factor in ['상세시가', '상세고가', '상세저가', '상세종가', '시가', '고가', '저가', '종가', '종료시간',
                #                           '현재시간', '장시작시간', '장종료시간']:  # 삭제에서 제외
                #             df_check.drop(factor, axis=1, inplace=True)
                #             li_factor.append(factor)
            df = self.dict_option["exchange"].get_kis_ohlcv(ohlcv)
            if dict_info["check_compare"]:  # 비교대상일 경우
                df = detail_to_compare(df, dict_info["봉"])
                # df = df.add_prefix(f'{ticker}_{bong}_') #XRP_15분봉_시가 컬럼명 앞에넣기
                df = df.add_suffix(f'_{ticker}_{dict_info["봉"]}') #시가_XRP_15분봉 컬럼명 뒤에넣기
            if not dict_info["check_compare"]:  # 진입대상일 경우
                df_standard, df = self.detail_to_spread(market = self.market,df_min=df, bong=dict_info["봉"], compare=False)
        elif self.market =='bybit' or self.market == '업비트':
            df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            df['거래대금'] = df['종가']*df['거래량']
            df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
            df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
            df['날짜'] = df['날짜'].dt.tz_localize(None)
            df.set_index('날짜', inplace=True)
            if self.market == 'bybit':
                df.index = df.index - pd.Timedelta(hours=9)
            if dict_info["check_compare"]: #비교대상일 경우
                df = detail_to_compare(df, dict_info["봉"])
                # df = df.add_prefix(f'{ticker}_{bong}_') #XRP_15분봉_시가 컬럼명 앞에넣기
                df = df.add_suffix(f'_{ticker}_{dict_info["봉"]}') #시가_XRP_15분봉 컬럼명 뒤에넣기
            else: #진입대상일 경우
                df_standard, df = self.detail_to_spread(market = self.market,df_min=df, bong=dict_info["봉"], compare=False)
            if self.market == 'bybit':
                df.index = df.index + pd.Timedelta(hours=9)
        else:
            print(f"마켓 확인 {self.market= }")
            df = pd.DataFrame()
        if dict_info["req"] == 'real_chart':  # real_chart로 df를 보낼때
            df = df.apply(pd.to_numeric, errors='coerce')
            self.df_real_chart.emit(df)
        elif dict_info["req"] == 'trade':
            df.fillna(method='ffill', inplace=True)
            if dict_info['현재시간']-df.loc[df.index[-1],'현재봉시간'] > self.dict_bong_time_datetime[dict_info['봉']]:
                print(f"common_def_make_df: {dict_info['현재시간']}    {df.loc[df.index[-1],'현재봉시간']}")
            else:
                self.send_make_df.emit(df,dict_info)
        else:
            print(f"common(QObject) {dict_info= }")
            quit()
        # data = df.to_numpy(dtype=float)
        # return df

    def resample_df(self, df, bong, rule, name, compare):
        ohlc_dict = {
            '상세시가': 'first',
            '상세고가': 'max',
            '상세저가': 'min',
            '상세종가': 'last',
            '상세거래량': 'sum',
            '상세거래대금': 'sum'
        }
        # try:
        df = df.resample(rule).apply(ohlc_dict).dropna()
        # except TypeError:
        #     print('타입에러')
        #     df.index = pd.to_datetime(df.index)
        #     df = df.resample(rule).apply(ohlc_dict).dropna()
        if bong == name:  # 기준봉일 경우
            df.rename(columns={f'상세시가': f'시가', f'상세고가': f'고가', f'상세저가': f'저가', f'상세종가': f'종가',
                               f'상세거래량': f'거래량', f'상세거래대금': f'거래대금'}, inplace=True)  # 컬럼명 변경
            if compare:
                df = convert_df_compare(df)
            else:
                df = convert_df(df)
            df['현재봉시간'] = df.index
            # df[f'시가_{name}'] = df['시가'].copy()
            # df[f'고가_{name}'] = df['고가'].copy()
            # df[f'저가_{name}'] = df['저가'].copy()
            # df[f'종가_{name}'] = df['종가'].copy()
            # df[f'거래량_{name}'] = df['거래량'].copy()
            # # df[f'거래대금_{name}'] = df['거래대금'].copy()
            # df[f'이평5_{name}'] = df['이평5'].copy()
            # df[f'이평20_{name}'] = df['이평20'].copy()
            # df[f'이평60_{name}'] = df['이평60'].copy()

        else:
            df.rename(columns={'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
                               '상세거래량': f'거래량_{name}', '상세거래대금': f'거래대금_{name}'}, inplace=True)  # 컬럼명 변경
            df[f'이평5_{name}'] = talib.MA(df[f'종가_{name}'], 5)
            df[f'이평20_{name}'] = talib.MA(df[f'종가_{name}'], 20)
            df[f'이평60_{name}'] = talib.MA(df[f'종가_{name}'], 60)
            df[f'데이터길이_{name}'] = np.arange(1, len(df.index.tolist()) + 1,
                                            1)  # start=1, stop=len(df.index.tolist())+1, step=1
        return df

    # bong을 ''로 받으면 기준이 되는 봉이 없기 때문에 일단 시가,고가,저가 가 없고
    def detail_to_spread(self, market, df_min, bong, bong_detail: str = '1분봉',
                         compare: bool = False):  # df=특정봉데이터반환, df_combined=전체봉데이터반환

        df_min.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                               '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
        detail_unit = self.dict_bong_stamp[bong_detail]
        bong = self.dict_bong_int_reverse[bong]
        if detail_unit == self.dict_bong_stamp['1분봉']:
            df_1min = self.resample_df(df_min, bong, '1min', '1분봉', compare)
        if detail_unit < self.dict_bong_stamp['3분봉']:
            df_3min = self.resample_df(df_min, bong, '3min', '3분봉', compare)
        if detail_unit < self.dict_bong_stamp['5분봉']:
            df_5min = self.resample_df(df_min, bong, '5min', '5분봉', compare)
        if detail_unit < self.dict_bong_stamp['15분봉']:
            df_15min = self.resample_df(df_min, bong, '15min', '15분봉', compare)
        if detail_unit < self.dict_bong_stamp['30분봉']:
            df_30min = self.resample_df(df_min, bong, '30min', '30분봉', compare)
        if detail_unit < self.dict_bong_stamp['1시간봉']:
            df_60min = self.resample_df(df_min, bong, '60min', '1시간봉', compare)
        if detail_unit < self.dict_bong_stamp['4시간봉'] and (market == 'bybit' or market == '업비트'):
            df_4h = self.resample_df(df_min, bong, '240min', '4시간봉', compare)
        df_daily = self.resample_df(df_min, bong, 'D', '일봉', compare)
        df_weekly = self.resample_df(df_min, bong, 'W', '주봉', compare)
        # df_monthly = resample_df(df_min, bong, 'ME', '월봉',compare)
        df_daily['date'] = df_daily.index.date
        df_weekly['week'] = df_weekly.index.to_period('W').astype(str)
        # df_monthly['month'] = df_monthly.index.to_period('M').astype(str)
        df_min['date'] = df_min.index.date
        df_min['week'] = df_min.index.to_period('W').astype(str)
        # df_min['month'] = df_min.index.to_period('M').astype(str)

        # if detail_unit == self.dict_bong_stamp['1분봉']:
        #     df_min = pd.merge(df_min, df_1min, left_index=True, right_index=True, how='left')
        if detail_unit < self.dict_bong_stamp['3분봉']:
            df_min = pd.merge(df_min, df_3min, left_index=True, right_index=True,
                              how='outer').sort_index()  # 결측없이 모두 합친후 인덱스 기준으로 정렬
        if detail_unit < self.dict_bong_stamp['5분봉']:
            df_min = pd.merge(df_min, df_5min, left_index=True, right_index=True, how='outer').sort_index()
        if detail_unit < self.dict_bong_stamp['15분봉']:
            df_min = pd.merge(df_min, df_15min, left_index=True, right_index=True, how='outer').sort_index()
        if detail_unit < self.dict_bong_stamp['30분봉']:
            df_min = pd.merge(df_min, df_30min, left_index=True, right_index=True, how='outer').sort_index()
        if detail_unit < self.dict_bong_stamp['1시간봉']:
            df_min = pd.merge(df_min, df_60min, left_index=True, right_index=True, how='outer').sort_index()
        if detail_unit < self.dict_bong_stamp['4시간봉'] and market == 'bybit':
            df_min = pd.merge(df_min, df_4h, left_index=True, right_index=True, how='outer').sort_index()
        df_combined = df_min.merge(df_daily, on='date', how='left', suffixes=('', '_daily')).sort_index()
        df_combined = df_combined.merge(df_weekly, on='week', how='left', suffixes=('', '_weekly')).sort_index()
        # df_combined = df_combined.merge(df_monthly, on='month',how='left', suffixes=('', '_monthly'))
        df_combined.fillna(method='ffill', inplace=True)
        list_idx = df_min.index.tolist()
        df_combined.ffill(inplace=True)
        df_combined.index = list_idx  # fillna를 하면 인덱스가 숫자로 바뀜
        df_combined.index.rename('날짜', inplace=True)  # 인덱스명 변경
        df_combined.drop('date', axis=1, inplace=True)
        df_combined.drop('week', axis=1, inplace=True)
        # df_combined.drop('month', axis=1, inplace=True)

        df = df_1min if bong == '1분봉' else df_3min if bong == '3분봉' else df_5min if bong == '5분봉' else df_15min if (
                bong == '15분봉') else df_30min if bong == '30분봉' else df_60min if bong == '1시간봉' else df_4h if (
                bong == '4시간봉') else df_daily if bong == '일봉' else df_weekly if bong == '주봉' else pd.DataFrame()
        ####################################################### 이하 df에 기준봉에 대한 데이터말고 30분봉, 4시간봉 등 추가하기
        # list_idx = df.index.tolist()
        # df['date'] = df.index.date
        # df['week'] = df.index.to_period('W').astype(str)
        # if dict_bong_stamp[bong] < dict_bong_stamp['3분봉']:
        #     df = pd.merge(df, df_3min, left_index=True, right_index=True, how='left')
        # if dict_bong_stamp[bong] < dict_bong_stamp['5분봉']:
        #     df = pd.merge(df, df_5min, left_index=True, right_index=True, how='left')
        # if dict_bong_stamp[bong] < dict_bong_stamp['15분봉']:
        #     df = pd.merge(df, df_15min, left_index=True, right_index=True, how='left')
        # if dict_bong_stamp[bong] < dict_bong_stamp['30분봉']:
        #     df = pd.merge(df, df_30min, left_index=True, right_index=True, how='left')
        # if dict_bong_stamp[bong] < dict_bong_stamp['1시간봉']:
        #     df = pd.merge(df, df_60min, left_index=True, right_index=True, how='left')
        # if dict_bong_stamp[bong] < dict_bong_stamp['4시간봉']:
        #     df = pd.merge(df, df_4h, left_index=True, right_index=True, how='left')
        # df = df.merge(df_daily, on='date',how='left', suffixes=('', '_daily'))
        # df = df.merge(df_weekly, on='week',how='left', suffixes=('', '_weekly'))
        # df.ffill(inplace=True)
        # df.index = list_idx
        # df.index.rename('날짜', inplace=True)  # 인덱스명 변경
        # df.drop('date', axis=1, inplace=True)
        # df.drop('week', axis=1, inplace=True)
        #######################################################
        # df = df[[col for col in df.columns if not col.endswith(bong)]] #컬럼명이 기준봉으로 끝나는 컬럼명은 삭제
        return df, df_combined

    def trend_time(self):
        now_dt = datetime.datetime.now().replace(second=0,microsecond=0)
        self.df_trend = self.dict_option["exchange"].add_trend(현재시간=now_dt,df_trend=self.df_trend,COND_MRKT=self.dict_option['cond_mrkt']) #투자자별
        self.send_trend_df.emit(self.df_trend)


def fetch_inverse_list(market,dict_ex):
    if market == 'bybit':
        # 바이비트 inverse 종목 정리
        list_bybit_inverse = []
        if not dict_ex['bybit'] == None:
            markets = dict_ex['bybit'].load_markets()
            # inverse 종목만 필터링
            inverse_markets = {}
            for symbol, market in markets.items():
                if market.get('inverse') == True:
                    inverse_markets[symbol] = market
            # inverse 종목 목록 출력
            for symbol in inverse_markets:
                list_bybit_inverse.append(symbol[:symbol.index('/')])
        else:
            list_bybit_inverse = []
        list_inverse = list(set(list_bybit_inverse))
    elif market == 'binance':
        # res = ex_binance.fetch_balance(params={"type": 'delivery'})
        markets = dict_ex['spot'].load_markets()
        # Coin-M Perpetual 종목만 필터링
        perpetual_symbols = []
        for symbol, identity in markets.items():
            if identity['type'] == 'swap' and identity['settle'] != 'USDT' and identity['quote'] == 'USD':
                perpetual_symbols.append({
                    'symbol': symbol,
                    'base': identity['base'],
                    'quote': identity['quote'],
                    'settle': identity['settle'],
                    'contract_size': identity['contractSize'],
                    'active': identity['active']
                })
        df_inverse = pd.DataFrame(perpetual_symbols)
        list_inverse = df_inverse['base'].tolist()
    else:
        list_inverse = []
    return list_inverse


def detail_to_compare(df, bong):
    dict_bong_rule = {'1분봉': '1min', '3분봉': '3min', '5분봉': '5min', '15분봉': '15min', '30분봉': '30min', '1시간봉': '60min', '4시간봉': '240min', '일봉': 'D',
                       '주봉': 'W'}
    df.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
    df = resample_df(df, bong, dict_bong_rule[bong], bong, True)
    # 컬럼명중에 bong 이름이 들어가는 컬럼을 제거 ( '시가_일봉_BTC_일봉' 이렇게 나오기 때문에)
    df = df.drop(columns=df.filter(like='_'+bong).columns)
    return df
def make_exchange_bybit(api: str ='', secret: str=''):
    import pickle
    import os
    token_name = "DB/token.dat"
    if os.path.isfile(token_name):  # 파일이 있으면
        f = open(token_name, "rb")
        data = pickle.load(f)
        f.close()
    else:
        data = {}
    if "bybit" in data.keys():
        api = data["bybit"]['api']
        secret = data["bybit"]['secret']
    else:
        data["bybit"] = {}
        data["bybit"]['api'] = api
        data["bybit"]['secret'] = secret
        with open(token_name, "wb") as f:
            pickle.dump(data, f)
    exchange_ccxt = ccxt.bybit(config={
        'apiKey': api,
        'secret': secret,
        'enableRateLimit': True,
        'options': {'position_mode': True,},
        })
    exchange_pybit = HTTP(
            testnet = False,
            api_key = api,
            api_secret = secret,
        )
    return exchange_ccxt, exchange_pybit

def make_exchange_upbit(api: str ='', secret: str=''):
    import pickle
    import os
    token_name = "DB/token.dat"
    if os.path.isfile(token_name):  # 파일이 있으면
        f = open(token_name, "rb")
        data = pickle.load(f)
        f.close()
    else:
        data = {}
    if "업비트" in data.keys():
        api = data["업비트"]['api']
        secret = data["업비트"]['secret']
    else:
        data["업비트"] = {}
        data["업비트"]['api'] = api
        data["업비트"]['secret'] = secret
        with open(token_name, "wb") as f:
            pickle.dump(data, f)
    client = ccxt.upbit({
        "apiKey": api,
        "secret": secret
    })
    return client
def make_exchange_upbit_ws(api: str ='', secret: str=''):
    import pickle
    import os
    token_name = "DB/token.dat"
    if os.path.isfile(token_name):  # 파일이 있으면
        f = open(token_name, "rb")
        data = pickle.load(f)
        f.close()
    else:
        data = {}
    api = data.get("업비트", {}).get('api', '')
    secret = data.get("업비트", {}).get('secret', '')
    client = ccxtpro.upbit({
        "apiKey": api,
        "secret": secret
    })
    return client
def make_exchange_upbit_pro(api: str ='', secret: str=''):
    import pickle
    import os
    token_name = "DB/token.dat"
    if os.path.isfile(token_name):  # 파일이 있으면
        f = open(token_name, "rb")
        data = pickle.load(f)
        f.close()
    else:
        data = {}
    if "업비트" in data.keys():
        api = data["업비트"]['api']
        secret = data["업비트"]['secret']
    else:
        data["업비트"] = {}
        data["업비트"]['api'] = api
        data["업비트"]['secret'] = secret
        with open(token_name, "wb") as f:
            pickle.dump(data, f)
    client = ccxtpro.upbit({'apiKey': api, 'secret': secret})
    return client
def replace_indicators(text):
    indicators = ['rsi', 'macd', 'ema', 'sma', 'roc', 'cci','macdn','macd_signal','macd_hist']
    replacements = {ind.lower(): ind.upper() for ind in indicators}
    pattern = re.compile(r'\b(' + '|'.join(replacements.keys()) + r')\b', re.IGNORECASE)
    return pattern.sub(lambda m: replacements[m.group().lower()], text)

def make_exchange_binance():
    conn = sqlite3.connect('DB/setting.db')
    df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
    conn.close()
    api = df.loc['binance_API', 'value']
    secret = df.loc['binance_SECRET', 'value']
    if api == None or secret == None:
        # or np.isnan(api) or np.isnan(secret):
        print('binance API 확인 필요')
        spot = None
        linear = None
        coinm = None
        active = False
    else:
        spot = ccxt.binance(config={
            'apiKey': api,
            'secret': secret,
            'enableRateLimit': True,
            'options': {'position_mode': True, }, })
        linear = ccxt.binance(config={
            'apiKey': api,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                # 'position_mode': True,  #롱 & 숏을 동시에 유지하면서 리스크 관리(헷징)할 때
                'defaultType': 'future'}, })
        coinm = ccxt.binance({
            'apiKey': api,
            'secret': secret,
            #                 'sandbox': sandbox,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'delivery'  # COIN-M Futures
            }})
        active = True
        try:
            spot.load_markets()
        # except ccxt.base.errors.AuthenticationError as e:
        except:
            print("바이낸스 API 연결 에러",
                  '''binance {"code":-2015,"msg":"Invalid API-key, IP, or permissions for action."}''')
    return {'active': active, 'spot': spot, 'linear': linear, 'coinm': coinm}


def make_start_stop(df_detail, detail_stamp):
###########################################################################
    # 백터화 된 방법으로 변경
    # 날짜 추출
    dates = pd.Series(df_detail.index.date, index=df_detail.index)

    # 첫/마지막 인덱스
    first_idx = dates.drop_duplicates(keep='first').index
    last_idx = dates.drop_duplicates(keep='last').index

    # 딕셔너리 생성
    date_to_times = {
        'first': dict(zip(df_detail.loc[first_idx].index.date,
                          df_detail.loc[first_idx].index)),
        'last': dict(zip(df_detail.loc[last_idx].index.date,
                         df_detail.loc[last_idx].index))
    }
    # 매핑
    date_array = pd.Series(df_detail.index.date)
    df_detail['장시작시간'] = date_array.map(date_to_times['first']).values
    df_detail['장종료시간'] = date_array.map(date_to_times['last']).values
###########################################################################
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
    ###
    return df_detail

def get_df_detail(ticker:str,frdate:str,todate:str,bong:str,bong_detail:str='1분봉') -> pd.DataFrame:
    if ticker in ['BTC','ETH','LTC']:
        market = 'bybit'
        val_range = None
    elif ticker in ['선물','미니선물','콜옵션','풋옵션','위클리_콜옵션','위클리_풋옵션']:
        market = '국내선옵'
        val_range = None
    else:
        market = '국내주식'

    frdate = datetime.datetime.strptime(frdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(todate, '%Y-%m-%d')

    if market == 'bybit':
        conn_DB = sqlite3.connect('DB/DB_bybit.db')
    elif market == '국내주식' :
        conn_DB = sqlite3.connect('DB/DB_stock.db')
    elif market == '국내선옵':
        conn_DB = sqlite3.connect('DB/DB_futopt.db')
    else:
        conn_DB = ''

    dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '1시간봉': 60, '4시간봉': 240, '일봉': 1440,
                       '주봉': 10080}
    # if val_range is None:
    ticker_detail = ticker + '_' + bong_detail
    df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", conn_DB).set_index('날짜')
    df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
    df_detail = df_detail.loc[(df_detail.index >= frdate) & (df_detail.index <= todate)]
    if market == 'bybit':
        df_detail.index = df_detail.index - pd.Timedelta(hours=9)
        df, df_detail = detail_to_spread('bybit',df_detail, bong, bong_detail)
        df_detail.index = df_detail.index + pd.Timedelta(hours=9)
        df.index = df.index + pd.Timedelta(hours=9) # 판다스 버전차이로 아래로 변경
        # df.index = df.index.shift(9, freq='H')
        for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
            start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
            end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
            df_detail.loc[start_time:end_time, '장시작시간'] = start_time
            df_detail.loc[start_time:end_time, '장종료시간'] = end_time

    elif market == '국내주식' or market == '국내선옵':
        df_detail.index = df_detail.index - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
        # df_detail = df_detail[df_detail.index >= datetime.strptime("20200326","%Y%m%d")]
        df, df_detail = detail_to_spread(market,df_detail, bong, bong_detail)
        df_detail = make_start_stop(df_detail, dict_bong_stamp[bong_detail])
    df_detail['현재시간'] = df_detail.index
    if bong == '일봉':
        df_detail['종료시간'] = df_detail['장종료시간'].copy()
    elif bong != '일봉' and bong != '주봉' and bong != '월봉':
        # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
        # df_detail['종료시간'] = df_detail.index
        # df_detail_end_time = df_detail['종료시간'].resample(f'{dict_bong_stamp[bong]}min').last()
        # del df_detail['종료시간']
        # df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
        # df_detail.ffill(inplace=True)
        # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
        df_detail_end_time = df_detail['현재시간'].resample(f'{dict_bong_stamp[bong]}min').last()
        df_detail_end_time = pd.Series(df_detail_end_time, name='종료시간')  # 추출한 시리즈의 이름을 종료시간으로 변경
        df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
        df_detail.ffill(inplace=True)
        df_detail['종료시간'] = df_detail['종료시간'] + pd.Timedelta(seconds=59) # 59초 더하기
        df_detail['장종료시간'] = df_detail['장종료시간'] + pd.Timedelta(seconds=59)

    df_detail['데이터길이'] = df_detail['데이터길이'].fillna(1)  # nan을 0으로 채우기
    df_detail['시분초'] = df_detail.index.hour * 10000 + df_detail.index.minute * 100 + df_detail.index.second
    df['매수가'] = np.nan
    df['매도가'] = np.nan
    df['보유수량'] = np.nan
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

    exclude_cols = ['현재시간', '시분초'] # 방법 2: 제외할 컬럼을 명시적으로 리스트로 만들어서 중복되는 행 삭제
    subset_cols = [col for col in df_detail.columns if col not in exclude_cols]
    df_detail = df_detail.drop_duplicates(subset=subset_cols,keep='first') #백테스트 시간단축을위해 중복되는행 삭제

    return market, df, df_detail
def keep_first_if_all_same_fast(df_detail, group_col='데이터길이'):
    # 삭제할 그룹 찾기 / 데이터길이가 같은행 중에 상세시가,상세고가,상세저가,상세종가가 같은행은 삭제
    """
    간결한 버전
    """
    price_cols = ['상세시가', '상세고가', '상세저가', '상세종가']

    # 각 그룹 처리
    result_dfs = []

    for name, group in df_detail.groupby(group_col):
        # 모든 가격이 같은지 체크
        if all(group[col].nunique() == 1 for col in price_cols):
            # 첫 번째만
            result_dfs.append(group.head(1))
        else:
            # 모두
            result_dfs.append(group)
    return pd.concat(result_dfs).sort_index()

def export_sql(df,file_path,table_name):
    con = sqlite3.connect(file_path)
    df.to_sql(table_name, con, if_exists='replace')
    con.close()
    print(f"common_def.export_sql({table_name}) 저장완료")
def import_sql(file_path,table_name):
    # 데이터베이스 연결
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    # 테이블에 대한 인덱스 정보 가져오기
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='index' AND tbl_name=?
    """, (table_name,))

    # 결과 출력
    index_names = cursor.fetchall()

    # 인덱스 이름 출력
    # for index in index_names:
    #     print(index[0])
    idx = index_names[0][0]
    # rindex = idx.rindex('_')
    idx = idx[idx.rindex('_')+1:]
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn).set_index(idx)
    # 연결 종료
    conn.close()
    return df
def replace_tabs_with_spaces(text): #스페이스랑 탭 혼용 시 (들여쓰기)에러 방지용
    space_count = 4
    return text.replace('\t', ' ' * space_count)

def convert_column_types(df): #데이터프레임 중 숫자로 바꿀 수 있는데이터는 숫자로 변환
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
        except ValueError:
            pass
    return df
def stamp_to_int(stamp_time):
    dt = datetime.datetime.fromtimestamp(stamp_time)
    dt = dt.strftime('%Y%m%d%H%M')
    return int(dt)
def stamp_to_str(stamp_time):
    date_time = stamp_to_datetime(stamp_time)
    return datetime.datetime.strftime(date_time,"%Y-%m-%d %H:%M:%S")
def str_to_datetime(str):
    try:
        return datetime.datetime.strptime(str,'%Y-%m-%d %H:%M:%S')
    except:
        print(f"{str= }")
        raise
        return datetime.datetime.strptime(str,'%Y-%m-%d %H:%M:%S')
def str_to_stamp(str):
    dt =  datetime.datetime.strptime(str,'%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp())
def int_to_stamp(int_time):
    dt = datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
    return int(dt.timestamp())
def int_to_datetime(int_time):
    return datetime.datetime.strptime(str(int_time),'%Y%m%d%H%M')
def stamp_to_datetime(stamp_time):
    if len(str(int(stamp_time))) == 13:
        stamp_time = stamp_time / 1000  # 밀리초단위일 경우
    int_time = stamp_to_int(stamp_time)
    return datetime.datetime.strptime(str(int_time), '%Y%m%d%H%M')
def datetime_to_stamp(date_time):
    return int(time.mktime(date_time.timetuple()))
def datetime_to_str(date_time):
    return datetime.datetime.strftime((date_time), "%Y-%m-%d %H:%M:%S")
def datetime_to_int_time(date_time):
    return int(datetime.datetime.strftime((date_time), "%H%M%S"))
def purple(text):
    return f'\033[38;2;215;95;215m{text}\033[0m'
def red(text):
    return f'\033[31m{text}\033[0m'
def fie(text):
    return f'\033[91m{text}\033[0m'
def blue(text):
    return f'\033[34m{text}\033[0m'
def cyan(text):
    return f'\033[36m{text}\033[0m'
def yellow(text):
    return f'\033[33m{text}\033[0m'
def green(text):
    return f'\033[32m{text}\033[0m'

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.highlightingRules = []

        # Keyword formatting
        orangeFormat = QTextCharFormat()
        orangeFormat.setForeground(QColor("orange"))
        keywords_orange = ["if", "True", "False", ":", "and", 'or', "{", "}", "not", "elif", "else", "pass"]
        for keyword in keywords_orange:
            pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((pattern, orangeFormat))

        # 'self' formatting
        purpleFormat = QTextCharFormat()
        purpleFormat.setForeground(QColor("purple"))
        keywords_purple = ["self", "print", "[", "]"]
        for keyword in keywords_purple:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, purpleFormat))

        # Number formatting
        cyanFormat = QTextCharFormat()
        cyanFormat.setForeground(QColor("cyan"))
        keywords_purple = ["[0-9]+", "[0-9]-"]
        for keyword in keywords_purple:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, cyanFormat))

        greenFormat = QTextCharFormat()
        greenFormat.setForeground(QColor("yellowgreen"))
        keywords_green = ["진입대상", "봉", "상세봉", "방향", "배팅금액", "레버리지", "분할매수", "분할매도"]
        for keyword in keywords_green:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, greenFormat))

        self.grayFormat = QTextCharFormat()
        self.grayFormat.setForeground(QColor("gray"))
        self.grayFormat.setFontItalic(True)  # 기울임꼴
        keywords_gray = [r"#.*"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, self.grayFormat))

        pinkFormat = QTextCharFormat()
        pinkFormat.setForeground(QColor("pink"))
        keywords_gray = ["매수가", "매수", "매도가", "매도", "매입율", "매도전환"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, pinkFormat))

        darkCyanFormat = QTextCharFormat()
        darkCyanFormat.setForeground(QColor("darkCyan"))
        keywords_gray = ["매도가", "매도"]
        for keyword in keywords_gray:
            Pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlightingRules.append((Pattern, darkCyanFormat))

        # darkGrayFormat = QTextCharFormat()
        # darkGrayFormat.setForeground(QColor("darkGray"))
        # keywords_gray = ["#"]
        # for keyword in keywords_gray:
        #     Pattern = QRegExp(f"\\b{keyword}\\b")
        #     self.highlightingRules.append((Pattern, darkGrayFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        ################################ 괄호
        bracketStack = []
        for i, char in enumerate(text):
            if char in '({[':
                bracketStack.append((char, i))
                # color = self.bracketColors[len(bracketStack) % len(self.bracketColors)]
                format = QTextCharFormat()
                # format.setForeground(color)
                self.setFormat(i, 1, format)
            elif char in ')}]':
                if bracketStack:
                    bracket, pos = bracketStack.pop()
                    # color = self.bracketColors[len(bracketStack) % len(self.bracketColors)]
                    format = QTextCharFormat()
                    # format.setForeground(color)
                    self.setFormat(i, 1, format)
        ################################ 주석처리
        comment_pattern = QRegExp(r"#.*")
        index = comment_pattern.indexIn(text)
        while index >= 0:
            length = comment_pattern.matchedLength()
            self.setFormat(index, length, self.grayFormat)
            index = comment_pattern.indexIn(text, index + length)
        self.setCurrentBlockState(0)


class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)
        self.setFont(QFont("Courier", 10))

    def keyPressEvent(self, event):
        # Check for the '(' key press
        if event.key() == Qt.Key_ParenLeft:
            cursor = self.textCursor()
            cursor.insertText('()')
            cursor.movePosition(cursor.Left)
            self.setTextCursor(cursor)
        # if event.key() == Qt.Key_ParenLeft:
        #     cursor = self.textCursor()
        #     cursor.insertText('{}')
        #     cursor.movePosition(cursor.Left)
        #     self.setTextCursor(cursor)
        # if event.key() == Qt.Key_ParenLeft:
        #     cursor = self.textCursor()
        #     cursor.insertText('[]')
        #     cursor.movePosition(cursor.Left)
        #     self.setTextCursor(cursor)
        else:
            super(CodeEditor, self).keyPressEvent(event)
if __name__ == "__main__":
    ticker = 'BTC'
    ex = make_exchange_upbit()
    # from datetime import datetime
    import time

    # 방법 1: 직접 계산
    dt = datetime.datetime(2025, 2, 13, 0, 0, 0)
    since = int(dt.timestamp())
    print(since)  # 1739376000 (UTC 기준)

    # 방법 2: 확인
    print(datetime.datetime.fromtimestamp(1739372400))  # 이게 몇 년인지 출력해보세요
    # since = 1770986640
    print(stamp_to_datetime(since))
    ohlcv = ex.fetch_ohlcv(symbol=ticker + '/KRW', timeframe="1m", limit=200, since=since*1000)
    # pprint(ohlcv)
    df = pd.DataFrame(ohlcv, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
    df['거래대금'] = df['종가'] * df['거래량']
    df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
    df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
    df['날짜'] = df['날짜'].dt.tz_localize(None)
    df.set_index('날짜', inplace=True)

    print(df)
