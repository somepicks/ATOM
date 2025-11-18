import os
import time

import numpy as np
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
import KIS
import requests
from bs4 import BeautifulSoup
import urllib.request as req
from pprint import pprint
from matplotlib.ticker import ScalarFormatter
import yfinance as yf

class ScreenCaptureBot():
    def __init__(self, bot_token, chat_id,ex,cond, ticker_future,save_folder="images"):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.telegram_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        self.save_folder = save_folder
        self.ticker_future = ticker_future
        self.ex = ex
        self.cond = cond
        self.df_trend = pd.DataFrame()
        self.df_world = pd.DataFrame()

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
    def send_bar_sum_graph(self,dic_data,text):
        print(f"{text}   {dic_data}")
        stocks = list(dic_data.keys())
        values = list(dic_data.values())
        # 막대그래프 그리기
        plt.figure(figsize=(10, 6))
        plt.bar(stocks, values)
        # 그래프 제목과 라벨 추가
        plt.title(text, fontsize=14, pad=20)
        plt.xlabel('종목명')
        plt.ylabel('거래대금 (원)')
        # 글자 겹침 방지
        plt.xticks(rotation=30)
        filename = "trend_sum.png"
        plt.savefig(filename, bbox_inches="tight", pad_inches=0.1, dpi=150)
        plt.close()
        # 그래프 표시

        # 5. 텔레그램 전송
        files = {'photo': open(filename, 'rb')}
        data = {
            'chat_id': self.chat_id,
            'caption': text
        }
        response = requests.post(self.telegram_url, data=data, files=files)

        if response.status_code == 200:
            print(f"✅ 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ 텔레그램 전송 실패: {response.status_code} - {response.text}")
        time.sleep(1)
    def send_to_df_etf(self):
        pass
    def ect_time(self):
        pass
    def trend_time(self):
        현재시간 = datetime.datetime.now()
        self.df_trend = self.ex.add_trend(현재시간,df_trend=self.df_trend,COND_MRKT=self.cond) #투자자별
        output=self.ex.fetch_domestic_price(market_code="F",symbol=self.ticker_future)
        self.df_trend.loc[현재시간,'KOSPI200'] = float(output['현재가'])

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
        import sqlite3
        db_file = 'DB/trend.db'
        conn = sqlite3.connect(db_file)
        self.df_trend.to_sql(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),conn,if_exists='replace')



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

        ######################## 이하 투자자별 거래대금
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
            df_future = df_trend[['선물_외인','선물_개인','선물_기관']]
            df_call = df_trend[['콜옵션_외인','콜옵션_개인','콜옵션_기관']]
            df_put = df_trend[['풋옵션_외인','풋옵션_개인','풋옵션_기관']]
            df_call_w = df_trend[['콜_위클리_외인','콜_위클리_개인','콜_위클리_기관']]
            df_put_w = df_trend[['풋_위클리_외인','풋_위클리_개인','풋_위클리_기관']]
            df_etf = df_trend[['ETF_외인','ETF_개인','ETF_기관']]
            df_trend['매수_외인'] =  (df_trend['코스피_외인']+df_trend['선물_외인']+df_trend['콜옵션_외인']
                                  +df_trend['ETF_외인']+df_trend['콜_위클리_외인']
                                  -df_trend['풋옵션_외인']-df_trend['풋_위클리_외인'])
            df_trend['매수_개인'] =  (df_trend['코스피_개인']+df_trend['선물_개인']+df_trend['콜옵션_개인']
                                  +df_trend['ETF_개인']+df_trend['콜_위클리_개인']
                                  -df_trend['풋옵션_개인']-df_trend['풋_위클리_개인'])
            df_trend['매수_기관'] =  (df_trend['코스피_기관']+df_trend['선물_기관']+df_trend['콜옵션_기관']
                                  +df_trend['ETF_기관']+df_trend['콜_위클리_기관']
                                  -df_trend['풋옵션_기관']-df_trend['풋_위클리_기관'])
            df_sum = df_trend[['매수_외인','매수_개인','매수_기관']]

            fig, axes = plt.subplots(4, 2, figsize=(10, 14))
            axes = axes.flatten()
            # dfs = [df_kospi,df_future,df_call,df_put,df_call_w,df_put_w]
            dfs = [df_kospi,df_future,df_call,df_put,df_call_w,df_put_w,df_etf,df_sum]
            colors = ["blue", "orange", "green"]
            # 범례 이름 통일
            legend_labels = ["외인", "개인", "기관"]
            for i, df in enumerate(dfs):
                # 각 데이터프레임의 컬럼마다 색상 적용
                for j, col in enumerate(df.columns):
                    # df[col].plot(ax=axes[i], color=colors[j % len(colors)], label=col)
                    df[col].plot(ax=axes[i], color=colors[j % len(colors)], label=legend_labels[j])

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

            # 8. 이미지 저장
            filename = "DB/df_plot_sum.png"
            # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)
            plt.savefig(filename)
            plt.close()
            caption = f"거래대금-코스피 (ETF, ETN, ELW 미포함)\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            # 5. 텔레그램 전송
            files = {'photo': open(filename, 'rb')}
            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }
            response = requests.post(self.telegram_url, data=data, files=files)

            if response.status_code == 200:
                print(f"✅ 거래대금 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ 거래대금 텔레그램 전송 실패: {response.status_code} - {response.text}")
        ######################## 이하 세계는 지금
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
            dfs = [df_usd, 니케이,항셍,나스닥]
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))  # 3행 2열
            axes = axes.flatten()  # 2D 배열을 1D로 바꿔서 반복문 돌리기 편하게

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
            filename = "DB/df_plot_world.png"
            # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)
            plt.savefig(filename)
            plt.close()
            caption = f"world\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            # 5. 텔레그램 전송
            files = {'photo': open(filename, 'rb')}
            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }
            response = requests.post(self.telegram_url, data=data, files=files)

            if response.status_code == 200:
                print(f"✅ world 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ world 텔레그램 전송 실패: {response.status_code} - {response.text}")
        ################################### 옵션 현재가

        df_call_week, df_put_week, cond, past_day, ex_day = self.ex.display_opt_weekly(datetime.datetime.now())
        # d = (ex_day-datetime.datetime.now().date()).days
        df = self.ex.display_fut()
        ticker_fut = df.index[0]
        output = self.ex.fetch_domestic_price(market_code="F", symbol=ticker_fut)
        txt=f'위클리 옵션 만기일:{ex_day} [-{(ex_day-datetime.datetime.now().date()).days} 일]'
        self.get_option(df_call_week, df_put_week,txt)
        df_call, df_put, past_date, expiry_date = self.ex.display_opt(datetime.datetime.now())
        txt=f"본옵션 만기일:{expiry_date} [-{(expiry_date-datetime.datetime.now().date()).days} 일] 베이시스: {output['베이시스']} 이론가: {['이론가']}"
        self.get_option(df_call, df_put,txt,output['현재가'])

    def get_option(self,df_call, df_put,caption,fut_price):
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
        # 8. 이미지 저장
        filename = "DB/df_plot_opt.png"
        # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)
        plt.savefig(filename)
        plt.close()
        # caption = f"ETF\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # 5. 텔레그램 전송
        files = {'photo': open(filename, 'rb')}
        data = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        response = requests.post(self.telegram_url, data=data, files=files)


        # df_call, df_put, past_date, expiry_date = ex.display_opt(datetime.datetime.today())

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
    def list_KOSPI(self):
        import bs4
        from urllib.request import urlopen  # url의 소스코드를 긁어오는 기능
        stock_code = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
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
        stock_code = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
        # stock_code = stock_code[['회사명', '종목코드']]
        # rename(columns = {'원래 이름' : '바꿀 이름'}) 칼럼 이름 바꾸기
        # stock_code = stock_code.rename(columns={'회사명': 'company', '종목코드': 'code'})
        # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
        stock_code.code = stock_code.종목코드.map('{:06}'.format)  # 6자리가 아닌 수를 앞에 0으로 채우기 위함
        stock_code.index = stock_code.종목코드
        # stock_code.tail(3)
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
    def sorting_kospi200_list(self,li,df_kospi):
        dic_frgn = {}
        dic_orgn = {}
        dic_prsn = {}
        dict_nowadays_frgn = {}
        dict_nowadays_orgn = {}
        dict_nowadays_prsn = {}
        tday = datetime.datetime.today().strftime('%Y%m%d')
        for i,ticker in enumerate(li):
            df = self.ex.investor_trend_stock(ticker)
            print(ticker)
            print(df)
            df = df[-5:]
            if tday in df.index.tolist():
                if df.isnull().any().any():
                    print(f"{ticker} NAN 또는 0 존재")
                else:
                    dic_frgn[ticker] = df.loc[tday,'외국인순매수거래대금']
                    dic_orgn[ticker] = df.loc[tday,'기관계순매수거래대금']
                    dic_prsn[ticker] = df.loc[tday,'개인순매수거래대금']
                    dict_nowadays_frgn[ticker] = df['외국인순매수거래대금'].sum()
                    dict_nowadays_orgn[ticker] = df['기관계순매수거래대금'].sum()
                    dict_nowadays_prsn[ticker] = df['개인순매수거래대금'].sum()
            else:
                print(f"{ticker} : {tday} 데이터 없음")
            if i == 10:
                break
            time.sleep(1)
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
        self.send_bar_sum_graph(top_dic_frgn,'외국인 순매수 거래대금 상위')
        self.send_bar_sum_graph(top_dic_orgn,'기관 순매수 거래대금 상위')
        self.send_bar_sum_graph(top_dic_prsn,'개인 순매수 거래대금 상위')
        self.send_bar_sum_graph(top_nowadays_frgn,'외국인 최근 5거래일 순매수 거래대금 상위')
        self.send_bar_sum_graph(top_nowadays_orgn,'기관 최근 5거래일 순매수 거래대금 상위')
        self.send_bar_sum_graph(top_nowadays_prsn,'개인 최근 5거래일 순매수 거래대금 상위')
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
        filename = "DB/df_plot_etf.png"
        # plt.savefig(bbox_inches="tight", pad_inches=0.1, dpi=150)
        plt.savefig(filename)
        plt.close()
        caption = f"ETF\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # 5. 텔레그램 전송
        files = {'photo': open(filename, 'rb')}
        data = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        response = requests.post(self.telegram_url, data=data, files=files)
        if response.status_code == 200:
            print(f"✅ 거래대금 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ 거래대금 텔레그램 전송 실패: {response.status_code} - {response.text}")

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
            colors = df.applymap(lambda x: 'color: red' if x > 0 else ('color: blue' if x < 0 else 'color: black'))

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
        filename = 'DB/df_etf.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print("이미지가 'df_etf.png'로 저장되었습니다.")
        plt.close()
        print(df_leverage.index[-1])
        print(df_leverage.index.dtype)
        print(df_leverage.index[-1])
        print(datetime.datetime.now().date())
        if df_leverage.index[-1] == datetime.datetime.now().date().strftime('%Y-%m-%d'):
            print('금일 데이터 있음')
            orgn=df_leverage.loc[df_leverage.index[-1],'기관']+df_kodex.loc[df_kodex.index[-1],'기관']+df_invers.loc[df_invers.index[-1],'기관']+df_2x.loc[df_2x.index[-1],'기관']
            prsn=df_leverage.loc[df_leverage.index[-1],'개인']+df_kodex.loc[df_kodex.index[-1],'개인']+df_invers.loc[df_invers.index[-1],'개인']+df_2x.loc[df_2x.index[-1],'개인']
            frgn=df_leverage.loc[df_leverage.index[-1],'외국인']+df_kodex.loc[df_kodex.index[-1],'외국인']+df_invers.loc[df_invers.index[-1],'외국인']+df_2x.loc[df_2x.index[-1],'외국인']
            caption = f"지수 ETF 총 합 = 외국인: {frgn}억, 기관: {orgn}억, 개인: {prsn}억"

        else:

            caption = f"ETF\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # 5. 텔레그램 전송
        files = {'photo': open(filename, 'rb')}
        data = {
            'chat_id': self.chat_id,
            'caption': caption
        }
        response = requests.post(self.telegram_url, data=data, files=files)
        if response.status_code == 200:
            print(f"✅ 거래대금 텔레그램 전송 성공: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ 거래대금 텔레그램 전송 실패: {response.status_code} - {response.text}")






