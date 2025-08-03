# import talib
# import statsmodels.api as sm
# import pandas as pd
#
#
# def initialize(context):
#     context.security = symbol('AAPL')
#     # set_universe(universe.DollarVolumeUniverse(floor_percentile=98.0,ceiling_percentile=100.0))
#
#
# def bar_data(OHLC_type, bars_nr):
#     bar_data_func = (history((bars_nr + 1), '1d', OHLC_type).iloc[0]).astype('float')
#     return bar_data_func
#
#
# def handle_data(context, data):
#     ######### FEEDING DATA
#     # Bar data
#     bar_close = 'close_price'
#     bar_open = 'open_price'
#     bar_high = 'high'
#     bar_low = 'low'
#     bar_volume = 'volume'
#
#     # current_price = data[context.security].price
#     price_history = history(bar_count=1, frequency='1d', field='price')
#     for s in data:
#         current_price = price_history[s][-1]
#
#     ######### ADVANCED DATA
#     # Spread data
#     yesterday_spread = bar_data(bar_high, 1) - bar_data(bar_low, 1)
#     up_bar = bar_data(bar_close, 1) > bar_data(bar_close, 2)
#     down_bar = bar_data(bar_close, 1) < bar_data(bar_close, 2)
#
#     two_days_ago_spread = bar_data(bar_high, 2) - bar_data(bar_low, 2)
#     up_bar_2_bars_ago = bar_data(bar_close, 2) > bar_data(bar_close, 3)
#     down_bar_2_bars_ago = bar_data(bar_close, 2) < bar_data(bar_close, 3)
#
#     # Average spread
#     last_i_highs = history(30, '1d', 'high')
#     last_i_lows = history(30, '1d', 'low')
#     average_spread = last_i_highs - last_i_lows
#     average_spread = average_spread.mean()
#
#     # Spread factors
#     wide_spread_factor = 1.5
#     narrow_spread_factor = 0.7
#     wide_spread_bar = yesterday_spread > (wide_spread_factor * average_spread)
#     wide_spread_bar_2_bars_ago = two_days_ago_spread > (wide_spread_factor * average_spread)
#     narrow_spread_bar = yesterday_spread < (narrow_spread_factor * average_spread)
#
#     # Bar close range
#     bar_range = yesterday_spread / (bar_data(bar_close, 1) - bar_data(bar_low, 1))
#     very_high_close_bar = bar_range < 1.35
#     high_close_bar = bar_range < 2
#     mid_close_bar = (bar_range < 2.2) & (bar_range > 1.8)
#     down_close_bar = bar_range > 2
#
#     # Volume data
#     volume_history = history(bar_count=100, frequency='1d', field='volume')
#     volume_series = volume_history[context.security]
#     volume_average = talib.EMA(volume_series, timeperiod=30)
#
#     # Volume moving average
#     last_i_volumes = history(30, '1d', 'volume')
#     average_volume = last_i_volumes.mean()
#
#     # Trend definition - Linear Regressions
#     long_term_history = history(bar_count=40, frequency='1d', field='price')
#     medium_term_history = history(bar_count=15, frequency='1d', field='price')
#     short_term_history = history(bar_count=5, frequency='1d', field='price')
#
#     for S in data:
#         long_y = long_term_history[S].values / long_term_history[S].mean()
#         long_x = range(len(long_term_history))
#         long_a = sm.add_constant(long_x)
#         long_results = sm.OLS(long_y, long_a).fit()
#         long_interB, long_slopeM = long_results.params
#
#         medium_y = medium_term_history[S].values / medium_term_history[S].mean()
#         medium_x = range(len(medium_term_history))
#         medium_a = sm.add_constant(medium_x)
#         medium_results = sm.OLS(medium_y, medium_a).fit()
#         medium_interB, medium_slopeM = medium_results.params
#
#         short_y = short_term_history[S].values / short_term_history[S].mean()
#         short_x = range(len(short_term_history))
#         short_a = sm.add_constant(short_x)
#         short_results = sm.OLS(short_y, short_a).fit()
#         short_interB, short_slopeM = short_results.params
#
#     # Returns true if yesterday's volume is lower than the 2 previous days
#     two_days_lowest_volume = (bar_data(bar_volume, 1) < bar_data(bar_volume, 2)) & (
#                 bar_data(bar_volume, 1) < bar_data(bar_volume, 3))
#
#     # Calculate ATR (14)
#     atr_highs = history(15, '1d', 'high')
#     atr_lows = history(15, '1d', 'low')
#     atr_closes = history(15, '1d', 'close_price')
#     ATR = pd.DataFrame(index=atr_closes.index, columns=atr_closes.columns)
#     for security in list(atr_closes.columns.values):
#         ATR[security] = talib.ATR(atr_highs[security], atr_lows[security], atr_closes[security], timeperiod=14)
#
#     # Weakness signal 1
#     weakness_signal_1 = wide_spread_bar & down_close_bar & (short_slopeM > 0)
#
#     # Strength signal 1
#     strength_signal_1 = two_days_lowest_volume & (bar_data(bar_volume, 1) < bar_data(bar_volume, 2)) & (high_close_bar)
#
#     ######### TRADE MANAGEMENT
#     position = context.portfolio.positions[context.security].amount
#     stop_loss = bar_data(bar_open, 0) - ATR.tail(1)
#     take_profit = bar_data(bar_open, 0) + 2 * ATR.tail(1)
#     stop_loss_hit = bar_data(bar_low, 0) < stop_loss
#     take_profit_hit = bar_data(bar_low, 0) > take_profit
#
#     if strength_signal_1[0] and (position == 0):
#         order_target_percent(context.security, 0.20)
#     elif position != 0 or (stop_loss_hit is True) or (take_profit_hit is True):
#         order_target_percent(context.security, 0)


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import talib
import yfinance as yf
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class VSAIndicator:
    def __init__(self, data):
        """
        VSA (Volume Spread Analysis) 지표 클래스

        Parameters:
        data (pd.DataFrame): OHLCV 데이터 (columns: Open, High, Low, Close, Volume)
        """
        self.data = data.copy()
        self.prepare_data()

    def prepare_data(self):
        """데이터 전처리 및 기본 지표 계산"""
        # 컬럼명 통일
        self.data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        # 기본 지표 계산
        self.data['Spread'] = self.data['High'] - self.data['Low']
        self.data['Body'] = abs(self.data['Close'] - self.data['Open'])
        self.data['Upper_Shadow'] = self.data['High'] - np.maximum(self.data['Open'], self.data['Close'])
        self.data['Lower_Shadow'] = np.minimum(self.data['Open'], self.data['Close']) - self.data['Low']

        # 이동평균 계산
        self.data['Avg_Spread_30'] = self.data['Spread'].rolling(window=30, min_periods=1).mean()
        self.data['Avg_Volume_30'] = self.data['Volume'].rolling(window=30, min_periods=1).mean()

        # ATR 계산
        self.data['ATR'] = talib.ATR(self.data['High'].values,
                                     self.data['Low'].values,
                                     self.data['Close'].values,
                                     timeperiod=14)

        # 가격 변화
        self.data['Price_Change'] = self.data['Close'].diff()
        self.data['Up_Bar'] = self.data['Price_Change'] > 0
        self.data['Down_Bar'] = self.data['Price_Change'] < 0

    def calculate_vsa_factors(self):
        """VSA 팩터들 계산"""
        # 스프레드 분석
        wide_spread_factor = 1.5
        narrow_spread_factor = 0.7

        self.data['Wide_Spread'] = self.data['Spread'] > (wide_spread_factor * self.data['Avg_Spread_30'])
        self.data['Narrow_Spread'] = self.data['Spread'] < (narrow_spread_factor * self.data['Avg_Spread_30'])

        # 볼륨 분석
        high_volume_factor = 1.5
        low_volume_factor = 0.7
        climax_volume_factor = 2.0

        self.data['High_Volume'] = self.data['Volume'] > (high_volume_factor * self.data['Avg_Volume_30'])
        self.data['Low_Volume'] = self.data['Volume'] < (low_volume_factor * self.data['Avg_Volume_30'])
        self.data['Climax_Volume'] = self.data['Volume'] > (climax_volume_factor * self.data['Avg_Volume_30'])

        # 바 클로즈 레인지 분석 (원본 코드 로직)
        self.data['Bar_Range'] = np.where(
            (self.data['Close'] - self.data['Low']) != 0,
            self.data['Spread'] / (self.data['Close'] - self.data['Low']),
            0
        )

        self.data['Very_High_Close'] = self.data['Bar_Range'] < 1.35
        self.data['High_Close'] = self.data['Bar_Range'] < 2
        self.data['Mid_Close'] = (self.data['Bar_Range'] < 2.2) & (self.data['Bar_Range'] > 1.8)
        self.data['Low_Close'] = self.data['Bar_Range'] > 2

        # 스프레드 및 볼륨 비율
        self.data['Spread_Ratio'] = self.data['Spread'] / self.data['Avg_Spread_30']
        self.data['Volume_Ratio'] = self.data['Volume'] / self.data['Avg_Volume_30']

    def detect_vsa_signals(self):
        """VSA 신호 감지"""
        self.calculate_vsa_factors()

        # 약세 신호들
        # 1. Weakness Signal - 와이드 스프레드 + 낮은 종가 + 상승바
        self.data['Weakness_Signal_1'] = (
                self.data['Wide_Spread'] &
                self.data['Low_Close'] &
                self.data['Up_Bar']
        )

        # 2. Selling Climax - 클라이맥스 볼륨 + 와이드 스프레드 + 하락바
        self.data['Selling_Climax'] = (
                self.data['Climax_Volume'] &
                self.data['Wide_Spread'] &
                self.data['Down_Bar']
        )

        # 3. No Demand - 내로우 스프레드 + 낮은 볼륨 + 상승바
        self.data['No_Demand'] = (
                self.data['Narrow_Spread'] &
                self.data['Low_Volume'] &
                self.data['Up_Bar']
        )

        # 강세 신호들
        # 1. Strength Signal (원본 코드 로직) - 연속 낮은 볼륨 + 높은 종가
        volume_decreasing = (
                (self.data['Volume'] < self.data['Volume'].shift(1)) &
                (self.data['Volume'] < self.data['Volume'].shift(2))
        )
        self.data['Strength_Signal_1'] = (
                volume_decreasing &
                self.data['High_Close']
        )

        # 2. Effort vs Result - 와이드 스프레드 + 높은 종가 + 상승바 + 낮은 볼륨
        self.data['Effort_Result'] = (
                self.data['Wide_Spread'] &
                self.data['High_Close'] &
                self.data['Up_Bar'] &
                self.data['Low_Volume']
        )

        # 3. Support - 와이드 스프레드 + 클라이맥스 볼륨 + 높은 종가
        self.data['Support'] = (
                self.data['Wide_Spread'] &
                self.data['Climax_Volume'] &
                self.data['High_Close']
        )

        # 종합 신호
        self.data['Bearish_Signal'] = (
                self.data['Weakness_Signal_1'] |
                self.data['Selling_Climax'] |
                self.data['No_Demand']
        )

        self.data['Bullish_Signal'] = (
                self.data['Strength_Signal_1'] |
                self.data['Effort_Result'] |
                self.data['Support']
        )

    def plot_vsa_analysis(self, start_date=None, end_date=None, figsize=(15, 12)):
        """VSA 분석 차트 그리기"""

        # 날짜 범위 설정
        if start_date:
            mask = self.data.index >= start_date
            if end_date:
                mask &= self.data.index <= end_date
            plot_data = self.data[mask].copy()
        else:
            plot_data = self.data.tail(100).copy()  # 최근 100일

        fig, axes = plt.subplots(4, 1, figsize=figsize, height_ratios=[3, 2, 2, 1])
        fig.suptitle('VSA (Volume Spread Analysis) Comprehensive Analysis', fontsize=16, fontweight='bold')

        # 1. 가격 차트 + VSA 신호
        ax1 = axes[0]
        ax1.plot(plot_data.index, plot_data['Close'], label='종가', color='black', linewidth=1)
        ax1.plot(plot_data.index, plot_data['High'], label='고가', color='red', alpha=0.5, linewidth=0.5)
        ax1.plot(plot_data.index, plot_data['Low'], label='저가', color='green', alpha=0.5, linewidth=0.5)

        # VSA 신호 표시
        bearish_signals = plot_data[plot_data['Bearish_Signal']]
        bullish_signals = plot_data[plot_data['Bullish_Signal']]

        if not bearish_signals.empty:
            ax1.scatter(bearish_signals.index, bearish_signals['Close'],
                        color='red', marker='v', s=100, label='약세 신호', alpha=0.8, zorder=5)

        if not bullish_signals.empty:
            ax1.scatter(bullish_signals.index, bullish_signals['Close'],
                        color='green', marker='^', s=100, label='강세 신호', alpha=0.8, zorder=5)

        ax1.set_title('가격 차트 및 VSA 신호')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. 스프레드 분석
        ax2 = axes[1]
        bars = ax2.bar(plot_data.index, plot_data['Spread'],
                       color='orange', alpha=0.7, label='스프레드', width=0.8)
        ax2.plot(plot_data.index, plot_data['Avg_Spread_30'],
                 color='blue', label='평균 스프레드(30일)', linewidth=2)

        # 와이드/내로우 스프레드 강조
        wide_spread_data = plot_data[plot_data['Wide_Spread']]
        narrow_spread_data = plot_data[plot_data['Narrow_Spread']]

        for idx in wide_spread_data.index:
            if idx in plot_data.index:
                idx_pos = list(plot_data.index).index(idx)
                bars[idx_pos].set_color('red')
                bars[idx_pos].set_alpha(0.8)

        for idx in narrow_spread_data.index:
            if idx in plot_data.index:
                idx_pos = list(plot_data.index).index(idx)
                bars[idx_pos].set_color('lightblue')
                bars[idx_pos].set_alpha(0.8)

        ax2.axhline(y=plot_data['Avg_Spread_30'].iloc[-1] * 1.5,
                    color='red', linestyle='--', alpha=0.7, label='와이드 기준')
        ax2.axhline(y=plot_data['Avg_Spread_30'].iloc[-1] * 0.7,
                    color='blue', linestyle='--', alpha=0.7, label='내로우 기준')

        ax2.set_title('스프레드 분석')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. 볼륨 분석
        ax3 = axes[2]
        volume_bars = ax3.bar(plot_data.index, plot_data['Volume'],
                              color='lightblue', alpha=0.7, label='거래량', width=0.8)
        ax3.plot(plot_data.index, plot_data['Avg_Volume_30'],
                 color='purple', label='평균 거래량(30일)', linewidth=2)

        # 볼륨 특성 강조
        high_volume_data = plot_data[plot_data['High_Volume']]
        climax_volume_data = plot_data[plot_data['Climax_Volume']]
        low_volume_data = plot_data[plot_data['Low_Volume']]

        for idx in high_volume_data.index:
            if idx in plot_data.index:
                idx_pos = list(plot_data.index).index(idx)
                volume_bars[idx_pos].set_color('orange')

        for idx in climax_volume_data.index:
            if idx in plot_data.index:
                idx_pos = list(plot_data.index).index(idx)
                volume_bars[idx_pos].set_color('red')

        for idx in low_volume_data.index:
            if idx in plot_data.index:
                idx_pos = list(plot_data.index).index(idx)
                volume_bars[idx_pos].set_color('lightgray')

        ax3.set_title('볼륨 분석')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. 스프레드 & 볼륨 비율
        ax4 = axes[3]
        ax4.plot(plot_data.index, plot_data['Spread_Ratio'],
                 label='스프레드 비율', color='orange', linewidth=2)
        ax4.plot(plot_data.index, plot_data['Volume_Ratio'],
                 label='볼륨 비율', color='blue', linewidth=2)

        ax4.axhline(y=1.5, color='red', linestyle='--', alpha=0.7, label='높음 기준')
        ax4.axhline(y=1.0, color='gray', linestyle='-', alpha=0.5, label='평균')
        ax4.axhline(y=0.7, color='green', linestyle='--', alpha=0.7, label='낮음 기준')

        ax4.set_title('스프레드 & 볼륨 비율')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def get_signal_summary(self, days=30):
        """최근 신호 요약"""
        recent_data = self.data.tail(days)

        summary = {
            '기간': f"최근 {days}일",
            '약세 신호': {
                'Weakness Signal': recent_data['Weakness_Signal_1'].sum(),
                'Selling Climax': recent_data['Selling_Climax'].sum(),
                'No Demand': recent_data['No_Demand'].sum(),
                '총 약세 신호': recent_data['Bearish_Signal'].sum()
            },
            '강세 신호': {
                'Strength Signal': recent_data['Strength_Signal_1'].sum(),
                'Effort vs Result': recent_data['Effort_Result'].sum(),
                'Support': recent_data['Support'].sum(),
                '총 강세 신호': recent_data['Bullish_Signal'].sum()
            },
            '현재 상태': {
                '스프레드 비율': round(recent_data['Spread_Ratio'].iloc[-1], 2),
                '볼륨 비율': round(recent_data['Volume_Ratio'].iloc[-1], 2),
                'ATR': round(recent_data['ATR'].iloc[-1], 2)
            }
        }

        return summary

    def print_signal_summary(self, days=30):
        """신호 요약 출력"""
        summary = self.get_signal_summary(days)

        print(f"\n=== VSA 신호 분석 ({summary['기간']}) ===")
        print(f"\n📉 약세 신호:")
        for signal, count in summary['약세 신호'].items():
            print(f"  • {signal}: {count}회")

        print(f"\n📈 강세 신호:")
        for signal, count in summary['강세 신호'].items():
            print(f"  • {signal}: {count}회")

        print(f"\n📊 현재 상태:")
        for indicator, value in summary['현재 상태'].items():
            print(f"  • {indicator}: {value}")

        # 해석
        bearish_total = summary['약세 신호']['총 약세 신호']
        bullish_total = summary['강세 신호']['총 강세 신호']

        print(f"\n💡 해석:")
        if bearish_total > bullish_total:
            print(f"  약세 신호가 우세합니다 (약세: {bearish_total}, 강세: {bullish_total})")
        elif bullish_total > bearish_total:
            print(f"  강세 신호가 우세합니다 (강세: {bullish_total}, 약세: {bearish_total})")
        else:
            print(f"  신호가 균형을 이루고 있습니다 (강세: {bullish_total}, 약세: {bearish_total})")


