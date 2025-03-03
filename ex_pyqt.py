import pandas as pd
import matplotlib.pyplot as plt
import requests
import time
from datetime import datetime, timedelta
import matplotlib.dates as mdates


def get_funding_rate_history(symbols, limit=100):
    """
    바이비트 API를 사용하여 여러 심볼의 펀딩 수수료율 히스토리를 가져오는 함수

    Parameters:
    symbols (list): 펀딩 수수료율을 가져올 심볼 리스트 (예: ["BTCUSDT", "ETHUSDT"])
    limit (int): 각 심볼당 가져올 데이터 포인트 수 (최대 200)

    Returns:
    dict: 심볼별 펀딩 수수료율 데이터프레임을 포함하는 딕셔너리
    DataFrame: 모든 심볼의 펀딩 수수료율을 포함하는 통합 데이터프레임
    """
    base_url = "https://api.bybit.com"
    endpoint = "/v5/market/funding/history"

    # 결과를 저장할 딕셔너리와 통합 데이터프레임을 위한 리스트 초기화
    results = {}
    all_data = []

    for symbol in symbols:
        # API 요청 파라미터 설정
        params = {
            'category': 'linear',
            'symbol': symbol,
            'limit': limit
        }

        try:
            # API 요청
            response = requests.get(base_url + endpoint, params=params)
            data = response.json()

            # 응답 확인
            if data['retCode'] == 0 and 'list' in data['result']:
                # 데이터 파싱
                funding_data = data['result']['list']

                # 데이터프레임 생성
                df = pd.DataFrame(funding_data)

                # 컬럼 변환
                df['fundingRate'] = df['fundingRate'].astype(float)
                df['fundingRateTimestamp'] = pd.to_datetime(df['fundingRateTimestamp'].astype(int), unit='ms')

                # 심볼 정보 추가
                df['symbol'] = symbol

                # 결과 저장
                results[symbol] = df
                all_data.append(df)

                # API 호출 사이에 약간의 지연 추가
                time.sleep(0.5)
            else:
                print(f"{symbol} 데이터 가져오기 실패: {data}")
        except Exception as e:
            print(f"{symbol} 요청 중 오류 발생: {e}")

    # 모든 심볼 데이터를 하나의 데이터프레임으로 통합
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return results, combined_df
    else:
        return results, pd.DataFrame()


def plot_funding_rates(symbol_dfs, symbols):
    """
    여러 심볼의 펀딩 수수료율을 하나의 차트에 시각화하는 함수

    Parameters:
    symbol_dfs (dict): 심볼별 펀딩 수수료율 데이터프레임을 포함하는 딕셔너리
    symbols (list): 차트에 표시할 심볼 리스트
    """
    plt.figure(figsize=(12, 6))

    for symbol in symbols:
        if symbol in symbol_dfs:
            df = symbol_dfs[symbol]
            plt.plot(df['fundingRateTimestamp'], df['fundingRate'].astype(float) * 100, label=symbol)

    plt.title('바이비트 펀딩 수수료율 히스토리 (%)')
    plt.xlabel('날짜')
    plt.ylabel('펀딩 수수료율 (%)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # x축 날짜 포맷 설정
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()


# 사용 예시
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]  # 관심 있는 심볼 리스트
symbol_dfs, combined_df = get_funding_rate_history(symbols, limit=100)

# 데이터프레임 출력
for symbol, df in symbol_dfs.items():
    print(f"\n{symbol} 펀딩 수수료율:")
    print(df[['fundingRateTimestamp', 'fundingRate', 'symbol']].head())

# 차트 그리기
plot_funding_rates(symbol_dfs, symbols)

# 통합 데이터프레임 확인
print("\n통합 데이터프레임:")
print(combined_df.head())

# 데이터 분석 - 평균 펀딩 수수료율
print("\n심볼별 평균 펀딩 수수료율:")
avg_rates = combined_df.groupby('symbol')['fundingRate'].mean() * 100
print(avg_rates)

# 데이터 분석 - 최대/최소 펀딩 수수료율
print("\n심볼별 최대 펀딩 수수료율:")
max_rates = combined_df.groupby('symbol')['fundingRate'].max() * 100
print(max_rates)

print("\n심볼별 최소 펀딩 수수료율:")
min_rates = combined_df.groupby('symbol')['fundingRate'].min() * 100
print(min_rates)

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