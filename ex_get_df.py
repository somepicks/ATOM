import sqlite3
import pandas as pd
# import math
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
# import cal_krx
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QWaitCondition,QMutex
import KIS
# from pykrx import stock
from pprint import pprint
import polars as pl
import common_def



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
    key = 'test'
    secret = 'tN8OWANevTk9MiLqXwcKe2DNFI7FnptAS84hoXAIU='
    acc_no = "63761517-01"
    # broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no)
    exchange = KIS.KoreaInvestment(api_key=key, api_secret=secret, acc_no=acc_no, market='주식', mock=True)
    return exchange


def mapping(x, i_min, i_max, o_min, o_max):
    return (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min  # mapping()함수 정의.


def compare_price(price, vars):
    i_min = price.min()  # 현재가.min
    i_max = price.max()
    return price.apply(mapping, args=(i_min, i_max, vars.min(), vars.max()))


def convert_df(df):
    df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
    df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
    df['이평5'] = talib.MA(df['종가'], 5)
    df['이평20'] = talib.MA(df['종가'], 20)
    df['이평60'] = talib.MA(df['종가'], 60)
    df['이평120'] = talib.MA(df['종가'], 120)
    df['이평240'] = talib.MA(df['종가'], 240)
    df['거래량이평3'] = talib.MA(df['거래량'], 3)
    df['거래량이평20'] = talib.MA(df['거래량'], 20)
    df['거래량이평60'] = talib.MA(df['거래량'], 60)
    df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
    df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
    df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
    df['ATR10'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
    df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
    df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
    df['밴드20상'], df['밴드20중'], df['밴드20하'] = talib.BBANDS(df['종가'].shift(1), 20, 2)
    df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
    return df


def leak_to_fill(df_detail, detail_stamp):
    # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
    df_detail['장시작시간'] = np.nan
    serise_start_t = df_detail.groupby(df_detail.index.date).transform(
        lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
    df_detail['장시작시간'] = serise_start_t
    df_detail['장종료시간'] = np.nan
    serise_end_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
    df_detail['장종료시간'] = serise_end_t
    # 시작 시간과 종료 시간 확인
    start_time = df_detail.index.min()
    end_time = df_detail.index.max()
    # 전체 1분 단위의 시간 인덱스 생성
    full_time_index = pd.date_range(start=start_time, end=end_time, freq=f'{detail_stamp}T')
    # 기존 데이터프레임을 새로운 인덱스에 맞춰 재인덱싱
    df_detail = df_detail.reindex(full_time_index)
    # 누락된 데이터를 바로 위의 데이터로 채우기
    df_detail = df_detail.fillna(method='ffill')
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


def get_df_multi(market, ticker, bong, bong_detail, QLE_start, QLE_end, dict_bong_stamp, stocks_info):
    st = time.time()
    print(market)
    if market == '전체':
        print('******************전체에 대한 백테스트 아직 정의 안됨******************')
        return 0
    elif market == '국내주식' or market == '국내선옵':
        market = '국내시장'
        db_file = 'DB/DB_stock.db'
        if ticker in stocks_info.index.tolist():
            trade_market = stocks_info.loc[ticker, '시장구분']
        elif ticker in ['10100', '코스피200선물', '미니코스피200선물', '코스닥150선물', '미국달러선물', '3년국채선물', '10년국채선물', '금연결선물']:
            trade_market = '선물'
        else:
            raise
    elif market == '코인':
        db_file = 'DB/DB_bybit.db'
        trade_market = 'bybit'
    else:
        db_file = ''
        raise

    dict_bong = {'1분봉': '1m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉': '4h', '일봉': 'd',
                 '주봉': 'W', '월봉': 'M'}

    ticker_bong = ticker + '_' + dict_bong[bong]
    ticker_detail = ticker + '_' + dict_bong[bong_detail]

    # print(f"{market}, {ticker}  기준봉: {ticker} = {bong}  |  상세봉: {ticker} = {bong_detail}  |  ", end='')
    con_db = sqlite3.connect(db_file)
    cursor = con_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = np.concatenate(cursor.fetchall()).tolist()

    list_bong = [x[x.index('_') + 1:] for x in table_list if x[:x.index('_')] == ticker]  # 해당 ticker가 갖고있는 db를 리스트화 [1m,3m,5m...]
    dict_bong = {key: value for key, value in dict_bong.items() if value in list_bong}  # 리스트에있는 원소만 딕셔너리에 남기기
    if ticker_bong in table_list:
        df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", con_db).set_index('날짜')
        df.index = pd.to_datetime(df.index)  # datime형태로 변환
        if market == '국내시장' and bong != '일봉' and bong != '주봉' and bong != '월봉':  # 국내시장의 기준이 분봉일 경우
            df.index = df.index - timedelta(minutes=dict_bong_stamp[bong])  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨

        # 입력받은 날짜로 자르기
        # start_day = datetime.strptime(QLE_start, '%Y-%m-%d')
        # end_day = datetime.strptime(QLE_end, '%Y-%m-%d')
        # df = df[df.index >= start_day]
        # df = df[df.index < end_day + timedelta(days=1)]

        if bong != bong_detail:
            print(' 디테일 사용')
            df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", con_db).set_index('날짜')
            df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
            if df_detail.empty:
                print(f"df_detail 데이터 없음 DB 시간 확인 요망")
                quit()
            del dict_bong[bong]  # 기준봉은 삭제
            del dict_bong[bong_detail]  # 디테일 사용 시 디테일봉 삭제

            if market == '국내시장':
                if bong_detail != '일봉' and bong_detail != '주봉' and bong_detail != '월봉':
                    df_detail.index = df_detail.index - timedelta(minutes=dict_bong_stamp[bong_detail])  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨
                df_detail = leak_to_fill(df_detail, dict_bong_stamp[bong_detail])  # 누락되는 분봉 채우기
            elif market == '코인':
                pass
            # df_detail.to_sql('detail',sqlite3.connect('DB/bt.db'), if_exists='replace')
            # quit()
            # df_detail = df_detail[df_detail.index >= start_day]
            # df_detail = df_detail[df_detail.index < end_day + timedelta(days=1)]
            if df_detail.empty:
                print(f"df_detail 데이터 없음 DB 시간 확인 요망")
                quit()

            # # df와 df_detail에 있는 날짜로만 자르기
            if df.index[0] < df_detail.index[
                0] and bong == '일봉' and market == '국내시장':  # 일봉의 경우 인덱스의 시간이 0시 기준이기 때문에 -1일 해줘야됨
                df = df[df.index >= df_detail.index[0] - timedelta(days=1)]
                df_detail = df_detail[df_detail.index >= df.index[0]]
            elif df.index[0] < df_detail.index[0]:
                df = df[df.index >= df_detail.index[0]]
                df_detail = df_detail[df_detail.index >= df.index[0]]
            elif df.index[0] > df_detail.index[0]:
                df_detail = df_detail[df_detail.index >= df.index[0]]
            if df.index[-1] > df_detail.index[-1]:
                df = df[df.index <= df_detail.index[-1]]
                df_detail = df_detail[df_detail.index < df.index[-1]]
                df = df[df.index < df_detail.index[-1]]
            elif df.index[-1] < df_detail.index[
                -1] and bong == '일봉' and market == '국내시장':  # 일봉의 경우 인덱스의 시간이 0시 기준이기 때문에 +1일 해줘야됨
                df_detail = df_detail[df_detail.index < df.index[-1] + timedelta(days=1)]
                df = df[df.index <= df_detail.index[-1]]
            elif df.index[-1] < df_detail.index[-1]:
                df_detail = df_detail[df_detail.index <= df.index[-1]]
                df = df[df.index <= df_detail.index[-1]]

        elif bong == bong_detail:
            print(' 디테일 사용 X')
            df_detail = df.copy()
            del dict_bong[bong]  # 기준봉은 삭제
            if market == '국내시장' and bong != '일봉' and bong != '주봉' and bong != '월봉':
                df_detail['장종료시간'] = np.nan
                serise_end_t = df_detail.groupby(df_detail.index.date).transform(
                    lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
                df_detail['장종료시간'] = serise_end_t
                # df.loc[df.index < datetime.strptime('2016-08-01', '%Y-%m-%d'),'종료시간'] = df['장종료시간'] + timedelta(hours=15, minutes=10)
                # df.loc[df.index >= datetime.strptime('2016-08-01', '%Y-%m-%d'),'종료시간'] = df['장종료시간'] + timedelta(hours=15, minutes=40)
                df_detail['장시작시간'] = np.nan
                serise_start_t = df_detail.groupby(df_detail.index.date).transform(
                    lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
                df_detail['장시작시간'] = serise_start_t
                # if 현재시간 == 장종료시간: False 조건이 먹히기 위해서는 장종료시간에서 bong_detail만큼 빼줘야됨
                df_detail['장종료시간'] = df_detail['장종료시간'] - timedelta(minutes=dict_bong_stamp[bong])
            elif market == '국내시장' and (bong == '일봉' or bong == '주봉' or bong == '월봉'):
                df_detail['장종료시간'] = df_detail.index
                df_detail['장시작시간'] = df_detail.index
        st = time.time()
        if market == '국내시장':
            if trade_market == '선물':
                if bong_detail == '일봉':
                    df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                              '전일대비': '상세전일대비', '거래량': '상세거래량', '거래대금': '상세거래대금',
                                              '선물이론가': '상세선물이론가', '베이시스': '상세베이시스', }, inplace=True)
                elif bong_detail == '주봉' or bong_detail == '월봉':
                    df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                              '거래량': '상세거래량', '거래대금': '상세거래대금'}, inplace=True)
                else:  # 분봉
                    df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                              '거래량': '상세거래량', '거래대금': '상세거래대금', '누적체결매도수량': '상세누적체결매도수량',
                                              '누적체결매수수량': '상세누적체결매수수량'}, inplace=True)

            else:  # 주식
                if bong_detail == '일봉':
                    df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                              '전일대비': '상세전일대비', '거래량': '상세거래량', '거래대금': '상세거래대금',
                                              '상장주식수': '상세상장주식수', '시가총액': '상세시가총액', '외국인현보유수량': '상세외국인현보유수량',
                                              '외국인현보유비율': '상세외국인현보유비율', '기관순매수량': '상세기관순매수량', '기관누적순매수량': '상세기관누적순매수량'},
                                     inplace=True)
                elif bong_detail == '주봉' or bong_detail == '월봉':
                    df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                              '거래량': '상세거래량', '거래대금': '상세거래대금'}, inplace=True)
                else:  # 분봉
                    df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가',
                                              '거래량': '상세거래량', '거래대금': '상세거래대금', '누적체결매도수량': '상세누적체결매도수량',
                                              '누적체결매수수량': '상세누적체결매수수량'}, inplace=True)
            if bong == '일봉':
                # 기준봉이 일봉일 경우 detail봉에서 장 시작시간을 가져와 일봉에 넣기 위함
                df_detail['장시작시간'] = np.nan
                # serise_start_t = df_detail.groupby(df_detail.index.date).transform(lambda x: x.index[0]).장시작시간 #날짜별 시간을 같은행에 넣기
                serise_start_t = df_detail.groupby(df_detail.index.date).transform(
                    lambda x: x.index[0]).장시작시간  # 날짜별 시간을 같은행에 넣기
                df_detail['장시작시간'] = serise_start_t
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

                df_detail['종료시간'] = df_detail['장종료시간'].copy()

            elif bong != '일봉' and bong != '주봉' and bong != '월봉':
                # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
                df_detail['종료시간'] = df_detail.index
                df_detail_end_time = df_detail['종료시간'].resample(f'{dict_bong_stamp[bong]}min').last()
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
            df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가', '거래량': '상세거래량'},
                             inplace=True)

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
                df_detail_end_time = df_detail['종료시간'].resample(f'{dict_bong_stamp[bong]}min').last()
                del df_detail['종료시간']
                df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')

        st = time.time()
        # df = convert_df(df)
        df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
        df_detail = pd.merge(df_detail, df, left_index=True, right_index=True, how='left')

        df_detail.fillna(method='ffill', inplace=True)
        # df_detail.to_sql('detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
        df_detail['데이터길이'] = df_detail['데이터길이'].fillna(0)  # nan을 0으로 채우기

        df_detail['현재시간'] = df_detail.index
        dict_bong_reverse = dict(zip(dict_bong.values(), dict_bong.keys()))

        start_day = df_detail.index[0]
        end_day = df_detail.index[-1]
        st = time.time()
        print('멀티봉 생성 중..')
        for bong_add in dict_bong_reverse.keys():
            if market == '코인':  # bybit일 경우
                df_add = pd.read_sql(f"SELECT * FROM '{ticker}_{bong_add}'", con_db).set_index('날짜')
                df_add.index = pd.to_datetime(df_add.index)  # datime형태로 변환
                df_add = df_add[df_add.index >= start_day]
                df_add = df_add[df_add.index < end_day + timedelta(days=1)]
                if df_add.empty:
                    print(f"** {dict_bong_reverse[bong_add]} '데이터는 없음'")
                    del dict_bong[dict_bong_reverse[bong_add]]
                    pass
                else:
                    df_add[f'데이터길이_{dict_bong_reverse[bong_add]}'] = np.arange(1, len(df_add.index.tolist()) + 1,
                                                                               1)  # start=1, stop=len(df.index.tolist())+1, step=1

                    df_add.rename(
                        columns={'시가': f'시가_{dict_bong_reverse[bong_add]}',
                                 '고가': f'고가_{dict_bong_reverse[bong_add]}',
                                 '저가': f'저가_{dict_bong_reverse[bong_add]}',
                                 '종가': f'종가_{dict_bong_reverse[bong_add]}',
                                 '거래량': f'거래량_{dict_bong_reverse[bong_add]}'}, inplace=True)  # 컬럼명 변경

                    df_add[f'이평20_{dict_bong_reverse[bong_add]}'] = talib.MA(
                        df_add[f'종가_{dict_bong_reverse[bong_add]}'], 20)
                    df_add[f'이평60_{dict_bong_reverse[bong_add]}'] = talib.MA(
                        df_add[f'종가_{dict_bong_reverse[bong_add]}'], 60)
                    df_detail = pd.merge(df_detail, df_add, left_index=True, right_index=True, how='left')
            elif market == '국내시장':  # 국내시장일 경우
                df_add = pd.read_sql(f"SELECT * FROM '{ticker}_{bong_add}'", con_db).set_index('날짜')
                df_add.index = pd.to_datetime(df_add.index)  # datime형태로 변환
                df_add = df_add[df_add.index >= start_day]
                df_add = df_add[df_add.index < end_day + timedelta(days=1)]
                if df_add.empty:
                    print(f"** {dict_bong_reverse[bong_add]} '데이터는 없음'")
                    del dict_bong[dict_bong_reverse[bong_add]]
                    pass
                else:
                    if dict_bong_reverse[bong_add] in ['1분봉', '3분봉', '5분봉', '15분봉', '30분봉', '60분봉']:
                        df_add.index = df_add.index - timedelta(minutes=dict_bong_stamp[
                            dict_bong_reverse[bong_add]])  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 5분 빼줘야됨

                    elif dict_bong_reverse[bong_add] == '주봉' or dict_bong_reverse[bong_add] == '월봉':  # 일봉일 경우 제외
                        # 주봉과 월봉의 경우 장 시간을 찾아서 인덱스를 맞추기 (나중에 인덱스에 맞춰 merge 시키기 위해)
                        # 주봉과 월봉의 경우 대신증권에서 주봉은 주의 첫번째, 두번째, 월은 단순 월을 넘겨주기 때문에 가공해서
                        # 주봉은 주의 월요일날짜 월요일은 월의 첫번째 요일을 받음 때문에 해당일이 휴일일경우도 있어서 추가 가공해줘야됨
                        # df_add = df_add[df_add.index.date >= df_detail.index[0].date()]
                        serise_day = df_detail.groupby(df_detail.index.date)
                        list_detail_day = serise_day.size().index.tolist()
                        list_add_day = df_add.index.date.tolist()
                        list_extra_day = set(list_add_day) - set(
                            list_detail_day)  # df_add에는 있지만 df_detail에는 없는날(휴일)을 리스트화

                        for extra_day in list_extra_day:  # 휴일을 돌아가면서 +1일 씩 함
                            cha_day = extra_day
                            # quit()
                            while not cha_day in list_detail_day:
                                cha_day = cha_day + timedelta(days=1)
                                if cha_day in list_detail_day:  # + 1일 씩 하면서 df_detail에 날짜가 있으면
                                    list_add_day[list_add_day.index(extra_day)] = cha_day  # 원래 있던 자리에 저장
                                    break
                                elif cha_day - extra_day > timedelta(
                                        days=7):  # 7일 이상 더했는데도 저장이 안된다면 휴일이 7일 이상이거나 데이터 날짜가 서로 안맞는거임
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

                    df_add[f'데이터길이_{dict_bong_reverse[bong_add]}'] = np.arange(1, len(df_add.index.tolist()) + 1,
                                                                               1)  # start=1, stop=len(df.index.tolist())+1, step=1
                    df_add.rename(
                        columns={'시가': f'시가_{dict_bong_reverse[bong_add]}', '고가': f'고가_{dict_bong_reverse[bong_add]}',
                                 '저가': f'저가_{dict_bong_reverse[bong_add]}', '종가': f'종가_{dict_bong_reverse[bong_add]}',
                                 '거래량': f'거래량_{dict_bong_reverse[bong_add]}',
                                 '거래대금': f'거래대금_{dict_bong_reverse[bong_add]}',
                                 '누적체결매도수량': f'누적체결매도수량_{dict_bong_reverse[bong_add]}',
                                 '누적체결매수수량': f'누적체결매수수량_{dict_bong_reverse[bong_add]}', }, inplace=True)  # 컬럼명 변경
                    df_add[f'이평20_{dict_bong_reverse[bong_add]}'] = talib.MA(
                        df_add[f'종가_{dict_bong_reverse[bong_add]}'], 20)
                    df_add[f'이평60_{dict_bong_reverse[bong_add]}'] = talib.MA(
                        df_add[f'종가_{dict_bong_reverse[bong_add]}'], 60)

                    df_detail = pd.merge(df_detail, df_add, left_index=True, right_index=True, how='left')
        print(f"4 걸린시간{time.time() - st}")
        st = time.time()
        print(f'사용가능한 캔들 {dict_bong.keys()}')
        cursor.close()
        con_db.close()

        df_detail.fillna(method='ffill', inplace=True)
        df_detail.index.rename('날짜', inplace=True)  # 인덱스명 변경

        # df_detail.to_sql('detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
        # df['매수가'] = np.nan
        # df['매도가'] = np.nan
        # df['수량'] = np.nan
        # df['수익률'] = np.nan
        # df['최고수익률'] = np.nan
        # df['최저수익률'] = np.nan
        # df['수익금'] = np.nan
        # df['전략수익률'] = np.nan
        # df['매수금액'] = np.nan
        # df['매도금액'] = np.nan
        # df['잔고'] = np.nan
        # df['수수료'] = np.nan
        # df['자산'] = np.nan
        # quit()
        return df, df_detail, trade_market, dict_bong, dict_bong_reverse

    else:
        print(f"{ticker_bong=}")
        print(f"{table_list=}")
        raise print('데이터 확인 요망')


