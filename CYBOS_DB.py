# -*- coding: utf-8 -*-
import time

import pandas as pd
import win32com.client
from pandas import Series, DataFrame
from datetime import datetime,timedelta, date
import sqlite3
import numpy as np
from pykrx import stock
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다


class db_down():
    def __init__(self):
        self.dict_bong = {'1분봉': ['m', 1, '1m'], '3분봉': ['m', 3, '3m'], '5분봉': ['m', 5, '5m'], '15분봉': ['m', 15, '15m'],
                     '30분봉': ['m', 30, '30m'], '60분봉': ['m', 60, '60m'], '일봉': ['D', 1, 'd'], '주봉': ['W', 1, 'W'],
                     '월봉': ['M', 1, 'M']}
        # self.get_candle(instChart, market, ticker, bong, start_day, end_day)
    def get_candle(self,instChart,market, ticker, bong, start_day, end_day):
        df_amount = pd.DataFrame()
        exist_end_day = end_day
        while True:
            # print(f"요청: {start_day} ~ {end_day}")
            time.sleep(0.2)
            # SetInputValue
            instChart.SetInputValue(0, ticker)  # 종목코드
            if bong in ['1분봉', '3분봉', '5분봉', '30분봉','일봉']:
                instChart.SetInputValue(1, ord('1'))  # 요청구분, '1': 기간별데이터 , '2'" 개수데이터
                instChart.SetInputValue(2, int(end_day))  # 요청 종료일 / 기재한 날짜포함 출력됨 / today
                instChart.SetInputValue(3, start_day)  # 요청시작일
            elif bong in ['주봉', '월봉']:
                instChart.SetInputValue(1, ord('2'))  # 요청구분, '1': 기간별데이터 , '2'" 개수데이터
                instChart.SetInputValue(4, 1000)  # 요청개수
            if bong == '일봉': #일봉일 경우만 전일대비 첨가
                if market == '국내주식':
                    instChart.SetInputValue(5, (0, 1, 2, 3, 4, 5, 6, 8, 9,12,13,16,17,20,21))
                    # 필드 또는 필드 배열, 0: 날짜, 1: 시간, 2~5: 시고저종, 6: 전일대비, 8: 거래량,9:거래대금 12: 상장주식수(ulonglong),
                    # 13: 시가총액(ulonglong), 14: 외국인주문한도수량(ulong), 15: 외국인주문가능수량(ulong), 16: 외국인현보유수량(ulong),
                    # 17: 외국인현보유비율(float), 18: 수정주가일자(ulong) - YYYYMMDD, 19: 수정주가비율(float), 20: 기관순매수(long),
                    # 21: 기관누적순매수(long), 22: 등락주선(long), 23: 등락비율(float), 24: 예탁금(ulonglong), 25: 주식회전율(float), 26: 거래성립률(float)
                elif market == '국내선옵':
                    instChart.SetInputValue(5, (0, 1, 2, 3, 4, 5, 6, 8, 9, 28, 29))
                    # 필드 또는 필드 배열, 0: 날짜, 1: 시간, 2~5: 시고저종, 6: 전일대비, 8: 거래량,9:거래대금 12: 상장주식수(ulonglong),
                    # 13: 시가총액(ulonglong), 14: 외국인주문한도수량(ulong), 15: 외국인주문가능수량(ulong), 16: 외국인현보유수량(ulong),
                    # 17: 외국인현보유비율(float), 18: 수정주가일자(ulong) - YYYYMMDD, 19: 수정주가비율(float),
                    # 20: 기관순매수(long), 21: 기관누적순매수(long), 22: 등락주선(long), 23: 등락비율(float), 24: 예탁금(ulonglong), 25: 주식회전율(float),
                    # 26: 거래성립률(float), 28: 선물이론가(선물 일간데이터에서만 제공)  29: 베이시스
                    #
                    # 30: 옵션이론가 (옵션일 때만 제공)

            elif bong in ['1분봉', '3분봉', '5분봉', '15분봉','30분봉','60분봉']:
                if market == '국내주식':
                    instChart.SetInputValue(5, (0, 1, 2, 3, 4, 5, 8, 9,10,11))
                    # 필드 또는 필드 배열, 0: 날짜, 1: 시간, 2~5: 시고저종, 6: 전일대비, 8: 거래량,9:거래대금 10:누적체결매도수량(ulong or ulonglong) 11:누적체결매수수량(ulong or ulonglong)
                elif market == '국내선옵':
                    instChart.SetInputValue(5, (0, 1, 2, 3, 4, 5, 8, 9,10,11))
                    # 필드 또는 필드 배열, 0: 날짜, 1: 시간, 2~5: 시고저종, 6: 전일대비, 8: 거래량,9:거래대금
                    # 10: 누적체결매도수량(ulong or ulonglong), 11: 누적체결매수수량(ulong or ulonglong)
            else: #주봉, 월봉
                    instChart.SetInputValue(5, (0, 1, 2, 3, 4, 5, 8, 9))  # 필드 또는 필드 배열, 0: 날짜, 1: 시간, 2~5: 시고저종,
                    # 6: 전일대비, 8: 거래량,9:거래대금 12: 상장주식수(ulonglong), 13: 시가총액(ulonglong), 14: 외국인주문한도수량(ulong), 15: 외국인주문가능수량(ulong), 16: 외국인현보유수량(ulong), 17: 외국인현보유비율(float), 18: 수정주가일자(ulong) - YYYYMMDD, 19: 수정주가비율(float), 20: 기관순매수(long), 21: 기관누적순매수(long), 22: 등락주선(long), 23: 등락비율(float), 24: 예탁금(ulonglong), 25: 주식회전율(float), 26: 거래성립률(float)


            instChart.SetInputValue(6, ord(self.dict_bong[bong][0]))  # 차트구분 틱, 분봉, 일봉, 주봉, 월봉
            instChart.SetInputValue(7, self.dict_bong[bong][1])  # 주기
            instChart.SetInputValue(9, ord('1'))  # 0: 무수정주가  , 1: 수정주가

            # BlockRequest
            instChart.BlockRequest()
            # rqStatus = instChart.GetDibStatus()
            # rqRet = instChart.GetDibMsg1()
            # print("통신상태", rqStatus, rqRet)
            # if rqStatus != 0:
            #     print('error')
            #     return False

            # GetHeaderValue
            numData = instChart.GetHeaderValue(3)  # 3: 수신개수
            numField = instChart.GetHeaderValue(1)  # 1: 필드개수(위에서 SetInputValue의 5번 항목의 갯수)
            nameField = instChart.GetHeaderValue(2)  # 2: 필드명(컬럼명)

            # 데이터 받아오기
            df = DataFrame()
            for i in range(numField):
                a = []
                for j in range(numData):
                    a.append(instChart.GetDataValue(i, j))
                df[instChart.GetHeaderValue(2)[i]] = a
            # df_ex = df[::-1] #거꾸로 뒤집기
            # df.to_sql(ticker+'_'+self.dict_bong[bong][2], conn, if_exists='replace')

            if bong in ['1분봉', '3분봉', '5분봉', '30분봉','일봉']:
                dates = df['날짜']
                dates = list(set(dates))
                dates.sort()
                end_day = dates[0] #데이터의 가장 오래된날짜 갖고오기 (int형)
                end_day = datetime.strptime(str(end_day), '%Y%m%d').date() # datetime으로 변경
                # print(f"실제: {end_day} ~ {dates[-1]}")
                # end_day = end_day + timedelta(days=1) #datetime에서 하루 빼기
                end_day = end_day.strftime('%Y%m%d') #하루 뺀 날짜를 str 타입으로 변경
                end_day = int(end_day)
                # print(f"다음 end_day: {end_day}")

                if exist_end_day == end_day:
                    break
                elif not exist_end_day == end_day:
                    exist_end_day = end_day
                    df_amount = pd.concat([df_amount,df])
                else:
                    raise
            elif bong == '주봉':
                df['날짜'] = df['날짜'].apply(self.convert_to_date)
                df = df.set_index('날짜')
                del df['시간']
                return df
            elif bong == '월봉':
                df['날짜'] = df['날짜'].apply(self.convert_to_last_weekday)
                df = df.set_index('날짜')
                del df['시간']
                return df
            # break
        # df_amount = df_amount[::-1]  # 거꾸로 뒤집기
        if bong == '일봉':
            df_amount['날짜'] = df_amount['날짜'].astype('str')
            df_amount.index = df_amount['날짜']

        elif bong in ['1분봉','3분봉','5분봉','30분봉']:
            df_amount['날짜'] = df_amount['날짜'].astype('str')
            df_amount['시간'] = df_amount['시간'].astype('str')
            df_amount['시간'] = df_amount['시간'].apply(lambda x: x.zfill(4))  #df조건 '시간'열의 앞자리가 3자리일 경우 앞에 '0'을 삽입
            df_amount['시간'] = df_amount['시간']+'00' # 분봉일경우 시간 마지막에 초를 더하기
            df_amount.index = df_amount['날짜'] + df_amount['시간']

        del df_amount['날짜']
        del df_amount['시간']
        df_amount.index.rename('날짜',inplace=True) # 인덱스명 변경
        # duplicates = df_amount[df_amount.duplicated(keep=False)]
        df_amount = df_amount.loc[~df_amount.index.duplicated(keep='last')] #중복인덱스 제거
        df_amount.index = pd.to_datetime(df_amount.index)  # datime형태로 변환

        # print(duplicates)
        return df_amount


    def convert_to_date(self,date_int):
        date_str = str(date_int)
        year = int(date_str[:4])
        month = int(date_str[4:6])
        week = int(date_str[6:7])
        # 해당 연도와 월의 첫 번째 날 계산
        first_day_of_month = date(year, month, 1)
        # 해당 연도와 월의 첫 번째 날의 요일 (월요일=0, 일요일=6)
        first_day_weekday = first_day_of_month.weekday()

        # # 첫 번째 금요일 날짜 계산
        # first_friday = first_day_of_month + timedelta(days=(4 - first_day_weekday) % 7)
        # 첫 번째 월요일 날짜 계산
        first_friday = first_day_of_month + timedelta(days=(7 - first_day_weekday) % 7)

        # 주차에 따라 날짜 계산
        target_friday = first_friday + timedelta(weeks=week - 1)
        return target_friday


    def convert_to_last_weekday(self,date_int):
        date_str = str(date_int)
        year = int(date_str[:4])
        month = int(date_str[4:6])

        # 해당 연도와 월의 마지막 날 계산
        # next_month = month % 12 + 1
        # next_month_first_day = date(year if next_month != 1 else year + 1, next_month, 1)
        # last_day_of_month = next_month_first_day - timedelta(days=1)
        # 마지막 날이 주말이면 마지막 평일로 조정
        # if last_day_of_month.weekday() > 4:  # 5 = 토요일, 6 = 일요일
        #     last_day_of_month -= timedelta(days=last_day_of_month.weekday() - 4)
        # return last_day_of_month

        # 해당 연도와 월의 첫 번째 날 계산
        first_day_of_month = date(year, month, 1)
        # 첫 번째 날이 주말이면 첫 번째 평일로 조정
        if first_day_of_month.weekday() >= 5:  # 5 = 토요일, 6 = 일요일
            first_day_of_month += timedelta(days=(7 - first_day_of_month.weekday()))
        return first_day_of_month


    def get_stock_market_types(self):
        # KOSPI 종목 가져오기
        kospi = stock.get_market_ticker_list(market="KOSPI")
        kospi_names = [stock.get_market_ticker_name(ticker) for ticker in kospi]

        # KOSDAQ 종목 가져오기
        kosdaq = stock.get_market_ticker_list(market="KOSDAQ")
        kosdaq_names = [stock.get_market_ticker_name(ticker) for ticker in kosdaq]

        # ETF 종목 가져오기
        etf = stock.get_etf_ticker_list()
        etf_names = [stock.get_etf_ticker_name(ticker) for ticker in etf]

        # 데이터프레임 생성
        kospi_df = pd.DataFrame({"종목코드": kospi, "종목명": kospi_names, "시장구분": "KOSPI"})
        kosdaq_df = pd.DataFrame({"종목코드": kosdaq, "종목명": kosdaq_names, "시장구분": "KOSDAQ"})
        etf_df = pd.DataFrame({"종목코드": etf, "종목명": etf_names, "시장구분": "ETF"})

        # 데이터프레임 병합
        df = pd.concat([kospi_df, kosdaq_df, etf_df])
        df.reset_index(drop=True, inplace=True)
        df = df.set_index('종목코드')
        return df

    def get_stock_info(self):
        stock_list = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[
            0]
        stock_list.종목코드 = stock_list.종목코드.map('{:06d}'.format)  # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
        stock_list = stock_list[['회사명', '종목코드', '업종', '주요제품', '상장일']]  # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
        # list_tickers = stock_list['종목코드'].tolist()
        stock_list.set_index('종목코드',inplace=True)
        return stock_list

