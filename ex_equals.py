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

pd.set_option('display.max_columns', None)  # 모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment', None)  # SettingWithCopyWarning 경고를 끈다


class BinanceAssetChecker:
    def __init__(self, market, api_key, api_secret, sandbox=False):
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
                # 'sandbox': sandbox,
                'enableRateLimit': True,
            })

            # USD-M Futures 거래소 초기화
            self.usdm_exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                #                 'sandbox': sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'  # USD-M Futures
                }
            })

            # COIN-M Futures 거래소 초기화
            self.coinm_exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                #                 'sandbox': sandbox,
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
            self.ex_bybit = ccxt.bybit(config={
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'position_mode': True, }})

    def get_spot_balance(self):
        """스팟 잔고 조회"""

        balance = self.spot_exchange.fetch_balance()
        tickers = self.spot_exchange.fetch_tickers()
        # 0이 아닌 잔고만 필터링
        dict_balance = {}
        USDT_used = 0
        USDT_free = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime']:
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    if not currency == 'USDT':
                        dict_balance[currency]['price'] = tickers[currency + '/USDT']['close']
                    else:
                        dict_balance[currency]['price'] = 1
                    dict_balance[currency]['USDT'] = dict_balance[currency]['price'] * dict_balance[currency]['total']
                    if dict_balance[currency]['USDT'] < 1:
                        dict_balance.pop(currency)
                    else:
                        if currency == 'USDT':
                            USDT_free = dict_balance[currency]['free']
                            USDT_used += dict_balance[currency]['USDT'] - dict_balance[currency]['free']
                        else:
                            USDT_used += dict_balance[currency]['USDT']
        df = pd.DataFrame.from_dict(dict_balance, orient='index')
        return df, USDT_free, USDT_used

    def get_coinm_futures_balance(self):
        """COIN-M Futures 잔고 조회"""
        # try:
        balance = self.coinm_exchange.fetch_balance()
        tickers = self.coinm_exchange.fetch_tickers()
        # 0이 아닌 잔고만 필터링
        # pprint(balance)
        dict_balance = {}
        USDT = 0
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime']:
                if amounts['total'] > 0:
                    dict_balance[currency] = amounts
                    # if not currency == 'USDT':
                    dict_balance[currency]['price'] = tickers[f"{currency}/USD:{currency}"]['close']
                    # else:
                    #     dict_balance[currency]['close'] = 1
                    dict_balance[currency]['USDT'] = dict_balance[currency]['price'] * dict_balance[currency]['total']
                    if dict_balance[currency]['USDT'] < 1:
                        dict_balance.pop(currency)
                    else:
                        USDT += dict_balance[currency]['USDT']
        df = pd.DataFrame.from_dict(dict_balance, orient='index')
        return df, USDT

        # except Exception as e:
        #     print(f"COIN-M Futures 잔고 조회 오류: {e}")
        #     return {}

    def get_usdm_futures_balance(self):
        """USD-M Futures 잔고 조회"""
        if self.market == 'binance':
            # try:
            balance = self.usdm_exchange.fetch_balance()
            tickers = self.usdm_exchange.fetch_tickers()
            # 0이 아닌 잔고만 필터링
            dict_balance = {}
            USDT = 0
            # 전체
            for currency, amounts in balance.items():
                if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime', 'debt']:
                    if amounts['total'] > 0:
                        dict_balance[currency] = amounts
                        if not currency == 'USDT':
                            dict_balance[currency]['price'] = tickers[currency + '/USDT:USDT']['close']
                        else:
                            dict_balance[currency]['price'] = 1
                        dict_balance[currency]['USDT'] = dict_balance[currency]['price'] * dict_balance[currency][
                            'total']
                        if not dict_balance[currency]['USDT'] < 1:
                            USDT += dict_balance[currency]['USDT']

            res = self.usdm_exchange.fetch_positions()
            dict_linear = {}
            for data in res:
                ticker = 'binance_'+data['symbol'][:-10]+'_'+data['side']
                dict_linear[ticker] = {}
                dict_linear[ticker]['market'] = 'binance'
                dict_linear[ticker]['ticker'] = ticker
                dict_linear[ticker]['매수금액'] = data['info']['isolatedWallet']
                dict_linear[ticker]['진입수량'] = data['contracts']
                dict_linear[ticker]['진입가'] = data['entryPrice']
                dict_linear[ticker]['레버리지'] = data['entryPrice']
                dict_linear[ticker]['현재가'] = data['markPrice']
                dict_linear[ticker]['방향'] = data['side']
                dict_linear[ticker]['청산가'] = data['info']['liquidationPrice']
                dict_linear[ticker]['레버리지'] = round(data['notional'] / data['initialMargin'])

                if data['side'] == 'long':
                    dict_linear[ticker]['수익률'] = ((data['markPrice'] - data['entryPrice']) / data['entryPrice']) * \
                                                 dict_linear[ticker]['레버리지'] * 100
                    dict_linear[ticker]['수익금'] = (data['markPrice'] - data['entryPrice']) * data['contracts']
                elif data['side'] == 'short':
                    dict_linear[ticker]['수익률'] = ((data['entryPrice'] - data['markPrice']) / data['entryPrice']) * \
                                                 dict_linear[ticker]['레버리지'] * 100
                    dict_linear[ticker]['수익금'] = (data['entryPrice'] - data['markPrice']) * data['contracts']

            df_linear = pd.DataFrame.from_dict(dict_linear, orient='index')
            # df_linear.index = 'bybit_' + df_linear['ticker']
        elif self.market == 'bybit':
            list_linear = self.ex_bybit.fetch_positions()
            pprint(list_linear)
            dict_linear = {}
            for data in list_linear:
                ticker = 'bybit_'+data['symbol'][:-10]+'_'+data['side']
                dict_linear[ticker] = {}
                dict_linear[ticker]['market'] = 'bybit'
                dict_linear[ticker]['ticker'] = data['symbol'][:-10]
                dict_linear[ticker]['매수금액'] = data['collateral']
                dict_linear[ticker]['진입수량'] = data['contracts']
                dict_linear[ticker]['진입가'] = data['entryPrice']
                dict_linear[ticker]['레버리지'] = data['leverage']
                dict_linear[ticker]['현재가'] = data['markPrice']
                dict_linear[ticker]['청산가'] = data['liquidationPrice']
                dict_linear[ticker]['방향'] = data['side']
                if data['side'] == 'long':
                    dict_linear[ticker]['수익률'] = ((data['markPrice'] - data['entryPrice']) / data['entryPrice']) * data[
                        'leverage'] * 100
                    dict_linear[ticker]['수익금'] = (data['markPrice'] - data['entryPrice']) * data['contracts']
                elif data['side'] == 'short':
                    dict_linear[ticker]['수익률'] = ((data['entryPrice'] - data['markPrice']) / data['entryPrice']) * data[
                        'leverage'] * 100
                    dict_linear[ticker]['수익금'] = (data['entryPrice'] - data['markPrice']) * data['contracts']
            df_linear = pd.DataFrame.from_dict(dict_linear, orient='index')
            # df_linear.index = 'bybit_' + df_linear['ticker']
            USDT = df_linear['매수금액'].sum()

        return df_linear, USDT
        # except Exception as e:
        #     print(f"USD-M Futures 잔고 조회 오류: {e}")
        #     return {}

    def get_unified_balance(self):
        balance = self.ex_bybit.fetch_balance()
        if balance['info']['result']['list'][0]['accountType'] == 'UNIFIED':
            # usdm_balance,USDT=self.get_usdm_futures_balance()
            tickers = self.ex_bybit.fetch_tickers()
            # 0이 아닌 잔고만 필터링
            dict_balance = {}
            for currency, amounts in balance.items():
                if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime',
                                    'debt']:  # 바이비트에는 'debt'가있음
                    if amounts['total'] > 0:
                        dict_balance[currency] = amounts
                        if not currency == 'USDT':
                            dict_balance[currency]['현재가'] = tickers[currency + '/USDT:USDT']['close']
                        else:
                            dict_balance[currency]['현재가'] = 1

            list_coins = balance['info']['result']['list'][0]['coin']
            hold_tickers = dict_balance.keys()
            for data in list_coins:
                if data['coin'] in hold_tickers:
                    dict_balance[data['coin']]['market'] = 'bybit'
                    dict_balance[data['coin']]['ticker'] = data['coin']
                    # dict_balance[data['coin']]['cumRealisedPnl'] =  float(data['cumRealisedPnl'])
                    # dict_balance[data['coin']]['unrealisedPnl'] =  float(data['unrealisedPnl'])
                    # dict_balance[data['coin']]['total'] =  dict_balance[data['coin']]['total']+float(dict_balance[data['coin']]['unrealisedPnl'])
                    # dict_balance[data['coin']]['total'] =  float(data['equity'])
                    # dict_balance[data['coin']]['equity'] =  data['equity']
                    # dict_balance[data['coin']]['USDT'] =  dict_balance[data['coin']]['total']*float(dict_balance[data['coin']]['price'])
                    dict_balance[data['coin']]['합계(USD)'] = float(data['usdValue'])
                    if dict_balance[data['coin']]['합계(USD)'] < 1:
                        dict_balance.pop(data['coin'])
            df = pd.DataFrame.from_dict(dict_balance, orient='index')
            df.drop(labels='debt', axis=1, inplace=True)
            df.rename(columns={'free': 'free(qty)', 'used': 'used(qty)', 'total': 'total(qty)'}, inplace=True)
            df['배팅가능합계(USD)'] = df['free(qty)'] * df['현재가']
            df['주문최소금액(USD)'] = 1
            df.index = 'bybit_' + df['ticker']
            all_assets = df['합계(USD)'].sum()
        return all_assets, df

    def get_all_assets(self):
        """모든 자산 정보 조회 및 출력"""
        print(f"{self.market} 자산 조회 중...")

        if self.market == 'binance':
            # 스팟 잔고 조회
            # spot의 개별티커 종목은 전부 수량*현재가 USDT로-used, USDT 종목은-free
            # 매수 후 자동으로 계좌를 coin-m으로 옮기기 때문에 free 수량을 따로 잡지 않는다
            df_spot, USDT_free, USDT_used = self.get_spot_balance()

            # COIN-M Futures 잔고 조회
            df_coinm, USDT_COIN = self.get_coinm_futures_balance()

            # linear Futures 잔고 조회
            df_linear, USDT_USD = self.get_usdm_futures_balance()

            df = df_coinm.copy()
            # usdt 행 추가
            df.loc['USDT'] = [USDT_free, USDT_used + USDT_USD, USDT_free + USDT_used + USDT_USD, 1,
                              USDT_free + USDT_used + USDT_USD]  # 각 열에 맞는 값 입력

            df['합계(USD)'] = df['total'] * df['price']
            df['배팅가능합계(USD)'] = df['free'] * df['price']
            df.rename(columns={'free': 'free(qty)', 'used': 'used(qty)', 'total': 'total(qty)', 'price': '현재가'},
                      inplace=True)
            all_assets = df['합계(USD)'].sum()

        else:
            all_assets, df = self.get_unified_balance()
            df_linear, USDT_linear = self.get_usdm_futures_balance()

        return all_assets, df, df_linear


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
    all_assets, df, df_linear = asset_checker.get_all_assets()

    print('df')
    print(df)
    print('===================================')
    print('df_linear')
    print(df_linear)
    print('===================================')
    print(f"총 보유 USDT: {all_assets}")
    print(df['합계(USD)'].sum())


if __name__ == "__main__":
    main()