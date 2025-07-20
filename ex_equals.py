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
import ccxt
import pandas as pd
from decimal import Decimal
import math
pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다
class BinanceAssetChecker:
    def __init__(self,market, api_key, api_secret, sandbox=False):
        self.market = market
        if self.market == 'binance':
            """
            바이낸스 자산 조회 클래스
    
            Args:
                api_key: 바이낸스 API 키
                api_secret: 바이낸스 API 시크릿
                sandbox: 테스트넷 사용 여부
            """
            # Spot 거래소 초기화
            self.spot_exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': sandbox,
                'enableRateLimit': True,
            })

            # USD-M Futures 거래소 초기화
            self.usdm_exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'  # USD-M Futures
                }
            })

            # COIN-M Futures 거래소 초기화
            self.coinm_exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'delivery'  # COIN-M Futures
                }
            })
        elif self.market == 'bybit':
            """
            바이비트 자산 조회 클래스

            Args:
                api_key: 바이비트 API 키
                api_secret: 바이비트 API 시크릿
                sandbox: 테스트넷 사용 여부
            """
            self.usdm_exchange = ccxt.bybit(config={
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'position_mode': True, }})


    def get_spot_balance(self):
        """스팟 잔고 조회"""
        # try:
        balance = self.spot_exchange.fetch_balance()
        tickers = self.spot_exchange.fetch_tickers()
        # 0이 아닌 잔고만 필터링
        dict_balance = {}
        USDT = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total','timestamp','datetime']:
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    if not currency == 'USDT':
                        dict_balance[currency]['price'] = tickers[currency+'/USDT']['close']
                    else:
                        dict_balance[currency]['price'] = 1
                    dict_balance[currency]['USDT'] = dict_balance[currency]['price']*dict_balance[currency]['total']
                    if dict_balance[currency]['USDT'] <1:
                        dict_balance.pop(currency)
                    else:
                        USDT += dict_balance[currency]['USDT']
        return dict_balance, USDT
        # except Exception as e:
        #     print(f"스팟 잔고 조회 오류: {e}")
        #     return {}
        # print('=================')
        # quit()
    def get_usdm_futures_balance(self):
        """USD-M Futures 잔고 조회"""
        # try:
        balance = self.usdm_exchange.fetch_balance()
        tickers = self.usdm_exchange.fetch_tickers()
        # 0이 아닌 잔고만 필터링
        dict_balance = {}
        USDT = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total','timestamp','datetime','debt']: #바이비트에는 'debt'가있음
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    if not currency == 'USDT':
                        dict_balance[currency]['price'] = tickers[currency+'/USDT:USDT']['close']
                    else:
                        dict_balance[currency]['price'] = 1
                    dict_balance[currency]['USDT'] = dict_balance[currency]['price']*dict_balance[currency]['total']
                    if dict_balance[currency]['USDT'] < 1:
                        dict_balance.pop(currency)
                    else:
                        USDT += dict_balance[currency]['USDT']
        return dict_balance, USDT
        # except Exception as e:
        #     print(f"USD-M Futures 잔고 조회 오류: {e}")
        #     return {}

    def get_coinm_futures_balance(self):
        """COIN-M Futures 잔고 조회"""
        # try:
        balance = self.coinm_exchange.fetch_balance()
        tickers = self.coinm_exchange.fetch_tickers()
        # 0이 아닌 잔고만 필터링
        dict_balance = {}
        USDT = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total','timestamp','datetime']:
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    # if not currency == 'USDT':
                    dict_balance[currency]['price'] = tickers[f"{currency}/USD:{currency}"]['close']
                    # else:
                    #     dict_balance[currency]['close'] = 1
                    dict_balance[currency]['USDT'] = dict_balance[currency]['price']*dict_balance[currency]['total']
                    if dict_balance[currency]['USDT'] < 1:
                        dict_balance.pop(currency)
                    else:
                        USDT += dict_balance[currency]['USDT']
        return dict_balance, USDT
        # except Exception as e:
        #     print(f"COIN-M Futures 잔고 조회 오류: {e}")
        #     return {}

    def get_usdm_positions(self):
        """USD-M Futures 포지션 조회"""
        try:
            positions = self.usdm_exchange.fetch_positions()
            # 활성 포지션만 필터링
            active_positions = [pos for pos in positions if pos['contracts'] > 0]
            return active_positions
        except Exception as e:
            print(f"USD-M Futures 포지션 조회 오류: {e}")
            return []

    def get_coinm_positions(self):
        """COIN-M Futures 포지션 조회"""
        try:
            positions = self.coinm_exchange.fetch_positions()
            # 활성 포지션만 필터링
            active_positions = [pos for pos in positions if pos['contracts'] > 0]
            return active_positions
        except Exception as e:
            print(f"COIN-M Futures 포지션 조회 오류: {e}")
            return []

    def display_balance(self, balance, title):
        """잔고 정보를 표 형태로 출력"""
        if not balance:
            print(f"\n=== {title} ===")
            print("잔고가 없습니다.")
            return

        print(f"\n=== {title} ===")
        df = pd.DataFrame.from_dict(balance, orient='index')
        print(df.to_string())

    def display_positions(self, positions, title):
        """포지션 정보를 표 형태로 출력"""
        if not positions:
            print(f"\n=== {title} ===")
            print("활성 포지션이 없습니다.")
            return

        print(f"\n=== {title} ===")
        pos_data = []
        for pos in positions:
            pos_data.append({
                'Symbol': pos['symbol'],
                'Side': pos['side'],
                'Size': pos['contracts'],
                'Entry Price': pos['entryPrice'],
                'Mark Price': pos['markPrice'],
                'Percentage': pos['percentage'],
                'leverage' : math.trunc(1 / pos['initialMarginPercentage']),
                '매수금액*레버리지':pos['collateral'],
                '수익금': pos['unrealizedPnl'],
                '매수금액': pos['collateral']/math.trunc(1 / pos['initialMarginPercentage']),
                'USDT':pos['unrealizedPnl']+pos['collateral']/math.trunc(1 / pos['initialMarginPercentage'])
            })

        df = pd.DataFrame(pos_data)
        print(df.to_string(index=False))

    def get_all_assets(self):
        """모든 자산 정보 조회 및 출력"""
        print(f"{self.market} 자산 조회 중...")

        if self.market == 'binance':
            # 스팟 잔고 조회
            spot_balance,USDT_SPOT = self.get_spot_balance()
            self.display_balance(spot_balance, "SPOT 잔고")

            # USD-M Futures 잔고 조회
            usdm_balance,USDT_USD = self.get_usdm_futures_balance()
            self.display_balance(usdm_balance, "USD-M Futures 잔고")

            # COIN-M Futures 잔고 조회
            coinm_balance,USDT_COIN = self.get_coinm_futures_balance()
            self.display_balance(coinm_balance, "COIN-M Futures 잔고")

            # # USD-M Futures 포지션 조회
            usdm_positions = self.get_usdm_positions()
            self.display_positions(usdm_positions, "USD-M Futures 활성 포지션")
            #
            # # COIN-M Futures 포지션 조회
            coinm_positions = self.get_coinm_positions()
            self.display_positions(coinm_positions, "COIN-M Futures 활성 포지션")

            return {
                'spot': spot_balance,
                'usdm_futures': usdm_balance,
                'coinm_futures': coinm_balance,
                'usdm_positions': usdm_positions,
                'coinm_positions': coinm_positions,
                'USDT': USDT_SPOT+USDT_USD+USDT_COIN
            }
        else:
            usdm_balance,USDT=self.get_usdm_futures_balance()
            self.display_balance(usdm_balance, "USD-M Futures 잔고")
            print(USDT)
            pprint(self.usdm_exchange.fetch_balance())
            print('=====================================')
            pprint(self.usdm_exchange.fetch_positions())

