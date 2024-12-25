import numpy as np
import pandas as pd
import sqlite3
import datetime

conn_DB = sqlite3.connect('DB/bt.db')

ticker_1 = 'bt_numpy_detail'
ticker_2 = 'bt'


df1 = pd.read_sql(f"SELECT * FROM '{ticker_1}'", conn_DB).set_index('날짜')
df2 = pd.read_sql(f"SELECT * FROM '{ticker_2}'", conn_DB).set_index('날짜')
df1.index = pd.to_datetime(df1.index)  # datime형태로 변환
df2.index = pd.to_datetime(df2.index)  # datime형태로 변환

# df1 = df1[df1.index < datetime.datetime.strptime("20240617","%Y%m%d")]
# df2 = df2[df2.index < datetime.datetime.strptime("20240617","%Y%m%d")]
print(df1)
print(df2)

col1 = df1.columns.tolist()
col2 = df2.columns.tolist()
intersection = list(set(col1) & set(col2))
print(intersection)

# li_col = ['상세시가','상세고가','상세저가','상세종가','상세거래량','시가','고가','저가','종가']
li_col = ['상세시가','상세고가','상세저가','상세종가','상세거래량','데이터길이','데이터길이_5분봉','데이터길이_30분봉','데이터길이_4시간봉','데이터길이_주봉']
df1 = df1[li_col]
df2 = df2[li_col]
print(df1)
print(df2)


# 데이터프레임 비교
comparison = df1.eq(df2)
differences = comparison.ne(True)
print(differences)

# 차이점이 있는 부분만 추출
diff_positions = differences.where(differences, np.nan)

# 차이점이 있는 행과 열 출력
for row, col in zip(*np.where(differences)):
    print(f"Difference at row {row}, column {col} (df1: {df1.iat[row, col]}, df2: {df2.iat[row, col]})")

if df1.equals(df2):
    print('데이터 동일')
else:
    print('데이터 다름')


# 차이점이 있는 데이터프레임 출력
print("\nDifferences DataFrame:\n", diff_positions)

# 값이 1인 행만 추출
diff_df = differences[(differences == 1).any(axis=1)]
diff_df.to_sql('diff_positions',conn_DB,if_exists='replace')

non_nan_columns = diff_positions.columns[diff_positions.notna().any()].tolist()
print(non_nan_columns)
