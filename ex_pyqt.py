import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class VolumeSA:
    def __init__(self):
        # Volume settings
        self.smoothing_type = "SMA"  # SMA, EMA, HMA, RMA, WMA
        self.vol_sma_length = 20
        self.vol_threshold = 70  # High volume threshold %
        self.vol_a_threshold = 70  # High active volume threshold %
        self.use_relative_volume = False

        # Visual settings
        self.buy_vol_color = 'teal'
        self.buy_vol_active_color = 'green'
        self.sell_vol_color = 'maroon'
        self.sell_vol_active_color = 'red'
        self.total_vol_color = 'gray'

        # Initialize exchange
        self.exchange = ccxt.bybit({
            'sandbox': False,  # Set to True for testnet
        })

    def fetch_data(self, symbol='BTC/USDT', timeframe='4h', limit=500):
        """Fetch OHLCV data from Bybit"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def smooth_data(self, data, length, method='SMA'):
        """Apply smoothing to data"""
        if method == 'SMA':
            return data.rolling(window=length).mean()
        elif method == 'EMA':
            return data.ewm(span=length).mean()
        elif method == 'RMA':
            return data.ewm(alpha=1 / length).mean()
        elif method == 'WMA':
            weights = np.arange(1, length + 1)
            return data.rolling(length).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
        elif method == 'HMA':
            half_length = int(length / 2)
            sqrt_length = int(np.sqrt(length))
            wma_half = data.rolling(half_length).apply(
                lambda x: np.dot(x, np.arange(1, half_length + 1)) / np.sum(np.arange(1, half_length + 1)), raw=True)
            wma_full = data.rolling(length).apply(
                lambda x: np.dot(x, np.arange(1, length + 1)) / np.sum(np.arange(1, length + 1)), raw=True)
            hull_ma_input = 2 * wma_half - wma_full
            return hull_ma_input.rolling(sqrt_length).apply(
                lambda x: np.dot(x, np.arange(1, sqrt_length + 1)) / np.sum(np.arange(1, sqrt_length + 1)), raw=True)
        else:
            return data.rolling(window=length).mean()

    def calculate_volume_analysis(self, df):
        """Calculate volume strength analysis"""
        # Determine buy/sell volume based on close direction
        df['price_direction'] = df['close'] >= df['close'].shift(1)
        df['buy_volume'] = np.where(df['price_direction'], df['volume'], 0)
        df['sell_volume'] = np.where(~df['price_direction'], df['volume'], 0)

        # Active volumes (volume higher than previous)
        df['volume_increased'] = df['volume'] > df['volume'].shift(1)
        df['buy_volume_active'] = np.where(df['price_direction'] & df['volume_increased'], df['volume'], 0)
        df['sell_volume_active'] = np.where(~df['price_direction'] & df['volume_increased'], df['volume'], 0)

        # Total volumes
        df['total_buy_vol'] = df['buy_volume']
        df['total_sell_vol'] = df['sell_volume']
        df['total_vol'] = df['total_buy_vol'] + df['total_sell_vol']

        df['total_buy_vol_active'] = df['buy_volume_active']
        df['total_sell_vol_active'] = df['sell_volume_active']
        df['total_vol_active'] = df['total_buy_vol_active'] + df['total_sell_vol_active']

        # Volume moving average
        df['vol_sma'] = self.smooth_data(df['total_vol'], self.vol_sma_length, self.smoothing_type)

        # Relative volumes if enabled
        if self.use_relative_volume:
            df['total_buy_vol_rel'] = df['total_buy_vol'] / df['vol_sma']
            df['total_sell_vol_rel'] = df['total_sell_vol'] / df['vol_sma']
            df['total_vol_rel'] = df['total_buy_vol_rel'] + df['total_sell_vol_rel']

            df['total_buy_vol_active_rel'] = df['total_buy_vol_active'] / df['vol_sma']
            df['total_sell_vol_active_rel'] = df['total_sell_vol_active'] / df['vol_sma']
            df['total_vol_active_rel'] = df['total_buy_vol_active_rel'] + df['total_sell_vol_active_rel']

            # Use relative volumes
            df['final_buy_vol'] = df['total_buy_vol_rel']
            df['final_sell_vol'] = df['total_sell_vol_rel']
            df['final_total_vol'] = df['total_vol_rel']
            df['final_buy_vol_active'] = df['total_buy_vol_active_rel']
            df['final_sell_vol_active'] = df['total_sell_vol_active_rel']
            df['final_total_vol_active'] = df['total_vol_active_rel']
        else:
            # Use absolute volumes
            df['final_buy_vol'] = df['total_buy_vol']
            df['final_sell_vol'] = df['total_sell_vol']
            df['final_total_vol'] = df['total_vol']
            df['final_buy_vol_active'] = df['total_buy_vol_active']
            df['final_sell_vol_active'] = df['total_sell_vol_active']
            df['final_total_vol_active'] = df['total_vol_active']

        # Calculate percentages
        df['buy_vol_perc'] = df['final_buy_vol'] / df['final_total_vol'] * 100
        df['sell_vol_perc'] = df['final_sell_vol'] / df['final_total_vol'] * 100

        # Avoid division by zero for active volumes
        df['buy_vol_perc_active'] = np.where(
            df['final_total_vol_active'] > 0,
            df['final_buy_vol_active'] / df['final_total_vol_active'] * 100,
            0
        )
        df['sell_vol_perc_active'] = np.where(
            df['final_total_vol_active'] > 0,
            df['final_sell_vol_active'] / df['final_total_vol_active'] * 100,
            0
        )

        # High volume conditions
        df['high_buy_vol'] = df['buy_vol_perc'] >= self.vol_threshold
        df['high_sell_vol'] = df['sell_vol_perc'] >= self.vol_threshold
        df['high_buy_vol_active'] = df['buy_vol_perc_active'] >= self.vol_a_threshold
        df['high_sell_vol_active'] = df['sell_vol_perc_active'] >= self.vol_a_threshold

        # Volume-active volume divergence
        df['vol_divergence'] = (
                ((df['buy_vol_perc_active'] > df['sell_vol_perc_active']) & (
                            df['buy_vol_perc'] < df['sell_vol_perc'])) |
                ((df['buy_vol_perc_active'] < df['sell_vol_perc_active']) & (df['buy_vol_perc'] > df['sell_vol_perc']))
        )

        # Dominant volumes
        df['dominant_vol'] = np.where(df['final_buy_vol'] >= df['final_sell_vol'], df['final_buy_vol'],
                                      df['final_sell_vol'])
        df['dominant_vol_active'] = np.where(df['final_buy_vol_active'] >= df['final_sell_vol_active'],
                                             df['final_buy_vol_active'], df['final_sell_vol_active'])

        return df

    def plot_analysis(self, df, symbol='BTC/USDT', days_back=30):
        """Plot the volume strength analysis"""
        # Filter data for the specified period
        end_date = df.index[-1]
        start_date = end_date - timedelta(days=days_back)
        df_plot = df[df.index >= start_date].copy()

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12), sharex=True)

        # Plot 1: Price with anomaly markers
        ax1.plot(df_plot.index, df_plot['close'], 'b-', linewidth=0.5, label='Close Price')

        # Mark high volume anomalies on price chart
        high_buy_idx = df_plot[df_plot['high_buy_vol']].index
        high_sell_idx = df_plot[df_plot['high_sell_vol']].index
        high_buy_active_idx = df_plot[df_plot['high_buy_vol_active']].index
        high_sell_active_idx = df_plot[df_plot['high_sell_vol_active']].index
        divergence_idx = df_plot[df_plot['vol_divergence']].index

        if len(high_buy_idx) > 0:
            ax1.scatter(high_buy_idx, df_plot.loc[high_buy_idx, 'close'],
                        color=self.buy_vol_color, marker='^', s=50, alpha=0.7, label='High Buy Volume')

        if len(high_sell_idx) > 0:
            ax1.scatter(high_sell_idx, df_plot.loc[high_sell_idx, 'close'],
                        color=self.sell_vol_color, marker='v', s=50, alpha=0.7, label='High Sell Volume')

        if len(high_buy_active_idx) > 0:
            ax1.scatter(high_buy_active_idx, df_plot.loc[high_buy_active_idx, 'close'],
                        color=self.buy_vol_active_color, marker='^', s=30, alpha=0.8, label='High Active Buy')

        if len(high_sell_active_idx) > 0:
            ax1.scatter(high_sell_active_idx, df_plot.loc[high_sell_active_idx, 'close'],
                        color=self.sell_vol_active_color, marker='v', s=30, alpha=0.8, label='High Active Sell')

        if len(divergence_idx) > 0:
            ax1.scatter(divergence_idx, df_plot.loc[divergence_idx, 'close'],
                        color='fuchsia', marker='x', s=40, alpha=0.8, label='Volume Divergence')

        ax1.set_ylabel('Price (USDT)')
        ax1.set_title(f'{symbol} - Volume Strength Analysis (4H)', fontsize=14, fontweight='bold')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Volume bars with buy/sell breakdown
        ax2.bar(df_plot.index, df_plot['final_total_vol'], color=self.total_vol_color, alpha=0.3, label='Total Volume')
        ax2.bar(df_plot.index, df_plot['dominant_vol'],
                color=[self.buy_vol_color if buy >= sell else self.sell_vol_color
                       for buy, sell in zip(df_plot['final_buy_vol'], df_plot['final_sell_vol'])],
                alpha=0.7, label='Dominant Volume')
        ax2.bar(df_plot.index, df_plot['dominant_vol_active'],
                color=[self.buy_vol_active_color if buy >= sell else self.sell_vol_active_color
                       for buy, sell in zip(df_plot['final_buy_vol_active'], df_plot['final_sell_vol_active'])],
                alpha=0.9, label='Dominant Active Volume')

        # Volume moving average
        if not self.use_relative_volume:
            ax2.plot(df_plot.index, df_plot['vol_sma'], color='orange', linewidth=2, label='Volume MA')
        else:
            ax2.axhline(y=1, color='orange', linewidth=2, label='Relative Volume = 1')

        ax2.set_ylabel('Volume')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Volume percentages
        ax3.bar(df_plot.index, df_plot['buy_vol_perc'], color=self.buy_vol_color, alpha=0.6, label='Buy Volume %')
        ax3.bar(df_plot.index, -df_plot['sell_vol_perc'], color=self.sell_vol_color, alpha=0.6, label='Sell Volume %')
        ax3.bar(df_plot.index, df_plot['buy_vol_perc_active'], color=self.buy_vol_active_color, alpha=0.8,
                label='Active Buy %')
        ax3.bar(df_plot.index, -df_plot['sell_vol_perc_active'], color=self.sell_vol_active_color, alpha=0.8,
                label='Active Sell %')

        # Threshold lines
        ax3.axhline(y=self.vol_threshold, color='red', linestyle='--', alpha=0.7,
                    label=f'Volume Threshold ({self.vol_threshold}%)')
        ax3.axhline(y=-self.vol_threshold, color='red', linestyle='--', alpha=0.7)
        ax3.axhline(y=self.vol_a_threshold, color='orange', linestyle=':', alpha=0.7,
                    label=f'Active Threshold ({self.vol_a_threshold}%)')
        ax3.axhline(y=-self.vol_a_threshold, color='orange', linestyle=':', alpha=0.7)
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)

        ax3.set_ylabel('Volume %')
        ax3.set_xlabel('Date')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.grid(True, alpha=0.3)

        # Format x-axis
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        plt.show()

    def get_latest_signals(self, df, n=10):
        """Get the latest volume signals"""
        latest_data = df.tail(n).copy()

        signals = []
        for idx, row in latest_data.iterrows():
            signal_list = []

            if row['high_buy_vol']:
                signal_list.append('High Buy Volume')
            if row['high_sell_vol']:
                signal_list.append('High Sell Volume')
            if row['high_buy_vol_active']:
                signal_list.append('High Active Buy')
            if row['high_sell_vol_active']:
                signal_list.append('High Active Sell')
            if row['vol_divergence']:
                signal_list.append('Volume Divergence')

            signals.append({
                'datetime': idx,
                'close': row['close'],
                'buy_vol_perc': round(row['buy_vol_perc'], 1),
                'sell_vol_perc': round(row['sell_vol_perc'], 1),
                'buy_vol_active_perc': round(row['buy_vol_perc_active'], 1),
                'sell_vol_active_perc': round(row['sell_vol_perc_active'], 1),
                'signals': ', '.join(signal_list) if signal_list else 'No signals'
            })

        return signals


# Usage example
if __name__ == "__main__":
    # Initialize the VSA analyzer
    vsa = VolumeSA()

    # You can adjust these parameters
    vsa.vol_threshold = 70
    vsa.vol_a_threshold = 70
    vsa.use_relative_volume = False  # Set to True for relative volume analysis

    print("Fetching BTC/USDT 4H data from Bybit...")
    df = vsa.fetch_data('BTC/USDT', '4h', 500)

    if df is not None:
        print("Calculating volume strength analysis...")
        df_analyzed = vsa.calculate_volume_analysis(df)

        print("\nLatest 5 signals:")
        latest_signals = vsa.get_latest_signals(df_analyzed, 5)
        for signal in latest_signals:
            print(f"{signal['datetime'].strftime('%Y-%m-%d %H:%M')} | Price: ${signal['close']:,.0f} | "
                  f"Buy: {signal['buy_vol_perc']}% | Sell: {signal['sell_vol_perc']}% | "
                  f"Active Buy: {signal['buy_vol_active_perc']}% | Active Sell: {signal['sell_vol_active_perc']}% | "
                  f"Signals: {signal['signals']}")

        print("\nGenerating plots...")
        vsa.plot_analysis(df_analyzed, 'BTC/USDT', days_back=30)

        # Print summary statistics
        print(f"\nSummary (Last 30 days):")
        recent_data = df_analyzed.tail(180)  # Approximately 30 days of 4H data
        print(f"High Buy Volume signals: {recent_data['high_buy_vol'].sum()}")
        print(f"High Sell Volume signals: {recent_data['high_sell_vol'].sum()}")
        print(f"High Active Buy signals: {recent_data['high_buy_vol_active'].sum()}")
        print(f"High Active Sell signals: {recent_data['high_sell_vol_active'].sum()}")
        print(f"Volume Divergence signals: {recent_data['vol_divergence'].sum()}")

    else:
        print("Failed to fetch data. Please check your connection and try again.")