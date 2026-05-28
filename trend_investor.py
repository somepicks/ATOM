import os
import sqlite3
import time
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QWidget,QVBoxLayout,QApplication,QTextEdit)
from PyQt5.QtCore import QThread,QTimer,pyqtSignal,QObject,QTime

import numpy as np
from pathlib import Path

from PIL import ImageGrab

from io import BytesIO
from pykrx import stock
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import KIS
import requests
from bs4 import BeautifulSoup
import urllib.request as req
from pprint import pprint
from matplotlib.ticker import ScalarFormatter
import yfinance as yf
from telegram import Bot
import asyncio
class Worker(QObject):
    off = pyqtSignal()
    QTE = pyqtSignal(str)

    def __init__(self, parent,bot_token, chat_id, ex,cond, ticker_future):
        super().__init__(parent)
        self.bot_token = bot_token
        self.bot = Bot(token=self.bot_token)
        self.chat_id = chat_id
        self.ticker_future = ticker_future
        self.ex = ex
        self.cond = cond
        self.df_trend = pd.DataFrame()
        self.df_world = pd.DataFrame()
        self.save_folder = "images"
        if not os.path.exists(self.save_folder):        # images 폴더가 없으면 생성
            os.makedirs(self.save_folder)
            print(f"📁 '{self.save_folder}' 폴더가 생성되었습니다.")


    def capture_and_send(self):
        """스크린샷을 캡처하고 저장한 후 텔레그램으로 전송하는 메인 함수"""
    ######################## 화면 캡처 및 파일 저장
        image_buffer = self.capture_screen_region(x1=0,y1=100,x2=1700,y2=1950)
        if image_buffer == None :
            print(f" 캡처에 실패했습니다.")
            self.QTE.emit(f"스크린샷 캡처에 실패했습니다.")
        else:
            # 텔레그램으로 전송
            # self.send_to_telegram(image_buffer, filepath)
            caption = f"📸 화면 캡처\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            # self.send_tele_async(image_buffer=image_buffer, caption=caption, title="화면 캡쳐")
            asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="화면 캡쳐"))
            image_buffer.close()
    ######################## 화면 캡처 및 파일 저장
        time.sleep(1)
        image_buffer = self.capture_screen_region_chart(x1=1700,y1=100,x2=3800,y2=1950)
        if image_buffer == None:
            print(f" 캡처에 실패했습니다.")
            self.QTE.emit(f"스크린샷 캡처에 실패했습니다.")
        else:
            # 텔레그램으로 전송
            # self.send_to_telegram(image_buffer, filepath)
            caption = f"📸 화면 캡처\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            # self.send_tele_async(image_buffer=image_buffer, caption=caption, title="화면 캡쳐")
            asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="화면 캡쳐"))
            image_buffer.close()
    ######################## 이하 투자자별 거래대금
        image_buffer = self.sum_trend()
        title = "투자자별 거래대금"
        if image_buffer == None :
            self.QTE.emit(f"스크린샷 캡처에 실패했습니다.")
            print(f"{title} 캡처에 실패했습니다.")
        else:
            caption = f"거래대금-코스피 (ETF, ETN, ELW 미포함)\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#             self.send_tele_async(image_buffer=image_buffer, caption=caption, title="투자자별 거래대금")
            asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title=title))

            image_buffer.close()

    ######################## 이하 세계는 지금
        image_buffer = self.now_world()
        title = "세계는 지금"
        if image_buffer == None :
            self.QTE.emit(f"{title} 캡처에 실패했습니다.")
            print(f"{title} 캡처에 실패했습니다.")
        else:
            caption = f"world\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#             self.send_tele_async(image_buffer=image_buffer, caption=caption, title="세계는 지금")
            asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="세계는 지금"))

            image_buffer.close()

    ######################## 옵션 현재가
