"""
12h Wave Strategy Backtest (WaveTrend Oscillator 기반)
파라미터: (10, 12, 3, 60, 53, -60, -53)

업비트 또는 바이낸스 OHLCV 데이터를 받아 백테스트 수행
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams

# 한글 폰트 설정
rcParams['font.family'] = 'Malgun Gothic'  # Windows
rcParams['axes.unicode_minus'] = False


# ─────────────────────────────────────────
# 1. 데이터 로드 (ccxt로 실시간 또는 CSV)
# ─────────────────────────────────────────

def fetch_ohlcv_ccxt(symbol='BTC/USDT', timeframe='1d', limit=1000):
    """ccxt로 OHLCV 데이터 가져오기"""
    try:
        import ccxt
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except ImportError:
        print("ccxt 미설치: pip install ccxt")
        return None


def load_from_csv(filepath):
    """CSV 파일에서 로드 (timestamp, open, high, low, close, volume 컬럼 필요)"""
    df = pd.read_csv(filepath, parse_dates=['timestamp'], index_col='timestamp')
    return df


def make_sample_data():
    """샘플 데이터 생성 (실제 데이터 없을 때 테스트용)"""
    np.random.seed(42)
    dates = pd.date_range('2021-01-01', '2022-01-05', freq='D')
    n = len(dates)
    
    close = [40000]
    for _ in range(n - 1):
        close.append(close[-1] * (1 + np.random.normal(0, 0.03)))
    close = np.array(close)
    
    df = pd.DataFrame({
        'open':   close * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high':   close * (1 + np.random.uniform(0,     0.02, n)),
        'low':    close * (1 - np.random.uniform(0,     0.02, n)),
        'close':  close,
        'volume': np.random.uniform(1e9, 5e9, n),
    }, index=dates)
    return df
def make_real_data():
    import ccxt
    ohlcv = ccxt.binance().fetch_ohlcv('BTC/USDT', timeframe='1d', limit=10000,since=pd.to_datetime('2021-05-01'))
    df = pd.DataFrame(ohlcv, columns=['날짜', 'open', 'high', 'low', 'close', 'volume'])
    df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
    df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
    df['날짜'] = df['날짜'].dt.tz_localize(None)
    df.set_index('날짜', inplace=True)
    return df

# ─────────────────────────────────────────
# 2. WaveTrend Oscillator 계산
# ─────────────────────────────────────────

def calc_wavetrend(df, n1=10, n2=12, signal_len=3):
    """
    WaveTrend Oscillator (LazyBear)
    n1: Channel Length
    n2: Average Length
    signal_len: 시그널선 기간
    """
    hlc3 = (df['high'] + df['low'] + df['close']) / 3

    # ESA: hlc3의 EMA(n1)
    esa = hlc3.ewm(span=n1, adjust=False).mean()

    # D: |hlc3 - ESA|의 EMA(n1)
    d = (hlc3 - esa).abs().ewm(span=n1, adjust=False).mean()

    # CI: (hlc3 - ESA) / (0.015 * D)
    ci = (hlc3 - esa) / (0.015 * d)

    # WT1: CI의 EMA(n2)
    wt1 = ci.ewm(span=n2, adjust=False).mean()

    # WT2: WT1의 SMA(signal_len) → 시그널선
    wt2 = wt1.rolling(window=signal_len).mean()

    df = df.copy()
    df['wt1'] = wt1
    df['wt2'] = wt2
    df['wt_diff'] = wt1 - wt2
    return df


# ─────────────────────────────────────────
# 3. 매매 신호 생성
# ─────────────────────────────────────────

def generate_signals(df,
                     ob1=60, ob2=53,    # 과매수 레벨 (배경색 표시용)
                     os1=-60, os2=-53): # 과매도 레벨 (배경색 표시용)
    """
    매수: WT1이 WT2를 골든크로스 (레벨 제한 없음)
    매도: WT1이 WT2를 데드크로스 (레벨 제한 없음)

    차트 분석:
    - 12월 구간에서 Buy→Sell→Buy→Sell 연속 발생
    - 과매도 구간이 아닌 중간 레벨에서도 신호 발생
    → 레벨 필터 없이 순수 교차만으로 신호 생성
    """
    df = df.copy()

    wt1 = df['wt1']
    wt2 = df['wt2']

    # 골든크로스: 전봉에서 wt1 <= wt2, 현재봉에서 wt1 > wt2
    cross_up   = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))
    # 데드크로스: 전봉에서 wt1 >= wt2, 현재봉에서 wt1 < wt2
    cross_down = (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))

    df['signal'] = 0
    df.loc[cross_up,   'signal'] = 1    # 매수
    df.loc[cross_down, 'signal'] = -1   # 매도

    # 레벨 정보는 시각화용으로만 보존
    df['ob1'] = ob1
    df['ob2'] = ob2
    df['os1'] = os1
    df['os2'] = os2

    return df


# ─────────────────────────────────────────
# 4. 백테스트 엔진
# ─────────────────────────────────────────

def backtest(df, initial_capital=10_000_000, fee_rate=0.0005):
    """
    단순 롱 온리 백테스트
    - 매수 신호: 포지션 진입 (전액)
    - 매도 신호: 포지션 청산
    - fee_rate: 수수료 (0.05% = 0.0005)
    """
    capital = initial_capital
    position = 0.0       # 보유 코인 수량
    entry_price = 0.0
    trades = []
    equity_curve = []

    for i, (idx, row) in enumerate(df.iterrows()):
        price = row['close']
        sig   = row['signal']

        # 매수: 포지션 없을 때만
        if sig == 1 and position == 0 and capital > 0:
            fee = capital * fee_rate
            position = (capital - fee) / price
            entry_price = price
            capital = 0
            trades.append({
                'date': idx, 'type': '매수', 'price': price,
                'amount': position, 'fee': fee, 'pnl': None
            })

        # 매도: 포지션 있을 때만
        elif sig == -1 and position > 0:
            proceeds = position * price
            fee = proceeds * fee_rate
            pnl = proceeds - fee - (position * entry_price)
            capital = proceeds - fee
            trades.append({
                'date': idx, 'type': '매도', 'price': price,
                'amount': position, 'fee': fee, 'pnl': pnl
            })
            position = 0
            entry_price = 0

        # 평가 자산 (포지션 보유 중이면 시가 평가)
        total = capital + position * price
        equity_curve.append({'date': idx, 'equity': total})

    # 미청산 포지션 종가로 강제 청산
    if position > 0:
        last_price = df['close'].iloc[-1]
        proceeds = position * last_price
        fee = proceeds * fee_rate
        capital = proceeds - fee
        trades.append({
            'date': df.index[-1], 'type': '강제청산', 'price': last_price,
            'amount': position, 'fee': fee,
            'pnl': proceeds - fee - (position * entry_price)
        })

    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity_curve).set_index('date')

    return trades_df, equity_df


# ─────────────────────────────────────────
# 5. 성과 분석
# ─────────────────────────────────────────

def calc_metrics(trades_df, equity_df, initial_capital):
    sells = trades_df[trades_df['type'].isin(['매도', '강제청산'])].copy()
    
    total_return  = (equity_df['equity'].iloc[-1] / initial_capital - 1) * 100
    n_trades      = len(sells)
    win_trades    = sells[sells['pnl'] > 0]
    lose_trades   = sells[sells['pnl'] <= 0]
    win_rate      = len(win_trades) / n_trades * 100 if n_trades else 0

    avg_win  = win_trades['pnl'].mean()  if len(win_trades)  else 0
    avg_loss = lose_trades['pnl'].mean() if len(lose_trades) else 0

    # 손익비 (RR): 평균 수익 / 평균 손실 절댓값
    rr_ratio = (avg_win / abs(avg_loss)) if avg_loss != 0 else float('inf')

    # 수익 팩터: 총수익합 / 총손실합 절댓값
    profit_factor = (win_trades['pnl'].sum() / abs(lose_trades['pnl'].sum())
                     if lose_trades['pnl'].sum() != 0 else float('inf'))

    # 거래당 기대값: 승률 * 평균수익 + 패율 * 평균손실
    lose_rate = 100 - win_rate
    expected_value = (win_rate / 100 * avg_win) + (lose_rate / 100 * avg_loss)

    # 최대 낙폭 (MDD)
    rolling_max = equity_df['equity'].cummax()
    drawdown    = (equity_df['equity'] - rolling_max) / rolling_max * 100
    mdd         = drawdown.min()

    # 바이앤홀드 수익률
    bah = (equity_df['equity'].iloc[-1] / equity_df['equity'].iloc[0] - 1) * 100

    print("=" * 55)
    print("           📊 백테스트 결과 요약")
    print("=" * 55)
    print(f"  총 수익률          : {total_return:+.2f}%")
    print(f"  최대 낙폭 (MDD)    : {mdd:.2f}%")
    print(f"  총 거래 횟수       : {n_trades}회")
    print(f"  승률               : {win_rate:.1f}%  ({len(win_trades)}승 {len(lose_trades)}패)")
    print(f"  평균 수익 (승)     : {avg_win:+,.0f}원")
    print(f"  평균 손실 (패)     : {avg_loss:+,.0f}원")
    print(f"  손익비 (RR)        : {rr_ratio:.2f}")
    print(f"  수익 팩터          : {profit_factor:.2f}")
    print(f"  거래당 기대값      : {expected_value:+,.0f}원")
    print("-" * 55)
    breakeven_wr = 1 / (1 + rr_ratio) * 100 if rr_ratio != float('inf') else 0
    print(f"  손익분기 승률      : {breakeven_wr:.1f}%  (현재 {win_rate:.1f}% {'✅ 초과' if win_rate > breakeven_wr else '❌ 미달'})")
    print("=" * 55)

    return {
        'total_return': total_return, 'mdd': mdd, 'n_trades': n_trades,
        'win_rate': win_rate, 'rr_ratio': rr_ratio,
        'profit_factor': profit_factor, 'expected_value': expected_value
    }


# ─────────────────────────────────────────
# 6. 시각화
# ─────────────────────────────────────────

def plot_results(df, trades_df, equity_df):
    fig, axes = plt.subplots(3, 1, figsize=(14, 12),
                              gridspec_kw={'height_ratios': [3, 2, 2]})
    fig.suptitle('12h Wave Strategy 백테스트', fontsize=15, fontweight='bold')

    # ── 차트 1: 가격 + 매수/매도 포인트
    ax1 = axes[0]
    ax1.plot(df.index, df['close'], color='#4A90D9', linewidth=1.2, label='종가')
    
    buys  = trades_df[trades_df['type'] == '매수']
    sells = trades_df[trades_df['type'].isin(['매도', '강제청산'])]
    
    ax1.scatter(buys['date'],  buys['price'],  marker='^', color='#E74C3C',
                s=80, zorder=5, label='매수')
    ax1.scatter(sells['date'], sells['price'], marker='v', color='#2ECC71',
                s=80, zorder=5, label='매도')
    ax1.set_ylabel('가격')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(alpha=0.3)

    # ── 차트 2: WaveTrend Oscillator
    ax2 = axes[1]
    ax2.plot(df.index, df['wt1'], color='#4A90D9', linewidth=1.2, label='WT1')
    ax2.plot(df.index, df['wt2'], color='#E67E22', linewidth=1.0,
             linestyle='--', label='WT2 (시그널)')

    # 골든크로스/데드크로스 영역 채우기
    ax2.fill_between(df.index, df['wt1'], df['wt2'],
                     where=df['wt1'] >= df['wt2'], alpha=0.2, color='#2ECC71', label='골든크로스 구간')
    ax2.fill_between(df.index, df['wt1'], df['wt2'],
                     where=df['wt1'] < df['wt2'],  alpha=0.2, color='#E74C3C', label='데드크로스 구간')

    # 과매수/과매도 레벨 수평선
    for level, color, ls, lw in [(60, '#E74C3C', '-', 1.0), (53, '#E74C3C', '--', 0.7),
                                  (-60, '#2ECC71', '-', 1.0), (-53, '#2ECC71', '--', 0.7)]:
        ax2.axhline(level, color=color, linewidth=lw, linestyle=ls, alpha=0.8)
        ax2.text(df.index[2], level + 1.5, str(level), fontsize=8, color=color, alpha=0.9)

    # 과매수/과매도 배경 음영 (차트와 동일하게)
    ax2.axhspan(53, 100, alpha=0.05, color='#E74C3C')
    ax2.axhspan(-100, -53, alpha=0.05, color='#2ECC71')

    ax2.axhline(0, color='gray', linewidth=0.5)
    ax2.set_ylim(-100, 100)
    ax2.set_ylabel('WaveTrend')
    ax2.legend(loc='upper left', fontsize=8, ncol=2)
    ax2.grid(alpha=0.3)

    # ── 차트 3: 자산 곡선
    ax3 = axes[2]
    ax3.plot(equity_df.index, equity_df['equity'] / 1e6,
             color='#9B59B6', linewidth=1.5, label='전략 자산')
    ax3.fill_between(equity_df.index, equity_df['equity'] / 1e6,
                     equity_df['equity'].iloc[0] / 1e6,
                     alpha=0.1, color='#9B59B6')
    ax3.set_ylabel('자산 (백만원)')
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(alpha=0.3)

    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    plt.tight_layout()
    # plt.savefig('/mnt/user-data/outputs/backtest_result.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("차트 저장: backtest_result.png")


# ─────────────────────────────────────────
# 7. 메인 실행
# ─────────────────────────────────────────

if __name__ == '__main__':

    # ── 데이터 로드 (원하는 방식 선택) ──
    # df = fetch_ohlcv_ccxt('BTC/USDT', '1d', limit=1000)  # ccxt 실시간
    # df = load_from_csv('btc_ohlcv.csv')                   # CSV 파일
    # df = make_sample_data()                                  # 샘플 데이터 (테스트용)
    df = make_real_data()                                  # 샘플 데이터 (테스트용)

    # ── 전략 파라미터 ──
    N1         = 10    # Channel Length
    N2         = 12    # Average Length
    SIGNAL_LEN = 3     # 시그널선 기간
    OB1, OB2   = 60, 53    # 과매수 레벨
    OS1, OS2   = -60, -53  # 과매도 레벨

    INITIAL_CAPITAL = 10_000_000  # 초기 자본 1천만원
    FEE_RATE        = 0.0005      # 수수료 0.05%

    # ── 실행 ──
    df = calc_wavetrend(df, N1, N2, SIGNAL_LEN)
    df = generate_signals(df, OB1, OB2, OS1, OS2)

    trades_df, equity_df = backtest(df, INITIAL_CAPITAL, FEE_RATE)

    print(f"\n📋 거래 내역 ({len(trades_df)}건):")
    print(trades_df.to_string(index=False))

    metrics = calc_metrics(trades_df, equity_df, INITIAL_CAPITAL)

    plot_results(df, trades_df, equity_df)