# 사용 예시
def main():
    # API 키와 시크릿을 입력하세요
    BINANCE_API_KEY = 'fYs2tykmSutKiF3ZQySbDz387rqzIDJa88VszteWjqpgDlMtbejg2REN0wdgLc9e'
    BINANCE_API_SECRET = 'ddsuJMwqbMd5SQSnOkCzYF6BU5pWytmufN8p0tUM3qzlnS4HYZ1w5ZhlnFCuQos6'
    BYBIT_API_KEY = 'k3l5BpTorsRTHvPmAj'
    BYBIT_API_SECRET = 'bdajEM0VJJLXCbKw0i9VfGemAlfRGga4C5jc'


    # market = 'binance'
    market = 'bybit'
    if market == 'binance':
        API_KEY = BINANCE_API_KEY
        API_SECRET = BINANCE_API_SECRET
    else:
        API_KEY = BYBIT_API_KEY
        API_SECRET = BYBIT_API_SECRET


    # 바이낸스 자산 체커 초기화
    asset_checker = BinanceAssetChecker(market, API_KEY, API_SECRET, sandbox=False)


    # 모든 자산 정보 조회
    all_assets = asset_checker.get_all_assets()


    # print(f"총 보유 USDT: {all_assets['USDT']}")


if __name__ == "__main__":
    main()