#         df_call_week, df_put_week, cond, past_day, ex_day = self.ex.display_opt_weekly(datetime.datetime.now())
#         df = self.ex.display_fut()
#         ticker_fut = df.index[0]
#         output = self.ex.fetch_domestic_price(market_code="F", symbol=ticker_fut)
#         if cond == '만기주':
#             df_call, df_put, past_date, expiry_date = self.ex.display_opt(datetime.datetime.now())
#             caption=f"본옵션 만기일:{expiry_date} [-{(expiry_date-datetime.datetime.now().date()).days} 일] 베이시스: {output['베이시스']} 이론가: {['이론가']}"
#             image_buffer = self.get_option(df_call, df_put,float(output['현재가']))
#         else:
#             caption=f'위클리 옵션 만기일:{ex_day} [-{(ex_day-datetime.datetime.now().date()).days} 일]'
#             image_buffer = self.get_option(df_call_week, df_put_week,float(output['현재가']))
# #         self.send_tele_async(image_buffer=image_buffer, caption=caption, title="옵션 현재가")
#         asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="옵션 현재가"))
#         image_buffer.close()


    def capture_screen_region(self,x1,y1,x2,y2):
        """지정된 영역의 스크린샷을 캡처하고 파일로 저장합니다."""
        try:
            # 지정된 영역 캡처
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            # 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)

            # 이미지를 파일로 저장
            screenshot.save(filepath, format='PNG')

            # 메모리에도 이미지를 저장 (텔레그램 전송용)
            img_buffer = BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            # print(f"capture_screen_region, {img_buffer}  {filepath}   {filename}")

            return img_buffer
        except Exception as e:
            print(f"스크린샷 캡처 중 오류 발생: {e}")
            self.QTE.emit(f"스크린샷 캡처 중 오류 발생:.")

            return None
    def capture_screen_region_chart(self,x1,y1,x2,y2):
        """지정된 영역의 스크린샷을 캡처하고 파일로 저장합니다."""
        try:
            # 지정된 영역 캡처
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            # 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_chart_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)

            # 이미지를 파일로 저장
            screenshot.save(filepath, format='PNG')

            # 메모리에도 이미지를 저장 (텔레그램 전송용)
            img_buffer = BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            # print(f"capture_screen_region, {img_buffer}  {filepath}   {filename}")

            return img_buffer
        except Exception as e:
            print(f"스크린샷 캡처 중 오류 발생: {e}")
            self.QTE.emit(f"스크린샷 캡처 중 오류 발생:.")
            return None

    async def send_to_telegram(self, image_buffer, caption,title):
        """캡처한 이미지를 텔레그램으로 전송합니다."""
        try:
            # 현재 시간과 파일 정보를 캡션으로 추가
            # filename = os.path.basename(filepath)
            files = {
                'photo': ('screenshot.png', image_buffer, 'image/png')
            }
            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }
            self.telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"

            response = requests.post(self.telegram_url, files=files, data=data)

            if response.status_code == 200:
                print(f"✅ {title} 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.QTE.emit(f"{title} 텔레그램 전송 성공")
            else:
                print(f"❌ {title} 텔레그램 전송 실패: {response.status_code} - {response.text}")
                self.QTE.emit(f"{title} 텔레그램 전송 실패")
        except Exception as e:
            print(f"{title} 텔레그램 전송 중 오류 발생: {e}")

    async def send_tele_async(self, image_buffer, caption, title):
        try:
            # image_buffer.seek(0)

            # 비동기로 사진 전송
            self.bot = Bot(token=self.bot_token)
            await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=image_buffer,
                caption=caption,
                filename="asdf",
                read_timeout=10,
                write_timeout=10,
                connect_timeout=10
            )

            print(f"✅ {title} 텔레그램 1차 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")



        except Exception as e:
            # asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=txt))
            try:
                self.bot = Bot(token=self.bot_token)
                asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=f"❌ {title} 텔레그램 1차 전송 실패:"))
            except:
                # print('텔레그램 오류')
                pass

            print(f"❌ {title} 텔레그램 1차 전송 실패: {e}")
            try:
                self.bot = Bot(token=self.bot_token)
                asyncio.run(self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=image_buffer,
                    caption=caption,
                    # filename=file_name,
                    request_kwargs={
                        'timeout': (10, 10)  # (connect_timeout, read_timeout)
                    }
                    ))
                print(f"✅ {title} 텔레그램 2차 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"❌ {title} 텔레그램 2차 전송 실패: {e}")
                try:
                    self.bot = Bot(token=self.bot_token)
                    asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=f"❌ {title} 텔레그램 2차 전송 실패:"))
                except:
                    # print('텔레그램 오류')
                    pass
    # def send_screenshot(self, filepath, image_buffer):
    #     """동기 함수에서 호출할 수 있는 래퍼"""
    #     print('send_screenshot')
    #     try:
    #         asyncio.run(self.send_tele_async(filepath, image_buffer))
    #     except:
    #         pass


    def send_to_df_chart(self):
        today = datetime.datetime.today()
        past_day = today - datetime.timedelta(days=120)
        df = stock.get_market_trading_value_by_date(past_day.strftime("%Y%m%d"), today.strftime("%Y%m%d"), "KOSPI")
        time.sleep(10)
        # df = stock.get_market_trading_value_by_date("20250910", "20250917", "KOSPI", etf=True, etn=True, elw=True)
        caption = f"거래대금-코스피 (ETF, ETN, ELW 미포함)\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        df_kospi = stock.get_index_fundamental(past_day.strftime("%Y%m%d"), today.strftime("%Y%m%d"), '1001')  # 코스피
        print(df_kospi)
        df = pd.concat([df, df_kospi[['종가']]], axis=1)
        df.rename(columns={'종가': '코스피'}, inplace=True)
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


        # 5. 텔레그램 전송
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='PNG')
        image_buffer.seek(0)
        plt.close()
        # asyncio.run(self.send_tele_async(image_buffer=image_buffer, caption=caption, title="KOSPI 지수 vs 거래대금"))
        asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="KOSPI 지수 vs 거래대금"))
        image_buffer.close()

    def send_bar_sum_graph(self,dic_data,text,color):
        print(f"{text}   {dic_data}")
        stocks = list(dic_data.keys())
        values = list(dic_data.values())
        # 막대그래프 그리기
        plt.figure(figsize=(10, 6))
        plt.bar(stocks, values,color=color)
        # 그래프 제목과 라벨 추가
        plt.title(text, fontsize=14, pad=20)
        plt.xlabel('종목명')
        plt.ylabel('거래대금 (원)')
        # 글자 겹침 방지
        plt.xticks(rotation=30)
        # 5. 텔레그램 전송
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='PNG')
        image_buffer.seek(0)
        plt.close()
#         asyncio.run(self.send_tele_async(image_buffer=image_buffer, caption=text, title="거래대금"))
        asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=text, title="거래대금"))
        image_buffer.close()

    def trend_time(self):
        현재시간 = datetime.datetime.now().replace(second=0,microsecond=0)
        self.df_trend = self.ex.add_trend(현재시간=현재시간,df_trend=self.df_trend,COND_MRKT=self.cond) #투자자별
        output=self.ex.fetch_domestic_price(market_code="F",symbol=self.ticker_future)
        self.df_trend.loc[현재시간,'KOSPI200'] = float(output['현재가'])
        print(f"{self.df_trend=}")
        # print('trend_time')
        try:
            now_on = datetime.datetime.now().strftime("%H:%M")
            url = "https://finance.naver.com/marketindex"
            res = req.urlopen(url)

            soup = BeautifulSoup(res, "html.parser")
            usd = soup.select_one("a.head.usd > div.head_info > span.value").string
            usd = usd.replace(",","")
            usd = float(usd)
            # print("usd/krw =", usd)

            # 달러인덱스 값이 안변하기 때문에 무의미
            # usd_idx = soup.select_one("a.head.usd_idx > div.head_info > span.value").string
            # usd_idx = str(usd_idx)
            # usd_idx = float(usd_idx)
#             print("달러인덱스 =", usd_idx)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
            data = requests.get('https://finance.naver.com/world/sise.naver?symbol=NII@NI225', headers=headers)

            soup = BeautifulSoup(data.text, 'html.parser')

            니케이 = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
            니케이 = 니케이.text.strip()
            니케이 = 니케이.replace(",","")
            니케이 = float(니케이)
#             print(f"{니케이= }")

            data = requests.get('https://finance.naver.com/world/sise.naver?symbol=HSI@HSI', headers=headers)

            soup = BeautifulSoup(data.text, 'html.parser')

            항셍 = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
            항셍 = 항셍.text.strip()
            항셍 = 항셍.replace(",","")
            항셍 = float(항셍)
#             print(f"{항셍= }")

            nq = yf.Ticker("NQ=F")  # 나스닥 100 선물
            df = nq.history(period="1d", interval="1m")
            나스닥 = df.loc[df.index[-1], 'Close']
#             print(f"{나스닥= }")


            # 안변하기 때문에 무의미
            # data = requests.get('https://finance.naver.com/world/sise.naver?symbol=SPI@SPX', headers=headers)
            #
            # soup = BeautifulSoup(data.text, 'html.parser')
            #
            # SNP = soup.select_one("#content > div.rate_info > div.today > p.no_today > em")
            # SNP = SNP.text.strip()
            # SNP = SNP.replace(",","")
            # SNP = float(SNP)
