import sys
from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSlot
from datetime import datetime, timedelta


class HourlyScheduler:
    def __init__(self):
        self.setup_timer()

    def setup_timer(self):
        """타이머 설정"""
        # 정각에 실행될 타이머
        self.hourly_timer = QTimer()
        self.hourly_timer.setSingleShot(True)
        self.hourly_timer.timeout.connect(self.on_hourly_trigger)

        # 첫 번째 정각 실행 시작
        self.start_next_hourly_timer()

    def start_next_hourly_timer(self):
        """다음 정각까지의 타이머 시작"""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        delay_ms = int((next_hour - now).total_seconds() * 1000)

        print(f"다음 실행 시간: {next_hour.strftime('%H:%M:%S')}")
        print(f"대기 시간: {delay_ms / 1000:.0f}초")

        if delay_ms > 0:
            self.hourly_timer.start(delay_ms)
        else:
            # 이미 지난 시간이면 즉시 실행
            self.on_hourly_trigger()

    def on_hourly_trigger(self):
        """매시 정각에 실행될 함수"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n=== 함수 실행: {current_time} ===")

        # 실제 작업 실행
        self.my_hourly_function()

        # 다음 정각을 위한 타이머 재설정
        self.start_next_hourly_timer()

    def my_hourly_function(self):
        """실제로 실행하고 싶은 작업"""
        print("사용자 정의 함수가 정각에 실행되었습니다!")
        # 여기에 원하는 작업을 구현하세요
        # 예: 파일 처리, 데이터베이스 작업, API 호출 등


def main():
    # QCoreApplication 사용 (GUI 없음)
    app = QCoreApplication(sys.argv)

    scheduler = HourlyScheduler()

    print("QTimer 스케줄러가 시작되었습니다.")
    print("매시 정각에 함수가 실행됩니다.")
    print("중단하려면 Ctrl+C를 누르세요.\n")

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n스케줄러가 중단되었습니다.")


if __name__ == '__main__':
    main()