def main():
    # 텔레그램 봇 설정
    BOT_TOKEN = "1883109215:AAHM6-d42-oNmdDO6vmT3SWxB0ICH_od86M"  # 여기에 봇 토큰을 입력하세요
    CHAT_ID = "1644533124"  # 여기에 채팅 ID를 입력하세요 (bot 채팅)
    # CHAT_ID = "-1002919914781"  # 여기에 채팅 ID를 입력하세요 (텔레그램 채널)
    # api = 'PS03yEfsiLWpVOZFyv1IoLiprgXvpHcQQMCb'
    # secrets = 'MBLgiwO7TG3JKPTYpqLylhiWen8KGtHN2jmxr+VjkM4c9tTb9Dxt0KlRkMoVBDhu4D2QeGsnMa4kPU0t2V1q9c5YjAaEOLTMp9T15cHsaqg8Y4jdN2uDm5+JMFGFzhOplG8Ftm/DAtPkz/xu6rT49/YGzrXcxNyB/gA0DPw9zJ5pt8ZqYFk='
    # acc = '63761517-01'

    # ex = KIS.KoreaInvestment(api_key=api,secret_key=secrets,acc_no=acc,market='국내선옵',mock=False)
    ex = KIS.KoreaInvestment(market='국내선옵',mock=False)
    # df = ex.display_fut()
    # ticker_fut = df.index[0]
    # output = ex.fetch_domestic_price(market_code="F",symbol=ticker_fut)

    # pprint(ex.investor_trend_stock("005930"))
    # pprint(ex.investor_trend_estimate("005930"))
    ticker_future=ex.display_fut().index[0]

    df_call, df_put, cond, past_day, ex_day = ex.display_opt_weekly(datetime.datetime.now())

    # 봇 인스턴스 생성 (images 폴더에 저장)
    bot = ScreenCaptureBot(BOT_TOKEN, CHAT_ID,ex,cond,ticker_future, save_folder="images")
    df_kospi,li_kospi = bot.fetch_kospi_200_list()
    li_kospi = stock.get_index_portfolio_deposit_file("1028")
    # screen_width, screen_height = bot.get_screen_size()
    # print(f"현재 화면 크기: {screen_width} x {screen_height}")
    # 해당 행사가를 가진 행만 추출

    # 기존 저장된 이미지 개수 확인
    # saved_count = bot.get_saved_images_count()
    # print(f"현재 저장된 이미지 개수: {saved_count}개")

    # 캡처 영역 설정 (예시: 화면 전체의 왼쪽 절반)
    x1=0
    y1=100
    x2=1700
    y2=2000
    bot.set_capture_region(x1, y1, x2, y2)

    # 스케줄 설정 - 1시간마다 실행
    #################################### test
    # bot.trend_time()
    # bot.capture_and_send()
    # quit()
    ####################################
    bot.sorting_kospi200_list(li_kospi, df_kospi)

    # schedule.every(15).minutes.do(bot.capture_and_send)
    while True:
        now = datetime.datetime.now()
        if now.hour > 8 and now.minute >= 44:
            break
        time.sleep(1)
    schedule.every(1).minutes.do(bot.trend_time)
    schedule.every(15).minutes.do(bot.capture_and_send)

    bot.send_to_df_chart()
    # 스케줄러 실행
    # capture_signal = False
    try:
        while True:
            # 현재 시간 확인
            now = datetime.datetime.now()
            # if now.hour == 9 and now.minute >= 45:
            #     if capture_signal == False:
            #         capture_signal = True
            # 오후 3시 30분 체크 (15:30)
            if now.hour >= 15 and now.minute >= 45:
                print(f"\n🕐 오후 3시 45분넘어 프로그램을 종료합니다.")
                time.sleep(600)

                bot.save_data()
                # final_count = bot.get_saved_images_count()

                # print(f"📁 총 {final_count}개의 이미지가 저장되어 있습니다.")
                bot.capture_and_send()
                bot.send_to_df_chart()
                bot.sorting_kospi200_list(li_kospi, df_kospi)
                bot.etf_trending()

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