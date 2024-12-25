# import sys
# from PyQt5.QtCore import QThread, pyqtSignal, QObject
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
#
#
# class Worker(QObject):
#     # 작업이 끝났을 때 신호를 발생시킨다.
#     finished = pyqtSignal()
#
#     def run(self):
#         # 첫 번째 작업
#         print("작업 1 시작")
#         QThread.sleep(2)  # 2초 동안 대기 (작업 시뮬레이션)
#         print("작업 1 끝")
#
#         # 첫 번째 작업이 끝난 후 두 번째 작업을 진행
#         self.finished.emit()  # 첫 번째 작업이 끝났음을 신호로 알림
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("QThread 예제")
#         self.setGeometry(100, 100, 300, 200)
#
#         self.button = QPushButton("작업 시작")
#         self.button.clicked.connect(self.start_work)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.button)
#
#         container = QWidget()
#         container.setLayout(layout)
#         self.setCentralWidget(container)
#
#     def start_work(self):
#         # 워커 객체 생성
#         self.worker = Worker()
#         # 워커 스레드에서 작업이 끝나면 다음 작업을 진행하도록 신호 연결
#         self.worker.finished.connect(self.second_task)
#
#         # 워커를 위한 스레드 생성
#         self.thread = QThread()
#         self.worker.moveToThread(self.thread)
#
#         # 스레드 시작
#         self.thread.started.connect(self.worker.run)
#         self.thread.start()
#
#     def second_task(self):
#         print("작업 2 시작")
#         # 두 번째 작업 시뮬레이션
#         QThread.sleep(1)
#         print("작업 2 끝")
#
#         # 추가적으로 필요한 후속 작업을 여기에서 진행
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())





import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# 첫 번째 작업을 수행할 스레드 클래스
class FirstThread(QThread):
    # 데이터를 전달하는 신호 (인자 3개)
    data_ready = pyqtSignal(int, float, str)

    def run(self):
        print("첫 번째 스레드 시작")
        # 데이터 생성
        time.sleep(2)
        data1 = 42       # 정수
        data2 = 3.14     # 실수
        data3 = "PyQt5"  # 문자열
        print("첫 번째 스레드 완료, 생성 데이터:", data1, data2, data3)
        self.data_ready.emit(data1, data2, data3)  # 신호로 데이터 전달

# 두 번째 작업을 수행할 스레드 클래스
class SecondThread(QThread):
    def __init__(self):
        super().__init__()
        self.data1 = None
        self.data2 = None
        self.data3 = None

    def set_data(self, data1, data2, data3):
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3

    def run(self):
        print("두 번째 스레드 시작")
        if self.data1 is not None and self.data2 is not None and self.data3 is not None:
            print(f"두 번째 스레드에서 받은 데이터: {self.data1}, {self.data2}, {self.data3}")
            time.sleep(3)  # 작업 시간
            print("두 번째 스레드 완료")
        else:
            print("두 번째 스레드에 전달된 데이터 없음")

# 메인 윈도우 클래스
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QThread 다중 데이터 전달 예제")
        self.layout = QVBoxLayout()

        self.label = QLabel("스레드 상태: 대기 중")
        self.layout.addWidget(self.label)

        self.button = QPushButton("작업 시작")
        self.button.clicked.connect(self.start_threads)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        # 스레드 생성
        self.first_thread = FirstThread()
        self.second_thread = SecondThread()

        # 첫 번째 스레드의 데이터 신호를 연결
        self.first_thread.data_ready.connect(self.on_data_ready)

    def start_threads(self):
        self.label.setText("스레드 상태: 첫 번째 스레드 실행 중")
        self.first_thread.start()

    def on_data_ready(self, data1, data2, data3):
        self.label.setText("스레드 상태: 두 번째 스레드 실행 중")
        print("메인 윈도우에서 받은 데이터:", data1, data2, data3)
        self.second_thread.set_data(data1, data2, data3)
        self.second_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())