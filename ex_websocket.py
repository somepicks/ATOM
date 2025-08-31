# # pingpong 및 연결 종료 발생 시 자동 재 시작 추가
# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
# from PyQt5.QtCore import QThread, pyqtSignal
# import asyncio
# import websockets
# import json
# import requests
# import time
#
#
# class WebSocket(QThread):
#     event_data = pyqtSignal(str)
#
#     def __init__(self):
#         super().__init__()
#         self.is_running = True
#
#     def get_real_time_key(self):
#         global APP_KEY
#         global APP_SECRET
#         global Virtual_Actual_check
#
#         BASE_URL = "https://openapivts.koreainvestment.com:29443"  #모의
#
#         url = f"{BASE_URL}/oauth2/Approval"
#         headers = {"Content-Type": "application/json"}
#         param = {"appkey": APP_KEY, "secretkey": APP_SECRET}
#         response = requests.post(url, headers=headers, json=param)
#
#         if response.status_code == 200:
#             data = response.json()
#             real_time_key = data.get("approval_key")
#             return real_time_key
#         else:
#             return None
#
#     async def connect(self):
#         global designated_stock_List
#
#         try:
#             g_approval_key = self.get_real_time_key()
#             if not g_approval_key:
#                 return
#
#             url = 'ws://ops.koreainvestment.com:31000' # 모의투자계좌
#             code_list = [['1', 'H0IFCNT0', "101V12"]]
#
#             senddata_list = []
#
#             for i, j, k in code_list:
#                 temp = '{"header":{"approval_key": "%s","custtype":"P","tr_type":"%s","content-type":"utf-8"},"body":{"input":{"tr_id":"%s","tr_key":"%s"}}}' % (
#                     g_approval_key, i, j, k)
#                 senddata_list.append(temp)
#
#             async with websockets.connect(url, ping_interval=None) as websocket:
#                 for senddata in senddata_list:
#                     await websocket.send(senddata)
#                     await asyncio.sleep(0.5)
#                     self.event_data.emit(f"Input Command: {senddata}")
#
#                 while self.is_running:
#                     data = await websocket.recv()
#
#                     if data[0] == '0' or data[0] == '1':
#                         self.event_data.emit(f"Received Data: {data}")
#
#                     else:
#                         jsonObject = json.loads(data)
#                         trid = jsonObject["header"]["tr_id"]
#
#                         if trid != "PINGPONG":
#                             rt_cd = jsonObject["body"]["rt_cd"]
#
#                             if rt_cd == '1':
#                                 if jsonObject["body"]["msg1"] != 'ALREADY IN SUBSCRIBE':
#                                     print("### ERROR RETURN CODE")
#                                 break
#
#                             elif rt_cd == '0':
#                                 print("### RETURN CODE")
#                                 if trid == "H0IFCNI0" or trid == "H0MFCNI0" or trid == "H0EUCNI0":  # 지수/상품/주식 선물옵션 & 야간선물옵션
#                                     aes_key = jsonObject["body"]["output"]["key"]
#                                     aes_iv = jsonObject["body"]["output"]["iv"]
#                                     print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))
#
#                         elif trid == "PINGPONG":
#                             print("### RECV [PINGPONG] [%s]" % (data))
#                             await websocket.pong(data)  # 요게 없으면 강제 연결 종료됨
#                             print("### SEND [PINGPONG] [%s]" % (data))
#
#         except Exception as e:
#             self.event_data.emit(f"Error: {str(e)}")
#             time.sleep(0.1)
#             await connect()              # 웹소켓 다시 시작
#
#     def run(self):
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(self.connect())
#
#     def stop(self):
#         self.is_running = False
#         self.quit()
#         self.wait()
#
#
# class MyWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.start_button = QPushButton("Start WebSocket")
#         self.stop_button = QPushButton("Stop WebSocket")
#
#         self.start_button.clicked.connect(self.start_websocket)
#         self.stop_button.clicked.connect(self.stop_websocket)
#
#         layout = QVBoxLayout()
#         # layout.addWidget(self.label)
#         layout.addWidget(self.start_button)
#         layout.addWidget(self.stop_button)
#
#         container = QWidget()
#         container.setLayout(layout)
#         self.setCentralWidget(container)
#
#         self.websocket_thread = WebSocket()
#         self.websocket_thread.event_data.connect(self.update_label)
#
#     def start_websocket(self):
#          self.websocket_thread.start()
#
#     def stop_websocket(self):
#         self.websocket_thread.stop()
#
#     def update_label(self, data):
#         self.label.setText(data)
#
# if __name__ == "__main__":
#     APP_KEY = ""
#     APP_SECRET = ""
#     app = QApplication([])
#     window = MyWindow()
#     window.show()
#     app.exec_()








