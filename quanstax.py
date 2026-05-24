import numpy as np
import pandas as pd
import common_def
from pykrx import stock
import matplotlib.pyplot as plt
#import FinanceDataReader as fdr
frdate = '20200903'
todate = '20251231'
universe = ['122630']
import sqlite3
df = stock.get_etf_ohlcv_by_date(fromdate=frdate, todate= todate, ticker = universe[0])
# conn = sqlite3.connect('DB/DB_krx.db')
# df = pd.read_sql(f"SELECT * FROM '122630'", conn).set_index('날짜')  # 머니탑 테이블 갖고오기
# conn.close()
# df = fdr.DataReader("122630")
# df = df[2500:]
"""1번조건 :  당일 저가 > 전일 저가

2번조건 : 당일 거래량 < 3일 거래량 이동평균

3번조건 : 이격도(20일 이동평균 사용) < 98

4번조건 : 이격도(20일 이동평균 사용) > 106"""
print(df)

dayopen, dayhigh, daylow , dayclose, dayvolume = df.시가, df.고가, df.저가, df.종가, df.거래량

이격도20이평 = (dayclose.shift(1) / dayclose.rolling(20).mean().shift(1)) * 100
print(이격도20이평)
df['이격도20이평'] = 이격도20이평
entry_cond = ((dayvolume.shift(1) < dayvolume.shift(1).rolling(3).mean()) | (daylow.shift(1) > daylow.shift(2))) & ((이격도20이평 < 98) | (이격도20이평 > 106))
print(entry_cond)
df["거래량이평3"] = dayvolume.shift(1).rolling(3).mean()
df["전일저가"] = daylow.shift(2)
df["거래량<거래량이평3"] = (dayvolume.shift(1) < dayvolume.shift(1).rolling(3).mean())
df["저가>전일저가"] = (daylow.shift(1) > daylow.shift(2))
df["1조건"] = np.where(df["거래량<거래량이평3"]|df["저가>전일저가"],True,False)
df["2조건"] = np.where((df["이격도20이평"]<98)|(df["이격도20이평"]>106),True,False)
df['entry_cond'] = entry_cond
exit_cond = entry_cond == False

position_cond = [entry_cond, exit_cond]
position_value = [1, -1]
position = np.select(position_cond, position_value, np.nan)
position = pd.DataFrame(position, index = df.index, columns = universe)

cond = (position < 0) & (position.shift(1) < 0)
position[cond] = np.nan

record1 = np.where((position == 1) & (pd.isnull(position.shift(1)) | (position.shift(1) < 0)), df[['시가']], df[['종가']].shift(1))
record2 = np.where((position < 0) & position.shift(1) == 1, df[['시가']], df[['종가']])
record1 = pd.DataFrame(record1, index = df.index, columns = universe)
record2 = pd.DataFrame(record2, index = df.index, columns = universe)
record1[pd.isnull(position)] = np.nan
record2[pd.isnull(position)] = np.nan
df['record1'] = record1
df['record2'] = record2
common_def.export_sql(df,"DB/bt.db","퀀스택스")
# conn = sqlite3.connect('quant.db')
# df.to_sql('퀀스택스',conn,if_exists='replace')
# conn.close()
profit = record2 / record1 - 1
profit = profit.fillna(0)

profit.cumsum().apply(np.exp).plot()
plt.show()