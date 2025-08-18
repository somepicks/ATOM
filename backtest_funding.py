
import pandas as pd
import numpy as np
import sqlite3

pd.set_option('display.max_columns',None) #모든 열을 보고자 할 때
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',1500)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('mode.chained_assignment',  None) # SettingWithCopyWarning 경고를 끈다

class FundingRateBacktester:
    def __init__(self,market, initial_capital, bong):
        self.initial_capital = initial_capital
        self.bong = bong
        if market == 'bybit':
            self.conn = sqlite3.connect('DB/DB_bybit.db')
        if market == 'binance':
            self.conn = sqlite3.connect('DB/DB_binance.db')
        self.conn = sqlite3.connect('funding_backtest.db')
    def merge_data(self, ticker):
        """OHLCV와 펀딩비 데이터 병합"""
        # ohlcv_df = pd.read_sql(f"SELECT * FROM '{ticker}'", self.conn).set_index('날짜')
        # funding_df = pd.read_sql(f"SELECT * FROM 'funding_rate'", self.conn).set_index('날짜')
        # funding_df = funding_df[[ticker]]
        # funding_df.rename(columns={ticker: 'funding_rate'}, inplace=True)  # 컬럼명 변경
        # ohlcv_df.index = pd.to_datetime(ohlcv_df.index)
        # funding_df.index = pd.to_datetime(funding_df.index)
        # ohlcv_df = ohlcv_df[ohlcv_df.index > '2024-01-01']
        # funding_df = funding_df[funding_df.index > '2024-01-01']
        # bong = '4시간봉'
        # ohlcv_df.index = ohlcv_df.index - pd.Timedelta(hours=9)
        # df, df_detail = common_def.detail_to_spread(df_min=ohlcv_df,bong=bong,bong_detail='1분봉',compare=False)
        # df.index = df.index + pd.Timedelta(hours=9)
        # df = pd.concat([df,funding_df],axis=1)



        # df.to_sql('test',sqlite3.connect('bt.db'),if_exists='replace')
        df = pd.read_sql(f"SELECT * FROM 'test'", sqlite3.connect('bt.db')).set_index('날짜')
        df.index = pd.to_datetime(df.index)
        df.drop(['데이터길이', '시가_4시간봉', '고가_4시간봉', '저가_4시간봉', '종가_4시간봉', '거래량_4시간봉',
                 '이평5_4시간봉', '이평20_4시간봉',  '이평60_4시간봉'],axis=1,inplace=True)
        df.drop(['등락율', '변화율', '이평5', '이평20', '이평60', '이평120', '이평240', '거래량이평3',
                 '거래량이평20', '거래량이평60', 'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'RSI18', 'RSI30', 'ATR',
                 'TRANGE', '이격도20이평' , '이격도60이평' , '밴드상' , '밴드중' , '밴드하' , '고저평균대비등락율'],axis=1,inplace=True)
        print(df)
        if market == 'binance':
            if ticker == 'BTC':
                self.min_order_size = 100
            else:
                self.min_order_size = 10
        elif market == 'bybit':
            self.min_order_size = 1
        # df['funding_rate'].fillna(method='ffill', inplace=True)


        # RSI 계산 (14 기간)
        # df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)

        return df

    def calculate_position_size(self, capital, price):
        """포지션 크기 계산 (최소 주문 금액 고려)"""
        max_position_value = capital
        position_size = max_position_value / price

        # 최소 주문 금액 체크
        if max_position_value < self.min_order_size:
            return 0

        return position_size

    def backtest_strategy(self, df, strategy_type,hoga):
        """백테스트 실행"""
        results = []
        USDT = self.initial_capital
        position = 0
        entry_price = 0
        profit_for_reinvest = 0
        df['USDT'] = float(USDT)
        df['진입수량'] = np.nan
        df['진입가'] = np.nan
        df['펀비'] = np.nan # 펀딩비로 받는 수량
        df['spot(free)'] = 0.0 # 펀딩비로 받는 수량 누적
        df['pnl'] = np.nan # 인버스 수익률
        df['주문가'] = np.nan # 인버스로 숏 들어갈 때 주문가 (지정가로 들어갔을 때 가장 좋은 지정가 찾기위함)
        df['체결'] = np.nan # 체결여부
        df['수익률'] = np.nan
        df['수수료'] = 0
        진입수량 = USDT/df.loc[df.index[0],'시가']
        진입가 = df.loc[df.index[0],'시가']
        free_qty = 0
        for i,(idx, row) in enumerate(df.iterrows()):
            종가 = row['종가']
            시가 = row['시가']
            고가 = row['고가']
            funding_rate = row['funding_rate']
            rsi = row['RSI14']
            # 포지션이 없을 때 진입
            df.loc[idx, 'USDT'] = USDT
            df.loc[idx, '진입수량'] = 진입수량
            df.loc[idx, '진입가'] = 진입가
            df.loc[idx, 'spot(free)'] = free_qty

            if strategy_type == 'basic':
                signal = True
            elif strategy_type == 'compound':
                signal = profit_for_reinvest >= self.min_order_size
            elif strategy_type == 'rsi_compound':
                signal = profit_for_reinvest >= self.min_order_size and rsi <= 80

            if not np.isnan(funding_rate):
                df.loc[idx, '펀비'] = 진입수량*funding_rate
                df.loc[idx, 'spot(free)'] = free_qty+df.loc[idx, '펀비']
                free_qty = df.loc[idx, 'spot(free)']

            if signal and free_qty*시가 >= self.min_order_size:

                if strategy_type == 'basic':
                    invest_amount = free_qty * 시가
                else:
                    invest_amount = profit_for_reinvest + self.initial_capital
                # position = self.calculate_position_size(invest_amount, 종가)
                주문가 = 시가+(시가*0.01*hoga)
                df.loc[idx, '주문가'] = 주문가
                if 주문가 < 고가:
                    bet = 주문가 * free_qty
                    df.loc[idx, 'spot(free)'] = 0
                    df.loc[idx, 'USDT'] = df.loc[idx, 'USDT']+bet
                    매수금액 = 진입수량 * 진입가
                    신규매수금액 = free_qty * 주문가
                    df.loc[idx, '진입수량'] = 진입수량 + free_qty
                    df.loc[idx, '진입가'] = (매수금액+신규매수금액)/(진입수량+free_qty)
                    df.loc[idx, '체결'] = float(True)

            USDT = df.loc[idx, 'USDT']
            진입수량 = df.loc[idx, '진입수량']
            진입가 = df.loc[idx, '진입가']
            free_qty = df.loc[idx, 'spot(free)']

        return df

    def run_all_strategies(self, ticker,hoga):
        # 데이터 병합
        df = self.merge_data(ticker)

        print(f"데이터 병합 완료: {len(df)} 행")

        strategies = {
            'basic': '기본 전략 (초기 자본만 사용)',
            # 'compound': '복리 전략 (100USD 이상시 재투자)',
            # 'rsi_compound': 'RSI 복리 전략 (100USD + RSI≤80시 재투자)',
            # 'MACD_compound': 'MACD 복리 전략 (100USD + MACD 데드 크로스시 재투자)'
        }

        all_results = []
        strategy_performance = {}

        for strategy_name, strategy_desc in strategies.items():
            print(f"\n{strategy_desc} 백테스트 중...")

            result = self.backtest_strategy(df, strategy_name,hoga)

            print(f"{strategy_name} 전략 저장")
            result.to_sql(strategy_name,self.conn,if_exists='replace')
            print(result)
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


if __name__ == '__main__':
    # 실제 사용시 API 키 설정 필요
    print("암호화폐 펀딩비 백테스팅 시스템")
    print("=" * 50)
    market = 'binance'
    ticker = 'OP'
    bong ='4시간봉'
    backtester = FundingRateBacktester(market=market, initial_capital=10000, bong=bong)

    # try:
    # 백테스트 실행
    results, performance = backtester.run_all_strategies(ticker,0.3)

    if results is not None and performance is not None:
        # 결과 출력
        backtester.display_results(performance)

        # SQLite에 저장
        backtester.save_to_sqlite(results, performance)

        # 추가 분석을 위한 샘플 데이터 출력
        print(f"\n샘플 백테스트 결과 (최근 5개):")
        print(results.tail())

