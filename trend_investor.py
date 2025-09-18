import os
import time
import schedule
# from datetime import datetime
from PIL import ImageGrab
import requests
from io import BytesIO
from pykrx import stock
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
class ScreenCaptureBot:
    def __init__(self, bot_token, chat_id, save_folder="images"):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.telegram_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        self.save_folder = save_folder

        # images 폴더가 없으면 생성
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
            print(f"📁 '{self.save_folder}' 폴더가 생성되었습니다.")

        # 캡처할 영역 설정 (x1, y1, x2, y2) - 픽셀 좌표
        # 예시: 화면 왼쪽 상단 800x600 영역
        self.capture_region = (0, 0, 800, 600)  # 필요에 따라 수정하세요

    def capture_screen_region(self):
        """지정된 영역의 스크린샷을 캡처하고 파일로 저장합니다."""
        try:
            # 지정된 영역 캡처
            screenshot = ImageGrab.grab(bbox=self.capture_region)

            # 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)

            # 이미지를 파일로 저장
            screenshot.save(filepath, format='PNG')
            print(f"💾 이미지 저장됨: {filepath}")

            # 메모리에도 이미지를 저장 (텔레그램 전송용)
            img_buffer = BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            return img_buffer, filepath
        except Exception as e:
            print(f"스크린샷 캡처 중 오류 발생: {e}")
            return None, None

    def send_to_telegram(self, image_buffer, filepath):
        """캡처한 이미지를 텔레그램으로 전송합니다."""
        try:
            # 현재 시간과 파일 정보를 캡션으로 추가
            filename = os.path.basename(filepath)
            caption = f"📸 화면 캡처\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📁 {filename}"

            files = {
                'photo': ('screenshot.png', image_buffer, 'image/png')
            }

            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }

            response = requests.post(self.telegram_url, files=files, data=data)

            if response.status_code == 200:
                print(f"✅ 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ 텔레그램 전송 실패: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"텔레그램 전송 중 오류 발생: {e}")
    def send_to_df_chart(self):
        today = datetime.datetime.today()
        past_day = today - datetime.timedelta(days=30)
        df = stock.get_market_trading_value_by_date(past_day.strftime("%Y%m%d"), today.strftime("%Y%m%d"), "KOSPI")
        # print(df)
        time.sleep(10)
        # df = stock.get_market_trading_value_by_date("20250910", "20250917", "KOSPI", etf=True, etn=True, elw=True)
        caption = f"거래대금-코스피 (ETF, ETN, ELW 미포함)\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        df_kospi = stock.get_index_fundamental(past_day.strftime("%Y%m%d"), today.strftime("%Y%m%d"), '1001')  # 코스피
        df = pd.concat([df, df_kospi[['종가']]], axis=1)
        df.rename(columns={'종가': '코스피'}, inplace=True)
        print(df)
        # self.send_to_df_chart(df, caption)
        # 1. '기타법인' 열 삭제 (존재할 경우만)
        if "기타법인" in df.columns:
            df = df.drop(columns=["기타법인"])

        # 2. 0만 있는 열 삭제
        df = df.loc[:, (df != 0).any(axis=0)]

        # 3. 코스피와 거래대금 데이터 분리
        kospi_data = None
        trading_data = df.copy()

        if "코스피" in df.columns:
            kospi_data = df["코스피"]
            trading_data = df.drop(columns=["코스피"]) / 1e8  # 억원 단위 변환
        else:
            trading_data = df / 1e8  # 억원 단위 변환

        # 4. 듀얼 y축 라인 그래프 생성
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 왼쪽 y축: KOSPI 지수
        if kospi_data is not None:
            ax1.set_xlabel("날짜")
            ax1.set_ylabel("KOSPI 지수", color="red")
            ax1.plot(df.index, kospi_data, color="red", linewidth=2, label="KOSPI")
            ax1.tick_params(axis="y", labelcolor="red")
            ax1.grid(True, linestyle="--", alpha=0.3)

        # 오른쪽 y축: 거래대금 (억원)
        ax2 = ax1.twinx()
        ax2.set_ylabel("거래대금 (억원)", color="blue")

        # 거래대금 데이터 플롯 (코스피 제외한 나머지)
        colors = ["blue", "orange", "green", "purple", "brown", "pink"]
        for i, column in enumerate(trading_data.columns):
            color = colors[i % len(colors)]
            ax2.plot(trading_data.index, trading_data[column],
                     color=color, marker="o", markersize=4, linewidth=2,
                     label=column)

        ax2.tick_params(axis="y", labelcolor="blue")

        # 5. x축 날짜 포맷 지정
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45, ha="right")

        # 6. 범례 통합 및 위치 조정
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2,
                   loc="upper left", bbox_to_anchor=(0, 1))

        # 7. 레이아웃 조정
        plt.title("KOSPI 지수 vs 거래대금", fontsize=14, pad=20)
        plt.tight_layout(pad=2.0)

        # 8. 이미지 저장
        filename = "df_plot.png"
        plt.savefig(filename, bbox_inches="tight", pad_inches=0.1, dpi=150)
        plt.close()

        # 5. 텔레그램 전송
        files = {'photo': open(filename, 'rb')}
        data = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        response = requests.post(self.telegram_url, data=data, files=files)

        if response.status_code == 200:
            print(f"✅ 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ 텔레그램 전송 실패: {response.status_code} - {response.text}")
    def capture_and_send(self):
        """스크린샷을 캡처하고 저장한 후 텔레그램으로 전송하는 메인 함수"""
        print(f"📸 스크린샷 캡처 시작: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 화면 캡처 및 파일 저장
        image_buffer, filepath = self.capture_screen_region()

        if image_buffer and filepath:
            # 텔레그램으로 전송
            self.send_to_telegram(image_buffer, filepath)
            image_buffer.close()
        else:
            print("스크린샷 캡처에 실패했습니다.")

    def set_capture_region(self, x1, y1, x2, y2):
        """캡처할 영역을 설정합니다."""
        self.capture_region = (x1, y1, x2, y2)
        print(f"캡처 영역이 설정되었습니다: ({x1}, {y1}) to ({x2}, {y2})")

    def get_screen_size(self):
        """현재 화면 크기를 반환합니다."""
        screenshot = ImageGrab.grab()
        return screenshot.size

    def get_saved_images_count(self):
        """저장된 이미지 파일 개수를 반환합니다."""
        try:
            images = [f for f in os.listdir(self.save_folder) if f.endswith('.png')]
            return len(images)
        except:
            return 0

    def clean_old_images(self, keep_days=7):
        """지정된 일수보다 오래된 이미지 파일들을 삭제합니다."""
        try:
            current_time = time.time()
            deleted_count = 0

            for filename in os.listdir(self.save_folder):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.save_folder, filename)
                    file_time = os.path.getctime(filepath)

                    # 파일이 keep_days보다 오래된 경우 삭제
                    if (current_time - file_time) > (keep_days * 24 * 3600):
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"🗑️ 오래된 파일 삭제: {filename}")

            if deleted_count > 0:
                print(f"📁 {deleted_count}개의 오래된 파일이 삭제되었습니다.")

        except Exception as e:
            print(f"파일 정리 중 오류 발생: {e}")


