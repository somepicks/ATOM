import sys
import ccxt
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from datetime import datetime


class CandlestickItem(pg.GraphicsObject):
    """캔들스틱 차트를 그리기 위한 커스텀 아이템"""

    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.picture)

        w = 0.3  # 캔들 너비
        for i, (t, open_, high, low, close) in enumerate(self.data):
            # 상승/하락에 따른 색상 결정
            if close >= open_:
                p.setPen(pg.mkPen('g'))
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))

            # 고가-저가 세로선
            p.drawLine(pg.QtCore.QPointF(i, low), pg.QtCore.QPointF(i, high))

            # 캔들 몸통
            if close != open_:
                p.drawRect(pg.QtCore.QRectF(i - w / 2, open_, w, close - open_))
            else:
                p.drawLine(pg.QtCore.QPointF(i - w / 2, open_), pg.QtCore.QPointF(i + w / 2, open_))

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return pg.QtCore.QRectF(self.picture.boundingRect())


class BinanceMultiChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('바이낸스 BTC/USDT 실시간 멀티차트')
        self.setGeometry(100, 100, 1600, 900)

        # CCXT 바이낸스 거래소 설정
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
        })

        # 데이터 저장용
        self.df = pd.DataFrame()
        self.max_candles = 100  # 표시할 최대 캔들 수

        # UI 설정
        self.setup_ui()

        # 초기 데이터 로드
        self.load_initial_data()

        # 타이머 설정 (1분마다 업데이트)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(60000)  # 60000ms = 1분

        # 실시간 느낌을 위한 빠른 업데이트 타이머 (10초마다)
        self.fast_timer = QTimer()
        self.fast_timer.timeout.connect(self.update_charts)
        self.fast_timer.start(10000)  # 10초마다 차트 갱신

    def setup_ui(self):
        """UI 레이아웃 설정"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout()
        central_widget.setLayout(layout)

        # PyQtGraph 설정
        pg.setConfigOptions(antialias=True)

        # 3행 4열 차트 생성
        self.plots = []
        titles = [
            ['캔들차트 + MA', 'MA(5)', 'MA(10)', 'MA(20)'],
            ['MA(50)', 'MA(100)', 'MA(200)', 'EMA(12)'],
            ['EMA(26)', 'SMA(7)', 'SMA(14)', 'SMA(21)']
        ]

        for row in range(3):
            for col in range(4):
                plot_widget = pg.PlotWidget(title=titles[row][col])
                plot_widget.showGrid(x=True, y=True, alpha=0.3)
                plot_widget.setLabel('left', 'Price (USDT)')
                plot_widget.setLabel('bottom', 'Time')
                layout.addWidget(plot_widget, row, col)
                self.plots.append(plot_widget)

    def load_initial_data(self):
        """초기 데이터 로드"""
        try:
            # 바이낸스에서 1분봉 데이터 가져오기
            ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', '1m', limit=self.max_candles)

            self.df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ms')

            # 이동평균선 계산
            self.calculate_moving_averages()

            # 차트 업데이트
            self.update_charts()

            print(f"초기 데이터 로드 완료: {len(self.df)}개 캔들")

        except Exception as e:
            print(f"데이터 로드 에러: {e}")

    def calculate_moving_averages(self):
        """다양한 이동평균선 계산"""
        periods = [5, 10, 20, 50, 100, 200, 7, 14, 21]

        for period in periods:
            self.df[f'MA{period}'] = self.df['close'].rolling(window=period).mean()

        # EMA (지수이동평균)
        self.df['EMA12'] = self.df['close'].ewm(span=12, adjust=False).mean()
        self.df['EMA26'] = self.df['close'].ewm(span=26, adjust=False).mean()

    def update_data(self):
        """새로운 데이터 가져오기"""
        try:
            ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', '1m', limit=5)
            new_df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')

            # 기존 데이터와 병합
            self.df = pd.concat([self.df, new_df]).drop_duplicates(subset='timestamp').tail(self.max_candles)
            self.df = self.df.reset_index(drop=True)

            # 이동평균선 재계산
            self.calculate_moving_averages()

            # 차트 업데이트
            self.update_charts()

            print(f"데이터 업데이트: {datetime.now()}")

        except Exception as e:
            print(f"데이터 업데이트 에러: {e}")

    def update_charts(self):
        """모든 차트 업데이트"""
        if self.df.empty:
            return

        x = np.arange(len(self.df))

        # 1행 1열: 캔들차트 + MA
        self.plots[0].clear()

        # 캔들스틱 데이터 준비
        candle_data = list(zip(x,
                               self.df['open'].values,
                               self.df['high'].values,
                               self.df['low'].values,
                               self.df['close'].values))

        candle_item = CandlestickItem(candle_data)
        self.plots[0].addItem(candle_item)

        # MA5, MA20 추가
        self.plots[0].plot(x, self.df['MA5'].values, pen=pg.mkPen('y', width=1), name='MA5')
        self.plots[0].plot(x, self.df['MA20'].values, pen=pg.mkPen('c', width=1), name='MA20')

        # 나머지 차트들: 각각의 이동평균선
        ma_configs = [
            ('MA5', 'y'),
            ('MA10', 'g'),
            ('MA20', 'c'),
            ('MA50', 'm'),
            ('MA100', 'r'),
            ('MA200', 'b'),
            ('EMA12', 'orange'),
            ('EMA26', 'purple'),
            ('MA7', 'lightblue'),
            ('MA14', 'pink'),
            ('MA21', 'lime')
        ]

        for i in range(1, 12):
            if i < len(self.plots):
                self.plots[i].clear()
                ma_name, color = ma_configs[i - 1]

                if ma_name in self.df.columns:
                    valid_data = self.df[ma_name].dropna()
                    if len(valid_data) > 0:
                        valid_x = x[-len(valid_data):]
                        self.plots[i].plot(valid_x, valid_data.values,
                                           pen=pg.mkPen(color, width=2))

                        # 현재가와 MA 표시
                        if len(self.df) > 0:
                            current_price = self.df['close'].iloc[-1]
                            current_ma = self.df[ma_name].iloc[-1] if not pd.isna(self.df[ma_name].iloc[-1]) else 0

                            text = f"현재가: ${current_price:.2f}\n{ma_name}: ${current_ma:.2f}"
                            text_item = pg.TextItem(text, color='w')
                            text_item.setPos(valid_x[0], valid_data.values[0])
                            self.plots[i].addItem(text_item)


def main():
    app = QApplication(sys.argv)
    window = BinanceMultiChart()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()