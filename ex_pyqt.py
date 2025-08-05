import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pandas as pd
import numpy as np
from datetime import datetime
import sys

# PyQt 애플리케이션 설정
app = QtGui.QApplication([])

# 한글 폰트 설정
font = QtGui.QFont('Malgun Gothic', 10)
app.setFont(font)

# 예시 데이터 리스트
major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
mid_coins = ['SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'MATICUSDT']
small_coins = ['DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT', 'FLOKIUSDT']


class FundingRateViewer:
    def __init__(self, df, coin_lists, titles):
        self.df = df
        self.coin_lists = coin_lists
        self.titles = titles
        self.colors = [
            (255, 0, 0),  # 빨강
            (0, 255, 0),  # 초록
            (0, 0, 255),  # 파랑
            (255, 255, 0),  # 노랑
            (255, 0, 255),  # 마젠타
            (0, 255, 255),  # 시안
            (255, 128, 0),  # 주황
            (128, 0, 255),  # 보라
        ]
        self.setup_ui()

    def setup_ui(self):
        # 메인 윈도우 생성
        self.win = pg.GraphicsWindow(title="암호화폐 펀딩비 분석")
        self.win.resize(1500, 600)
        self.win.setWindowTitle('암호화폐 펀딩비 분석')

        # 3개 플롯 생성 (나란히 배치)
        self.plots = []
        for i, title in enumerate(self.titles):
            if i > 0:
                self.win.nextColumn()

            plot = self.win.addPlot(title=title)
            plot.setLabel('left', '펀딩비 (%)')
            plot.setLabel('bottom', '시간')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.addLine(y=0, pen=pg.mkPen('white', width=2))  # 0선 추가

            # 범례 추가
            plot.addLegend()

            self.plots.append(plot)

        self.plot_data()

    def plot_data(self):
        # 시간 축을 숫자로 변환 (pyqtgraph용)
        time_axis = np.arange(len(self.df.index))

        for i, (coin_list, plot) in enumerate(zip(self.coin_lists, self.plots)):
            # 해당 리스트의 티커들이 데이터프레임에 있는지 확인
            available_coins = [coin for coin in coin_list if coin in self.df.columns]

            if not available_coins:
                # 데이터가 없을 때 텍스트 표시
                text = pg.TextItem('데이터 없음', anchor=(0.5, 0.5))
                plot.addItem(text)
                text.setPos(len(time_axis) // 2, 0)
                continue

            # 각 코인별로 라인 그리기
            for j, coin in enumerate(available_coins):
                if coin in self.df.columns:
                    data = self.df[coin].values

                    # NaN 값 처리
                    valid_mask = ~np.isnan(data)
                    if valid_mask.any():
                        color = self.colors[j % len(self.colors)]

                        # 선 그리기
                        plot.plot(time_axis[valid_mask], data[valid_mask],
                                  pen=pg.mkPen(color=color, width=2),
                                  name=coin)

    def show(self):
        self.win.show()
        return self.win


# 고급 버전 - 실시간 업데이트와 상호작용 기능
class InteractiveFundingRateViewer:
    def __init__(self, df, coin_lists, titles):
        self.df = df
        self.coin_lists = coin_lists
        self.titles = titles
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255)
        ]
        self.setup_ui()

    def setup_ui(self):
        # 메인 위젯 생성
        self.widget = QtGui.QWidget()
        self.widget.setWindowTitle('상호작용 암호화폐 펀딩비 분석')
        self.widget.resize(1600, 800)

        layout = QtGui.QVBoxLayout()
        self.widget.setLayout(layout)

        # 컨트롤 패널
        control_layout = QtGui.QHBoxLayout()

        # 시간 범위 선택
        self.time_range_combo = QtGui.QComboBox()
        self.time_range_combo.addItems(['전체', '최근 24시간', '최근 7일', '최근 30일'])
        self.time_range_combo.currentTextChanged.connect(self.update_time_range)
        control_layout.addWidget(QtGui.QLabel('시간 범위:'))
        control_layout.addWidget(self.time_range_combo)

        # 평활화 옵션
        self.smooth_check = QtGui.QCheckBox('평활화')
        self.smooth_check.stateChanged.connect(self.update_plots)
        control_layout.addWidget(self.smooth_check)

        # 통계 표시 버튼
        self.stats_btn = QtGui.QPushButton('통계 표시')
        self.stats_btn.clicked.connect(self.show_statistics)
        control_layout.addWidget(self.stats_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 그래프 영역
        self.graphics_widget = pg.GraphicsWindow()
        layout.addWidget(self.graphics_widget)

        # 3개 플롯 생성
        self.plots = []
        for i, title in enumerate(self.titles):
            if i > 0:
                self.graphics_widget.nextColumn()

            plot = self.graphics_widget.addPlot(title=title)
            plot.setLabel('left', '펀딩비 (%)')
            plot.setLabel('bottom', '시간')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.addLine(y=0, pen=pg.mkPen('white', width=2))
            plot.addLegend()

            # 마우스 이벤트 연결
            plot.scene().sigMouseClicked.connect(self.on_plot_clicked)

            self.plots.append(plot)

        # 상태 표시줄
        self.status_label = QtGui.QLabel('준비')
        layout.addWidget(self.status_label)

        self.plot_data()

    def plot_data(self):
        # 기존 플롯 클리어
        for plot in self.plots:
            plot.clear()
            plot.addLine(y=0, pen=pg.mkPen('white', width=2))

        time_axis = np.arange(len(self.df.index))

        for i, (coin_list, plot) in enumerate(zip(self.coin_lists, self.plots)):
            available_coins = [coin for coin in coin_list if coin in self.df.columns]

            if not available_coins:
                continue

            for j, coin in enumerate(available_coins):
                if coin in self.df.columns:
                    data = self.df[coin].values

                    # 평활화 적용
                    if self.smooth_check.isChecked():
                        data = self.smooth_data(data)

                    valid_mask = ~np.isnan(data)
                    if valid_mask.any():
                        color = self.colors[j % len(self.colors)]

                        curve = plot.plot(time_axis[valid_mask], data[valid_mask],
                                          pen=pg.mkPen(color=color, width=2),
                                          name=coin)

                        # 호버 효과 추가
                        curve.curve.setClickable(True)

    def smooth_data(self, data, window=5):
        """데이터 평활화"""
        return pd.Series(data).rolling(window=window, center=True).mean().values

    def update_time_range(self, range_text):
        """시간 범위 업데이트"""
        # 여기서 데이터 필터링 로직 구현
        self.status_label.setText(f'시간 범위 변경: {range_text}')
        self.plot_data()

    def update_plots(self):
        """플롯 업데이트"""
        self.plot_data()
        self.status_label.setText('플롯 업데이트 완료')

    def on_plot_clicked(self, event):
        """플롯 클릭 이벤트"""
        self.status_label.setText(f'플롯 클릭: 위치 ({event.scenePos().x():.2f}, {event.scenePos().y():.2f})')

    def show_statistics(self):
        """통계 정보 표시"""
        stats_text = "=== 펀딩비 통계 ===\n"

        for i, (coin_list, title) in enumerate(zip(self.coin_lists, self.titles)):
            stats_text += f"\n[{title}]\n"
            available_coins = [coin for coin in coin_list if coin in self.df.columns]

            for coin in available_coins:
                if coin in self.df.columns:
                    data = self.df[coin].dropna()
                    if not data.empty:
                        stats_text += f"{coin}: 평균={data.mean():.4f}%, 최대={data.max():.4f}%, 최소={data.min():.4f}%\n"

        # 통계 창 표시
        msg = QtGui.QMessageBox()
        msg.setWindowTitle('펀딩비 통계')
        msg.setText(stats_text)
        msg.exec_()

    def show(self):
        self.widget.show()
        return self.widget


# 사용 예시 함수들
def create_simple_viewer(df, coin_lists, titles):
    """간단한 뷰어 생성"""
    viewer = FundingRateViewer(df, coin_lists, titles)
    return viewer.show()


def create_interactive_viewer(df, coin_lists, titles):
    """상호작용 뷰어 생성"""
    viewer = InteractiveFundingRateViewer(df, coin_lists, titles)
    return viewer.show()


# 메인 실행 함수
def main():
    # 테스트용 더미 데이터 생성
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='H')
    np.random.seed(42)

    all_coins = major_coins + mid_coins + small_coins
    data = {}
    for coin in all_coins:
        data[coin] = np.random.normal(0, 0.05, len(dates))

    df = pd.DataFrame(data, index=dates)

    coin_lists = [major_coins, mid_coins, small_coins]
    titles = ['주요 코인', '중형 코인', '소형 코인']

    # 간단한 버전 사용
    # win = create_simple_viewer(df, coin_lists, titles)

    # 상호작용 버전 사용
    win = create_interactive_viewer(df, coin_lists, titles)

    # 실제 사용시에는 아래와 같이 사용
    """
    # 실제 데이터로 사용하는 방법
    df = your_funding_dataframe
    major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    mid_coins = ['SOLUSDT', 'DOTUSDT', 'LINKUSDT'] 
    small_coins = ['DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT']

    coin_lists = [major_coins, mid_coins, small_coins]
    titles = ['주요 코인', '중형 코인', '소형 코인']

    win = create_interactive_viewer(df, coin_lists, titles)
    """

    # 이벤트 루프 실행
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()


if __name__ == '__main__':
    main()