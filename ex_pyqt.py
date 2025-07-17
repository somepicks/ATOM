import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont


class WorkerThread(QThread):
    """메인 작업을 수행하는 스레드"""
    progress_signal = pyqtSignal(str)
    counter_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.is_running = False

        # 1초마다 실행되는 타이머
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.function1)

        # 10초 후 2번 함수 실행을 위한 타이머
        self.timer_10sec = QTimer()
        self.timer_10sec.timeout.connect(self.start_function2)
        self.timer_10sec.setSingleShot(True)  # 한 번만 실행

        # 2번 함수의 3초 지연을 위한 타이머
        self.timer_3sec_delay = QTimer()
        self.timer_3sec_delay.timeout.connect(self.function2_continue)
        self.timer_3sec_delay.setSingleShot(True)

    def run(self):
        """스레드 실행"""
        self.is_running = True
        self.progress_signal.emit("작업 스레드 시작")

        # 타이머들을 이 스레드로 이동
        self.timer1.moveToThread(self)
        self.timer_10sec.moveToThread(self)
        self.timer_3sec_delay.moveToThread(self)

        # 1초마다 실행되는 타이머 시작
        self.timer1.start(1000)

        # 10초 후 2번 함수 실행 타이머 시작
        self.timer_10sec.start(10000)

        # 이벤트 루프 실행
        self.exec_()

    def stop_worker(self):
        """작업 중지"""
        self.is_running = False
        self.timer1.stop()
        self.timer_10sec.stop()
        self.timer_3sec_delay.stop()
        self.quit()

    def function1(self):
        """1번 함수: 1초마다 실행"""
        if self.is_running:
            self.counter += 1
            self.counter_signal.emit(self.counter)
            self.progress_signal.emit(f"1번 함수 실행 - 카운터: {self.counter}")
            print(time.time())
    def start_function2(self):
        """2번 함수 시작 (10초 후 실행)"""
        self.progress_signal.emit("2번 함수 시작")

        # 3초 지연을 위한 타이머 시작 (블로킹하지 않음)
        self.timer_3sec_delay.start(3000)

    def function2_continue(self):
        """2번 함수 계속 (3초 지연 후)"""
        self.progress_signal.emit("2번 함수 - 3초 지연 완료, 나머지 작업 진행")

        # 여기서 나머지 작업 수행
        self.progress_signal.emit("2번 함수 완료")


