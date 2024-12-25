from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox,QHBoxLayout
from PyQt5.QtCore import QThread,pyqtSlot,pyqtSignal
import sqlite3
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import talib
from pprint import pprint
# import polars as pl
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
import sys
from PyQt5.QtWidgets import *
import common_def

class Workertest(QThread):
    result_ready = pyqtSignal(pd.DataFrame,pd.DataFrame,bool)

    def __init__(self,market,ticker,bong,bong_detail):
        super().__init__()


        self.market = market
        self.ticker = ticker
        self.bong = bong
        self.bong_detail = bong_detail


        # self.run()
    def run(self):
        print('run')
        print('=================================================================================================================')
        market = self.market
        ticker = self.ticker
        bong = self.bong
        bong_detail = self.bong_detail
        self.conn_DB = sqlite3.connect('DB/DB_bybit.db')
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}  # 국내시장의 경우 일봉을 기본으로하기 때문에 일봉은 제외
        ticker_bong = ticker + '_'+self.dict_bong[bong]
        ticker_detail = ticker + '_'+self.dict_bong[bong_detail]
        df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", self.conn_DB).set_index('날짜')
        df.index = pd.to_datetime(df.index)  # datime형태로 변환
        df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", self.conn_DB).set_index('날짜')
        df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
        save = True
        self.result_ready.emit(df, df_detail, save)