def get_sample_data(symbol='AAPL', period='6mo'):
    """샘플 데이터 가져오기 (yfinance 사용)"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data[['Open', 'High', 'Low', 'Close', 'Volume']]
    except:
        # yfinance가 없는 경우 샘플 데이터 생성
        print("yfinance가 설치되지 않아 샘플 데이터를 생성합니다.")
        dates = pd.date_range(start='2024-01-01', end='2024-07-01', freq='D')
        np.random.seed(42)

        # 랜덤 가격 데이터 생성
        base_price = 150
        prices = []
        for i in range(len(dates)):
            change = np.random.normal(0, 0.02)
            if i == 0:
                price = base_price
            else:
                price = prices[-1] * (1 + change)
            prices.append(price)

        data = pd.DataFrame(index=dates)
        data['Close'] = prices
        data['Open'] = data['Close'].shift(1) * (1 + np.random.normal(0, 0.01, len(data)))
        data['High'] = np.maximum(data['Open'], data['Close']) * (1 + abs(np.random.normal(0, 0.01, len(data))))
        data['Low'] = np.minimum(data['Open'], data['Close']) * (1 - abs(np.random.normal(0, 0.01, len(data))))
        data['Volume'] = np.random.randint(1000000, 5000000, len(data))

        return data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()


# 한글 폰트 설정 함수
def setup_korean_font():
    """한글 폰트 설정"""
    import platform

    system = platform.system()

    if system == 'Windows':
        # Windows
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
        except:
            try:
                plt.rcParams['font.family'] = 'Microsoft YaHei'
            except:
                plt.rcParams['font.family'] = 'SimHei'
    elif system == 'Darwin':  # macOS
        try:
            plt.rcParams['font.family'] = 'AppleGothic'
        except:
            try:
                plt.rcParams['font.family'] = 'Helvetica'
            except:
                plt.rcParams['font.family'] = 'DejaVu Sans'
    else:  # Linux
        try:
            plt.rcParams['font.family'] = 'NanumGothic'
        except:
            try:
                plt.rcParams['font.family'] = 'DejaVu Sans'
            except:
                # 한글 폰트가 없는 경우 영문으로 대체
                print("한글 폰트를 찾을 수 없어 영문으로 표시됩니다.")
                plt.rcParams['font.family'] = 'sans-serif'

    plt.rcParams['axes.unicode_minus'] = False


# 사용 예시
if __name__ == "__main__":
    # 한글 폰트 설정
    setup_korean_font()

    # 데이터 로드
    print("데이터를 가져오는 중...")
    data = get_sample_data('MSFT', '1y')  # AAPL 6개월 데이터

    # VSA 분석기 초기화
    print("VSA 분석 중...")
    vsa = VSAIndicator(data)
    vsa.detect_vsa_signals()

    # 결과 출력
    vsa.print_signal_summary(days=30)

    # 차트 그리기
    print("\n차트를 생성하는 중...")
    vsa.plot_vsa_analysis()

    # 특정 신호만 확인
    print("\n=== 최근 강세 신호 발생일 ===")
    recent_bullish = vsa.data[vsa.data['Bullish_Signal']].tail(5)
    if not recent_bullish.empty:
        for date, row in recent_bullish.iterrows():
            signals = []
            if row['Strength_Signal_1']: signals.append("Strength")
            if row['Effort_Result']: signals.append("Effort vs Result")
            if row['Support']: signals.append("Support")
            print(f"{date.strftime('%Y-%m-%d')}: {', '.join(signals)} (종가: ${row['Close']:.2f})")
    else:
        print("최근 강세 신호가 없습니다.")

    print("\n=== 최근 약세 신호 발생일 ===")
    recent_bearish = vsa.data[vsa.data['Bearish_Signal']].tail(5)
    if not recent_bearish.empty:
        for date, row in recent_bearish.iterrows():
            signals = []
            if row['Weakness_Signal_1']: signals.append("Weakness")
            if row['Selling_Climax']: signals.append("Selling Climax")
            if row['No_Demand']: signals.append("No Demand")
            print(f"{date.strftime('%Y-%m-%d')}: {', '.join(signals)} (종가: ${row['Close']:.2f})")
    else:
        print("최근 약세 신호가 없습니다.")