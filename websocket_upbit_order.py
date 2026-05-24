import jwt
import uuid
import json
import time
from websocket import WebSocketApp
from threading import Thread
import datetime

class UpbitPrivate:
    def __init__(self, access_key, secret_key, callback=print):
        self.access_key = access_key
        self.secret_key = secret_key
        self.callback = callback

        self.ws = None
        self.running = False

    # ---------------- JWT 생성 ---------------- #
    def _make_headers(self):
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload, self.secret_key)
        return {"Authorization": f"Bearer {jwt_token}"}

    # ---------------- 이벤트 ---------------- #
    def on_message(self, ws, message):
        try:
            data = json.loads(message.decode('utf-8'))
            self.callback(data)
        except Exception as e:
            print("parse error:", e)

    def on_error(self, ws, err):
        self.callback(f"error: {err}")

    def on_close(self, ws, *args):
        self.callback("closed")

    def on_open(self, ws):
        th = Thread(target=self.subscribe, daemon=True)
        th.start()

    # ---------------- 기능 ---------------- #
    def subscribe(self):
        request = [
            {"ticket": "private"},
            {"type": "myOrder"}  # 주문/체결
        ]
        self.ws.send(json.dumps(request))

    # ---------------- 실행 ---------------- #
    def start(self):
        self.running = True

        while self.running:
            try:
                headers = self._make_headers()
                # REST fallback thread
                Thread(target=self.rest_fallback, daemon=True).start()

                self.ws = WebSocketApp(
                    "wss://api.upbit.com/websocket/v1/private",
                    header=headers,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )

                self.ws.run_forever(ping_interval=30, ping_timeout=10)

            except Exception as e:
                print("error:", e)

            time.sleep(2)  # 재연결 대기

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

    # def add_order(self, order_id, symbol):
    #     self.open_orders[order_id] = symbol

    def rest_fallback(self):
        while self.running:
            time.sleep(30)
            print(f'rest fallback {datetime.datetime.now()}')
            # for order_id, symbol in list(self.open_orders.items()):
            #     try:
            #         order = self.ex_ws.fetch_order(order_id, symbol)
            #         status = order['status']
            #
            #         if status == 'closed':
            #             dic_out = {
            #                 order_id: {
            #                     'state': '체결',
            #                     'amount': order['amount'],
            #                     'price': order['average']
            #                 }
            #             }
            #             self.callback(dic_out)
            #             del self.open_orders[order_id]
            #
            #         elif status == 'canceled':
            #             dic_out = {
            #                 order_id: {
            #                     'state': '취소',
            #                     'amount': order['amount'],
            #                     'price': 0
            #                 }
            #             }
            #             self.callback(dic_out)
            #             del self.open_orders[order_id]
            #
            #     except Exception as e:
            #         print("REST fallback error:", e)
def callback(data):
    print("📡 체결 데이터:", data)


if __name__ == "__main__":
    upbit_private = UpbitPrivate(
        access_key="FqPwE4yDhwe14wYr3htfN7KmtUwGphxK9xYDhVAx",
        secret_key="rDwksoNBntNqqcSdg1VxpeV4vx7aYZZe423Mw8Fg",
        callback=callback
    )

    upbit_private.start()