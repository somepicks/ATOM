from turtledemo.forest import doit1

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
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QTimer, QRegExp
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QFontMetrics, QFont, QColor, QSyntaxHighlighter, QTextCharFormat
import datetime
from pprint import pprint

def convert_df(df):
    # print(convert_df)
    df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
    df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
    df['이평5'] = talib.MA(df['종가'], 5)
    df['이평20'] = talib.MA(df['종가'], 20)
    df['이평60'] = talib.MA(df['종가'], 60)
    df['이평120'] = talib.MA(df['종가'], 120)
    df['이평240'] = talib.MA(df['종가'], 200)
    df['거래량이평3'] = talib.MA(df['거래량'], 3)
    df['거래량이평20'] = talib.MA(df['거래량'], 20)
    df['거래량이평60'] = talib.MA(df['거래량'], 60)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(df['종가'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
    df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
    df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
    df['ATR'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
    df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
    df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
    df['이격도60이평'] = df['종가'].shift(1) / df['이평60'].shift(1) * 100
    df['밴드상'], df['밴드중'], df['밴드하'] = talib.BBANDS(df['종가'].shift(1), 20, 2)
    df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    # df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df
def convert_df_compare(df):
    # print(convert_df)
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
    df['밴드상'], df['밴드중'], df['밴드하'] = talib.BBANDS(df['종가'].shift(1), 20, 2)
    # df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df
def futopt_set_tickers(df_f,df_c,df_p,df_c_weekly,df_p_weekly,COND_MRKT):
    # 조건에 '시가_풋옵션_5분봉' 과같은 팩터가 올 수 있으니 비율을 똑같이 해줘야 함


    현재가 = df_f.loc[df_f.index[0], '현재가']
    df_c = df_c[df_c['행사가'] > 현재가 - 30]
    df_c = df_c[df_c['행사가'] < 현재가 + 30]
    df_c['종목명'] = '콜옵션'
    df_p = df_p[df_p['행사가'] > 현재가 - 30]
    df_p = df_p[df_p['행사가'] < 현재가 + 30]
    df_p['종목명'] = '풋옵션'

    df_f.rename(columns={'이론가': '이론가/행사가'}, inplace=True)
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

    df_combined = df_combined[['종목코드', '현재가','시가',  '이론가/행사가', '거래량', '거래대금', '전일대비','종목명']]
    return df_combined

def resample_df(df, bong, rule, name, compare):
    ohlc_dict = {
        '상세시가': 'first',
        '상세고가': 'max',
        '상세저가': 'min',
        '상세종가': 'last',
        '상세거래량': 'sum',
        # '상세거래대금': 'sum'
    }

    df = df.resample(rule).apply(ohlc_dict).dropna()

    if bong == name:  # 기준봉일 경우
        df.rename(columns={f'상세시가': f'시가', f'상세고가': f'고가', f'상세저가': f'저가', f'상세종가': f'종가',
                           f'상세거래량': f'거래량', f'상세거래대금': f'거래대금'}, inplace=True)  # 컬럼명 변경
        if not compare == True:
            df = convert_df(df)
        else:
            df = convert_df_compare(df)

        df[f'시가_{name}'] = df['시가'].copy()
        df[f'고가_{name}'] = df['고가'].copy()
        df[f'저가_{name}'] = df['저가'].copy()
        df[f'종가_{name}'] = df['종가'].copy()
        df[f'거래량_{name}'] = df['거래량'].copy()
        # df[f'거래대금_{name}'] = df['거래대금'].copy()
        df[f'이평5_{name}'] = df['이평5'].copy()
        df[f'이평20_{name}'] = df['이평20'].copy()
        df[f'이평60_{name}'] = df['이평60'].copy()
        # print(df)
    else:
        df.rename(columns={'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
                     '상세거래량': f'거래량_{name}', '상세거래대금': f'거래대금_{name}'}, inplace=True)  # 컬럼명 변경
        df[f'이평5_{name}'] = talib.MA(df[f'종가_{name}'], 5)
        df[f'이평20_{name}'] = talib.MA(df[f'종가_{name}'], 20)
        df[f'이평60_{name}'] = talib.MA(df[f'종가_{name}'], 60)
        df[f'데이터길이_{name}'] = np.arange(1, len(df.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df

def get_kis_ohlcv(market, ohlcv):
    df = pd.DataFrame(ohlcv)
    dt = pd.to_datetime(df['stck_bsop_date'] + df['stck_cntg_hour'], format="%Y%m%d%H%M%S")
    df.set_index(dt, inplace=True)
    df = df.apply(to_numeric)
    if market == '국내주식':
        df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_prpr', 'cntg_vol', 'acml_tr_pbmn']]
        df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
        df['거래대금'] = df['누적거래대금'] - df['누적거래대금'].shift(-1)
        df['거래대금'] = df['거래대금'].clip(lower=0)  # 음수를 0으로 변환

        # 날짜 변경 여부 확인
        df['날짜변경'] = df.index.to_series().dt.date != df.index.to_series().shift(-1).dt.date

        # 날짜 변경 시 누적거래대금 값 유지
        df.loc[df['날짜변경'], '거래대금'] = df['누적거래대금']

        # 날짜변경 컬럼 제거 (선택 사항)
        df.drop(columns=['날짜변경'], inplace=True)
    elif market == '국내선옵':
        df = df[['futs_oprc', 'futs_hgpr', 'futs_lwpr', 'futs_prpr', 'cntg_vol', 'acml_tr_pbmn']]
        df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
        df['거래대금'] = df['누적거래대금'] - df['누적거래대금'].shift(-1)
        df['거래대금'] = df['거래대금'].clip(lower=0)  # 음수를 0으로 변환

        # 날짜 변경 여부 확인
        df['날짜변경'] = df.index.to_series().dt.date != df.index.to_series().shift(-1).dt.date

        # 날짜 변경 시 누적거래대금 값 유지
        df.loc[df['날짜변경'], '거래대금'] = df['누적거래대금']

        # 날짜변경 컬럼 제거 (선택 사항)
        df.drop(columns=['날짜변경'], inplace=True)

    df.index.name = "날짜"
    df = df[::-1]  # 거꾸로 뒤집기
    return df

def get_bybit_ohlcv(ex_bybit, ohlcv, stamp_date_old, ticker_full_name, ticker, bong, bong_detail):
    i = 0
    # print(f"{ohlcv= }, {stamp_date_old= }, {ticker= },{bong= }, {bong_detail= }")
    dict_bong_stamp ={'1분봉': 1*60, '3분봉': 3*60, '5분봉': 5*60, '15분봉': 15*60, '30분봉': 30*60, '60분봉': 60*60, '4시간봉': 240*60, '일봉': 1440*60,
                       '주봉': 10080*60}
    dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '1h', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외

    while True:
        try:
            list_ohlcv = ex_bybit.fetch_ohlcv(symbol=ticker + 'USDT', timeframe=dict_bong[bong_detail],
                                                   limit=10000, since=int(stamp_date_old*1000)) #밀리초로 전달
            # pprint(list_ohlcv)
            ohlcv = ohlcv + list_ohlcv
            stamp_date_old = list_ohlcv[-1][0]/1000 + dict_bong_stamp[bong_detail]  # 다음봉 시간 계산

            if stamp_date_old > time.time():
                return ohlcv
        except:
            time.sleep(1)
            i += 1
            if i > 9:
                print(f' {ticker_full_name=}, {bong=}, {i}회 이상 fetch_ohlcv 조회 에러')
                raise '조회에러'

def detail_to_spread(df_min, bong, bong_detail, compare):
    dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                       '주봉': 10080}
    df_min.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
    detail_unit = dict_bong_stamp[bong_detail]
    list_idx = df_min.index.tolist()
    # print(f"{dict_bong_stamp= }")
    if detail_unit == dict_bong_stamp['1분봉']:
        df_1min = resample_df(df_min, bong, '1min', '1분봉',compare)
    if detail_unit < dict_bong_stamp['3분봉']:
        df_3min = resample_df(df_min, bong, '3min', '3분봉',compare)
    if detail_unit < dict_bong_stamp['5분봉']:
        df_5min = resample_df(df_min, bong, '5min', '5분봉',compare)
    if detail_unit < dict_bong_stamp['15분봉']:
        df_15min = resample_df(df_min, bong, '15min', '15분봉',compare)
    if detail_unit < dict_bong_stamp['30분봉']:
        df_30min = resample_df(df_min, bong, '30min', '30분봉',compare)
    if detail_unit < dict_bong_stamp['60분봉']:
        df_60min = resample_df(df_min, bong, '60min', '60분봉',compare)
    if detail_unit < dict_bong_stamp['4시간봉']:
        df_4h = resample_df(df_min, bong, '240min', '4시간봉',compare)
    df_daily = resample_df(df_min, bong, 'D', '일봉',compare)
    df_weekly = resample_df(df_min, bong, 'W', '주봉',compare)
    # df_monthly = resample_df(df_min, bong, 'ME', '월봉',compare)

    df_daily['date'] = df_daily.index.date
    df_weekly['week'] = df_weekly.index.to_period('W').astype(str)
    # df_monthly['month'] = df_monthly.index.to_period('M').astype(str)
    df_min['date'] = df_min.index.date
    df_min['week'] = df_min.index.to_period('W').astype(str)
    # df_min['month'] = df_min.index.to_period('M').astype(str)

    if detail_unit < dict_bong_stamp['3분봉']:
        df_min = pd.merge(df_min, df_1min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['3분봉']:
        df_min = pd.merge(df_min, df_3min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['5분봉']:
        df_min = pd.merge(df_min, df_5min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['15분봉']:
        df_min = pd.merge(df_min, df_15min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['30분봉']:
        df_min = pd.merge(df_min, df_30min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['60분봉']:
        df_min = pd.merge(df_min, df_60min, left_index=True, right_index=True, how='left')
    if detail_unit < dict_bong_stamp['4시간봉']:
        df_min = pd.merge(df_min, df_4h, left_index=True, right_index=True, how='left')
    df_combined = df_min.merge(df_daily, on='date',how='left', suffixes=('', '_daily'))
    df_combined = df_combined.merge(df_weekly, on='week',how='left', suffixes=('', '_weekly'))
    # df_combined = df_combined.merge(df_monthly, on='month',how='left', suffixes=('', '_monthly'))

    # df_combined.fillna(method='ffill', inplace=True)
    df_combined.ffill(inplace=True)

    df_combined.index = list_idx
    df_combined.index.rename('날짜', inplace=True)  # 인덱스명 변경
    df_combined.drop('date', axis=1, inplace=True)
    df_combined.drop('week', axis=1, inplace=True)
    # df_combined.drop('month', axis=1, inplace=True)
    list_col = df_combined.columns.tolist()
    # 시가 ~ 데이터프레임 열까지 갖고오기
    if bong == '1분봉':
        df = df_1min
    elif bong == '3분봉':
        df = df_3min
    elif bong == '5분봉':
        df = df_5min
    elif bong == '15분봉':
        df = df_15min
    elif bong == '30분봉':
        df = df_30min
    elif bong == '60분봉':
        df = df_60min
    elif bong == '4시간봉':
        df = df_4h
    elif bong == '일봉':
        df = df_daily
    elif bong == '주봉':
        df = df_weekly
    # elif bong == '월봉':
    #     df = df_monthly
    else:
        df = pd.DataFrame()
    return df,df_combined
def detail_to_compare(df, ticker, bong):
    # print('==================')
    # # print(ticker_full_name)
    dict_bong_rule = {'1분봉': '1min', '3분봉': '3', '5분봉': '5min', '15분봉': '15min', '30분봉': '30min', '60분봉': '60min', '4시간봉': '240min', '일봉': 'D',
                       '주봉': 'W'}
    df.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                           '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
#     print(df)
    df = resample_df(df, bong, dict_bong_rule[bong], bong, True)
#     print(df)
    # 컬럼명중에 bong 이름이 들어가는 컬럼을 제거 ( '시가_일봉_BTC_일봉' 이렇게 나오기 때문에)
    df = df.drop(columns=df.filter(like='_'+bong).columns)
#     print(df)
    return df
def make_exchange_bybit():
    conn = sqlite3.connect('DB/setting.db')
    df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
    conn.close()

    if '코인_API' in df.index.tolist() and  '코인_SECRET' in df.index.tolist() :
        api = df.loc['코인_API','value']
        secret = df.loc['코인_SECRET','value']
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
    else:
        exchange_ccxt = None
        exchange_pybit = None
    return exchange_ccxt, exchange_pybit

def save_futopt_DB(check_simul,ex_kis,ticker,list_table,conn_DB):
    if not 'holiday' in list_table:
        df_holiday = pd.DataFrame()
    else:
        df_holiday = pd.read_sql(f"SELECT * FROM 'holiday'", conn_DB).set_index('날짜')
    now_day = datetime.datetime.now().date()

    if ticker == '콜옵션' or ticker == '풋옵션':
        df_call, df_put, past_expiry_date, expiry_date = ex_kis.display_opt(now_day)
        cond_mrkt = ticker
        if ticker == '콜옵션':
            df_display = df_call
        elif ticker == '풋옵션':
            df_display = df_put
    elif ticker == '콜옵션_위클리' or ticker == '풋옵션_위클리':
        df_call_weekly, df_put_weekly, cond_mrkt, past_expiry_date, expiry_date = ex_kis.display_opt_weekly(now_day)
        if ticker == '콜옵션_위클리':
            df_display = df_call_weekly
        elif ticker == '풋옵션_위클리':
            df_display = df_put_weekly
    elif ticker == '선물':
        df_display = ex_kis.display_fut()
        expiry_date, expiry_str, days_left,past_expiry_date,past_expiry_date_str = ex_kis.get_nearest_futures_expiry(now_day)
        cond_mrkt = ticker
    # expiry_date = datetime.datetime.strftime(expiry_date, '%Y%m%d')


    if cond_mrkt != '만기주':
        list_ticker = df_display.종목코드.tolist()
        expiry_date = check_holiday(check_simul,ex_kis,df_holiday,expiry_date)
        past_expiry_date = datetime.datetime.combine(past_expiry_date, datetime.time(15, 45, 0))  # 12:30:45 추가 past_expiry_date+시간

        for symbol in list_ticker:
            if ticker == '선물':
                ticker_symbol = '선물'
            else:
                ticker_symbol = ticker + '_' + symbol[-3:]
            ohlcv = []

            if ticker_symbol in list_table: #연속저장 (기존데이터가 있을 경우)
                df_exist = pd.read_sql(f"SELECT * FROM '{ticker_symbol}'", conn_DB).set_index('날짜')
                df_exist.index = pd.to_datetime(df_exist.index)
                final_time = df_exist.index[-1]
                d_day = now_day - final_time.date()
                ohlcv = ex_kis.fetch_1m_ohlcv(symbol=symbol, limit=d_day.days, ohlcv=ohlcv,
                                              now_day=final_time.strftime("%Y%m%d"),
                                              now_time=final_time.strftime("%H%M%S"))
                df = get_kis_ohlcv('국내선옵', ohlcv)
                df = df[df.index >= final_time]
                df['만기일'] = expiry_date
                if df.empty:
                    continue
                df = pd.concat([df_exist, df])
                df = df[~df.index.duplicated(keep='last')]

            else:
                d_day = now_day - past_expiry_date.date()
                ohlcv = ex_kis.fetch_1m_ohlcv(symbol=symbol, limit=d_day.days, ohlcv=ohlcv,
                                              now_day=now_day.strftime("%Y%m%d"),
                                              now_time=datetime.datetime.now().strftime("%H%M%S"))
                df = get_kis_ohlcv('국내선옵', ohlcv)
                df = df[df.index > past_expiry_date]
                df['만기일'] = expiry_date
                df['종목코드'] = symbol
            print(f"{symbol= }   {ticker_symbol= }    {d_day.days= }    {expiry_date= }    {past_expiry_date= }")


            # 데이터가 없을경우 해당하는 행 삭제
            now = datetime.datetime.now().replace(second=0, microsecond=0)
            df = df.drop(df.loc[df.index == now].index)
            if not df.empty:
                df.to_sql(ticker_symbol, conn_DB, if_exists='replace')
    else:
        df = pd.DataFrame()
        ticker_symbol = ''
    return df, ticker_symbol
def check_holiday(check_simul,ex_kis,df_holiday,expiry_date):
    now_day = datetime.datetime.now().date()
    if not datetime.datetime.strftime(expiry_date, '%Y%m%d') in df_holiday.index.tolist() or df_holiday.empty:
        conn_DB = sqlite3.connect('DB/DB_futopt.db')
        if check_simul:
            ex_kis = make_exchange_kis('실전선옵')
        if df_holiday.empty:
            now_day = now_day - datetime.timedelta(days=10)
        df_holiday_new = ex_kis.check_holiday_domestic_stock(now_day,expiry_date)
        df_holiday = pd.concat([df_holiday, df_holiday_new], axis=0)
        # 인덱스 중복 제거 (위쪽 행 삭제, 마지막 행 유지)
        df_holiday = df_holiday[~df_holiday.index.duplicated(keep='last')]
        df_holiday.to_sql('holiday', conn_DB, if_exists='replace')
        conn_DB.close()
    list_index = df_holiday.index.tolist()
    i = list_index.index(expiry_date.strftime("%Y%m%d"))
    while i >= -10:
        holiday = df_holiday.iloc[i, df_holiday.columns.tolist().index('개장일')]
        if holiday == 'Y':
            expiry_date = list_index[i]
            expiry_date = datetime.datetime.strptime(expiry_date, '%Y%m%d').date()
            return expiry_date
        else:
            i -= 1
    print('금일 휴장일')
    return now_day
def make_exchange_kis(trade_type):
    conn = sqlite3.connect('DB/setting.db')
    df = pd.read_sql(f"SELECT * FROM 'set'", conn).set_index('index')
    conn.close()
    if trade_type == '실전주식':
        try:
            key = df.loc['국내주식_API','value']
            secret = df.loc['국내주식_SECRET','value']
            acc_no = df.loc['국내주식_ACCOUNT','value']
            mock = False
        except:
            return None
        # broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no)
    elif trade_type == '모의주식':
        try:
            key = df.loc['국내주식_모의_API','value']
            secret = df.loc['국내주식_모의_SECRET','value']
            acc_no = df.loc['국내주식_모의_ACCOUNT','value']
            mock = True
        except:
            return None
    elif trade_type == '실전선옵':
        try:
            key = df.loc['국내선옵_API','value']
            secret = df.loc['국내선옵_SECRET','value']
            acc_no = df.loc['국내선옵_ACCOUNT','value']
            mock = False
        except:
            return None
    elif trade_type == '모의선옵':
        try:
            key = df.loc['국내선옵_모의_API','value']
            secret = df.loc['국내선옵_모의_SECRET','value']
            acc_no = df.loc['국내선옵_모의_ACCOUNT','value']
            mock = True
        except:
            return None
    elif trade_type == '해외선옵':
        try:
            key = df.loc['해외선옵_API','value']
            secret = df.loc['해외선옵_SECRET','value']
            acc_no = df.loc['해외선옵_ACCOUNT','value']
            mock = False
        except:
            return None
    elif trade_type == '모의해외선옵': # 지원안함
        try:
            key = df.loc['KIS_futopt_oversea_mock_api','value']
            secret = df.loc['KIS_futopt_oversea_mock_secret','value']
            acc_no = df.loc['KIS_futopt_oversea_mock_account','value']
            mock = True
        except:
            return None

    market = trade_type[2:]
    print(key)
    print(secret)
    print(acc_no)
    exchange = KIS.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, market=market, mock=mock)
    return exchange
def export_sql(df,text):
    con = sqlite3.connect('DB/bt.db')
    df.to_sql(text, con, if_exists='replace')
    con.close()
def import_sql(db_file,table_name):

    # 데이터베이스 연결
    conn = sqlite3.connect(db_file)
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
    # print(f"{stamp_time=},,,{dt=}")
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
    int_time=stamp_to_int(stamp_time)
    return datetime.datetime.strptime(str(int_time),'%Y%m%d%H%M')
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
        keywords_green = ["진입대상", "봉", "상세봉", "방향", "초기자금", "레버리지", "분할매수", "분할매도"]
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

# d1 = datetime.datetime.now().date()
# conn_DB = sqlite3.connect('DB/DB_futopt.db')
# df_holiday = pd.read_sql(f"SELECT * FROM 'holiday'", conn_DB).set_index('날짜')
# conn_DB.close()
# d2 = datetime.date(2025,3,13)
# res = check_holiday(df_holiday,d2)