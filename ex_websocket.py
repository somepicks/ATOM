# pingpong 및 연결 종료 발생 시 자동 재 시작 추가
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
import asyncio
import websockets
import json
import requests
import time


class WebSocket(QThread):
    event_data = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True

    def get_real_time_key(self):
        global APP_KEY
        global APP_SECRET
        global Virtual_Actual_check

        BASE_URL = "https://openapivts.koreainvestment.com:29443"  #모의

        url = f"{BASE_URL}/oauth2/Approval"
        headers = {"Content-Type": "application/json"}
        param = {"appkey": APP_KEY, "secretkey": APP_SECRET}
        response = requests.post(url, headers=headers, json=param)

        if response.status_code == 200:
            data = response.json()
            real_time_key = data.get("approval_key")
            return real_time_key
        else:
            return None

    async def connect(self):
        global designated_stock_List

        try:
            g_approval_key = self.get_real_time_key()
            if not g_approval_key:
                return

            url = 'ws://ops.koreainvestment.com:31000' # 모의투자계좌
            code_list = [['1', 'H0IFCNT0', "101V12"]]

            senddata_list = []

            for i, j, k in code_list:
                temp = '{"header":{"approval_key": "%s","custtype":"P","tr_type":"%s","content-type":"utf-8"},"body":{"input":{"tr_id":"%s","tr_key":"%s"}}}' % (
                    g_approval_key, i, j, k)
                senddata_list.append(temp)

            async with websockets.connect(url, ping_interval=None) as websocket:
                for senddata in senddata_list:
                    await websocket.send(senddata)
                    await asyncio.sleep(0.5)
                    self.event_data.emit(f"Input Command: {senddata}")

                while self.is_running:
                    data = await websocket.recv()

                    if data[0] == '0' or data[0] == '1':
                        self.event_data.emit(f"Received Data: {data}")

                    else:
                        jsonObject = json.loads(data)
                        trid = jsonObject["header"]["tr_id"]

                        if trid != "PINGPONG":
                            rt_cd = jsonObject["body"]["rt_cd"]

                            if rt_cd == '1':
                                if jsonObject["body"]["msg1"] != 'ALREADY IN SUBSCRIBE':
                                    print("### ERROR RETURN CODE")
                                break

                            elif rt_cd == '0':
                                print("### RETURN CODE")
                                if trid == "H0IFCNI0" or trid == "H0MFCNI0" or trid == "H0EUCNI0":  # 지수/상품/주식 선물옵션 & 야간선물옵션
                                    aes_key = jsonObject["body"]["output"]["key"]
                                    aes_iv = jsonObject["body"]["output"]["iv"]
                                    print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                        elif trid == "PINGPONG":
                            print("### RECV [PINGPONG] [%s]" % (data))
                            await websocket.pong(data)  # 요게 없으면 강제 연결 종료됨
                            print("### SEND [PINGPONG] [%s]" % (data))

        except Exception as e:
            self.event_data.emit(f"Error: {str(e)}")
            time.sleep(0.1)
            await connect()              # 웹소켓 다시 시작

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.start_button = QPushButton("Start WebSocket")
        self.stop_button = QPushButton("Stop WebSocket")

        self.start_button.clicked.connect(self.start_websocket)
        self.stop_button.clicked.connect(self.stop_websocket)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.websocket_thread = WebSocket()
        self.websocket_thread.event_data.connect(self.update_label)

    def start_websocket(self):
         self.websocket_thread.start()

    def stop_websocket(self):
        self.websocket_thread.stop()

    def update_label(self, data):
        self.label.setText(data)

if __name__ == "__main__":
    APP_KEY = ""
    APP_SECRET = ""
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()