def main():
    # 텔레그램 봇 설정
    BOT_TOKEN = "1883109215:AAHM6-d42-oNmdDO6vmT3SWxB0ICH_od86M"  # 여기에 봇 토큰을 입력하세요
    CHAT_ID = "1644533124"  # 여기에 채팅 ID를 입력하세요 (bot 채팅)
    # CHAT_ID = "-1002919914781"  # 여기에 채팅 ID를 입력하세요 (텔레그램 채널)

    # 봇 인스턴스 생성 (images 폴더에 저장)
    bot = ScreenCaptureBot(BOT_TOKEN, CHAT_ID, save_folder="images")

    # 현재 화면 크기 확인
    screen_width, screen_height = bot.get_screen_size()

    print(f"현재 화면 크기: {screen_width} x {screen_height}")

    # 기존 저장된 이미지 개수 확인
    saved_count = bot.get_saved_images_count()
    print(f"현재 저장된 이미지 개수: {saved_count}개")

    # 캡처 영역 설정 (예시: 화면 전체의 왼쪽 절반)
    x1=0
    y1=100
    x2=1700
    y2=2000
    bot.set_capture_region(x1, y1, x2, y2)

    # 스케줄 설정 - 1시간마다 실행
    schedule.every(15).minutes.do(bot.capture_and_send)

    # 매일 자정에 7일 이상 된 파일 정리 (선택사항)
    schedule.every().day.at("00:00").do(lambda: bot.clean_old_images(keep_days=7))

    # 테스트를 위해 즉시 한 번 실행
    print("테스트 캡처를 실행합니다...")
    bot.capture_and_send()

    print("⏰ 15분마다 스크린샷을 캡처하여 저장하고 텔레그램으로 전송합니다.")
    print("🕐 오후 3시 30분에 자동으로 종료됩니다.")
    print("💾 이미지는 'images' 폴더에 저장됩니다.")
    print("프로그램을 종료하려면 Ctrl+C를 누르세요.")

    # 스케줄러 실행
    try:
        while True:
            # 현재 시간 확인
            now = datetime.datetime.now()

            # 오후 3시 30분 체크 (15:30)
            if now.hour == 15 and now.minute >= 30:
                print(f"\n🕐 오후 3시 30분이 되어 프로그램을 종료합니다.")
                final_count = bot.get_saved_images_count()
                print(f"📁 총 {final_count}개의 이미지가 저장되어 있습니다.")
                bot.capture_and_send()
                bot.send_to_df_chart()
                print('윈도우 종료')
                os.system("shutdown /s /t 0")  # 윈도우 죵료
                break

            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
    except KeyboardInterrupt:
        print(f"\n사용자에 의해 프로그램이 종료되었습니다.")
        final_count = bot.get_saved_images_count()
        print(f"📁 총 {final_count}개의 이미지가 저장되어 있습니다.")


if __name__ == "__main__":
    main()