def replace_tabs_with_spaces(text):  # 스페이스랑 탭 혼용 시 에러 방지용
    space_count = 4
    return text.replace('\t', ' ' * space_count)



#
# def minute_to_daily(df_min, bong):
#     df_min.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
#                            '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경
#
#     def resample_df(df, bong, rule, name):
#         ohlc_dict = {
#             '상세시가': 'first',
#             '상세고가': 'max',
#             '상세저가': 'min',
#             '상세종가': 'last',
#             '상세거래량': 'sum',
#             # '상세거래대금': 'sum'
#         }
#
#         df = df.resample(rule).apply(ohlc_dict).dropna()
#
#         if bong == name:  # 기준봉일 경우
#             df.rename(columns={'상세시가': f'시가', '상세고가': f'고가', '상세저가': f'저가', '상세종가': f'종가',
#                                '상세거래량': f'거래량', '상세거래대금': f'거래대금'}, inplace=True)  # 컬럼명 변경
#             # df = common_def.convert_df(df)
#
#         else:
#             df.rename(
#                 columns={'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
#                          '상세거래량': f'거래량_{name}', '상세거래대금': f'거래대금_{name}'}, inplace=True)  # 컬럼명 변경
#             df[f'이평20_{name}'] = talib.MA(df[f'종가_{name}'], 20)
#             df[f'이평60_{name}'] = talib.MA(df[f'종가_{name}'], 60)
#             df[f'데이터길이_{name}'] = np.arange(1, len(df.index.tolist()) + 1,
#                                             1)  # start=1, stop=len(df.index.tolist())+1, step=1
#         return df
#
#     list_idx = df_min.index.tolist()
#     df_3min = resample_df(df_min, bong, '3min', '3분봉')
#     df_5min = resample_df(df_min, bong, '5min', '5분봉')
#     df_15min = resample_df(df_min, bong, '15min', '15분봉')
#     df_30min = resample_df(df_min, bong, '30min', '30분봉')
#     df_60min = resample_df(df_min, bong, '60min', '60분봉')
#     df_4hrs = resample_df(df_min, bong, '240min', '4시간봉')
#     df_daily = resample_df(df_min, bong, 'D', '일봉')
#     df_weekly = resample_df(df_min, bong, 'W', '주봉')
#     df_monthly = resample_df(df_min, bong, 'ME', '월봉')
#
#     df_daily['date'] = df_daily.index.date
#     df_weekly['week'] = df_weekly.index.to_period('W').astype(str)
#     df_monthly['month'] = df_monthly.index.to_period('M').astype(str)
#     df_min['date'] = df_min.index.date
#     df_min['week'] = df_min.index.to_period('W').astype(str)
#     df_min['month'] = df_min.index.to_period('M').astype(str)
#
#     df_min = pd.merge(df_min, df_3min, left_index=True, right_index=True, how='left')
#     df_min = pd.merge(df_min, df_5min, left_index=True, right_index=True, how='left')
#     df_min = pd.merge(df_min, df_15min, left_index=True, right_index=True, how='left')
#     df_min = pd.merge(df_min, df_30min, left_index=True, right_index=True, how='left')
#     df_min = pd.merge(df_min, df_60min, left_index=True, right_index=True, how='left')
#     df_min = pd.merge(df_min, df_4hrs, left_index=True, right_index=True, how='left')
#     df_combined = df_min.merge(df_daily, on='date', suffixes=('', '_daily'))
#     df_combined = df_combined.merge(df_weekly, on='week', suffixes=('', '_weekly'))
#     df_combined = df_combined.merge(df_monthly, on='month', suffixes=('', '_monthly'))
#
#     # df_combined.fillna(method='ffill', inplace=True)
#     df_combined.ffill(inplace=True)
#
#     df_combined.index = list_idx
#     df_combined.index.rename('날짜', inplace=True)  # 인덱스명 변경
#     df_combined.drop('date', axis=1, inplace=True)
#     df_combined.drop('week', axis=1, inplace=True)
#     df_combined.drop('month', axis=1, inplace=True)
#     return df_combined


