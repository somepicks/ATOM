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

import ccxt
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import talib
import warnings

warnings.filterwarnings('ignore')


class FundingRateBacktester:
    def __init__(self,ticker, initial_capital=10000, min_order_size=100):
        self.initial_capital = initial_capital
        self.min_order_size = min_order_size
        self.ticker = ticker
        # self.exchange = ccxt.binance({
        #     'apiKey': 'fYs2tykmSutKiF3ZQySbDz387rqzIDJa88VszteWjqpgDlMtbejg2REN0wdgLc9e',  # 실제 API 키로 교체
        #     'secret': 'ddsuJMwqbMd5SQSnOkCzYF6BU5pWytmufN8p0tUM3qzlnS4HYZ1w5ZhlnFCuQos6',  # 실제 시크릿으로 교체
        #     'sandbox': False,  # 테스트넷 사용 (실제 거래시 False)
        #     'enableRateLimit': True,
        # })

    # def fetch_ohlcv_data(self, symbol, timeframe='4h', limit=1000):
    #     """4시간봉 OHLCV 데이터 가져오기"""
    #     try:
    #         ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    #         df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    #         df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    #         df.set_index('datetime', inplace=True)
    #         df.drop('timestamp', axis=1, inplace=True)
    #         return df
    #     except Exception as e:
    #         print(f"OHLCV 데이터 가져오기 실패: {e}")
    #         return None

    # def fetch_funding_rate_history(self, symbol, limit=1000):
    #     """펀딩비 히스토리 가져오기"""
    #     try:
    #         # 바이낸스 선물 펀딩비 히스토리
    #         funding_rates = self.exchange.fetch_funding_rate_history(symbol, limit=limit)
    #         df = pd.DataFrame(funding_rates)
    #         df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    #         df.set_index('datetime', inplace=True)
    #         df = df[['fundingRate']].rename(columns={'fundingRate': 'funding_rate'})
    #         return df
    #     except Exception as e:
    #         print(f"펀딩비 데이터 가져오기 실패: {e}")
    #         return None

    def merge_data(self, ohlcv_df, funding_df):
        """OHLCV와 펀딩비 데이터 병합"""
        # 펀딩비는 8시간마다 발생하므로 4시간봉에 맞춰 보간
        merged_df = ohlcv_df.copy()

        # 펀딩비 데이터를 4시간 간격으로 리샘플링
        funding_resampled = funding_df.resample('4H').ffill()

        # 데이터 병합
        merged_df = merged_df.join(funding_resampled, how='left')
        merged_df['funding_rate'].fillna(method='ffill', inplace=True)

        # RSI 계산 (14 기간)
        merged_df['rsi'] = talib.RSI(merged_df['close'].values, timeperiod=14)

        return merged_df.dropna()

    def calculate_position_size(self, capital, price):
        """포지션 크기 계산 (최소 주문 금액 고려)"""
        max_position_value = capital
        position_size = max_position_value / price

        # 최소 주문 금액 체크
        if max_position_value < self.min_order_size:
            return 0

        return position_size

    def backtest_strategy(self, data, strategy_type='basic'):
        """백테스트 실행"""
        results = []
        capital = self.initial_capital
        position = 0
        entry_price = 0
        profit_for_reinvest = 0

        for idx, row in data.iterrows():
            current_price = row['close']
            funding_rate = row['funding_rate']
            rsi = row['rsi']

            # 포지션이 없을 때 진입
            if position == 0:
                can_invest = False

                if strategy_type == 'basic':
                    can_invest = True
                elif strategy_type == 'compound':
                    can_invest = profit_for_reinvest >= self.min_order_size
                elif strategy_type == 'rsi_compound':
                    can_invest = profit_for_reinvest >= self.min_order_size and rsi <= 80

                if can_invest and capital >= self.min_order_size:
                    # 1배 short 포지션 진입 (코인 매수 후 선물 short)
                    invest_amount = capital if strategy_type == 'basic' else profit_for_reinvest + self.initial_capital
                    position = self.calculate_position_size(invest_amount, current_price)

                    if position > 0:
                        entry_price = current_price
                        if strategy_type != 'basic':
                            capital += profit_for_reinvest
                            profit_for_reinvest = 0

            # 포지션이 있을 때 펀딩비 수익 계산
            if position > 0:
                # 펀딩비 수익 (4시간마다, short 포지션이므로 음의 펀딩비가 수익)
                funding_pnl = -funding_rate * position * current_price

                # 현물-선물 차익 (이론적으로는 0에 수렴)
                price_pnl = 0  # 완전한 헤지라고 가정

                total_pnl = funding_pnl + price_pnl
                profit_for_reinvest += total_pnl

                # 결과 저장
                results.append({
                    'datetime': idx,
                    'price': current_price,
                    'funding_rate': funding_rate,
                    'position': position,
                    'funding_pnl': funding_pnl,
                    'total_pnl': total_pnl,
                    'capital': capital,
                    'profit_for_reinvest': profit_for_reinvest,
                    'total_value': capital + profit_for_reinvest,
                    'rsi': rsi,
                    'strategy': strategy_type
                })

        return pd.DataFrame(results)

    def run_all_strategies(self, symbol='BTC/USDT'):
        """모든 전략 실행 및 비교"""
        print(f"{symbol} 데이터 수집 중...")

        # 데이터 수집
        ohlcv_data = self.fetch_ohlcv_data(symbol)
        if ohlcv_data is None:
            return None

        funding_data = self.fetch_funding_rate_history(symbol)
        if funding_data is None:
            return None

        # 데이터 병합
        merged_data = self.merge_data(ohlcv_data, funding_data)
        print(f"데이터 병합 완료: {len(merged_data)} 행")

        strategies = {
            'basic': '기본 전략 (초기 자본만 사용)',
            'compound': '복리 전략 (100USD 이상시 재투자)',
            'rsi_compound': 'RSI 복리 전략 (100USD + RSI≤80시 재투자)'
        }

        all_results = []
        strategy_performance = {}

        for strategy_name, strategy_desc in strategies.items():
            print(f"\n{strategy_desc} 백테스트 중...")
            result = self.backtest_strategy(merged_data, strategy_name)

            if not result.empty:
                all_results.append(result)

                # 성과 계산
                final_value = result['total_value'].iloc[-1]
                total_return = (final_value - self.initial_capital) / self.initial_capital * 100

                strategy_performance[strategy_name] = {
                    'final_value': final_value,
                    'total_return': total_return,
                    'description': strategy_desc
                }

                print(f"최종 자산: ${final_value:,.2f}")
                print(f"총 수익률: {total_return:.2f}%")

        # 결과 병합
        if all_results:
            combined_results = pd.concat(all_results, ignore_index=True)
            return combined_results, strategy_performance

        return None, None

    def save_to_sqlite(self, results, performance, db_name='funding_backtest.db'):
        """결과를 SQLite에 저장"""
        conn = sqlite3.connect(db_name)

        try:
            # 백테스트 결과 저장
            results.to_sql('backtest_results', conn, if_exists='replace', index=False)

            # 전략 성과 저장
            performance_df = pd.DataFrame(performance).T.reset_index()
            performance_df.columns = ['strategy', 'final_value', 'total_return', 'description']
            performance_df.to_sql('strategy_performance', conn, if_exists='replace', index=False)

            print(f"\n결과가 {db_name}에 저장되었습니다.")

            # 저장된 테이블 확인
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"저장된 테이블: {tables}")

        except Exception as e:
            print(f"데이터베이스 저장 실패: {e}")
        finally:
            conn.close()

    def display_results(self, performance):
        """결과 출력"""
        print("\n" + "=" * 60)
        print("전략별 성과 비교")
        print("=" * 60)

        # 성과순으로 정렬
        sorted_strategies = sorted(performance.items(),
                                   key=lambda x: x[1]['total_return'],
                                   reverse=True)

        for i, (strategy, perf) in enumerate(sorted_strategies, 1):
            print(f"\n{i}. {perf['description']}")
            print(f"   최종 자산: ${perf['final_value']:,.2f}")
            print(f"   총 수익률: {perf['total_return']:.2f}%")

            if i == 1:
                print("   ⭐ 최고 수익률 전략!")

        print("\n" + "=" * 60)


def main():
    # 백테스터 초기화
    backtester = FundingRateBacktester(ticker="BTC", initial_capital=10000, min_order_size=100)

    try:
        # 백테스트 실행
        results, performance = backtester.run_all_strategies('BTC/USDT')

        if results is not None and performance is not None:
            # 결과 출력
            backtester.display_results(performance)

            # SQLite에 저장
            backtester.save_to_sqlite(results, performance)

            # 추가 분석을 위한 샘플 데이터 출력
            print(f"\n샘플 백테스트 결과 (최근 5개):")
            print(results.tail())

        else:
            print("백테스트 실행에 실패했습니다.")

    except Exception as e:
        print(f"실행 중 오류 발생: {e}")


# 실행 예제
if __name__ == "__main__":
    # 실제 사용시 API 키 설정 필요
    print("암호화폐 펀딩비 백테스팅 시스템")
    print("=" * 50)
    print("주의: 실제 사용하려면 바이낸스 API 키를 설정해야 합니다.")
    print("현재는 데모 모드입니다.")

    main()  # API 키 설정 후 주석 해제