if __name__ == '__main__':
    instCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")

    if instCpCybos.IsConnect == 1:
        print(instCpCybos.IsConnect)
        print('대신증권 연결')
    else:
        print(instCpCybos.IsConnect)
        raise '연결 실패 코드가 맞는지 32비트로 실행 되었는지 관리자 권한으로 실행했는지 확인 필요'



    instCpCybos = win32com.client.Dispatch("CpUtil.CpOptionCode")
    opt_num = instCpCybos.GetCount() # 옵션 전체 갯수
    for i in range(opt_num):
        옵션코드 = instCpCybos.GetData(0,i)
        옵션이름 = instCpCybos.GetData(1,i)
        구분 = instCpCybos.GetData(2,i)
        행사월 = instCpCybos.GetData(3,i)
        행사가 = instCpCybos.GetData(4,i)
        print(f"{i}, {옵션코드= }, {옵션이름= }, {구분= }, {행사월= }, {행사가= }")

    print(instCpCybos.CodeToName ('201VA355'))

    quit()
    conn = sqlite3.connect('DB/DB_krx.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    try:
        table_list = np.concatenate(cursor.fetchall()).tolist()
    except:
        table_list = []

    dict_bong = {
        '1분봉': ['m', 1, '1m'], '3분봉': ['m', 3, '3m'], '5분봉': ['m', 5, '5m'],
        '15분봉': ['m', 15, '15m'],
                 '30분봉': ['m', 30, '30m'], '60분봉': ['m', 60, '60m'], '일봉': ['D', 1, 'd'], '주봉': ['W', 1, 'W'], '월봉': ['M', 1, 'M']}
    start_day = 20100101
    end_day = datetime.now().strftime("%Y%m%d")

    # market = '국내주식'
    # ticker = '122630'  # 코덱스레버리지
    # ticker = '전체'
    # ticker = 'A005930' #삼성전자

    market = '국내선옵'
    dict_ticker = {'코스피200선물': '10100', '미니코스피200선물':'10500','코스닥150선물':'10600','미국달러선물':'17500',
                   '3년국채선물': '16500','10년국채선물': '16700', '금연결선물': '18800'}
    # 종목코드
    ticker = '10100'
    # KODEX WTI 원유선물: A261220
    # KODEX 미국S & P500: A219480
    # KODEX 미국나스닥100선물: A304940
    # KODEX 중국본토csi300: A283580
    # ticker = '10100'  #선물


    df_krx_market = get_stock_market_types()
    if ticker == '전체':
        list_tickers = df_krx_market.index.tolist()
    else:
        list_tickers = [ticker]

    for ticker in list_tickers:
        for bong in dict_bong.keys():
            df_old = pd.DataFrame()
            print(f"{ticker} {bong} 저장..")
            #봉이 변경될 때 마다 instChart를 새로 갱신해줘야됨
            if market == '국내주식':
                instChart = win32com.client.Dispatch("CpSysDib.StockChart")  # 주식 데이터 연결
                # table_list = [x[:6] for x in table_list] #앞에 6자리만 잘라서 리스트로 다시 저장
                ticker_name = 'A'+ticker
            elif market == '국내선옵':
                instChart = win32com.client.Dispatch("CpSysDib.FutOptChart")  # 선물/옵션 데이터 연결
                ticker_name = ticker
            else:
                instChart = ''
                ticker_name = 'A'+ticker

            if ticker+'_'+dict_bong[bong][2] in table_list:
                df_old = pd.read_sql(f"SELECT * FROM '{ticker + '_' + dict_bong[bong][2]}'", conn).set_index('날짜')
                df_old.index = pd.to_datetime(df_old.index)  # datime형태로 변환
                start_day = df_old.index[-1].date() #인덱스의 마지막요소 추출
                start_day = datetime.strftime(start_day,'%Y%m%d')
                start_day = int(start_day)

            df = get_candle(instChart,market, ticker_name, bong, start_day, end_day,dict_bong)
            if bong == '일봉' or bong == '주봉' or bong == '월봉':
                df.drop(df.index[0],inplace=True) #가장 최근행은 아직 갱신중일 수 있으므로 삭제
            df = df[::-1]  # 거꾸로 뒤집기
            df = pd.concat([df_old, df])
            df = df.loc[~df.index.duplicated(keep='last')]  # 중복인덱스 제거

            df = round(df, 2)
            df.to_sql(ticker+'_'+dict_bong[bong][2], conn, if_exists='replace')
    print('저장 완료')
    #데이터누락 발생 분으로 확인할 것
    if 'ticker_info' in table_list:
        df_krx_market_old = pd.read_sql(f"SELECT * FROM 'ticker_info'", conn).set_index('종목코드')
    elif not 'ticker_info' in table_list:
        df_krx_market_old = pd.DataFrame()
    df_krx_market = pd.concat([df_krx_market_old, df_krx_market])
    df_krx_market = df_krx_market.loc[~df_krx_market.index.duplicated(keep='last')]  # 중복인덱스 제거

    df_stock_info = get_stock_info()
    df_stock_info = pd.merge(df_krx_market, df_stock_info, left_index=True, right_index=True, how='left')
    df_fund = stock.get_market_fundamental(datetime.now().strftime("%Y%m%d"))
    df_stock_info = pd.merge(df_stock_info, df_fund, left_index=True, right_index=True, how='left')
    print(df_stock_info)
    df_stock_info.to_sql('stocks_info',sqlite3.connect('DB/DB_krx.db'),if_exists='replace')


    # df.index = pd.to_datetime(df.index)  # datime형태로 변환
    # print(len(df))
    # df = df[::-1]  # 거꾸로 뒤집기

    # # # df = pd.read_sql(f"SELECT * FROM '122630_5m'", sqlite3.connect('DB/DB_krx.db')).set_index('날짜')
    # invalid_indices = df.index.to_series().groupby(df.index.date).first() #df의 인덱스를 그룹화해서 첫번째행만 추출
    # print(invalid_indices)
    # df = invalid_indices.to_frame(name='value')
    # df.to_sql('value',sqlite3.connect('DB/DB.db'),if_exists='replace')
    # filtered = invalid_indices[invalid_indices.index.to_series().groupby(invalid_indices.index.date).first() != pd.Timestamp('09:05')]
    # print(invalid_indices.index)