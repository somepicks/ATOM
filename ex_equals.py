# import numpy as np
# import pandas as pd
# import sqlite3
# import datetime
#
# conn_DB = sqlite3.connect('DB/bt.db')
#
# ticker_1 = 'bt_numpy_detail'
# ticker_2 = 'bt'
#
#
# df1 = pd.read_sql(f"SELECT * FROM '{ticker_1}'", conn_DB).set_index('날짜')
# df2 = pd.read_sql(f"SELECT * FROM '{ticker_2}'", conn_DB).set_index('날짜')
# df1.index = pd.to_datetime(df1.index)  # datime형태로 변환
# df2.index = pd.to_datetime(df2.index)  # datime형태로 변환
#
# # df1 = df1[df1.index < datetime.datetime.strptime("20240617","%Y%m%d")]
# # df2 = df2[df2.index < datetime.datetime.strptime("20240617","%Y%m%d")]
# print(df1)
# print(df2)
#
# col1 = df1.columns.tolist()
# col2 = df2.columns.tolist()
# intersection = list(set(col1) & set(col2))
# print(intersection)
#
# # li_col = ['상세시가','상세고가','상세저가','상세종가','상세거래량','시가','고가','저가','종가']
# li_col = ['상세시가','상세고가','상세저가','상세종가','상세거래량','데이터길이','데이터길이_5분봉','데이터길이_30분봉','데이터길이_4시간봉','데이터길이_주봉']
# df1 = df1[li_col]
# df2 = df2[li_col]
# print(df1)
# print(df2)
#
#
# # 데이터프레임 비교
# comparison = df1.eq(df2)
# differences = comparison.ne(True)
# print(differences)
#
# # 차이점이 있는 부분만 추출
# diff_positions = differences.where(differences, np.nan)
#
# # 차이점이 있는 행과 열 출력
# for row, col in zip(*np.where(differences)):
#     print(f"Difference at row {row}, column {col} (df1: {df1.iat[row, col]}, df2: {df2.iat[row, col]})")
#
# if df1.equals(df2):
#     print('데이터 동일')
# else:
#     print('데이터 다름')
#
#
# # 차이점이 있는 데이터프레임 출력
# print("\nDifferences DataFrame:\n", diff_positions)
#
# # 값이 1인 행만 추출
# diff_df = differences[(differences == 1).any(axis=1)]
# diff_df.to_sql('diff_positions',conn_DB,if_exists='replace')
#
# non_nan_columns = diff_positions.columns[diff_positions.notna().any()].tolist()
# print(non_nan_columns)

from pprint import pprint
import os
import pandas as pd
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다


def xlsx_sorting():
    # 불러올 폴더 경로 지정
    folder_path = "D:\PycharmProjects\ATOM"

    # 폴더 내의 파일 목록 중 xlsx만 추출
    xlsx_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx") and f.startswith("2025")]

    # 정렬
    xlsx_files.sort()
    print(xlsx_files)
    # 차례대로 불러와서 리스트에 저장
    dfs = []
    df_sum = pd.DataFrame()
    for file in xlsx_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path)
        df.rename(columns={'Unnamed: 0':'ticker'},inplace=True)
        df['file'] = file
        df_sum = pd.concat([df_sum,df],axis=0)
        dfs.append(df)
        print(df_sum)

    # 확인
    for i, df in enumerate(dfs, 1):
        print(f"파일 {i}: {xlsx_files[i-1]}")
        print(df.head(), "\n")
    for ticker, group_df in df_sum.groupby(['ticker']):
        print("그룹명:", ticker[0])
        group_df.drop(labels=['marginBalance','initialMargin','positionInitialMargin','maxWithdrawAmount','crossWalletBalance',
                              'crossUnPnl','availableBalance','maxQty','notionalValue','walletBalance','maintMargin','file'],axis=1,inplace=True)
        if ticker[0] == 'BTC':
            group_df['positionAmt'] = group_df['positionAmt']*100*-1
        else:
            group_df['positionAmt'] = group_df['positionAmt']*10*-1
        print(group_df, "\n")
        group_df['pnl'] = (group_df['entryPrice'] - group_df['price']) * group_df['positionAmt'] / group_df['price']
        group_df['pnl_비교'] = group_df['pnl']-group_df['unrealizedProfit']
        group_df['used_2'] = group_df['positionAmt'] / group_df['price']
        group_df['used_비교'] = group_df['used']-group_df['used_2']
        group_df.to_excel(excel_writer=f'{ticker[0]}.xlsx')
        if ticker[0] == 'WLD':
            dict_data = group_df.to_dict(orient="records")
            pprint(dict_data)

xlsx_sorting()

import ccxt
from pprint import pprint
binance_key = 'fYs2tykmSutKiF3ZQySbDz387rqzIDJa88VszteWjqpgDlMtbejg2REN0wdgLc9e'
binance_secret = 'ddsuJMwqbMd5SQSnOkCzYF6BU5pWytmufN8p0tUM3qzlnS4HYZ1w5ZhlnFCuQos6'

binance_m = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            #                 'sandbox': sandbox,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'delivery'  # COIN-M Futures
            }})
dic = {}
res = binance_m.fetch_funding_history()
pprint(type(res))
for li in res:
    print(li)