#
# def convert_df_day(df):
#     df['등락율'] = round((df['종가'] - df['종가'].shift(1)) / df['종가'].shift(1) * 100, 2)
#     df['변화율'] = round((df['종가'] - df['시가']) / df['시가'] * 100, 2)
#     df['이평5'] = talib.MA(df['종가'], 5)
#     df['이평20'] = talib.MA(df['종가'], 20)
#     df['이평60'] = talib.MA(df['종가'], 60)
#     df['이평120'] = talib.MA(df['종가'], 120)
#     df['이평240'] = talib.MA(df['종가'], 200)
#     df['거래량이평3'] = talib.MA(df['거래량'], 3)
#     df['거래량이평20'] = talib.MA(df['거래량'], 20)
#     df['거래량이평60'] = talib.MA(df['거래량'], 60)
#     df['MACD'],df['MACD_SIGNAL'],df['MACD_HIST'] = talib.MACD(df['종가'], fastperiod=12, slowperiod=26, signalperiod=9)
#     df['RSI14'] = talib.RSI(df["종가"], timeperiod=14).round(1)
#     df['RSI18'] = talib.RSI(df["종가"], timeperiod=18).round(1)
#     df['RSI30'] = talib.RSI(df["종가"], timeperiod=30).round(1)
#     df['ATR10'] = talib.ATR(df['고가'], df['저가'], df['종가'], timeperiod=10)
#     df['TRANGE'] = talib.TRANGE(df['고가'], df['저가'], df['종가'])
#     df['이격도20이평'] = df['종가'].shift(1) / df['이평20'].shift(1) * 100
#     df['밴드20상'], df['밴드20중'], df['밴드20하'] = talib.BBANDS(df['종가'].shift(1), 20, 2)
#     df['고저평균대비등락율'] = ((df['종가'] / ((df['고가'] + df['저가']) / 2) - 1) * 100).round(2)
#     df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
#     return df


