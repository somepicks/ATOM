"""
Bands Arrow Strategy Backtest
파라미터: (5, 10) → 단기 EMA 5, 장기 EMA 10

전략 로직 (차트 분석 기반):
- EMA5가 EMA10을 상향 돌파(골든크로스) → long 진입 (숏 포지션 있으면 청산 후 롱)
- EMA5가 EMA10을 하향 돌파(데드크로스) → short 진입 (롱 포지션 있으면 청산 후 숏)
- 반대 신호 발생 시 즉시 반전 (항상 포지션 유지)
- 손익은 % 기준으로 표시
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams

# 한글 폰트 설정
rcParams['font.family'] = 'Malgun Gothic'  # Windows
# rcParams['font.family'] = 'AppleGothic'  # Mac
rcParams['axes.unicode_minus'] = False


# ─────────────────────────────────────────
# 1. 데이터 로드
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
    df = pd.read_csv(filepath, parse_dates=['timestamp'], index_col='timestamp')
    return df


def make_sample_data():
    """샘플 데이터 생성 (테스트용)"""
    np.random.seed(42)
    dates = pd.date_range('2021-01-01', '2022-06-01', freq='D')
    n = len(dates)
    close = [40000]
    for _ in range(n - 1):
        close.append(close[-1] * (1 + np.random.normal(0, 0.025)))
    close = np.array(close)
    df = pd.DataFrame({
        'open':   close * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high':   close * (1 + np.abs(np.random.normal(0, 0.015, n))),
        'low':    close * (1 - np.abs(np.random.normal(0, 0.015, n))),
        'close':  close,
        'volume': np.random.uniform(1e9, 5e9, n),
    }, index=dates)
    return df
def make_real_data():
    import ccxt
    ohlcv = ccxt.binance().fetch_ohlcv('BTC/USDT', timeframe='1d', limit=10000)
    df = pd.DataFrame(ohlcv, columns=['날짜', 'open', 'high', 'low', 'close', 'volume'])
    df['날짜'] = pd.to_datetime(df['날짜'], utc=True, unit='ms')
    df['날짜'] = df['날짜'].dt.tz_convert("Asia/Seoul")
    df['날짜'] = df['날짜'].dt.tz_localize(None)
    df.set_index('날짜', inplace=True)
    return df

# ─────────────────────────────────────────
# 2. EMA 밴드 계산
# ─────────────────────────────────────────

def calc_bands(df, fast=5, slow=10):
    """
    단기/장기 EMA 계산
    fast: 단기 EMA 기간 (기본 5)
    slow: 장기 EMA 기간 (기본 10)
    """
    df = df.copy()
    df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
    df['band_diff'] = df['ema_fast'] - df['ema_slow']
    return df


# ─────────────────────────────────────────
# 3. 매매 신호 생성
# ─────────────────────────────────────────

def generate_signals(df):
    """
    골든크로스 → long (1)
    데드크로스 → short (-1)
    레벨 제한 없이 교차 즉시 신호
    """
    df = df.copy()

    fast = df['ema_fast']
    slow = df['ema_slow']

    # 골든크로스: 전봉 fast <= slow, 현재봉 fast > slow
    golden = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    # 데드크로스: 전봉 fast >= slow, 현재봉 fast < slow
    dead   = (fast < slow) & (fast.shift(1) >= slow.shift(1))

    df['signal'] = 0
    df.loc[golden, 'signal'] = 1    # long
    df.loc[dead,   'signal'] = -1   # short

    return df


# ─────────────────────────────────────────
# 4. 백테스트 엔진 (롱/숏 양방향)
# ─────────────────────────────────────────

def backtest(df, initial_capital=10_000_000, fee_rate=0.0005):
    """
    롱/숏 양방향 백테스트
    - 반대 신호 발생 시 현재 포지션 청산 후 즉시 반전 진입
    - position: 1=롱, -1=숏, 0=없음
    - 숏은 차입 매도 후 하락분 이익으로 계산
    """
    capital     = initial_capital
    position    = 0      # 1: 롱, -1: 숏, 0: 없음
    entry_price = 0.0
    qty         = 0.0    # 보유 수량 (롱) 또는 차입 수량 (숏)
    trades      = []
    equity_curve = []

    for idx, row in df.iterrows():
        price = row['close']
        sig   = row['signal']

        # ── 청산 처리 ──
        if sig != 0 and position != 0 and sig != position:
            if position == 1:   # 롱 청산
                proceeds = qty * price
                fee = proceeds * fee_rate
                pnl = proceeds - fee - (qty * entry_price)
                pnl_pct = pnl / (qty * entry_price) * 100
                capital = qty * entry_price + pnl  # 원금 + 손익
                trades.append({
                    'date': idx, 'type': '롱청산', 'price': price,
                    'pnl': pnl, 'pnl_pct': pnl_pct, 'fee': fee
                })
            elif position == -1:  # 숏 청산
                # 숏 손익: 진입가 - 청산가 (하락하면 이익)
                pnl_per_unit = entry_price - price
                pnl = pnl_per_unit * qty
                fee = qty * price * fee_rate
                pnl_pct = pnl_per_unit / entry_price * 100
                capital = capital + pnl - fee
                trades.append({
                    'date': idx, 'type': '숏청산', 'price': price,
                    'pnl': pnl, 'pnl_pct': pnl_pct, 'fee': fee
                })
            position    = 0
            entry_price = 0.0
            qty         = 0.0

        # ── 진입 처리 ──
        if sig == 1 and position == 0:    # 롱 진입
            fee = capital * fee_rate
            qty = (capital - fee) / price
            entry_price = price
            position = 1
            trades.append({
                'date': idx, 'type': '롱진입', 'price': price,
                'pnl': None, 'pnl_pct': None, 'fee': fee
            })

        elif sig == -1 and position == 0:  # 숏 진입
            fee = capital * fee_rate
            qty = (capital - fee) / price  # 차입 수량
            entry_price = price
            position = -1
            trades.append({
                'date': idx, 'type': '숏진입', 'price': price,
                'pnl': None, 'pnl_pct': None, 'fee': fee
            })

        # ── 평가 자산 계산 ──
        if position == 1:
            total = qty * price  # 롱: 시가 평가
        elif position == -1:
            unrealized = (entry_price - price) * qty
            total = capital + unrealized  # 숏: 미실현손익 반영
        else:
            total = capital

        equity_curve.append({'date': idx, 'equity': total})

    # ── 미청산 포지션 강제 청산 ──
    last_price = df['close'].iloc[-1]
    if position == 1:
        pnl = (last_price - entry_price) * qty
        fee = qty * last_price * fee_rate
        capital = qty * entry_price + pnl - fee
        trades.append({
            'date': df.index[-1], 'type': '강제청산(롱)', 'price': last_price,
            'pnl': pnl - fee, 'pnl_pct': (last_price - entry_price) / entry_price * 100,
            'fee': fee
        })
    elif position == -1:
        pnl = (entry_price - last_price) * qty
        fee = qty * last_price * fee_rate
        capital = capital + pnl - fee
        trades.append({
            'date': df.index[-1], 'type': '강제청산(숏)', 'price': last_price,
            'pnl': pnl - fee, 'pnl_pct': (entry_price - last_price) / entry_price * 100,
            'fee': fee
        })

    trades_df    = pd.DataFrame(trades)
    equity_df    = pd.DataFrame(equity_curve).set_index('date')

    return trades_df, equity_df


# ─────────────────────────────────────────
# 5. 성과 분석
# ─────────────────────────────────────────

def calc_metrics(trades_df, equity_df, initial_capital):
    closes = trades_df[trades_df['type'].isin([
        '롱청산', '숏청산', '강제청산(롱)', '강제청산(숏)'
    ])].copy()

    total_return = (equity_df['equity'].iloc[-1] / initial_capital - 1) * 100
    n_trades     = len(closes)
    win_trades   = closes[closes['pnl'] > 0]
    lose_trades  = closes[closes['pnl'] <= 0]
    win_rate     = len(win_trades) / n_trades * 100 if n_trades else 0

    avg_win      = win_trades['pnl'].mean()  if len(win_trades)  else 0
    avg_loss     = lose_trades['pnl'].mean() if len(lose_trades) else 0

    # 손익비
    rr_ratio     = (avg_win / abs(avg_loss)) if avg_loss != 0 else float('inf')

    # 수익 팩터
    profit_factor = (win_trades['pnl'].sum() / abs(lose_trades['pnl'].sum())
                     if lose_trades['pnl'].sum() != 0 else float('inf'))

    # 기대값
    lose_rate      = 100 - win_rate
    expected_value = (win_rate / 100 * avg_win) + (lose_rate / 100 * avg_loss)

    # MDD
    rolling_max = equity_df['equity'].cummax()
    drawdown    = (equity_df['equity'] - rolling_max) / rolling_max * 100
    mdd         = drawdown.min()

    # 롱/숏 분리 분석
    long_closes  = closes[closes['type'].isin(['롱청산', '강제청산(롱)'])]
    short_closes = closes[closes['type'].isin(['숏청산', '강제청산(숏)'])]

    print("=" * 55)
    print("        📊 Bands Arrow 백테스트 결과 요약")
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
    print("-" * 55)
    if len(long_closes):
        lw = long_closes[long_closes['pnl'] > 0]
        print(f"  롱 거래            : {len(long_closes)}회  승률 {len(lw)/len(long_closes)*100:.1f}%  합계 {long_closes['pnl'].sum():+,.0f}원")
    if len(short_closes):
        sw = short_closes[short_closes['pnl'] > 0]
        print(f"  숏 거래            : {len(short_closes)}회  승률 {len(sw)/len(short_closes)*100:.1f}%  합계 {short_closes['pnl'].sum():+,.0f}원")
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
                              gridspec_kw={'height_ratios': [3, 1, 2]})
    fig.suptitle('Bands Arrow Strategy (5, 10) 백테스트', fontsize=15, fontweight='bold')

    # ── 차트 1: 가격 + EMA 밴드 + 매매 포인트
    ax1 = axes[0]
    ax1.plot(df.index, df['close'],    color='#B0BEC5', linewidth=0.8, label='종가', alpha=0.7)
    ax1.plot(df.index, df['ema_fast'], color='#4A90D9', linewidth=1.5, label=f'EMA Fast(5)')
    ax1.plot(df.index, df['ema_slow'], color='#E67E22', linewidth=1.5, label=f'EMA Slow(10)')

    # EMA 사이 채우기
    ax1.fill_between(df.index, df['ema_fast'], df['ema_slow'],
                     where=df['ema_fast'] >= df['ema_slow'],
                     alpha=0.12, color='#2ECC71', label='롱 구간')
    ax1.fill_between(df.index, df['ema_fast'], df['ema_slow'],
                     where=df['ema_fast'] < df['ema_slow'],
                     alpha=0.12, color='#E74C3C', label='숏 구간')

    # 매매 포인트
    long_entry  = trades_df[trades_df['type'] == '롱진입']
    short_entry = trades_df[trades_df['type'] == '숏진입']
    long_close  = trades_df[trades_df['type'].isin(['롱청산', '강제청산(롱)'])]
    short_close = trades_df[trades_df['type'].isin(['숏청산', '강제청산(숏)'])]

    ax1.scatter(long_entry['date'],  long_entry['price'],  marker='^', color='#2ECC71', s=90, zorder=5, label='롱진입')
    ax1.scatter(short_entry['date'], short_entry['price'], marker='v', color='#E74C3C', s=90, zorder=5, label='숏진입')
    ax1.scatter(long_close['date'],  long_close['price'],  marker='x', color='#27AE60', s=60, zorder=5)
    ax1.scatter(short_close['date'], short_close['price'], marker='x', color='#C0392B', s=60, zorder=5)

    # 손익 레이블 표시
    closes = trades_df[trades_df['pnl_pct'].notna()]
    for _, row in closes.iterrows():
        color = '#2ECC71' if row['pnl'] > 0 else '#E74C3C'
        label = f"{'+' if row['pnl_pct'] > 0 else ''}{row['pnl_pct']:.1f}%"
        ax1.annotate(label, xy=(row['date'], row['price']),
                     xytext=(0, 12), textcoords='offset points',
                     fontsize=7, color=color, ha='center')

    ax1.set_ylabel('가격 (USDT)')
    ax1.legend(loc='upper left', fontsize=8, ncol=3)
    ax1.grid(alpha=0.3)

    # ── 차트 2: EMA 차이 (밴드 폭)
    ax2 = axes[1]
    band_diff = df['ema_fast'] - df['ema_slow']
    ax2.bar(df.index, band_diff,
            color=np.where(band_diff >= 0, '#2ECC71', '#E74C3C'), alpha=0.7, width=0.8)
    ax2.axhline(0, color='gray', linewidth=0.8)
    ax2.set_ylabel('EMA 차이')
    ax2.grid(alpha=0.3)

    # ── 차트 3: 자산 곡선
    ax3 = axes[2]
    ax3.plot(equity_df.index, equity_df['equity'] / 1e6,
             color='#9B59B6', linewidth=1.5, label='전략 자산')
    ax3.axhline(equity_df['equity'].iloc[0] / 1e6,
                color='gray', linewidth=0.8, linestyle='--', label='초기 자본')
    ax3.fill_between(equity_df.index,
                     equity_df['equity'] / 1e6,
                     equity_df['equity'].iloc[0] / 1e6,
                     where=equity_df['equity'] >= equity_df['equity'].iloc[0],
                     alpha=0.15, color='#2ECC71')
    ax3.fill_between(equity_df.index,
                     equity_df['equity'] / 1e6,
                     equity_df['equity'].iloc[0] / 1e6,
                     where=equity_df['equity'] < equity_df['equity'].iloc[0],
                     alpha=0.15, color='#E74C3C')
    ax3.set_ylabel('자산 (백만원)')
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(alpha=0.3)

    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    plt.tight_layout()
    # plt.savefig('/mnt/user-data/outputs/bands_arrow_result.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("차트 저장: bands_arrow_result.png")


# ─────────────────────────────────────────
# 7. 메인 실행
# ─────────────────────────────────────────

if __name__ == '__main__':

    # ── 데이터 로드 (원하는 방식 선택) ──
    # df = fetch_ohlcv_ccxt('BTC/USDT', '1d', limit=1000)  # ccxt 실시간
    # df = load_from_csv('btc_ohlcv.csv')                   # CSV 파일
    df = make_sample_data()                                  # 샘플 데이터 (테스트용)
    df = make_real_data()                                  # 샘플 데이터 (테스트용)

    # ── 전략 파라미터 ──
    FAST = 5    # 단기 EMA
    SLOW = 10   # 장기 EMA

    INITIAL_CAPITAL = 10_000_000  # 초기 자본 1천만원
    FEE_RATE        = 0.0005      # 수수료 0.05%

    # ── 실행 ──
    df = calc_bands(df, FAST, SLOW)
    df = generate_signals(df)

    trades_df, equity_df = backtest(df, INITIAL_CAPITAL, FEE_RATE)

    print(f"\n📋 거래 내역 ({len(trades_df)}건):")
    print(trades_df.to_string(index=False))

    metrics = calc_metrics(trades_df, equity_df, INITIAL_CAPITAL)

    plot_results(df, trades_df, equity_df)
