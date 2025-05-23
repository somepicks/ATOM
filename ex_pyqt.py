import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.button = QPushButton("Click Me")
        self.button.clicked.connect(self.on_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 2초(2000ms) 후에 버튼 클릭 시그널 보내기
        QTimer.singleShot(2000, self.button.click)

    def on_button_clicked(self):
        print("Button was clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
#
#
#
#
# class DoTrade(QThread):
#     # 스레드에서 메인 윈도우로 신호를 보내기 위한 시그널 정의
#     # 예: 거래 상태 업데이트를 위한 시그널
#     update_signal = pyqtSignal(str)
#
#     def __init__(self):
#         super().__init__()
#         self.trading = False
#         self.buy_requested = False
#
#     def run(self):
#         self.trading = True
#         while self.trading:
#             # 거래 로직 실행
#             self.update_signal.emit("거래 진행 중...")
#
#             # buy 신호 확인
#             if self.buy_requested:
#                 self.buy_stock()
#                 self.buy_requested = False
#
#             time.sleep(1)  # CPU 과부하 방지
#
#     def stop_trading(self):
#         self.trading = False
#
#     # 메인 윈도우의 Buy 버튼에 의해 호출될 메서드
#     def request_buy(self):
#         self.buy_requested = True
#         self.update_signal.emit("매수 요청 수신!")
#
#     def buy_stock(self):
#         # 실제 매수 로직 구현
#         self.update_signal.emit("매수 실행!")
#         # 매수 관련 작업...
#
#
# class Window(QMainWindow):
#     # DoTrade 스레드로 신호를 보내기 위한 시그널 정의
#     buy_signal = pyqtSignal()
#
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Trading Application")
#         self.setGeometry(300, 300, 400, 200)
#
#         # UI 구성
#         self.init_ui()
#
#         # 스레드 인스턴스 생성
#         self.trade_thread = DoTrade()
#
#         # 시그널 연결
#         self.QPB_start.clicked.connect(self.start_trading)
#         self.QPB_buy.clicked.connect(self.request_buy)
#
#         # 스레드의 시그널을 메인 윈도우의 슬롯에 연결
#         self.trade_thread.update_signal.connect(self.update_status)
#
#         # 메인 윈도우의 시그널을 스레드의 슬롯에 연결
#         self.buy_signal.connect(self.trade_thread.request_buy)
#
#     def init_ui(self):
#         # 중앙 위젯 및 레이아웃 설정
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QVBoxLayout(central_widget)
#
#         # 버튼 생성
#         self.QPB_start = QPushButton("Start Trading", self)
#         self.QPB_buy = QPushButton("Buy", self)
#         self.QPB_buy.setEnabled(False)  # 거래 시작 전에는 비활성화
#
#         # 레이아웃에 버튼 추가
#         layout.addWidget(self.QPB_start)
#         layout.addWidget(self.QPB_buy)
#
#     def start_trading(self):
#         if not self.trade_thread.isRunning():
#             self.trade_thread.start()
#             self.QPB_start.setText("Stop Trading")
#             self.QPB_buy.setEnabled(True)
#         else:
#             self.trade_thread.stop_trading()
#             self.trade_thread.wait()  # 스레드가 완전히 종료될 때까지 대기
#             self.QPB_start.setText("Start Trading")
#             self.QPB_buy.setEnabled(False)
#
#     def request_buy(self):
#         # 스레드로 buy 신호 발생
#         self.buy_signal.emit()
#
#     @pyqtSlot(str)
#     def update_status(self, message):
#         # 스레드로부터 받은 메시지 처리
#         print(message)  # 실제 앱에서는 상태 표시줄이나 로그 창에 표시
#
#     def closeEvent(self, event):
#         # 앱 종료 시 스레드 정리
#         if self.trade_thread.isRunning():
#             self.trade_thread.stop_trading()
#             self.trade_thread.wait()
#         event.accept()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = Window()
#     window.show()
#     sys.exit(app.exec_())


import sys
import os
import platform
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer

class MyApp(QWidget):
    def __init__(self, timeout_seconds=10):
        super().__init__()
        self.timeout_seconds = timeout_seconds
        self.initUI()
        self.startTimer()

    def initUI(self):
        self.setWindowTitle('PyQt5 Timer App')
        layout = QVBoxLayout()
        label = QLabel(f"This app will close in {self.timeout_seconds} seconds and go to sleep mode.")
        layout.addWidget(label)
        self.setLayout(layout)
        self.resize(400, 100)
        self.show()

    def startTimer(self):
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.shutdown_procedure)
        self.timer.start(self.timeout_seconds * 1000)  # milliseconds

    def shutdown_procedure(self):
        print("Time is up! Closing app and entering sleep mode.")
        self.close()  # Close the app window
        # self.enter_sleep_mode()

    def enter_sleep_mode(self):
        system = platform.system()
        if system == "Windows":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif system == "Darwin":  # macOS
            os.system("pmset sleepnow")
        elif system == "Linux":
            os.system("systemctl suspend")
        else:
            print("Sleep mode not supported on this OS.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp(timeout_seconds=10)  # 10초 후 절전 모드
    sys.exit(app.exec_())