def make_start_stop(df_detail, detail_stamp):
    # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
    df_detail['장시작시간'] = np.nan
    serise_start_t = df_detail.groupby(df_detail.index.date).transform(
        lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
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

def resample_polars(market,df, bong, rule, name):
    if market == '코인':
        df = df.group_by_dynamic(index_column="날짜", every=rule, closed="left").agg([
                                 pl.col("상세시가").first().alias("상세시가"),
                                 pl.col("상세고가").max().alias("상세고가"),
                                 pl.col("상세저가").min().alias("상세저가"),
                                 pl.col("상세종가").last().alias("상세종가"),
                                 pl.col("상세거래량").sum().alias("상세거래량")
                                 ])
    elif market == '국내주식' or market == '국내선옵':
        df = df.group_by_dynamic(index_column="날짜", every=rule, closed="left").agg([
                                 pl.col("상세시가").first().alias("상세시가"),
                                 pl.col("상세고가").max().alias("상세고가"),
                                 pl.col("상세저가").min().alias("상세저가"),
                                 pl.col("상세종가").last().alias("상세종가"),
                                 pl.col("상세거래량").sum().alias("상세거래량"),
                                 pl.col("상세거래대금").sum().alias("상세거래대금")
                                 ])
    if bong == name:  # 기준봉일 경우
        if market == '코인':
            df = df.rename({'상세시가':'시가', '상세고가':'고가', '상세저가':'저가', '상세종가':'종가',
                               '상세거래량':'거래량'})  # 컬럼명 변경

        elif market == '국내주식' or market == '국내선옵':
            df = df.rename({'상세시가':'시가', '상세고가':'고가', '상세저가':'저가', '상세종가':'종가',
                               '상세거래량':'거래량', '상세거래대금':'거래대금'})  # 컬럼명 변경
    #     df = convert_df_day(df)
    #
    else:
        if market == '코인':
            df=df.rename({'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
                         '상세거래량': f'거래량_{name}'})  # 컬럼명 변경
        elif market == '국내주식' or market == '국내선옵':
            df=df.rename({'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
                         '상세거래량': f'거래량_{name}', '상세거래대금': f'거래대금_{name}'})  # 컬럼명 변경
        # df[f'이평20_{name}'] = talib.MA(df[f'종가_{name}'], 20)
        # df[f'이평60_{name}'] = talib.MA(df[f'종가_{name}'], 60)
        # df[f'데이터길이_{name}'] = np.arange(1, len(df.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
    return df

def detail_parse(market,tikcer,bong,bong_detail):
    dict_bong_unit = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                       '주봉': 10080, '월봉':302400}
    dict_bong = {'1분봉': '1m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉': '4h', '일봉': 'd',
                 '주봉': 'W', '월봉': 'M'}
    if market == '코인':
        dbname = "DB/DB_bybit.db"  # sqlite3 db file path
    conn = sqlite3.connect(dbname)
    ticker_detail = f"{ticker}_{dict_bong[bong_detail]}"
    df = pl.read_database(
        query=f"SELECT * FROM {ticker_detail}",
        connection=conn,
        schema_overrides={"normalised_score": pl.UInt8}, )
    # df=df.rename(lambda column_name: "상세"+column_name[:])
    df=df.rename({"시가":"상세시가","고가":"상세고가","저가":"상세저가","종가":"상세종가","거래량":"상세거래량"})

    # '날짜' 열을 datetime 형식으로 변환
    df = df.with_columns(pl.col('날짜').str.strptime(pl.Datetime))
    # print(df)

    # '날짜' 열에서 9시간 빼기
    df = df.with_columns((pl.col('날짜') - pl.duration(hours=9)).alias('날짜'))
    # print(df)



    detail_unit = dict_bong_unit[bong_detail]
    print(detail_unit)
    # list_idx = df_min.index.tolist()



    if detail_unit < dict_bong_unit['3분봉']:
        df_3min = resample_polars(market, df, bong, '3m', '3분봉')
    if detail_unit < dict_bong_unit['5분봉']:
        df_5min = resample_polars(market, df, bong, '5m', '5분봉')
    if detail_unit < dict_bong_unit['15분봉']:
        df_15min = resample_polars(market, df, bong, '15m', '15분봉')
    if detail_unit < dict_bong_unit['30분봉']:
        df_30min = resample_polars(market, df, bong, '30m', '30분봉')
    if detail_unit < dict_bong_unit['60분봉']:
        df_1h = resample_polars(market, df, bong, '1h', '60분봉')
    if detail_unit < dict_bong_unit['4시간봉']:
        df_4hrs = resample_polars(market, df, bong, '4h', '4시간봉')
    if detail_unit < dict_bong_unit['일봉']:
        df_daily = resample_polars(market, df, bong, '1d', '일봉')
        # df_daily['date'] = df_daily.index.date
    if detail_unit < dict_bong_unit['주봉']:
        df_weekly = resample_polars(market, df, bong, '1w', '주봉')
    if detail_unit < dict_bong_unit['월봉']:
        df_monthly = resample_polars(market, df, bong, '1mo', '월봉')

    # df_weekly['week'] = df_weekly.index.to_period('W').astype(str)
    # df_monthly['month'] = df_monthly.index.to_period('M').astype(str)
    # df_min['date'] = df_min.index.date
    # df_min['week'] = df_min.index.to_period('W').astype(str)
    # df_min['month'] = df_min.index.to_period('M').astype(str)

    # 날짜, 주, 월 정보를 추가
    df = df.with_columns([
        pl.col('날짜').dt.truncate('1d').alias('date'),
        pl.col('날짜').dt.truncate('1w').alias('week'),
        pl.col('날짜').dt.truncate('1mo').alias('month')
    ])
    with pl.Config(fmt_str_lengths=1000, tbl_width_chars=1000):
        print(df)
    # 데이터 병합
    df_combined = (
        df
        .join(df_3min, on='날짜', how='left')
        .join(df_5min, on='날짜', how='left')
        .join(df_15min, on='날짜', how='left')
        .join(df_30min, on='날짜', how='left')
        .join(df_1h, on='날짜', how='left')
        .join(df_4hrs, on='날짜', how='left')
        .join(df_daily, on='날짜', suffix='_daily', how='left')
        .join(df_weekly, on='날짜', suffix='_weekly', how='left')
        .join(df_monthly, on='날짜', suffix='_monthly', how='left')
    )

    print(df_combined.glimpse())
    df_combined.fillna(method='ffill', inplace=True)

    df_combined.index = list_idx
    df_combined.index.rename('날짜', inplace=True)  # 인덱스명 변경
    df_combined.drop('date', axis=1, inplace=True)
    df_combined.drop('week', axis=1, inplace=True)
    df_combined.drop('month', axis=1, inplace=True)
    return df_combined