# class WorkerThread(QThread):
class WorkerThread():
    result_ready = pyqtSignal(pd.DataFrame,pd.DataFrame,bool)

    def __init__(self, dict_info):
        super().__init__()

        self.market = dict_info['market']
        self.ticker = dict_info['ticker']
        self.bong = dict_info['bong']
        self.bong_detail = dict_info['bong_detail']
        self.start_day = dict_info['start_day']
        self.end_day = dict_info['end_day']
        self.conn_DB = dict_info['connect']
        self.table_list_DB = dict_info['table_list_DB']
        self.trade_market = dict_info['trade_market']
        self.dict_bong = dict_info['dict_bong']
        self.dict_bong_reverse = dict_info['dict_bong_reverse']
        # self.run()
    def run(self):
        print('==============================================')
        dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60,'4시간봉': 240, '일봉': 1440, '주봉': 10080}
        st = time.time()
        if self.market == '국내주식' or self.market == '국내선옵' :
            market = '국내시장'
        elif self.market == '코인':
            market = self.market
        ticker = self.ticker
        bong = self.bong
        bong_detail = self.bong_detail
        # start_day = self.start_day
        # end_day = self.end_day
        trade_market = self.trade_market
        dict_bong = self.dict_bong
        dict_bong_reverse = self.dict_bong_reverse

        ticker_bong = ticker+'_'+dict_bong[bong]
        ticker_detail = ticker+'_'+dict_bong[bong_detail]


        list_bong = [x[x.index('_') + 1:] for x in self.table_list_DB if x[:x.index('_')] == ticker]  # 해당 ticker가 갖고있는 db를 리스트화 [1m,3m,5m...]
        dict_bong = {key: value for key, value in self.dict_bong.items() if value in list_bong}  # 리스트에있는 원소만 딕셔너리에 남기기
        if ticker_bong in self.table_list_DB:
            df = pd.read_sql(f"SELECT * FROM '{ticker_bong}'", self.conn_DB).set_index('날짜')
            df.index = pd.to_datetime(df.index)  # datime형태로 변환
            if market == '국내시장' and bong != '일봉' and bong != '주봉' and bong != '월봉':  # 국내시장의 기준이 분봉일 경우
                df.index = df.index - timedelta(minutes=dict_bong_stamp[bong])  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨

            # 입력받은 날짜로 자르기
            # start_day = datetime.strptime(start_day, '%Y-%m-%d')
            # end_day = datetime.strptime(end_day, '%Y-%m-%d')
            # df = df[df.index >= start_day]
            # df = df[df.index < end_day + timedelta(days=1)]

            if bong != bong_detail:
                print(' 디테일 사용')
                df_detail = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", self.conn_DB).set_index('날짜')
                df_detail.index = pd.to_datetime(df_detail.index)  # datime형태로 변환
                print(f"0 걸린시간 {time.time() - st}")
                st = time.time()
                if df_detail.empty:
                    print(f"df_detail 데이터 없음 DB 시간 확인 요망")
                    quit()
                del dict_bong[bong]  # 기준봉은 삭제
                del dict_bong[bong_detail]  # 디테일 사용 시 디테일봉 삭제

                if market == '국내시장':
                    if bong_detail != '일봉' and bong_detail != '주봉' and bong_detail != '월봉':
                        df_detail.index = df_detail.index - timedelta(minutes=dict_bong_stamp[bong_detail])  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨
                    df_detail = self.leak_to_fill(df_detail, dict_bong_stamp[bong_detail])  # 누락되는 분봉 채우기
                elif market == '코인':
                    pass
                st = time.time()
                # if market == '국내시장':

                # df_detail = df_detail[df_detail.index >= start_day]
                # df_detail = df_detail[df_detail.index < end_day + timedelta(days=1)]
                if df_detail.empty:
                    print(f"df_detail 데이터 없음 DB 시간 확인 요망")
                    quit()


                # # df와 df_detail에 있는 날짜로만 자르기
                if df.index[0] < df_detail.index[0] and bong == '일봉' and market == '국내시장':  # 일봉의 경우 인덱스의 시간이 0시 기준이기 때문에 -1일 해줘야됨
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
                elif df.index[-1] < df_detail.index[-1] and bong == '일봉' and market == '국내시장':  # 일봉의 경우 인덱스의 시간이 0시 기준이기 때문에 +1일 해줘야됨
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
            print(f"1 걸린시간{time.time() - st}")
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
                                                  '외국인현보유비율': '상세외국인현보유비율', '기관순매수량': '상세기관순매수량',
                                                  '기관누적순매수량': '상세기관누적순매수량'}, inplace=True)
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
                df_detail.rename(columns={'시가': '상세시가', '고가': '상세고가', '저가': '상세저가', '종가': '상세종가', '거래량': '상세거래량'},
                                 inplace=True)


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
            print(f"2 걸린시간{time.time() - st}")
            st = time.time()
            # df = self.convert_df(df)
            df = common_def.convert_df(df)
            df['데이터길이'] = np.arange(1, len(df.index.tolist()) + 1, 1)  # start=1, stop=len(df.index.tolist())+1, step=1
            df_detail = pd.merge(df_detail, df, left_index=True, right_index=True, how='left')

            df_detail.fillna(method='ffill', inplace=True)
            # df_detail.to_sql('detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
            df_detail['데이터길이'] = df_detail['데이터길이'].fillna(0)  # nan을 0으로 채우기

            df_detail['현재시간'] = df_detail.index
            dict_bong_reverse = dict(zip(dict_bong.values(), dict_bong.keys()))

            start_day = df_detail.index[0]
            end_day = df_detail.index[-1]
            print(f"3 걸린시간{time.time() - st}")
            st = time.time()
            print('멀티봉 생성 중..')
            for bong_add in dict_bong_reverse.keys():
                if market == '코인':  # bybit일 경우
                    df_add = pd.read_sql(f"SELECT * FROM '{ticker}_{bong_add}'", self.conn_DB).set_index('날짜')
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

                        df_add.rename(columns={'시가': f'시가_{dict_bong_reverse[bong_add]}',
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
                    df_add = pd.read_sql(f"SELECT * FROM '{ticker}_{bong_add}'", self.conn_DB).set_index('날짜')
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

                        df_add[f'데이터길이_{dict_bong_reverse[bong_add]}'] = np.arange(1, len(df_add.index.tolist()) + 1,1)  # start=1, stop=len(df.index.tolist())+1, step=1
                        df_add.rename(columns={'시가': f'시가_{dict_bong_reverse[bong_add]}',
                                               '고가': f'고가_{dict_bong_reverse[bong_add]}',
                                               '저가': f'저가_{dict_bong_reverse[bong_add]}',
                                               '종가': f'종가_{dict_bong_reverse[bong_add]}',
                                               '거래량': f'거래량_{dict_bong_reverse[bong_add]}',
                                               '거래대금': f'거래대금_{dict_bong_reverse[bong_add]}',
                                               '누적체결매도수량': f'누적체결매도수량_{dict_bong_reverse[bong_add]}',
                                               '누적체결매수수량': f'누적체결매수수량_{dict_bong_reverse[bong_add]}', },
                                      inplace=True)  # 컬럼명 변경
                        df_add[f'이평20_{dict_bong_reverse[bong_add]}'] = talib.MA(
                            df_add[f'종가_{dict_bong_reverse[bong_add]}'], 20)
                        df_add[f'이평60_{dict_bong_reverse[bong_add]}'] = talib.MA(
                            df_add[f'종가_{dict_bong_reverse[bong_add]}'], 60)

                        df_detail = pd.merge(df_detail, df_add, left_index=True, right_index=True, how='left')
            print(f"4 걸린시간{time.time() - st}")
            st = time.time()
            print(f'사용가능한 캔들 {dict_bong.keys()}')

            df_detail.fillna(method='ffill', inplace=True)
            df_detail.index.rename('날짜', inplace=True)  # 인덱스명 변경

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
            # return df, df_detail, trade_market, dict_bong, dict_bong_reverse
            save = True
            # df.to_sql('_df_', sqlite3.connect('DB/bt.db'), if_exists='replace')
            # df_detail.to_sql('_df_detail_', sqlite3.connect('DB/bt.db'), if_exists='replace')
            self.result_ready.emit(df, df_detail, save)
            return df, df_detail, save

        else:
            print(f"{ticker_bong=} {list_bong=}")
            raise print('데이터 확인 요망')

    def get_first_index(self,x):
        return x.index[0]
    def get_final_index(self,x):
        return x.index[-1]

    def leak_to_fill(self, df_detail, detail_stamp):
        # detail 1분봉 누락분에 대해서 메꿀 수 있는 방법
        df_detail['장시작시간'] = np.nan
        df_detail['장종료시간'] = np.nan
        serise_start_t = df_detail.groupby(df_detail.index.date).transform( lambda x: x.index[0]).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
        serise_end_t = df_detail.groupby(df_detail.index.date).transform( lambda x: x.index[-1]).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기
        # serise_start_t = df_detail.groupby(df_detail.index.date).transform(self.get_first_index).장시작시간  # 날짜별 마지막 시간을 같은행에 넣기
        # serise_end_t = df_detail.groupby(df_detail.index.date).transform(self.get_final_index).장종료시간  # 날짜별 마지막 시간을 같은행에 넣기



        df_detail['장시작시간'] = serise_start_t
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

        return df_detail


class WorkerThread_min_to_bong(QThread):
    result_ready = pyqtSignal(pd.DataFrame,pd.DataFrame,bool)

    def __init__(self, dict_info):
        super().__init__()

        self.market = dict_info['market']
        self.ticker = dict_info['ticker']
        self.bong = dict_info['bong']
        self.bong_detail = dict_info['bong_detail']
        self.start_day = dict_info['start_day']
        self.end_day = dict_info['end_day']
        self.conn_DB = dict_info['connect']
        self.table_list_DB = dict_info['table_list_DB']
        self.trade_market = dict_info['trade_market']
        self.dict_bong = dict_info['dict_bong']
        self.dict_bong_reverse = dict_info['dict_bong_reverse']
        # self.run()

    def run(self):
        print('run')
        self.dict_bong_stamp = {'1분봉': 1, '3분봉': 3, '5분봉': 5, '15분봉': 15, '30분봉': 30, '60분봉': 60,'4시간봉': 240}
        st = time.time()
        if self.market == '국내주식' or self.market == '국내선옵' :
            market = '국내시장'
        elif self.market == '코인':
            market = self.market
        ticker = self.ticker
        bong = self.bong
        bong_detail = self.bong_detail
        trade_market = self.trade_market
        dict_bong = self.dict_bong
        dict_bong_reverse = self.dict_bong_reverse

        ticker_bong = ticker+'_'+dict_bong[bong]
        ticker_detail = ticker+'_'+dict_bong[bong_detail]

        list_bong = [x[x.index('_') + 1:] for x in self.table_list_DB if x[:x.index('_')] == ticker]  # 해당 ticker가 갖고있는 db를 리스트화 [1m,3m,5m...]
        dict_bong = {key: value for key, value in self.dict_bong.items() if value in list_bong}  # 리스트에있는 원소만 딕셔너리에 남기기
        if ticker_detail in self.table_list_DB:
            df = pd.read_sql(f"SELECT * FROM '{ticker_detail}'", self.conn_DB).set_index('날짜')
            df.index = pd.to_datetime(df.index)  # datime형태로 변환
            df.index = df.index - timedelta(minutes=self.dict_bong_stamp[bong_detail])  # 대신증권 데이터의 경우 분봉시간이 봉 마감시간으로 나오기 때문에 빼줘야됨
            df = self.minute_to_daily(df,bong,bong_detail)
            # df.fillna(method='ffill', inplace=True)
            # df.index.rename('날짜', inplace=True)  # 인덱스명 변경
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
            # return df, df_detail, trade_market, dict_bong, dict_bong_reverse
            save = True
            df_detail = df.copy()
            df.to_sql('df', sqlite3.connect('DB/bt.db'), if_exists='replace')
            df_detail.to_sql('df_detail', sqlite3.connect('DB/bt.db'), if_exists='replace')
            self.result_ready.emit(df, df_detail, save)

        else:
            print(f"{ticker_bong=} {list_bong=}")
            raise print('데이터 확인 요망')

    def minute_to_daily(self, df_min, bong,bong_detail):
        def resample_df(df, bong, rule, name):
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
                df.rename(columns={'상세시가': f'시가', '상세고가': f'고가', '상세저가': f'저가', '상세종가': f'종가',
                                   '상세거래량': f'거래량', '상세거래대금': f'거래대금'}, inplace=True)  # 컬럼명 변경
                # df = self.convert_df(df)
                df = common_def.convert_df(df)

            else:
                df.rename(
                    columns={'상세시가': f'시가_{name}', '상세고가': f'고가_{name}', '상세저가': f'저가_{name}', '상세종가': f'종가_{name}',
                             '상세거래량': f'거래량_{name}', '상세거래대금': f'거래대금_{name}'}, inplace=True)  # 컬럼명 변경
                df[f'이평20_{name}'] = talib.MA(df[f'종가_{name}'], 20)
                df[f'이평60_{name}'] = talib.MA(df[f'종가_{name}'], 60)
                df[f'데이터길이_{name}'] = np.arange(1, len(df.index.tolist()) + 1,
                                                1)  # start=1, stop=len(df.index.tolist())+1, step=1
            return df

        df_min.rename(columns={'시가': f'상세시가', '고가': f'상세고가', '저가': f'상세저가', '종가': f'상세종가',
                               '거래량': f'상세거래량', '거래대금': f'상세거래대금'}, inplace=True)  # 컬럼명 변경

        detail_unit = self.dict_bong_stamp[bong_detail]

        list_idx = df_min.index.tolist()
        if detail_unit < self.dict_bong_stamp['3분봉']:
            df_3min = resample_df(df_min, bong, '3T', '3분봉')
        if detail_unit < self.dict_bong_stamp['5분봉']:
            df_5min = resample_df(df_min, bong, '5T', '5분봉')
        if detail_unit < self.dict_bong_stamp['15분봉']:
            df_15min = resample_df(df_min, bong, '15T', '15분봉')
        if detail_unit < self.dict_bong_stamp['30분봉']:
            df_30min = resample_df(df_min, bong, '30T', '30분봉')
        if detail_unit < self.dict_bong_stamp['60분봉']:
            df_60min = resample_df(df_min, bong, '60T', '60분봉')
        if detail_unit < self.dict_bong_stamp['4시간봉']:
            df_4h = resample_df(df_min, bong, '240T', '4시간봉')
        df_daily = resample_df(df_min, bong, 'D', '일봉')
        df_weekly = resample_df(df_min, bong, 'W', '주봉')
        df_monthly = resample_df(df_min, bong, 'M', '월봉')

        df_daily['date'] = df_daily.index.date
        df_weekly['week'] = df_weekly.index.to_period('W').astype(str)
        df_monthly['month'] = df_monthly.index.to_period('M').astype(str)
        df_min['date'] = df_min.index.date
        df_min['week'] = df_min.index.to_period('W').astype(str)
        df_min['month'] = df_min.index.to_period('M').astype(str)

        if detail_unit < self.dict_bong_stamp['3분봉']:
            df_min = pd.merge(df_min, df_3min, left_index=True, right_index=True, how='left')
        if detail_unit < self.dict_bong_stamp['5분봉']:
            df_min = pd.merge(df_min, df_5min, left_index=True, right_index=True, how='left')
        if detail_unit < self.dict_bong_stamp['15분봉']:
            df_min = pd.merge(df_min, df_15min, left_index=True, right_index=True, how='left')
        if detail_unit < self.dict_bong_stamp['30분봉']:
            df_min = pd.merge(df_min, df_30min, left_index=True, right_index=True, how='left')
        if detail_unit < self.dict_bong_stamp['60분봉']:
            df_min = pd.merge(df_min, df_60min, left_index=True, right_index=True, how='left')
        if detail_unit < self.dict_bong_stamp['4시간봉']:
            df_min = pd.merge(df_min, df_4h, left_index=True, right_index=True, how='left')
        df_combined = df_min.merge(df_daily, on='date', suffixes=('', '_daily'))
        df_combined = df_combined.merge(df_weekly, on='week', suffixes=('', '_weekly'))
        df_combined = df_combined.merge(df_monthly, on='month', suffixes=('', '_monthly'))

        df_combined.fillna(method='ffill', inplace=True)

        df_combined.index = list_idx
        df_combined.index.rename('날짜', inplace=True)  # 인덱스명 변경
        df_combined.drop('date', axis=1, inplace=True)
        df_combined.drop('week', axis=1, inplace=True)
        df_combined.drop('month', axis=1, inplace=True)
        return df_combined
    # def convert_df(self, df):
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

class Window_test(QWidget):
    def __init__(self):
        super().__init__()
        self.dict_bong = {'1분봉': '1m', '3분봉': '3m','5분봉': '5m', '15분봉': '15m', '30분봉': '30m', '60분봉': '60m', '4시간봉':'4h','일봉': 'd', '주봉': 'W', '월봉': 'M'}
        self.dict_market = {'코인':'bybit','국내주식':'stock','국내선옵':'futopt'}
        self.dict_ticker = {'코인':'BTC','국내주식':'122630','국내선옵':'10100'}
        self.dict_trade_market = {'코인':'bybit','국내주식':'ETF','국내선옵':'선물'}
        self.set_UI()
        self.QPB_start.clicked.connect(self.do_backtest_thread)
        self.QCB_market.activated[str].connect(self.selected_market)

    def set_UI(self):
        QVB_stg = QVBoxLayout()
        QGL = QGridLayout()
        self.QCB_market = QComboBox()
        self.QCB_market.addItems(['', '코인', '국내주식', '국내선옵'])
        self.QCB_chart = QCheckBox('차트보기')
        self.QCB_chart.setChecked(True)
        self.QCB_ticker = QComboBox()
        self.QCB_bong = QComboBox()
        self.QCB_bong.addItems(self.dict_bong.keys())
        self.QCB_bong_detail = QComboBox()
        self.QCB_bong_detail.addItems(self.dict_bong.keys())
        self.QLE_DB_ticker = QLineEdit()
        self.QPB_DB_save = QPushButton('DB 저장')
        self.QCB_stg_buy = QComboBox()
        self.QLE_stg_buy = QLineEdit()
        self.QLE_division_buy = QLineEdit()
        self.QPB_stg_buy_save = QPushButton('매수전략 저장')
        self.QPB_stg_buy_del = QPushButton('매수전략 삭제')
        self.QPB_stg_sell_del = QPushButton('매도전략 삭제')
        QL_start = QLabel('              시작일')
        self.QLE_start = QLineEdit()
        QL_bet = QLabel('        배팅사이즈')
        self.QLE_bet = QLineEdit('100')
        QL_end = QLabel('              종료일')
        self.QLE_end = QLineEdit()
        self.QCB_stg_sell = QComboBox()
        self.QLE_stg_sell = QLineEdit()
        self.QLE_division_sell = QLineEdit()
        self.QCB_bong.setCurrentText('5분봉')
        self.QPB_stg_sell_save = QPushButton('매도전략 저장')
        self.QPB_start = QPushButton('백테스트')
        self.QPB_stop = QPushButton('중지')
        self.QPB_save_bt = QPushButton('백테스트저장')
        self.QLE_start.setText('2010-01-01')
        self.QLE_end.setText(datetime.now().strftime('%Y-%m-%d'))
        QGL.addWidget(self.QCB_market,0,0)
        QGL.addWidget(self.QCB_ticker,0,1)
        QGL.addWidget(self.QCB_bong,1,0)
        QGL.addWidget(self.QCB_bong_detail,1,1)
        QGL.addWidget(self.QLE_DB_ticker,2,0)
        QGL.addWidget(self.QPB_DB_save,2,1)
        QGL.addWidget(self.QCB_stg_buy,3,0)
        QGL.addWidget(self.QLE_stg_buy,3,1)
        # QGL.addWidget(self.QPB_stg_buy_save,4,0,1,2)
        QGL.addWidget(self.QPB_stg_buy_save,4,0)
        QGL.addWidget(self.QPB_stg_buy_del,4,1)
        QGL.addWidget(QL_start,5,0)
        QGL.addWidget(self.QLE_start,5,1)
        QGL.addWidget(QL_end,6,0)
        QGL.addWidget(self.QLE_end,6,1)
        QGL.addWidget(QL_bet,7,0)
        QGL.addWidget(self.QLE_bet,7,1)
        QGL.addWidget(self.QPB_start,8,0)
        QGL.addWidget(self.QPB_stop,8,1)
        QGL.addWidget(self.QPB_save_bt,9,0)
        QGL.addWidget(self.QCB_chart,9,1)
        QGL.addWidget(self.QCB_stg_sell,10,0)
        QGL.addWidget(self.QLE_stg_sell,10,1)
        QGL.addWidget(self.QPB_stg_sell_save,11,0)
        QGL.addWidget(self.QPB_stg_sell_del,11,1)
        QHB_main = QHBoxLayout()
        QHB_main.addLayout(QVB_stg)
        QHB_main.addLayout(QGL)
        self.QCB_ticker.addItems(['BTC','122630','10100'])
        self.QCB_market.setCurrentText('코인')
        self.setLayout(QHB_main)
    def selected_market(self):
        ticker = self.dict_ticker[self.QCB_market.currentText()]
        print(ticker)
        self.QCB_ticker.setCurrentText(ticker)
    def do_backtest_thread(self):
        dict_bong_reverse = dict(zip(self.dict_bong.values(), self.dict_bong.keys()))

        conn_DB = sqlite3.connect(f'DB/DB_{self.dict_market[self.QCB_market.currentText()]}.db', check_same_thread=False)
        cursor = conn_DB.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list_DB = cursor.fetchall()
        table_list_DB = np.concatenate(table_list_DB).tolist()

        dict_info = {'market': self.QCB_market.currentText(), 'ticker': self.QCB_ticker.currentText(), 'bong': self.QCB_bong.currentText(),
                     'bong_detail': self.QCB_bong_detail.currentText(), 'start_day': self.QLE_start.text(), 'end_day': self.QLE_end.text(), 'connect': conn_DB,
                     'table_list_DB': table_list_DB, 'trade_market': self.dict_trade_market[self.QCB_market.currentText()],'dict_bong': self.dict_bong, 'dict_bong_reverse': dict_bong_reverse}
        st = time.time()
        worker = WorkerThread(dict_info)
        worker.result_ready.connect(self.run_backtest)
        worker.start()
        print(f"걸린시간: {time.time() - st}")
        st = time.time()

        # worker = WorkerThread_min_to_bong(dict_info)
        # worker.result_ready.connect(self.run_backtest)
        # worker.start()
        # print(f"걸린시간: {time.time() - st}")

    def run_backtest(self, df, df_detail, save):
        print(df)
        print(df_detail)
        print(save)

if __name__ == '__main__':
    # market = '국내주식'
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    app = QApplication(sys.argv)
    window = Window_test()
    window.setGeometry(2000,800,700,600)
    window.show()
    sys.exit(app.exec_())