#             print(f"{SNP= }")

            self.df_world.loc[now_on,'달러_원',] = usd
            # self.df_world.loc[now_on,'달러_인덱스',] = usd_idx
            self.df_world.loc[now_on,'니케이',] = 니케이
            self.df_world.loc[now_on,'항셍',] = 항셍
            self.df_world.loc[now_on,'나스닥',] = 나스닥
            # self.df_world.loc[now_on,'S&P',] = SNP

        except:
            pass

    def save_data(self):
        BASE_DIR = Path(__file__).resolve().parent
        db_file = BASE_DIR.parent / "DB" / "trend.db"

        # db_file = 'DB/trend.db'
        conn = sqlite3.connect(db_file)
        self.df_trend.to_sql(datetime.datetime.now().strftime('%Y%m%d'),conn,if_exists='replace')
        conn.close()
        db_file = BASE_DIR.parent / "DB" / "DB_futopt_kis.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        try:
            list_table = np.concatenate(cursor.fetchall()).tolist()
        except:
            list_table = []
        cursor.close()
        # now_day = datetime.datetime.now().date()
        # if not 'holiday' in list_table:
        #     df_holiday = self.ex.check_holiday_domestic_stock(now_day)
        #     df_holiday.to_sql('holiday', conn, if_exists='replace')
        # else:
        #     df_holiday = pd.read_sql(f"SELECT * FROM 'holiday'", conn).set_index('날짜')
        #     ex_day = now_day+datetime.timedelta(days=90)
        #     ex_day = datetime.datetime.strftime(ex_day,'%Y%m%d')
        #     if not ex_day in df_holiday.index.tolist():
        #         df_holiday = self.ex.check_holiday_domestic_stock(now_day)
        # conn.close()
        #날짜별로 저장
        # save_folder = "DB/futopt_db"
        # import glob
        # if not os.path.exists(save_folder):        # images 폴더가 없으면 생성
        #     os.makedirs(save_folder)
        # db_files = glob.glob(os.path.join(save_folder, "*.db"))

        # if not db_files:
        #     print("폴더에 .db 파일이 없습니다.")
        #     list_table = []
        # else:
        #     파일 이름 기준으로 정렬 후 가장 최신 선택
            # latest_db = max(db_files, key=lambda f: os.path.basename(f))
            # conn_old_db = sqlite3.connect(latest_db)
            # cursor = conn_old_db.cursor()
            # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            # try:
            #     list_table = np.concatenate(cursor.fetchall()).tolist()
            # except:
            #     list_table = []
            # cursor.close()
        # now_day = datetime.datetime.strftime(now_day,'%Y%m%d')
        # conn_new_db = sqlite3.connect(f"{save_folder}/{now_day}.db")

        today = datetime.datetime.today()

        list_market = ['선물', '미니선물', '본옵션', '위클리옵션', '야간선물', '야간미니선물', '야간본옵션', '야간위클리옵션']
        for target in list_market:
            list_ticker, past_expiry_date, expiry_date,df_display = self.ex.get_expiry_date(target=target, today=today)
            for symbol in list_ticker:
                ticker_symbol = self.ex.get_futopt_symbol(target=target, symbol=symbol, expiry_date=expiry_date)
                if ticker_symbol in list_table:  # 연속저장 (기존데이터가 있을 경우)
                    df_exist = pd.read_sql(f"SELECT * FROM '{ticker_symbol}'", conn).set_index('날짜')
                else:
                    df_exist = pd.DataFrame()
                df = self.ex.get_futopt_df(target=target, ticker_symbol=ticker_symbol,symbol=symbol,
                                       past_expiry_date=past_expiry_date,expiry_date=expiry_date,
                                           df_exist=df_exist,now_dt = now_dt)
                if not df.empty:
                    df.to_sql(f"{ticker_symbol}", conn, if_exists='replace')
        conn.close()
        # conn_old_db.close()
        # conn_new_db.close()
        # try:
        #     self.send_to_df_chart()
        # except:
        #     print('self.send_to_df_chart() 조회 안됨')
        df_kospi, li_kospi = self.fetch_kospi_200_list()
        tday = datetime.datetime.today().strftime('%Y%m%d')
        self.sorting_kospi200_list(li_kospi, df_kospi, tday)
        # try:
        #     self.etf_trending()
        # except:
        #     print('etf_trending() 조회 안됨')
        self.off.emit()
    def sum_trend(self):
        if not self.df_trend.empty:
            titles = [
                "코스피",
                "선물",
                "콜옵션",
                "풋옵션",
                "콜_위클리",
                "풋_위클리",
                "ETF",
                "매수총합"
            ]
            df_trend = self.df_trend.copy()
            df_kospi = df_trend[['코스피_외인','코스피_개인','코스피_기관']]
            df_kospi['이평20_외인'] = df_kospi['코스피_외인'].rolling(window=20).mean()
            df_kospi['이평60_외인'] = df_kospi['코스피_외인'].rolling(window=60).mean()
            df_kospi['이평20_개인'] = df_kospi['코스피_개인'].rolling(window=20).mean()
            df_kospi['이평60_개인'] = df_kospi['코스피_개인'].rolling(window=60).mean()
            df_kospi['이평20_기관'] = df_kospi['코스피_기관'].rolling(window=20).mean()
            df_kospi['이평60_기관'] = df_kospi['코스피_기관'].rolling(window=60).mean()
            df_future = df_trend[['선물_외인','선물_개인','선물_기관']]
            df_future['이평20_외인'] = df_future['선물_외인'].rolling(window=20).mean()
            df_future['이평60_외인'] = df_future['선물_외인'].rolling(window=60).mean()
            df_future['이평20_개인'] = df_future['선물_개인'].rolling(window=20).mean()
            df_future['이평60_개인'] = df_future['선물_개인'].rolling(window=60).mean()
            df_future['이평20_기관'] = df_future['선물_기관'].rolling(window=20).mean()
            df_future['이평60_기관'] = df_future['선물_기관'].rolling(window=60).mean()
            df_call = df_trend[['콜옵션_외인','콜옵션_개인','콜옵션_기관']]
            df_call['이평20_외인'] = df_call['콜옵션_외인'].rolling(window=20).mean()
            df_call['이평60_외인'] = df_call['콜옵션_외인'].rolling(window=60).mean()
            df_call['이평20_개인'] = df_call['콜옵션_개인'].rolling(window=20).mean()
            df_call['이평60_개인'] = df_call['콜옵션_개인'].rolling(window=60).mean()
            df_call['이평20_기관'] = df_call['콜옵션_기관'].rolling(window=20).mean()
            df_call['이평60_기관'] = df_call['콜옵션_기관'].rolling(window=60).mean()
            df_put = df_trend[['풋옵션_외인','풋옵션_개인','풋옵션_기관']]
            df_put['이평20_외인'] = df_put['풋옵션_외인'].rolling(window=20).mean()
            df_put['이평60_외인'] = df_put['풋옵션_외인'].rolling(window=60).mean()
            df_put['이평20_개인'] = df_put['풋옵션_개인'].rolling(window=20).mean()
            df_put['이평60_개인'] = df_put['풋옵션_개인'].rolling(window=60).mean()
            df_put['이평20_기관'] = df_put['풋옵션_기관'].rolling(window=20).mean()
            df_put['이평60_기관'] = df_put['풋옵션_기관'].rolling(window=60).mean()
            df_call_w = df_trend[['콜_위클리_외인','콜_위클리_개인','콜_위클리_기관']]
            df_call_w['이평20_외인'] = df_call_w['콜_위클리_외인'].rolling(window=20).mean()
            df_call_w['이평60_외인'] = df_call_w['콜_위클리_외인'].rolling(window=60).mean()
            df_call_w['이평20_개인'] = df_call_w['콜_위클리_개인'].rolling(window=20).mean()
            df_call_w['이평60_개인'] = df_call_w['콜_위클리_개인'].rolling(window=60).mean()
            df_call_w['이평20_기관'] = df_call_w['콜_위클리_기관'].rolling(window=20).mean()
            df_call_w['이평60_기관'] = df_call_w['콜_위클리_기관'].rolling(window=60).mean()
            df_put_w = df_trend[['풋_위클리_외인','풋_위클리_개인','풋_위클리_기관']]
            df_put_w['이평20_외인'] = df_put_w['풋_위클리_외인'].rolling(window=20).mean()
            df_put_w['이평60_외인'] = df_put_w['풋_위클리_외인'].rolling(window=60).mean()
            df_put_w['이평20_개인'] = df_put_w['풋_위클리_개인'].rolling(window=20).mean()
            df_put_w['이평60_개인'] = df_put_w['풋_위클리_개인'].rolling(window=60).mean()
            df_put_w['이평20_기관'] = df_put_w['풋_위클리_기관'].rolling(window=20).mean()
            df_put_w['이평60_기관'] = df_put_w['풋_위클리_기관'].rolling(window=60).mean()
            df_etf = df_trend[['ETF_외인','ETF_개인','ETF_기관']]
            df_etf['이평20_외인'] = df_etf['ETF_외인'].rolling(window=20).mean()
            df_etf['이평60_외인'] = df_etf['ETF_외인'].rolling(window=60).mean()
            df_etf['이평20_개인'] = df_etf['ETF_개인'].rolling(window=20).mean()
            df_etf['이평60_개인'] = df_etf['ETF_개인'].rolling(window=60).mean()
            df_etf['이평20_기관'] = df_etf['ETF_기관'].rolling(window=20).mean()
            df_etf['이평60_기관'] = df_etf['ETF_기관'].rolling(window=60).mean()
            df_trend['총합_외인'] =  (df_trend['코스피_외인']+df_trend['선물_외인']+df_trend['콜옵션_외인']
                                  +df_trend['ETF_외인']+df_trend['콜_위클리_외인']
                                  -df_trend['풋옵션_외인']-df_trend['풋_위클리_외인'])
            df_trend['총합_개인'] =  (df_trend['코스피_개인']+df_trend['선물_개인']+df_trend['콜옵션_개인']
                                  +df_trend['ETF_개인']+df_trend['콜_위클리_개인']
                                  -df_trend['풋옵션_개인']-df_trend['풋_위클리_개인'])
            df_trend['총합_기관'] =  (df_trend['코스피_기관']+df_trend['선물_기관']+df_trend['콜옵션_기관']
                                  +df_trend['ETF_기관']+df_trend['콜_위클리_기관']
                                  -df_trend['풋옵션_기관']-df_trend['풋_위클리_기관'])
            df_sum = df_trend[['총합_외인','총합_개인','총합_기관']]
            df_sum['이평20_외인'] = df_sum['총합_외인'].rolling(window=20).mean()
            df_sum['이평60_외인'] = df_sum['총합_외인'].rolling(window=60).mean()
            df_sum['이평20_개인'] = df_sum['총합_개인'].rolling(window=20).mean()
            df_sum['이평60_개인'] = df_sum['총합_개인'].rolling(window=60).mean()
            df_sum['이평20_기관'] = df_sum['총합_기관'].rolling(window=20).mean()
            df_sum['이평60_기관'] = df_sum['총합_기관'].rolling(window=60).mean()
            fig, axes = plt.subplots(4, 2, figsize=(10, 14))
            axes = axes.flatten()
            # dfs = [df_kospi,df_future,df_call,df_put,df_call_w,df_put_w]
            dfs = [df_kospi,df_future,df_call,df_put,df_call_w,df_put_w,df_etf,df_sum]
            # colors = ["blue", "orange", "green"]
            # 범례 이름 통일
            # legend_labels = ["외인", "개인", "기관"]
            for i, df in enumerate(dfs):
                # 각 데이터프레임의 컬럼마다 색상 적용
                for j, col in enumerate(df.columns):
                    # df[col].plot(ax=axes[i], color=colors[j % len(colors)], label=col)
                    if col.endswith('외인'):
                        if col.startswith('이평20'):
                            df[col].plot(ax=axes[i], color="blue", linestyle="--",label='_nolegend_')
                        elif col.startswith('이평60'):
                            df[col].plot(ax=axes[i], color="blue", linestyle=":",label='_nolegend_')
                        else:
                            df[col].plot(ax=axes[i], color="blue", label="외인")
                    elif col.endswith('개인'):
                        if col.startswith('이평20'):
                            df[col].plot(ax=axes[i], color="orange", linestyle="--",label='_nolegend_')
                        elif col.startswith('이평60'):
                            df[col].plot(ax=axes[i], color="orange", linestyle=":",label='_nolegend_')
                        else:
                            df[col].plot(ax=axes[i], color="orange", label="개인")
                    elif col.endswith('기관'):
                        if col.startswith('이평20'):
                            df[col].plot(ax=axes[i], color="green", linestyle="--",label='_nolegend_')
                        elif col.startswith('이평60'):
                            df[col].plot(ax=axes[i], color="green", linestyle=":",label='_nolegend_')
                        else:
                            df[col].plot(ax=axes[i], color="green", label="기관")

                ####### 가격만
                # axes[i].set_title(titles[i], fontsize=12, fontweight="bold")  # 각 차트별 제목
                # axes[i].legend()  # 범례 표시
                # axes[i].set_xlabel("Date")  # X축 라벨
                # axes[i].set_ylabel("Value")  # Y축 라벨

                ####### 코스피선물 추가
                # 오른쪽 축 (코스피 지수)
                ax2 = axes[i].twinx()
                ax2.plot(df_trend.index, df_trend["KOSPI200"], color="red", linestyle="--", label="KOSPI200", linewidth=1.5, alpha=0.7)
                ax2.set_ylabel("KOSPI200", color="red")
                ax2.tick_params(axis="y", labelcolor="red")

                # 왼쪽 범례만 표시 (코스피는 legend에 안 넣음)
                axes[i].legend(loc="upper left")

                # 제목 및 축 설정
                axes[i].set_title(titles[i], fontsize=12, fontweight="bold")
                # axes[i].set_xlabel("날짜")
                # axes[i].set_ylabel("거래대금")
                axes[i].tick_params(axis="x", rotation=45)

            plt.tight_layout()
            # BytesIO 객체 생성 (메모리 버퍼)
            # 8. 이미지 저장
            # filename = "df_plot_sum.png"
            # filepath = os.path.join(self.save_folder, filename)

            # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)

            image_buffer = BytesIO()
            plt.savefig(image_buffer, format='PNG')
            image_buffer.seek(0)
            plt.close()
            return image_buffer
        else:
            return None

    def now_world(self):
        if not self.df_world.empty:
            titles = [
                "달러_원",
                # "달러_인덱스",
                "니케이",
                "항셍",
                "나스닥",
                # "S&P",
            ]
            df_usd = self.df_world[['달러_원']]
            #             df_usd_idx = self.df_world[['달러_인덱스']]
            니케이 = self.df_world[['니케이']]
            항셍 = self.df_world[['항셍']]
            나스닥 = self.df_world[['나스닥']]
            #             SNP = self.df_world[['S&P']]
            #             dfs = [df_usd, df_usd_idx,니케이,항셍,나스닥,SNP]
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))  # 3행 2열
            axes = axes.flatten()  # 2D 배열을 1D로 바꿔서 반복문 돌리기 편하게
            dfs = [df_usd, 니케이, 항셍, 나스닥]

            for i, df in enumerate(dfs):
                colname = df.columns[0]  # 첫 번째 컬럼 이름
                axes[i].plot(df.index, df[colname], label=colname)  # 라인차트
                axes[i].set_title(titles[i], fontsize=12, fontweight="bold")  # 각 차트별 제목

                axes[i].legend()  # 범례 표시
                # axes[i].set_xlabel("Date")  # X축 라벨
                # axes[i].set_ylabel("Value")  # Y축 라벨
                axes[i].yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
                axes[i].ticklabel_format(style='plain', axis='y')
            plt.tight_layout()

            # 8. 이미지 저장
            # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)
            image_buffer = BytesIO()
            plt.savefig(image_buffer, format='PNG')
            image_buffer.seek(0)
            plt.close()
            return image_buffer
        else:
            return None

    def get_option(self,df_call, df_put,fut_price):
        df_call = self.ex.convert_column_types(df_call)
        df_put = self.ex.convert_column_types(df_put)
        df_call_chuchul = df_call[(df_call['현재가'] > 0.3) & (df_call['현재가'] < 5)]
        df_put_chuchul = df_put[(df_put['현재가'] > 0.3) & (df_put['현재가'] < 5)]
        list_common = list(set(df_call_chuchul['행사가'].tolist()) | set(df_put_chuchul['행사가'].tolist()))
        df_call = df_call
        df_call = df_call[df_call['행사가'].isin(list_common)]
        df_put = df_put[df_put['행사가'].isin(list_common)]
        df_call.index = df_call['환산현재가']
        df_put.index = df_put['환산현재가']
        df_call = df_call[['거래량', '현재가', '행사가']]
        df_call.rename(columns={'현재가': '콜_현재가', '거래량': '콜_거래량'},
                       inplace=True)
        df_put = df_put[['현재가', '거래량']]
        df_put.rename(columns={'현재가': '풋_현재가', '거래량': '풋_거래량'},
                      inplace=True)
        merged_df = pd.merge(df_call, df_put, left_index=True, right_index=True, how='inner')
        merged_df['양합'] = merged_df['콜_현재가'] + merged_df['풋_현재가']
        # 새로운 행 생성
        new_row = pd.DataFrame(index=['현재가'],columns=['행사가'],data=fut_price)
        merged_df = pd.concat([merged_df, new_row], ignore_index=False)
        merged_df = merged_df.sort_values(by='행사가')
        # merged_df.fillna(0, inplace=True)

        # merged_df = merged_df[['콜_거래량','콜_현재가','행사가','양합','풋_현재가','풋_거래량']]
        current_col_red = merged_df.columns[1]
        current_col_blue = merged_df.columns[3]
        current_col_green = merged_df.columns[5]
        fig, ax = plt.subplots(figsize=(6, 5))
        table = ax.table(cellText=merged_df.round(2).astype(str).values,
                         rowLabels=merged_df.index,
                         colLabels=merged_df.columns,
                         loc='center',
                         )
        table.scale(1, 1)
        # fontsize = 50
        for (i_row, j_col), cell in table.get_celld().items():
            # cell.get_text().set_fontsize(fontsize)
            if i_row == 0 or j_col == -1:  # 헤더
                cell.set_text_props(weight='bold', color='black')
            else:
                col_name = merged_df.columns[j_col]

                # 현재 열이면 빨간색
                if col_name == current_col_red:
                    cell.get_text().set_color('red')
                if col_name == current_col_blue:
                    cell.get_text().set_color('blue')
                if col_name == current_col_green:
                    cell.get_text().set_color('green')
        ax.axis('off')
        plt.tight_layout()
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='PNG')
        image_buffer.seek(0)
        plt.close()
        return image_buffer

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
    def trend_estimate(self,now_time):
        df = self.ex.investor_trend('buy')
        df = df[:10]
        df['거래대금'] = df['외국인순매수거래대금']+df['기관계순매수거래대금']+df['투자신탁순매수거래대금']
        dic_buy_estimate = dict(zip(df['종목명'], df['거래대금']))
        self.send_bar_sum_graph(dic_buy_estimate,f"{now_time} - 외국인+기관 매수상위","red")
        df = self.ex.investor_trend('sell')
        df = df[:10]
        df['거래대금'] = df['외국인순매수거래대금']+df['기관계순매수거래대금']+df['투자신탁순매수거래대금']
        dic_buy_estimate = dict(zip(df['종목명'], df['거래대금']))
        self.send_bar_sum_graph(dic_buy_estimate,f"{now_time} - 외국인+기관 매도상위","blue")
    def list_KOSPI(self):
        import bs4
        from urllib.request import urlopen  # url의 소스코드를 긁어오는 기능
        url ='http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
        stock_code = pd.read_html(url, header=0,encoding="euc-kr")[0]
        stock_code = stock_code[['회사명', '종목코드']]
        # rename(columns = {'원래 이름' : '바꿀 이름'}) 칼럼 이름 바꾸기
        stock_code = stock_code.rename(columns={'회사명': 'company', '종목코드': 'code'})
        # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
        stock_code.code = stock_code.code.map('{:06d}'.format)  # 6자리가 아닌 수를 앞에 0으로 채우기 위함
        stock_code.tail(3)
        company_name = []
        for i in range(1, 21):
            page = i
            url = 'https://finance.naver.com/sise/entryJongmok.nhn?&page={page}'.format(page=page)
            source = urlopen(url).read()
            source = bs4.BeautifulSoup(source, 'lxml')
            source = source.find_all('a', target='_parent')
            for j in range(len(source)):
                name = source[j].text
                company_name.append(name)
        code = []
        for i in company_name:
          for j in range(len(stock_code)):
            if stock_code['company'][j] == i:
              code.append(stock_code['code'][j])
              break
        print(code)
        return code
    def fetch_kospi_200_list(self):
        # 종목코드 불러오기
        url ='http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
        stock_code = pd.read_html(url, header=0,encoding="euc-kr")[0]
        stock_code.code = stock_code.종목코드.map('{:06}'.format)  # 6자리가 아닌 수를 앞에 0으로 채우기 위함
        stock_code.index = stock_code.종목코드
        import bs4
        from urllib.request import urlopen  # url의 소스코드를 긁어오는 기능
        company_name = []
        for i in range(1, 21):
            page = i
            url = 'https://finance.naver.com/sise/entryJongmok.nhn?&page={page}'.format(page=page)
            source = urlopen(url).read()
            source = bs4.BeautifulSoup(source, 'lxml')
            source = source.find_all('a', target='_parent')
            for j in range(len(source)):
                name = source[j].text
                company_name.append(name)
        code = []
        for i in company_name:
            for j in range(len(stock_code)):
                if stock_code['회사명'][j] == i:
                    code.append(stock_code['종목코드'][j])
                    break
        return stock_code,code
    def sorting_kospi200_list(self,li,df_kospi,day):
        dic_frgn = {}
        dic_orgn = {}
        dic_prsn = {}
        dict_nowadays_frgn = {}
        dict_nowadays_orgn = {}
        dict_nowadays_prsn = {}
        tday = datetime.datetime.today().strftime('%Y%m%d')
        for i,ticker in enumerate(li):
            df = self.ex.investor_trend_stock(ticker)
            if day != tday:
                df = df.drop(tday, errors='ignore')
            df = df[-5:] #최근5일
            if day in df.index.tolist():
                if df.isnull().any().any():
                    print(f"{ticker} NAN 또는 0 존재")
                else:
                    dic_frgn[ticker] = df.loc[day,'외국인순매수거래대금']
                    dic_orgn[ticker] = df.loc[day,'기관계순매수거래대금']
                    dic_prsn[ticker] = df.loc[day,'개인순매수거래대금']
                    dict_nowadays_frgn[ticker] = df['외국인순매수거래대금'].sum()
                    dict_nowadays_orgn[ticker] = df['기관계순매수거래대금'].sum()
                    dict_nowadays_prsn[ticker] = df['개인순매수거래대금'].sum()
            else:
                print(f"{ticker} : {day} 데이터 없음")
            time.sleep(0.2)
        list_out = list(set(li)-set(dic_frgn.keys()))
        top_dic_frgn = sorted(dic_frgn, key=dic_frgn.get, reverse=True)[:10]
        top_dic_orgn = sorted(dic_orgn, key=dic_orgn.get, reverse=True)[:10]
        top_dic_prsn = sorted(dic_prsn, key=dic_prsn.get, reverse=True)[:10]
        top_nowadays_frgn = sorted(dict_nowadays_frgn, key=dict_nowadays_frgn.get, reverse=True)[:10]
        top_nowadays_orgn = sorted(dict_nowadays_orgn, key=dict_nowadays_orgn.get, reverse=True)[:10]
        top_nowadays_prsn = sorted(dict_nowadays_prsn, key=dict_nowadays_prsn.get, reverse=True)[:10]
        top_dic_frgn = {df_kospi.loc[x,'회사명']:dic_frgn[x] for x in top_dic_frgn}
        top_dic_orgn = {df_kospi.loc[x,'회사명']:dic_orgn[x] for x in top_dic_orgn}
        top_dic_prsn = {df_kospi.loc[x,'회사명']:dic_prsn[x] for x in top_dic_prsn}

        top_nowadays_frgn = {df_kospi.loc[x,'회사명']:dict_nowadays_frgn[x] for x in top_nowadays_frgn}
        top_nowadays_orgn = {df_kospi.loc[x,'회사명']:dict_nowadays_orgn[x] for x in top_nowadays_orgn}
        top_nowadays_prsn = {df_kospi.loc[x,'회사명']:dict_nowadays_prsn[x] for x in top_nowadays_prsn}
        top_dic_frgn = {k: v//100 for k,v in top_dic_frgn.items()}
        top_dic_orgn = {k: v//100 for k,v in top_dic_orgn.items()}
        top_dic_prsn = {k: v//100 for k,v in top_dic_prsn.items()}
        top_nowadays_frgn = {k: v//100 for k,v in top_nowadays_frgn.items()}
        top_nowadays_orgn = {k: v//100 for k,v in top_nowadays_orgn.items()}
        top_nowadays_prsn = {k: v//100 for k,v in top_nowadays_prsn.items()}
        print(f"집계 제외 종목{[df_kospi.loc[x,'회사명'] for x in list_out ]}")


        top_dic_frgn_sell = sorted(dic_frgn, key=dic_frgn.get, reverse=False)[:10]
        top_dic_orgn_sell = sorted(dic_orgn, key=dic_orgn.get, reverse=False)[:10]
        top_dic_prsn_sell = sorted(dic_prsn, key=dic_prsn.get, reverse=False)[:10]
        top_nowadays_frgn_sell = sorted(dict_nowadays_frgn, key=dict_nowadays_frgn.get, reverse=False)[:10]
        top_nowadays_orgn_sell = sorted(dict_nowadays_orgn, key=dict_nowadays_orgn.get, reverse=False)[:10]
        top_nowadays_prsn_sell = sorted(dict_nowadays_prsn, key=dict_nowadays_prsn.get, reverse=False)[:10]
        top_dic_frgn_sell = {df_kospi.loc[x,'회사명']:dic_frgn[x] for x in top_dic_frgn_sell}
        top_dic_orgn_sell = {df_kospi.loc[x,'회사명']:dic_orgn[x] for x in top_dic_orgn_sell}
        top_dic_prsn_sell = {df_kospi.loc[x,'회사명']:dic_prsn[x] for x in top_dic_prsn_sell}
        top_nowadays_frgn_sell = {df_kospi.loc[x,'회사명']:dict_nowadays_frgn[x] for x in top_nowadays_frgn_sell}
        top_nowadays_orgn_sell = {df_kospi.loc[x,'회사명']:dict_nowadays_orgn[x] for x in top_nowadays_orgn_sell}
        top_nowadays_prsn_sell = {df_kospi.loc[x,'회사명']:dict_nowadays_prsn[x] for x in top_nowadays_prsn_sell}
        top_dic_frgn_sell = {k: v//100 for k,v in top_dic_frgn_sell.items()}
        top_dic_orgn_sell = {k: v//100 for k,v in top_dic_orgn_sell.items()}
        top_dic_prsn_sell = {k: v//100 for k,v in top_dic_prsn_sell.items()}
        top_nowadays_frgn_sell = {k: v//100 for k,v in top_nowadays_frgn_sell.items()}
        top_nowadays_orgn_sell = {k: v//100 for k,v in top_nowadays_orgn_sell.items()}
        top_nowadays_prsn_sell = {k: v//100 for k,v in top_nowadays_prsn_sell.items()}

        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_dic_frgn.items()}
        self.send_bar_sum_graph(top_dic_frgn,f'외국인 순매수 거래대금 상위 [{text}]',"red")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_dic_frgn_sell.items()}
        self.send_bar_sum_graph(top_dic_frgn_sell,f'외국인 순매도 거래대금 상위 [{text}]',"blue")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_dic_orgn.items()}
        self.send_bar_sum_graph(top_dic_orgn,f'기관 순매수 거래대금 상위 [{text}]',"red")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_dic_orgn_sell.items()}
        self.send_bar_sum_graph(top_dic_orgn_sell,f'기관 순매도 거래대금 상위 [{text}]',"blue")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_dic_prsn.items()}
        self.send_bar_sum_graph(top_dic_prsn,f'개인 순매수 거래대금 상위 [{text}]',"red")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_dic_prsn_sell.items()}
        self.send_bar_sum_graph(top_dic_prsn_sell,f'개인 순매도 거래대금 상위 [{text}]',"blue")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_nowadays_frgn.items()}
        self.send_bar_sum_graph(top_nowadays_frgn,f'외국인 최근 5거래일 순매수 거래대금 상위 [{text}]',"red")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_nowadays_frgn_sell.items()}
        self.send_bar_sum_graph(top_nowadays_frgn_sell,f'외국인 최근 5거래일 순매도 거래대금 상위 [{text}]',"blue")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_nowadays_orgn.items()}
        self.send_bar_sum_graph(top_nowadays_orgn,f'기관 최근 5거래일 순매수 거래대금 상위 [{text}]',"red")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_nowadays_orgn_sell.items()}
        self.send_bar_sum_graph(top_nowadays_orgn_sell,f'기관 최근 5거래일 순매도 거래대금 상위 [{text}]',"blue")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_nowadays_prsn.items()}
        self.send_bar_sum_graph(top_nowadays_prsn,f'개인 최근 5거래일 순매수 거래대금 상위 [{text}]',"red")
        time.sleep(10)
        text = {k: f"{v:,.1f}".rstrip('0').rstrip('.')+'억' for k,v in top_nowadays_prsn_sell.items()}
        self.send_bar_sum_graph(top_nowadays_prsn_sell,f'개인 최근 5거래일 순매도 거래대금 상위 [{text}]',"blue")
        time.sleep(10)

        print(f"집계 제외 종목{[df_kospi.loc[x,'회사명'] for x in list_out ]}")


    def etf_trending(self):
        today = datetime.datetime.today()
        past_day = today - datetime.timedelta(days=20)
        df_leverage = stock.get_etf_trading_volume_and_value(past_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'), '122630', "거래대금", "순매수")
        time.sleep(1)
        df_kodex = stock.get_etf_trading_volume_and_value(past_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'), '069500', "거래대금", "순매수")
        time.sleep(1)
        df_invers = stock.get_etf_trading_volume_and_value(past_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'), '114800', "거래대금", "순매수")
        time.sleep(1)
        df_2x = stock.get_etf_trading_volume_and_value(past_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'), '252670', "거래대금", "순매수")
        time.sleep(1)
        df_200 = stock.get_index_ohlcv(past_day.strftime('%Y%m%d'), today.strftime('%Y%m%d'), "1028")

        # 방법 1: set의 교집합 사용 (가장 효율적)
        common_dates = set(df_200.index)
        for df in [df_leverage, df_kodex, df_invers, df_2x]:
            common_dates = common_dates.intersection(set(df.index))

        # 공통 날짜로 필터링
        df_200 = df_200[df_200.index.isin(common_dates)]
        df_leverage = df_leverage[df_leverage.index.isin(common_dates)]
        df_kodex = df_kodex[df_kodex.index.isin(common_dates)]
        df_invers = df_invers[df_invers.index.isin(common_dates)]
        df_2x = df_2x[df_2x.index.isin(common_dates)]

        titles = [
            "KODEX 레버리지",
            "KODEX 200",
            "KODEX 200선물인버스2X",
            "KODEX 인버스",
        ]

        df_leverage = df_leverage[["기관", "개인", "외국인"]]
        df_kodex = df_kodex[["기관", "개인", "외국인"]]
        df_invers = df_invers[["기관", "개인", "외국인"]]
        df_2x = df_2x[["기관", "개인", "외국인"]]
        df_leverage=df_leverage//100000000
        df_kodex=df_kodex//100000000
        df_invers=df_invers//100000000
        df_2x=df_2x//100000000
        print('KODEX 레버리지')
        print(df_leverage)
        print('KODEX 200')
        print(df_kodex)
        print('KODEX 인버스')
        print(df_invers)
        print('KODEX 200선물인버스2X')
        print(df_2x)

        fig, axes = plt.subplots(2, 2, figsize=(8, 8))
        axes = axes.flatten()
        dfs = [df_leverage,df_kodex,df_2x,df_invers]
        colors = ["green","orange","blue"]
        # 범례 이름 통일
        legend_labels = ["기관", "개인", "외국인"]
        for i, df in enumerate(dfs):
            # 각 데이터프레임의 컬럼마다 색상 적용
            for j, col in enumerate(df.columns):
                # df[col].plot(ax=axes[i], color=colors[j % len(colors)], label=col)
                df[col].plot(ax=axes[i], color=colors[j % len(colors)], label=legend_labels[j])


            ax2 = axes[i].twinx()
            ax2.plot(df_200.index, df_200["종가"], color="red", linestyle="--", label="KOSPI200", linewidth=1.5, alpha=0.7)
            ax2.set_ylabel("KOSPI200", color="red")
            ax2.tick_params(axis="y", labelcolor="red")

            # 왼쪽 범례만 표시 (코스피는 legend에 안 넣음)
            axes[i].legend(loc="upper left")

            # 제목 및 축 설정
            axes[i].set_title(titles[i], fontsize=12, fontweight="bold")
            # axes[i].set_xlabel("날짜")
            # axes[i].set_ylabel("거래대금")
            axes[i].tick_params(axis="x", rotation=45)

        plt.tight_layout()
        # 8. 이미지 저장
        # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)
        caption = f"ETF\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='PNG')
        image_buffer.seek(0)
        plt.close()
        # asyncio.run(self.send_tele_async(image_buffer=image_buffer, caption=caption, title="ETF"))
        asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="ETF"))
        image_buffer.close()
################################# 이하 텍스트형식으로 표시
        import platform
        # 한글 폰트 설정
        if platform.system() == 'Windows':
            plt.rcParams['font.family'] = 'Malgun Gothic'
        elif platform.system() == 'Darwin':  # macOS
            plt.rcParams['font.family'] = 'AppleGothic'
        else:  # Linux
            plt.rcParams['font.family'] = 'NanumGothic'

        # 마이너스 기호 깨짐 방지
        plt.rcParams['axes.unicode_minus'] = False
        # 각 데이터프레임을 텍스트로 표시
        # 2x2 서브플롯 생성
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        # 플롯 간격 조정
        plt.subplots_adjust(wspace=0.4, hspace=0.4)

        # axes = axes.flatten()
        for i, ax in enumerate(axes.flat):
            df = dfs[i]

            # ✅ 인덱스가 datetime이면 날짜 문자열로 변환
            if isinstance(df.index, pd.DatetimeIndex):
                df.index = df.index.strftime('%Y-%m-%d')
            # 값에 따라 색 지정: 음수=파란색, 양수=빨간색, 0=검정색
            # colors = df.applymap(lambda x: 'color: red' if x > 0 else ('color: blue' if x < 0 else 'color: black'))

            # 값 자체를 문자열로 변환
            table_data = df.round(2).astype(str)

            # matplotlib table로 표시
            table = ax.table(cellText=table_data.values,
                             rowLabels=df.index,
                             colLabels=df.columns,
                             loc='center')

            # 셀 색상 적용
            for (i_row, j_col), cell in table.get_celld().items():
                if i_row == 0 or j_col == -1:  # 헤더 행/열
                    cell.set_text_props(weight='bold', color='black')
                else:
                    val = df.iloc[i_row - 1, j_col]
                    if val > 0:
                        cell.get_text().set_color('red')
                    elif val < 0:
                        cell.get_text().set_color('blue')
                    else:
                        cell.get_text().set_color('black')

            ax.axis('off')
            ax.set_title(titles[i], fontsize=12)

        plt.tight_layout()
        # filename = 'DB/df_etf.png'
        # plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        if df_leverage.index[-1] == datetime.datetime.now().date().strftime('%Y-%m-%d'):
            print('금일 데이터 있음')
            orgn=df_leverage.loc[df_leverage.index[-1],'기관']+df_kodex.loc[df_kodex.index[-1],'기관']+df_invers.loc[df_invers.index[-1],'기관']+df_2x.loc[df_2x.index[-1],'기관']
            prsn=df_leverage.loc[df_leverage.index[-1],'개인']+df_kodex.loc[df_kodex.index[-1],'개인']+df_invers.loc[df_invers.index[-1],'개인']+df_2x.loc[df_2x.index[-1],'개인']
            frgn=df_leverage.loc[df_leverage.index[-1],'외국인']+df_kodex.loc[df_kodex.index[-1],'외국인']+df_invers.loc[df_invers.index[-1],'외국인']+df_2x.loc[df_2x.index[-1],'외국인']
            caption = f"지수 ETF 총 합 = 외국인: {frgn}억, 기관: {orgn}억, 개인: {prsn}억"

        else:
            caption = f"ETF\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='PNG')
        image_buffer.seek(0)
        plt.close()
        # asyncio.run(self.send_tele_async(image_buffer=image_buffer, caption=caption, title="ETF"))
        asyncio.run(self.send_to_telegram(image_buffer=image_buffer, caption=caption, title="ETF"))
        image_buffer.close()





class Window(QMainWindow):

    def __init__(self, BOT_TOKEN, CHAT_ID):
        super().__init__()
        QVB_main = QVBoxLayout()
        self.bool_light = True
        self.QTE = QTextEdit()
        self.QPB = QPushButton()
        QVB_main.addWidget(self.QTE)
        QVB_main.addWidget(self.QPB)
        QW_main = QWidget()
        QW_main.setLayout(QVB_main)
        self.setCentralWidget(QW_main)

        ex = KIS.KoreaInvestment(market='국내선옵',mock=False)
        ticker_future = ex.display_fut().index[0]
        df_call, df_put, cond, past_day, ex_day = ex.display_opt_weekly(datetime.datetime.now())
        # BASE_DIR = Path(__file__).resolve().parent
        # db_file = BASE_DIR.parent / "DB" / "DB_futopt_kis.db"

        # conn = sqlite3.connect(db_file)
        # cursor = conn.cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # try:
        #     list_table = np.concatenate(cursor.fetchall()).tolist()
        # except:
        #     list_table = []
        # cursor.close()
        # now_day = datetime.datetime.now().date()
        # if not 'holiday' in list_table:
        #     df_holiday = ex.check_holiday_domestic_stock(now_day)
        #     df_holiday.to_sql('holiday', conn, if_exists='replace')
        # else:
        #     df_holiday = pd.read_sql(f"SELECT * FROM 'holiday'", conn).set_index('날짜')
        #     ex_day = now_day+datetime.timedelta(days=90)
        #     ex_day = datetime.datetime.strftime(ex_day,'%Y%m%d')
        #     if not ex_day in df_holiday.index.tolist():
        #         df_holiday = ex.check_holiday_domestic_stock(now_day)
        # conn.close()

        # 봇 인스턴스 생성 (images 폴더에 저장)
        self.start_time = QTime(8,40,0)
        self.finish_time = QTime(15,45,0)
        # weekday(): 월요일=0, 화요일=1, ..., 토요일=5, 일요일=6

        self.thread = QThread()

        self.worker = Worker(self, BOT_TOKEN, CHAT_ID,ex,cond,ticker_future)

        self.worker.moveToThread(self.thread)
        self.worker.QTE.connect(self.QTE_txt)
        self.worker.off.connect(self.system_off)


        self.timer = QTimer()
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)
        if df_holiday.loc[datetime.datetime.today().date().strftime("%Y%m%d"), '개장일'] == "N":
            self.system_off()
    def LED_effect(self):
        self.bool_light = not self.bool_light
        if self.bool_light == True:
            self.QPB.setStyleSheet("background-color: green; border-radius: 25px;")
        else:
            self.QPB.setStyleSheet("background-color: gray; border-radius: 25px;")
    def QTE_txt(self,string):
        text = self.QTE.toPlainText()
        # print(string)
        # self.QTE.setText(text+"\n"+string)
        self.QTE.setText(string)

    def send_asdf(self):
        print('send_asdf')
    def check_orders(self):
        print('check_orders')
    def system_off(self):
        print('시스템을 종료합니다.')
        os.system("shutdown /s /t 0")  # 윈도우 죵료
        # quit()
    def on_tick(self):
        now = QTime.currentTime()
        if now > self.start_time:
            self.LED_effect()
            if now.second() == 0: #1분마다
                self.worker.trend_time()
                if now.hour() == 10 and now.minute() == 10:
                    self.worker.trend_estimate(f"{now.hour()}:{now.minute()}")
                if now.hour() == 11 and now.minute() == 30:
                    self.worker.trend_estimate(f"{now.hour()}:{now.minute()}")
                if now.hour() == 13 and now.minute() == 30:
                    self.worker.trend_estimate(f"{now.hour()}:{now.minute()}")
                if now.hour() == 14 and now.minute() == 40:
                    self.worker.trend_estimate(f"{now.hour()}:{now.minute()}")
            if (now.minute() % 15 == 0) & (now.second() == 0): #15분마다
                self.worker.capture_and_send()
            if now > self.finish_time:
                self.worker.save_data()




if __name__ == "__main__":
    # 텔레그램 봇 설정
    BOT_TOKEN = "1883109215:AAHM6-d42-oNmdDO6vmT3SWxB0ICH_od86M"  # 여기에 봇 토큰을 입력하세요
    # CHAT_ID = "1644533124"  # 여기에 채팅 ID를 입력하세요 (bot 채팅)
    CHAT_ID = "-1002919914781"  # 여기에 채팅 ID를 입력하세요 (텔레그램 채널)
    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    app = QApplication([])
    main_table = Window(BOT_TOKEN,CHAT_ID)
    main_table.setMinimumSize(600, 400)
    main_table.show()
    app.exec()