if __name__ == '__main__':
    class min_QCB():
        def __init__(self,signal:bool):
            self.signal = signal
        def isChecked(self):
            return self.signal

    start_time = time.time()

    # ticker = 'ETH'
    # market = '코인'
    # ticker = '122630'
    # market = '국내주식'
    ticker = '10100'
    market = '국내선옵'
    # ticker = '코스피200선물'

    bong = '5분봉'
    bong_detail = '1분봉'
    min = min_QCB(True)

    frdate = '2010-01-01'
    todate = datetime.now().strftime('%Y-%m-%d')
    # frdate = '2022-06-28'
    # todate = '2024-01-03'


    if market == '코인':
        conn_DB = sqlite3.connect('DB/DB_bybit.db')
        exchange = make_exchange_bybit()
        stocks_info = pd.DataFrame()

    elif market == '국내주식' or market == '국내선옵':
        conn_DB = sqlite3.connect('DB/DB_stock.db')
        stocks_info = pd.read_sql(f"SELECT * FROM 'stocks_info'", conn_DB).set_index('종목코드')
        exchange = make_exchange_kis()

    else:
        conn_DB = ''
        stocks_info = pd.DataFrame()

    dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60, '4시간봉': 240, '일봉': 1440,
                       '주봉': 10080}

    st = time.time()
    # df, df_detail, trade_market, dict_bong, dict_bong_reverse = \
    #     get_df_multi(market, ticker, bong, bong_detail, frdate, todate, dict_bong_stamp, stocks_info)  # 30분봉, 1시간봉, 4시간봉 사용
    # #
    # print(f"데이터로딩 걸린시간   {time.time()-st}")
    # print(df_detail.columns.tolist())
    # if '시가_x' in df_detail.columns.tolist():
    #     print('데이터프레임 확인')
    #     quit()
    # #
    # df_detail = df_detail[df_detail.index < datetime.strptime("20220101","%Y%m%d")]
    # df_detail.to_sql('bt_numpy_detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
    # df.to_sql('bt_numpy', sqlite3.connect('DB/bt.db'), if_exists='replace')
    #
    # ##############
    #
    dict_bong = {'1분봉': '1m', '5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉': '4h', '일봉': 'd',
                 '주봉': 'W', '월봉': 'M'}

    ticker_detail = ticker + '_' + dict_bong[bong_detail]
    df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", conn_DB).set_index('날짜')
    # df_detail['날짜'] = pd.to_datetime(df_detail['날짜'])  # datime형태로 변환
    df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
    st = time.time()
    if market == '코인':
        df_detail['날짜'] = df_detail['날짜'] - pd.Timedelta(hours=9)
        # df_detail = df_detail[df_detail.index >= datetime.strptime("20200326","%Y%m%d")]
        df, df_detail = common_def.detail_to_spread(df_detail,bong,bong_detail)
        df_detail.index = df_detail.index + pd.Timedelta(hours=9)
        for day in pd.date_range(start=df_detail.index[0], end=df_detail.index[-1]):
            start_time = pd.Timestamp(day).replace(hour=9, minute=0, second=0)
            end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
            df_detail.loc[start_time:end_time, '장시작시간'] = start_time
            df_detail.loc[start_time:end_time, '장종료시간'] = end_time
            df_detail['종료시간'] = np.nan  # 넣어야됨

    elif market == '국내주식' or market == '국내선옵':
        df_detail.index = df_detail.index - pd.Timedelta(minutes=dict_bong_stamp[bong_detail])
        # df_detail = df_detail[df_detail.index >= datetime.strptime("20200326","%Y%m%d")]
        df, df_detail = common_def.detail_to_spread(df_detail,bong,bong_detail)
        print(df)
        df_detail = make_start_stop(df_detail,dict_bong_stamp[bong_detail])
        if bong == '일봉':
            df_detail['종료시간'] = df_detail['장종료시간'].copy()
        elif bong != '일봉' and bong != '주봉' and bong != '월봉':
            # 기준봉 디테일봉 모두 분봉일 경우 종료시간 만들기
            df_detail['종료시간'] = df_detail.index
            df_detail_end_time = df_detail['종료시간'].resample(f'{dict_bong_stamp[bong]}min').last()
            del df_detail['종료시간']
            df_detail = pd.merge(df_detail, df_detail_end_time, left_index=True, right_index=True, how='left')
            # df_detail.fillna(method='ffill', inplace=True)
            df_detail.ffill(inplace=True)


    print(f"걸린시간: {time.time()-st}")
    # df_detail = df_detail[df_detail.index < datetime.strptime("20220101","%Y%m%d")]
    df_detail.to_sql('bt', sqlite3.connect('DB/bt.db'), if_exists='replace')

    # df_detail = detail_parse(market,ticker,bong,bong_detail)

    print(df_detail)