class AlternativeWorkerThread(QThread):
    """대안 방법: 여러 타이머 사용"""
    progress_signal = pyqtSignal(str)
    counter_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.is_running = False
        self.function2_step = 0  # 2번 함수 진행 단계

    def run(self):
        """스레드 실행"""
        self.is_running = True
        self.progress_signal.emit("대안 방법 스레드 시작")

        # 1초마다 실행되는 타이머
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.function1)
        self.timer1.start(1000)

        # 메인 작업 타이머 (100ms마다 체크)
        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self.main_loop)
        self.main_timer.start(100)

        self.start_time = time.time()
        self.function2_start_time = None

        # 이벤트 루프 실행
        self.exec_()

    def stop_worker(self):
        """작업 중지"""
        self.is_running = False
        if hasattr(self, 'timer1'):
            self.timer1.stop()
        if hasattr(self, 'main_timer'):
            self.main_timer.stop()
        self.quit()

    def function1(self):
        """1번 함수: 1초마다 실행"""
        if self.is_running:
            self.counter += 1
            self.counter_signal.emit(self.counter)
            self.progress_signal.emit(f"1번 함수 실행 - 카운터: {self.counter}")

    def main_loop(self):
        """메인 루프: 시간 체크 및 2번 함수 관리"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # 10초 후 2번 함수 시작
        if elapsed_time >= 10 and self.function2_step == 0:
            self.function2_step = 1
            self.function2_start_time = current_time
            self.progress_signal.emit("2번 함수 시작")

        # 2번 함수 진행 중 - 3초 지연 체크
        elif self.function2_step == 1:
            function2_elapsed = current_time - self.function2_start_time
            if function2_elapsed >= 3:
                self.function2_step = 2
                self.progress_signal.emit("2번 함수 - 3초 지연 완료, 나머지 작업 진행")
                self.progress_signal.emit("2번 함수 완료")


class BadWorkerThread(QThread):
    """잘못된 예제: 블로킹 사용"""
    progress_signal = pyqtSignal(str)
    counter_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.is_running = False

    def run(self):
        """스레드 실행 - 잘못된 방법"""
        self.is_running = True
        self.progress_signal.emit("잘못된 방법 스레드 시작")

        # 1초마다 실행되는 타이머
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.function1)
        self.timer1.start(1000)

        # 10초 후 2번 함수 실행을 위한 타이머
        self.timer_10sec = QTimer()
        self.timer_10sec.timeout.connect(self.bad_function2)
        self.timer_10sec.setSingleShot(True)
        self.timer_10sec.start(10000)

        # 이벤트 루프 실행
        self.exec_()

    def stop_worker(self):
        """작업 중지"""
        self.is_running = False
        if hasattr(self, 'timer1'):
            self.timer1.stop()
        if hasattr(self, 'timer_10sec'):
            self.timer_10sec.stop()
        self.quit()

    def function1(self):
        """1번 함수: 1초마다 실행"""
        if self.is_running:
            self.counter += 1
            self.counter_signal.emit(self.counter)
            self.progress_signal.emit(f"1번 함수 실행 - 카운터: {self.counter}")

    def bad_function2(self):
        """2번 함수 - 잘못된 방법 (블로킹 사용)"""
        self.progress_signal.emit("잘못된 2번 함수 시작")

        # 이렇게 하면 타이머가 3초간 멈춤!
        time.sleep(3)

        self.progress_signal.emit("잘못된 2번 함수 완료")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None

    def initUI(self):
        self.setWindowTitle('QThread 내 QTimer 비블로킹 처리')
        self.setGeometry(100, 100, 500, 400)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 상태 표시 레이블
        self.status_label = QLabel('대기 중...')
        self.status_label.setFont(QFont('Arial', 10))
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # 카운터 표시 레이블
        self.counter_label = QLabel('1번 함수 실행 횟수: 0')
        self.counter_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(self.counter_label)

        # 올바른 방법 버튼
        self.start_button = QPushButton('올바른 방법 시작')
        self.start_button.clicked.connect(self.start_correct_method)
        layout.addWidget(self.start_button)

        # 대안 방법 버튼
        self.alt_button = QPushButton('대안 방법 시작')
        self.alt_button.clicked.connect(self.start_alternative_method)
        layout.addWidget(self.alt_button)

        # 잘못된 방법 버튼
        self.bad_button = QPushButton('잘못된 방법 시작 (비교용)')
        self.bad_button.clicked.connect(self.start_bad_method)
        layout.addWidget(self.bad_button)

        # 중지 버튼
        self.stop_button = QPushButton('중지')
        self.stop_button.clicked.connect(self.stop_worker)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

    def start_correct_method(self):
        """올바른 방법으로 시작"""
        self.stop_worker()
        self.worker = WorkerThread()
        self.setup_worker_signals()
        self.worker.start()
        self.update_button_states(True)

    def start_alternative_method(self):
        """대안 방법으로 시작"""
        self.stop_worker()
        self.worker = AlternativeWorkerThread()
        self.setup_worker_signals()
        self.worker.start()
        self.update_button_states(True)

    def start_bad_method(self):
        """잘못된 방법으로 시작"""
        self.stop_worker()
        self.worker = BadWorkerThread()
        self.setup_worker_signals()
        self.worker.start()
        self.update_button_states(True)

    def setup_worker_signals(self):
        """워커 시그널 연결"""
        self.worker.progress_signal.connect(self.update_status)
        self.worker.counter_signal.connect(self.update_counter)

    def stop_worker(self):
        """워커 중지"""
        if self.worker and self.worker.isRunning():
            self.worker.stop_worker()
            self.worker.wait()
        self.update_button_states(False)

    def update_status(self, message):
        """상태 업데이트"""
        current_text = self.status_label.text()
        new_text = f"{current_text}\n{message}"
        # 너무 길어지면 앞부분 제거
        lines = new_text.split('\n')
        if len(lines) > 10:
            lines = lines[-10:]
        self.status_label.setText('\n'.join(lines))

    def update_counter(self, count):
        """카운터 업데이트"""
        self.counter_label.setText(f'1번 함수 실행 횟수: {count}')

    def update_button_states(self, running):
        """버튼 상태 업데이트"""
        self.start_button.setEnabled(not running)
        self.alt_button.setEnabled(not running)
        self.bad_button.setEnabled(not running)
        self.stop_button.setEnabled(running)

    def closeEvent(self, event):
        """창 닫기 이벤트"""
        self.stop_worker()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())