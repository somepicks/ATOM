import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime

class ScreenWorker(QObject):
    finished = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(self, finish_time, interval_ms=1000):
        super().__init__()
        self.finish_time = finish_time

        self.timer = QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._on_timeout)

    @pyqtSlot()
    def start(self):
        print('start')
        self.log.emit("CaptureWorker 시작")
        self.timer.start()

    @pyqtSlot()
    def _on_timeout(self):
        now = datetime.datetime.now()

        if now >= self.finish_time:
            self.log.emit("종료 시간 도달")
            self.stop()
            return

        self.capture_and_send()

    def capture_and_send(self):
        # ✅ 기존 while True 안에 있던 핵심 로직
        try:
            self.log.emit("캡처 및 전송 실행")
            # 기존 코드 그대로
        except Exception as e:
            self.log.emit(f"에러: {e}")

    @pyqtSlot()
    def stop(self):
        self.timer.stop()
        self.finished.emit()


class MyWindow(QMainWindow):
    send_speed = pyqtSignal(int)
    stop_worker = pyqtSignal()
    def __init__(self):
        super().__init__()

        finish_time = datetime.datetime.now().replace(hour=23, minute=25, second=0, microsecond=0)
        self.worker = ScreenWorker(finish_time)

        self.thread = QThread()
        self.worker.moveToThread(self.thread)


        self.thread.started.connect(self.worker.start)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)


    @pyqtSlot(int, int)
    def user_slot(self, arg1, arg2):
        print(arg1, arg2)
    def on_tick(self):
        now = QTime.currentTime()
        if now.second() % 1 == 0: #5초마다
            self.worker.start()
        # if now.second() == 0: #1분마다
        #     self.send_asdf()
        # if now.minute() % 5 == 0:
        #     self.check_orders()
        # if now >= QTime(23, 59):
        #     self.close_market()

if __name__ == "__main__":
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)

    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()