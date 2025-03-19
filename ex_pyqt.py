from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import sys
import time


class DoTrade(QThread):
    # 스레드에서 메인 윈도우로 신호를 보내기 위한 시그널 정의
    # 예: 거래 상태 업데이트를 위한 시그널
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.trading = False
        self.buy_requested = False

    def run(self):
        self.trading = True
        while self.trading:
            # 거래 로직 실행
            self.update_signal.emit("거래 진행 중...")

            # buy 신호 확인
            if self.buy_requested:
                self.buy_stock()
                self.buy_requested = False

            time.sleep(1)  # CPU 과부하 방지

    def stop_trading(self):
        self.trading = False

    # 메인 윈도우의 Buy 버튼에 의해 호출될 메서드
    def request_buy(self):
        self.buy_requested = True
        self.update_signal.emit("매수 요청 수신!")

    def buy_stock(self):
        # 실제 매수 로직 구현
        self.update_signal.emit("매수 실행!")
        # 매수 관련 작업...


class Window(QMainWindow):
    # DoTrade 스레드로 신호를 보내기 위한 시그널 정의
    buy_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Application")
        self.setGeometry(300, 300, 400, 200)

        # UI 구성
        self.init_ui()

        # 스레드 인스턴스 생성
        self.trade_thread = DoTrade()

        # 시그널 연결
        self.QPB_start.clicked.connect(self.start_trading)
        self.QPB_buy.clicked.connect(self.request_buy)

        # 스레드의 시그널을 메인 윈도우의 슬롯에 연결
        self.trade_thread.update_signal.connect(self.update_status)

        # 메인 윈도우의 시그널을 스레드의 슬롯에 연결
        self.buy_signal.connect(self.trade_thread.request_buy)

    def init_ui(self):
        # 중앙 위젯 및 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 버튼 생성
        self.QPB_start = QPushButton("Start Trading", self)
        self.QPB_buy = QPushButton("Buy", self)
        self.QPB_buy.setEnabled(False)  # 거래 시작 전에는 비활성화

        # 레이아웃에 버튼 추가
        layout.addWidget(self.QPB_start)
        layout.addWidget(self.QPB_buy)

    def start_trading(self):
        if not self.trade_thread.isRunning():
            self.trade_thread.start()
            self.QPB_start.setText("Stop Trading")
            self.QPB_buy.setEnabled(True)
        else:
            self.trade_thread.stop_trading()
            self.trade_thread.wait()  # 스레드가 완전히 종료될 때까지 대기
            self.QPB_start.setText("Start Trading")
            self.QPB_buy.setEnabled(False)

    def request_buy(self):
        # 스레드로 buy 신호 발생
        self.buy_signal.emit()

    @pyqtSlot(str)
    def update_status(self, message):
        # 스레드로부터 받은 메시지 처리
        print(message)  # 실제 앱에서는 상태 표시줄이나 로그 창에 표시

    def closeEvent(self, event):
        # 앱 종료 시 스레드 정리
        if self.trade_thread.isRunning():
            self.trade_thread.stop_trading()
            self.trade_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

#
# import sys
# import time
# from PyQt5.QtCore import QThread, pyqtSignal
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
#
# # 첫 번째 작업을 수행할 스레드 클래스
# class FirstThread(QThread):
#     # 데이터를 전달하는 신호 (인자 3개)
#     data_ready = pyqtSignal(int, float, str)
#
#     def run(self):
#         print("첫 번째 스레드 시작")
#         # 데이터 생성
#         time.sleep(2)
#         data1 = 42       # 정수
#         data2 = 3.14     # 실수
#         data3 = "PyQt5"  # 문자열
#         print("첫 번째 스레드 완료, 생성 데이터:", data1, data2, data3)
#         self.data_ready.emit(data1, data2, data3)  # 신호로 데이터 전달
#
# # 두 번째 작업을 수행할 스레드 클래스
# class SecondThread(QThread):
#     def __init__(self):
#         super().__init__()
#         self.data1 = None
#         self.data2 = None
#         self.data3 = None
#
#     def set_data(self, data1, data2, data3):
#         self.data1 = data1
#         self.data2 = data2
#         self.data3 = data3
#
#     def run(self):
#         print("두 번째 스레드 시작")
#         if self.data1 is not None and self.data2 is not None and self.data3 is not None:
#             print(f"두 번째 스레드에서 받은 데이터: {self.data1}, {self.data2}, {self.data3}")
#             time.sleep(3)  # 작업 시간
#             print("두 번째 스레드 완료")
#         else:
#             print("두 번째 스레드에 전달된 데이터 없음")
#
# # 메인 윈도우 클래스
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("QThread 다중 데이터 전달 예제")
#         self.layout = QVBoxLayout()
#
#         self.label = QLabel("스레드 상태: 대기 중")
#         self.layout.addWidget(self.label)
#
#         self.button = QPushButton("작업 시작")
#         self.button.clicked.connect(self.start_threads)
#         self.layout.addWidget(self.button)
#
#         self.setLayout(self.layout)
#
#         # 스레드 생성
#         self.first_thread = FirstThread()
#         self.second_thread = SecondThread()
#
#         # 첫 번째 스레드의 데이터 신호를 연결
#         self.first_thread.data_ready.connect(self.on_data_ready)
#
#     def start_threads(self):
#         self.label.setText("스레드 상태: 첫 번째 스레드 실행 중")
#         self.first_thread.start()
#
#     def on_data_ready(self, data1, data2, data3):
#         self.label.setText("스레드 상태: 두 번째 스레드 실행 중")
#         print("메인 윈도우에서 받은 데이터:", data1, data2, data3)
#         self.second_thread.set_data(data1, data2, data3)
#         self.second_thread.start()
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())