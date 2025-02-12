import datetime
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, QTime, QDateTime


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # QTabWidget 생성
        self.tab_widget = QTabWidget()

        # 첫 번째 탭
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        self.button1 = QPushButton("첫 번째 탭 버튼")
        tab1_layout.addWidget(self.button1)
        tab1.setLayout(tab1_layout)
        self.button1.clicked.connect(self.del_stg1)
        # 두 번째 탭 (QPushButton 추가)
        self.tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        self.button2 = QPushButton("두 번째 탭 버튼")
        tab2_layout.addWidget(self.button2)
        self.tab2.setLayout(tab2_layout)
        self.button2.clicked.connect(self.del_stg2)

        # 세 번째 탭
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        self.button3 = QPushButton("첫 번째 탭 버튼")
        tab3_layout.addWidget(self.button3)
        self.button3.clicked.connect(self.del_stg3)

        tab3.setLayout(tab3_layout)

        # 탭 추가
        self.tab_widget.addTab(tab1, "탭 1")
        self.tab_widget.addTab(self.tab2, "탭 2")
        self.tab_widget.addTab(tab3, "탭 3")

        # 메인 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # 윈도우 설정
        self.setWindowTitle("QTabWidget 자동 클릭 예제")
        self.setGeometry(300, 300, 400, 300)
        self.show()

        # 특정 시간(오전 8시 50분)에 자동 클릭 설정
        while True:
            self.setAutoClickTime(15, 57)
    def del_stg1(self):
        print('tab1')

    def del_stg2(self):
        print('tab2')

    def del_stg3(self):
        print('tab3')
    def setAutoClickTime(self, hour, minute):
        print(datetime.datetime.now())
        """ 지정된 시간(hour, minute)에 버튼 클릭을 실행하는 함수 """
        now = QDateTime.currentDateTime()
        target_time = QDateTime(now.date(), QTime(hour, minute, 0))

        if now > target_time:
            # 현재 시간이 목표 시간보다 크면, 다음 날 실행하도록 설정
            target_time = target_time.addDays(1)

        # 목표 시간까지 남은 시간(밀리초 단위) 계산
        msec_until_target = now.msecsTo(target_time)

        # QTimer 설정
        QTimer.singleShot(msec_until_target, self.autoClickButton)

    def autoClickButton(self):
        """ 두 번째 탭의 버튼을 자동으로 클릭하는 함수 """
        self.tab_widget.setCurrentIndex(1)  # 두 번째 탭으로 변경
        self.button2.click()  # 버튼 클릭 이벤트 발생


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
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