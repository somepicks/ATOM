# import numpy as np
# import pandas as pd
# import sqlite3
# import datetime
#
# conn_DB = sqlite3.connect('DB/bt.db')
#
# ticker_1 = 'bt_numpy_detail'
# ticker_2 = 'bt'
#
#
# df1 = pd.read_sql(f"SELECT * FROM '{ticker_1}'", conn_DB).set_index('날짜')
# df2 = pd.read_sql(f"SELECT * FROM '{ticker_2}'", conn_DB).set_index('날짜')
# df1.index = pd.to_datetime(df1.index)  # datime형태로 변환
# df2.index = pd.to_datetime(df2.index)  # datime형태로 변환
#
# # df1 = df1[df1.index < datetime.datetime.strptime("20240617","%Y%m%d")]
# # df2 = df2[df2.index < datetime.datetime.strptime("20240617","%Y%m%d")]
# print(df1)
# print(df2)
#
# col1 = df1.columns.tolist()
# col2 = df2.columns.tolist()
# intersection = list(set(col1) & set(col2))
# print(intersection)
#
# # li_col = ['상세시가','상세고가','상세저가','상세종가','상세거래량','시가','고가','저가','종가']
# li_col = ['상세시가','상세고가','상세저가','상세종가','상세거래량','데이터길이','데이터길이_5분봉','데이터길이_30분봉','데이터길이_4시간봉','데이터길이_주봉']
# df1 = df1[li_col]
# df2 = df2[li_col]
# print(df1)
# print(df2)
#
#
# # 데이터프레임 비교
# comparison = df1.eq(df2)
# differences = comparison.ne(True)
# print(differences)
#
# # 차이점이 있는 부분만 추출
# diff_positions = differences.where(differences, np.nan)
#
# # 차이점이 있는 행과 열 출력
# for row, col in zip(*np.where(differences)):
#     print(f"Difference at row {row}, column {col} (df1: {df1.iat[row, col]}, df2: {df2.iat[row, col]})")
#
# if df1.equals(df2):
#     print('데이터 동일')
# else:
#     print('데이터 다름')
#
#
# # 차이점이 있는 데이터프레임 출력
# print("\nDifferences DataFrame:\n", diff_positions)
#
# # 값이 1인 행만 추출
# diff_df = differences[(differences == 1).any(axis=1)]
# diff_df.to_sql('diff_positions',conn_DB,if_exists='replace')
#
# non_nan_columns = diff_positions.columns[diff_positions.notna().any()].tolist()
# print(non_nan_columns)
import telegram
import os
import time
import schedule
from datetime import datetime
from PIL import ImageGrab
import requests
from io import BytesIO


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
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
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
            caption = f"📸 화면 캡처\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📁 {filename}"

            files = {
                'photo': ('screenshot.png', image_buffer, 'image/png')
            }

            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }

            response = requests.post(self.telegram_url, files=files, data=data)

            if response.status_code == 200:
                print(f"✅ 텔레그램 전송 성공: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ 텔레그램 전송 실패: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"텔레그램 전송 중 오류 발생: {e}")

    def capture_and_send(self):
        """스크린샷을 캡처하고 저장한 후 텔레그램으로 전송하는 메인 함수"""
        print(f"📸 스크린샷 캡처 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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
    BOT_TOKEN = "1883109215"  # 여기에 봇 토큰을 입력하세요
    CHAT_ID = "AAHM6-d42-oNmdDO6vmT3SWxB0ICH_od86M"  # 여기에 채팅 ID를 입력하세요
    BOT_TOKEN = "1883109215:AAHM6-d42-oNmdDO6vmT3SWxB0ICH_od86M"  # 여기에 봇 토큰을 입력하세요
    CHAT_ID = "1644533124"  # 여기에 채팅 ID를 입력하세요
    import asyncio

    # bot = telegram.Bot(token=BOT_TOKEN)
    # asyncio.run(bot.send_message(chat_id=CHAT_ID, text="asdf"))
    # 봇 인스턴스 생성 (images 폴더에 저장)
    bot = ScreenCaptureBot(BOT_TOKEN, CHAT_ID, save_folder="images")

    # 현재 화면 크기 확인
    screen_width, screen_height = bot.get_screen_size()
    print(f"현재 화면 크기: {screen_width} x {screen_height}")

    # 기존 저장된 이미지 개수 확인
    saved_count = bot.get_saved_images_count()
    print(f"현재 저장된 이미지 개수: {saved_count}개")

    # 캡처 영역 설정 (예시: 화면 전체의 왼쪽 절반)
    bot.set_capture_region(0, 0, screen_width // 2, screen_height)

    # 스케줄 설정 - 1시간마다 실행
    schedule.every().hour.do(bot.capture_and_send)

    # 매일 자정에 7일 이상 된 파일 정리 (선택사항)
    schedule.every().day.at("00:00").do(lambda: bot.clean_old_images(keep_days=7))

    # 테스트를 위해 즉시 한 번 실행
    print("테스트 캡처를 실행합니다...")
    bot.capture_and_send()

    print("⏰ 1시간마다 스크린샷을 캡처하여 저장하고 텔레그램으로 전송합니다.")
    print("💾 이미지는 'images' 폴더에 저장됩니다.")
    print("프로그램을 종료하려면 Ctrl+C를 누르세요.")

    # 스케줄러 실행
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
    except KeyboardInterrupt:
        print(f"\n프로그램이 종료되었습니다.")
        final_count = bot.get_saved_images_count()
        print(f"📁 총 {final_count}개의 이미지가 저장되어 있습니다.")


if __name__ == "__main__":
    main()