# import ccxt
# import pandas as pd
# import websocket
# import json
# import threading
# import time
# from datetime import datetime, timedelta
# import numpy as np
#
#
# class BinanceOHLCVManager:
#     def __init__(self, symbols=['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT']):
#         self.symbols = symbols
#         self.symbol_map = {symbol: symbol.replace('/', '').lower() + '@kline_1m' for symbol in symbols}
#         self.reverse_symbol_map = {v.split('@')[0]: k for k, v in self.symbol_map.items()}
#         print(self.symbols)
#         print(self.symbol_map)
#         print(self.reverse_symbol_map)
#         quit()
#         # CCXT 바이낸스 객체 초기화
#         self.exchange = ccxt.binance({
#             'apiKey': '',  # API 키가 필요하면 입력
#             'secret': '',  # 시크릿이 필요하면 입력
#             'sandbox': False,
#             'enableRateLimit': True,
#         })
#
#         # 데이터 저장소
#         self.ohlcv_data = {}
#         self.current_candles = {}  # 현재 진행중인 캔들
#
#         # 웹소켓 관련
#         self.ws = None
#         self.ws_url = "wss://stream.binance.com:9443/ws/"
#         self.running = False
#
#         # 콜백 함수들
#         self.on_candle_update = None
#         self.on_candle_complete = None
#
#     def fetch_initial_data(self, limit=1000):
#         print("초기 OHLCV 데이터를 가져오는 중...")
#         for symbol in self.symbols:
#             try:
#                 print(f"  {symbol} 데이터 가져오는 중...")
#
#                 # 1분봉 데이터 가져오기
#                 ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=limit)
#
#                 # DataFrame으로 변환
#                 df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#                 df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#                 df.set_index('timestamp', inplace=True)
#
#                 # 저장
#                 self.ohlcv_data[symbol] = df
#
#                 print(f"  {symbol}: {len(df)}개 캔들 로드 완료 (최신: {df.index[-1]})")
#
#                 # 마지막 캔들은 현재 진행중인 캔들일 수 있으므로 별도 저장
#                 self.current_candles[symbol] = df.iloc[-1].to_dict()
#
#             except Exception as e:
#                 print(f"  {symbol} 데이터 가져오기 실패: {e}")
#
#         print(f"초기 데이터 로드 완료! 총 {len(self.ohlcv_data)}개 심볼")
#
#     def on_message(self, ws, message):
#         """웹소켓 메시지 처리"""
#         try:
#             data = json.loads(message)
#
#             if 'k' in data:  # kline 데이터
#                 kline = data['k']
#                 symbol_ws = kline['s'].lower()  # btcusdt
#
#                 # 심볼 매핑
#                 if symbol_ws in self.reverse_symbol_map:
#                     symbol = self.reverse_symbol_map[symbol_ws]  # BTC/USDT
#
#                     # 캔들 데이터 추출
#                     timestamp = pd.to_datetime(kline['t'], unit='ms')  # 시작 시간
#                     open_price = float(kline['o'])
#                     high_price = float(kline['h'])
#                     low_price = float(kline['l'])
#                     close_price = float(kline['c'])
#                     volume = float(kline['v'])
#                     is_closed = kline['x']  # 캔들이 완료되었는지
#
#                     # 새로운 캔들 데이터
#                     new_candle = {
#                         'open': open_price,
#                         'high': high_price,
#                         'low': low_price,
#                         'close': close_price,
#                         'volume': volume
#                     }
#
#                     if is_closed:
#                         # 캔들이 완료된 경우 - 기존 데이터에 추가
#                         self.add_completed_candle(symbol, timestamp, new_candle)
#
#                         # 콜백 호출
#                         if self.on_candle_complete:
#                             self.on_candle_complete(symbol, timestamp, new_candle)
#                     else:
#                         # 진행중인 캔들 업데이트
#                         self.current_candles[symbol] = new_candle
#
#                         # 콜백 호출
#                         if self.on_candle_update:
#                             self.on_candle_update(symbol, timestamp, new_candle)
#
#         except Exception as e:
#             print(f"메시지 처리 오류: {e}")
#
#     def add_completed_candle(self, symbol, timestamp, candle_data):
#         """완료된 캔들을 기존 데이터에 추가"""
#         if symbol in self.ohlcv_data:
#             # 새로운 행 추가
#             new_row = pd.Series(candle_data, name=timestamp)
#
#             # 중복 체크 (같은 시간의 캔들이 이미 있는지)
#             if timestamp not in self.ohlcv_data[symbol].index:
#                 self.ohlcv_data[symbol] = pd.concat([self.ohlcv_data[symbol], new_row.to_frame().T])
#
#                 # 오래된 데이터 제거 (메모리 관리 - 최대 2000개 캔들만 유지)
#                 if len(self.ohlcv_data[symbol]) > 2000:
#                     self.ohlcv_data[symbol] = self.ohlcv_data[symbol].tail(2000)
#
#                 print(f"[{datetime.now().strftime('%H:%M:%S')}] {symbol} 새 캔들 추가: "
#                       f"시간={timestamp.strftime('%H:%M')}, "
#                       f"종가={candle_data['close']:.6f}, "
#                       f"거래량={candle_data['volume']:.2f}")
#             else:
#                 # 기존 캔들 업데이트 (마지막 캔들이 다시 들어오는 경우)
#                 self.ohlcv_data[symbol].loc[timestamp] = candle_data
#
#     def on_error(self, ws, error):
#         """웹소켓 오류 처리"""
#         print(f"웹소켓 오류: {error}")
#
#     def on_close(self, ws, close_status_code, close_msg):
#         """웹소켓 연결 종료"""
#         print("웹소켓 연결이 종료되었습니다.")
#
#         # 자동 재연결 시도
#         if self.running:
#             print("5초 후 재연결을 시도합니다...")
#             time.sleep(5)
#             self.start_websocket()
#
#     def on_open(self, ws):
#         """웹소켓 연결 성공"""
#         print("웹소켓 연결 성공!")
#
#         # 구독할 스트림들
#         streams = list(self.symbol_map.values())
#
#         # 구독 메시지 전송
#         subscribe_message = {
#             "method": "SUBSCRIBE",
#             "params": streams,
#             "id": 1
#         }
#
#         ws.send(json.dumps(subscribe_message))
#         print(f"구독 완료: {streams}")
#
#     def start_websocket(self):
#         """웹소켓 시작"""
#         if self.ws and not self.ws.sock.closed:
#             return
#
#         self.running = True
#
#         # 웹소켓 생성
#         self.ws = websocket.WebSocketApp(
#             self.ws_url,
#             on_message=self.on_message,
#             on_error=self.on_error,
#             on_close=self.on_close,
#             on_open=self.on_open
#         )
#
#         # 별도 스레드에서 실행
#         ws_thread = threading.Thread(target=self.ws.run_forever)
#         ws_thread.daemon = True
#         ws_thread.start()
#
#         return ws_thread
#
#     def stop_websocket(self):
#         """웹소켓 중지"""
#         self.running = False
#         if self.ws:
#             self.ws.close()
#
#     def get_latest_data(self, symbol, periods=100):
#         """
#         최신 데이터 가져오기 (현재 진행중인 캔들 포함)
#
#         Parameters:
#         symbol (str): 심볼 (예: 'BTC/USDT')
#         periods (int): 가져올 캔들 개수
#
#         Returns:
#         pd.DataFrame: OHLCV 데이터
#         """
#         if symbol not in self.ohlcv_data:
#             return pd.DataFrame()
#
#         # 기존 완료된 캔들들
#         completed_candles = self.ohlcv_data[symbol].tail(periods - 1).copy()
#
#         # 현재 진행중인 캔들 추가
#         if symbol in self.current_candles:
#             current_time = pd.Timestamp.now().floor('1min')  # 현재 분으로 맞춤
#             current_candle = pd.Series(self.current_candles[symbol], name=current_time)
#
#             # 진행중인 캔들 추가
#             result = pd.concat([completed_candles, current_candle.to_frame().T])
#             return result.tail(periods)
#         else:
#             return completed_candles
#
#     def get_current_prices(self):
#         """현재 가격 정보 출력"""
#         prices = {}
#         for symbol in self.symbols:
#             if symbol in self.current_candles:
#                 prices[symbol] = self.current_candles[symbol]['close']
#         return prices
#
#     def print_status(self):
#         """현재 상태 출력"""
#         print(f"\n=== 현재 상태 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
#
#         for symbol in self.symbols:
#             if symbol in self.ohlcv_data and symbol in self.current_candles:
#                 completed_count = len(self.ohlcv_data[symbol])
#                 current_price = self.current_candles[symbol]['close']
#                 latest_time = self.ohlcv_data[symbol].index[-1]
#
#                 print(f"{symbol:>8}: 완료캔들 {completed_count:>4}개 | "
#                       f"현재가 {current_price:>10.6f} | "
#                       f"최신시간 {latest_time.strftime('%H:%M')}")
#
#     def save_to_csv(self, directory="./data"):
#         """데이터를 CSV 파일로 저장"""
#         import os
#
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#
#         for symbol in self.symbols:
#             if symbol in self.ohlcv_data:
#                 filename = f"{directory}/{symbol.replace('/', '_')}_1m.csv"
#                 self.ohlcv_data[symbol].to_csv(filename)
#                 print(f"{symbol} 데이터를 {filename}에 저장했습니다.")
#
#
# def example_usage():
#     """사용 예시"""
#
#     # 관리자 생성
#     manager = BinanceOHLCVManager(['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT'])
#
#     # 콜백 함수 정의
#     def on_candle_complete(symbol, timestamp, candle):
#         print(f"✅ {symbol} 캔들 완료: {timestamp.strftime('%H:%M')} "
#               f"C:{candle['close']:.6f} V:{candle['volume']:.1f}")
#
#     def on_candle_update(symbol, timestamp, candle):
#         # 너무 많은 업데이트를 방지하기 위해 일부만 출력
#         if hash(symbol) % 10 == 0:  # 10분의 1만 출력
#             print(f"🔄 {symbol} 업데이트: C:{candle['close']:.6f}")
#
#     # 콜백 등록
#     manager.on_candle_complete = on_candle_complete
#     manager.on_candle_update = on_candle_update
#
#     try:
#         # 1. 초기 데이터 가져오기
#         manager.fetch_initial_data(limit=500)  # 최근 500개 캔들
#
#         # 2. 웹소켓 시작
#         print("\n웹소켓을 시작합니다...")
#         ws_thread = manager.start_websocket()
#
#         # 3. 주기적으로 상태 출력
#         start_time = time.time()
#
#         while True:
#             time.sleep(30)  # 30초마다
#
#             # 상태 출력
#             manager.print_status()
#
#             # 현재 가격들
#             prices = manager.get_current_prices()
#             print(f"현재 가격: {prices}")
#
#             # 10분마다 CSV 저장
#             if (time.time() - start_time) % 600 < 30:  # 약 10분마다
#                 manager.save_to_csv()
#
#             # 특정 심볼의 최신 데이터 확인
#             btc_data = manager.get_latest_data('BTC/USDT', periods=5)
#             if not btc_data.empty:
#                 print(f"BTC 최근 5분봉:")
#                 print(btc_data[['close', 'volume']].round(6))
#
#     except KeyboardInterrupt:
#         print("\n프로그램을 종료합니다...")
#         manager.stop_websocket()
#         manager.save_to_csv()  # 종료 전 저장
#
#
# if __name__ == "__main__":
#     example_usage()



# websocket은 코루틴을 사용하므로 asyncio 패키지 추가
import asyncio
# websockets 패키지 추가
import websockets

# 클라이언트가 연결되면 실행되는 함수
async def echo(ws):
    # 클라이언트가 연결되서 끊어질때 까지 무한 루프
    while True:
        try:
            # 클라이언트가 보내올 메시지를 받기 위해 대기
            msg = await ws.recv()
            # 메시지가 들어오면 화면에 출력
            print('receive the msg {}'.format(msg))
            # 원 메시지에 'send: '라는 문구를 추가해 클라이언트로 다시 보냄
            await ws.send('send: ' + msg)
        except:
            # 예외가 발생했다면 클라이언트가 연결해제 됐다고 보고 해당 함수 종료
            print('client disconnected')
            break

# 클라이언트를 대기하는 함수
async def server_loop():
    print('waiting for the client')
    # 무한 루프
    while True:
        # 서버 실행
        async with websockets.serve(echo, 'localhost', 3000) as ws:
            # 무한 대기
            await asyncio.Future()

# 서버 루프 시작
asyncio.run(server_loop())



