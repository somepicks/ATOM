import pyupbit
from pprint import pprint
import sqlite3
import pandas as pd
import talib
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True) #고정폭 폰트로 교정
# pd.set_option('display.max_rows', None)  # 출력 옵션 설정: 모든 열의 데이터 유형을 출력
# pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
ticker = 'USDT'
df_usdt = pyupbit.get_tickers('KRW-BTC')
pprint(df_usdt)

def get_upbit_ohlcv(ticker='BTC',interval='D',start_date='2019-01-01',end_date='2019-12-31'):
    print(ticker)
    # pyupbit.get_ohlcv(ticker,interval,start_date,end_date)
    dic_interval = {
        'D':'day', '1m':'minute1', '3m':'minute3', '5m':'minute5', '10m':'minute10', '15m':'minute15',
        '30m':'minute30', '1h':'minute60', '4h':'minute240', 'w':'week', 'm':'month'}
    df_usdt = pyupbit.get_ohlcv(ticker='KRW-'+ticker,interval=dic_interval[interval])
    pass
df_usdt = pyupbit.get_ohlcv(ticker='KRW-'+ticker,interval='minute60',count=20000,to='2025-10-20',period=0.1)
print(df_usdt)
print(len(df_usdt))
start_date = df_usdt.index[0]
start_date = start_date.strftime('%Y-%m-%d')
print(start_date)
#day/minute1/minute3/minute5/minute10/minute15/minute30/minute60/minute240/week/month


df_usdt.rename(columns={'open':'시가_USDT', 'high':'고가_USDT', 'low':'저가_USDT', 'close':'종가_USDT',
                   'volume':'거래량_USDT', 'value':'거래대금_USDT'},inplace=True)

# print(pyupbit.get_current_price(ticker))
print(df_usdt)
import yfinance as yf
df_exchange = yf.download(['USDKRW=X'],start=start_date,interval='1h',auto_adjust=True)
df_exchange.index = df_exchange.index.tz_convert('Asia/Seoul').tz_localize(None)
# 컬럼에서 티커(두 번째 레벨) 제거
df_exchange = df_exchange.droplevel(1, axis=1)
df_exchange.rename(columns={'Open':'시가_원달러', 'High':'고가_원달러', 'Low':'저가_원달러', 'Close':'종가_원달러',
                   'Volume':'거래량_원달러'},inplace=True)
df_exchange.drop(axis=1, columns=['거래량_원달러'], inplace=True)
print(df_exchange)

conn = sqlite3.connect('DB/exchange.db')
# data.to_sql('exchage', conn, if_exists='replace')
df = pd.concat([df_exchange, df_usdt], axis=1)
df.dropna(axis=0,inplace=True)
print(df)
df['김프'] = (df['종가_USDT']-df['종가_원달러'])/df['종가_원달러']*100
df['이평20'] = talib.MA(df['김프'], 20)
import matplotlib.pyplot as plt
plt.plot(df[['김프','이평20']])
avg = df['김프'].sum()/len(df)
print(avg)
plt.show()