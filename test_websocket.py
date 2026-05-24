import websocket
import requests
import json
import time
from threading import Thread
from pprint import pprint
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout, \
    QTableWidget, QSplitter, QApplication, QCheckBox, QTextEdit, QTableWidgetItem, QHeaderView, QComboBox, \
    QAbstractItemView, QHBoxLayout, QTimeEdit, QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import KIS

class KISReal(QThread):
    # def __init__(self, app_key, secret_key, callback=print):
    price_updated = pyqtSignal(dict)
    order_filled = pyqtSignal(dict)
    def __init__(self, dict_info, dict_orders):
        super().__init__()
        self.app_key = dict_info['key']
        self.secret_key = dict_info['secret']
        self.user_id = dict_info['ID']
        self.market = dict_info['market']
        # self.callback = callback

        self.ws = None
        self.running = False
        self._connect_key = None

        # 주문 체결용 복호화에 사용
        self.aes_key = None
        self.aes_iv = None
        # 구독할 종목 목록 (tr_id: [종목코드 리스트])
        self._subscriptions = {}

    # ---------------- 종목 등록 ---------------- #
    def subscribe(self, tr_id, codes):
        """예: subscribe('H0MFASP0', ['A05605', 'A01606'])"""
        self._subscriptions[tr_id] = codes
        print(f"{self._subscriptions= }")

    # ---------------- 인증 ---------------- #
    def _get_approval_key(self):
        url = "https://openapi.koreainvestment.com:9443/oauth2/Approval"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.secret_key
        }
        res = requests.post(url, headers={"content-type": "application/json"}, data=json.dumps(body))
        return res.json()["approval_key"]

    # ---------------- 구독 메시지 빌드 ---------------- #
    def _build_message(self, tr_id, tr_key, tr_type='1'):
        return json.dumps({
            "header": {
                "approval_key": self._connect_key,
                "custtype": "P",
                "tr_type": tr_type,
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key
                }
            }
        })

    # ---------------- 데이터 파싱 ---------------- #
    def _parse(self, data):
        parts = data.split('|')
        if len(parts) < 4:
            return
        tr_id = parts[1]
        raw = parts[3]
        if tr_id == 'H0IFASP0':  # 선물 호가
            self._parse_hoka('국내선물', raw)
        elif tr_id == 'H0IFCNT0':  # 선물 체결
            self._parse_contract('국내선물',raw)
        elif tr_id == 'H0MFASP0':  # 야간선물 호가
            self._parse_hoka('국내선물',raw)
        elif tr_id == 'H0MFCNT0':  # 야간선물 체결
            self._parse_contract('국내선물',raw)
        elif tr_id == 'H0STASP0':  # 국내주식 호가
            self._parse_hoka('국내주식', raw)
        elif tr_id == 'H0STCNT0':  # 국내주식 체결
            self._parse_contract('국내주식',raw)
        elif tr_id == 'H0STCNI0' or tr_id == 'H0STCNI9':  # 국내주식 체결통보
            self._parse_chegyeol(raw)
        elif tr_id == 'H0IFCNI0':  # 국내선옵 체결통보
            pprint(parts)
            self._parse_chegyeol(raw)
        else:
            print(f"[UNKNOWN TR] {tr_id}: {raw[:80]}")

    def _parse_hoka(self, market, raw):
        v = raw.split('^')
        pprint(v)
        if market == '국내주식':
            result = {
                'type': 'hoka',
                'code': v[0],
                'time': v[1],
                # 매도호가 1~5
                'ask1': v[3], 'ask2': v[4], 'ask3': v[5], 'ask4': v[6], 'ask5': v[7],
                # 매수호가 1~5
                'bid1': v[13], 'bid2': v[14], 'bid3': v[15], 'bid4': v[16], 'bid5': v[17],
                # 매도잔량 1~5
                'ask_qty1': v[23], 'ask_qty2': v[24], 'ask_qty3': v[25], 'ask_qty4': v[26], 'ask_qty5': v[27],
                # 매수잔량 1~5
                'bid_qty1': v[33], 'bid_qty2': v[34], 'bid_qty3': v[35], 'bid_qty4': v[36], 'bid_qty5': v[37],
                # 총잔량
                'total_ask_qty': v[43],
                'total_bid_qty': v[44],
            }
        elif market == '국내선물':
            result = {
                'type': 'hoka',
                'code': v[0],
                'time': v[1],
                # 매도호가 1~5
                'ask1': v[2], 'ask2': v[3], 'ask3': v[4], 'ask4': v[5], 'ask5': v[6],
                # 매수호가 1~5
                'bid1': v[7], 'bid2': v[8], 'bid3': v[9], 'bid4': v[10], 'bid5': v[11],
                # 매도잔량 1~5
                'ask_qty1': v[22], 'ask_qty2': v[23], 'ask_qty3': v[24], 'ask_qty4': v[25], 'ask_qty5': v[26],
                # 매수잔량 1~5
                'bid_qty1': v[27], 'bid_qty2': v[28], 'bid_qty3': v[29], 'bid_qty4': v[30], 'bid_qty5': v[31],
                # 총잔량
                'total_ask_qty': v[34],
                'total_bid_qty': v[35],
                '총매도호가잔량증감': v[36],
                '총매수호가잔량증감': v[37],
            }
        self.callback(result)

    def _decrypt(self, cipher_text):
        cipher = AES.new(self.aes_key.encode('utf-8'), AES.MODE_CBC, self.aes_iv.encode('utf-8'))
        return unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size).decode()

    def _parse_contract(self, market, raw):
        v = raw.split('^')
        if market == '국내주식':
            result = {
                'type': 'contract',
                'code': v[0],
                'time': v[1],
                'price': v[2],  # 현재가
                'sign': v[3],  # 전일대비부호
                'diff': v[4],  # 전일대비
                'rate': v[5],  # 전일대비율
                'open': v[7],  # 시가
                'high': v[8],  # 고가
                'low': v[9],  # 저가
                'ask': v[10],  # 매도호가
                'bid': v[11],  # 매수호가
                'vol': v[12],  # 체결거래량
                'acc_vol': v[13],  # 누적거래량
            }
        elif market == '국내선물':
            result = {
                'type': 'contract',
                'code': v[0],
                'time': v[1],
                'ratio': v[2],  # 선물 전일 대비
                'sign': v[3],  # 전일대비부호
                'diff': v[4],  # 전일대비
                'rate': v[5],  # 전일대비율
                'price': v[7],  # 선물 현재가
                'open': v[8],  # 선물 시가2
                'low': v[9],  # 선물 최저가
                'ask': v[10],  # 최종 거래량
                'vol': v[11],  # 누적 거래량
                'vol_price': v[12],  # 누적 거래 대금
            }
        self.callback(result)

    def _parse_chegyeol(self, raw):
        print(f"{self.aes_key= }")
        print(f"{self.aes_iv= }")
        if not self.aes_key or not self.aes_iv:
            print("[WARN] AES key not ready")
            return

        try:
            # 🔥 복호화
            dec = self._decrypt(raw)
            v = dec.split('^')

            result = {
                'type': 'chegyeol',
                'id': v[0],
                'acc': v[1],
                'uuid': v[2],
                'won_uuid': v[3],
                '매수매도': v[4],
                '정정': v[5],
                '주문종류': v[6],
                'ticker': v[8],
                '체결수량': v[9],
                'price': v[10],
                'time': v[11],
                '체결여부': v[13],
                '주문수량': v[16],
                '거래소': v[16],
                '실시간체결창 표시여부': v[20],
                '체결종목명': v[24],
                '주문가격': v[25],
            }
            print("[복호화 완료]")
            print(result)
            self.callback(result)

        except Exception as e:
            print("[DECRYPT ERROR]", e)

    # ---------------- 시스템 메시지 처리 ---------------- #
    def _handle_system(self, ws, data):
        print(f"_handle_system {data}")
        try:
            rdic = json.loads(data)
            tr_id = rdic['header']['tr_id']

            if tr_id == "PINGPONG":
                ws.send(data, websocket.ABNF.OPCODE_TEXT)
                return

            body = rdic.get('body')
            if body is None:
                return

            is_ok = body.get('rt_cd') == '0'
            msg = body.get('msg1', '')
            tr_key = rdic['header'].get('tr_key', '')

            if is_ok:
                print(f"[KIS] 구독 성공 ✅ tr_id={tr_id}, code={tr_key}, msg={msg}")
                if tr_id == "H0STCNI0" or tr_id == "H0STCNI9":
                    output = body.get('output', {})
                    self.aes_key = output.get('key')
                    self.aes_iv = output.get('iv')
                    print(f"[AES KEY SET] key={self.aes_key}, iv={self.aes_iv}")
            else:
                print(f"[KIS] 구독 실패 ❌ tr_id={tr_id}, msg={msg}")

        except Exception as e:
            print("system msg error:", e)


    # 밑에는 자동 재구독 보완
    def on_open(self, ws):
        # print("[WS OPEN] 재구독 시작")

        # 🔥 체결통보 대비 초기화
        self.aes_key = None
        self.aes_iv = None

        def _do_subscribe():
            time.sleep(0.5)  # 서버 준비 대기

            for tr_id, codes in self._subscriptions.items():
                for code in codes:
                    msg = self._build_message(tr_id, code)
                    ws.send(msg, websocket.ABNF.OPCODE_TEXT)
                    print(f"[재구독] {tr_id} / {code}")
                    time.sleep(0.2)

        Thread(target=_do_subscribe, daemon=True).start()

    def on_message(self, ws, data):
        if data[0] in ('0', '1'):
            self._parse(data)
        else:
            self._handle_system(ws, data)

    def on_error(self, ws, error):
        print(f"[KIS] error: {error}")

    def on_close(self, ws, status_code, close_msg):
        print(f"[KIS] closed: {status_code}, {close_msg}")

    # ---------------- 실행 / 종료 ---------------- #
    def run(self):
        self.running = True
        while self.running:
            try:
                if not self._connect_key:  # 실패했을 때만 재발급
                    self._connect_key = self._get_approval_key()
                print(f"[KIS] approval_key 발급 완료 {self._connect_key}")
                Thread(target=self.rest_fallback, daemon=True).start()

                self.ws = websocket.WebSocketApp(
                    "ws://ops.koreainvestment.com:21000",
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                print("연결 에러:", e)
                self._connect_key = None  # 에러 시 초기화해서 다음 루프에서 재발급
            if self.running:
                print("60초 후 재연결...")
                time.sleep(60)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

    def rest_fallback(self):
        while self.running:
            time.sleep(30)
            print(f'rest fallback {datetime.datetime.now()}')

    def callback(self,data):
        if data['type'] == 'hoka':
            print(
                f"[호가] {data['code']} | 매도1: {data['ask1']} ({data['ask_qty1']}) | 매수1: {data['bid1']} ({data['bid_qty1']})")
        elif data['type'] == 'contract':
            print(
                f"[체결] {data['code']} | 시간: {data['time']} | 가격: {data['price']} | 등락: {data['sign']}{data['diff']} ({data['rate']}%) | 거래량: {data['vol']}")
        elif data['type'] == 'chegyeol':
            print(f"chegyeol: {data}")

class Window(QMainWindow): #별도로 실행하고자 할 때
    send_orders = pyqtSignal(str,list)
    def __init__(self):
        super().__init__()
        self.QPB_start_stock = QPushButton('웹소켓 감시(주식)')
        self.QPB_start_futopt = QPushButton('웹소켓 감시(선옵)')
        self.QPB_start_futopt_night = QPushButton('웹소켓 감시(야간선옵)')
        self.QPB_start_chegyeol = QPushButton('체결감시')
        self.QPB_stop = QPushButton('웹소켓 중지')
        self.QPB_add = QPushButton('종목추가')
        self.QPB_del = QPushButton('종목삭제')
        self.QLE = QLineEdit()
        self.QTE = QTextEdit()

        QVB_main = QVBoxLayout()
        QVB_main.addWidget(self.QPB_start_stock)
        QVB_main.addWidget(self.QPB_start_futopt)
        QVB_main.addWidget(self.QPB_start_futopt_night)
        QVB_main.addWidget(self.QPB_start_chegyeol)
        QVB_main.addWidget(self.QPB_add)
        QVB_main.addWidget(self.QPB_del)
        QVB_main.addWidget(self.QLE)
        QVB_main.addWidget(self.QTE)

        QW_main = QWidget()
        QW_main.setLayout(QVB_main)
        self.setCentralWidget(QW_main)
        self.QPB_start_stock.clicked.connect(lambda:self.signal_start('국내주식'))
        self.QPB_start_futopt.clicked.connect(lambda:self.signal_start('국내선옵'))
        self.QPB_start_futopt_night.clicked.connect(lambda:self.signal_start('야간선옵'))

        self.QPB_add.clicked.connect(lambda: self.add_order(self.QLE.text()))
        self.QPB_del.clicked.connect(lambda: self.del_order(self.QLE.text()))
        self.dict_info = {}
    def signal_start(self,market):
        if market == '국내주식':
            key = "PSnRbdaAPoj86qrw73q25rCnIzc8zBqBs02J"
            secret = "68UdwXxybY6j19I/QW86VLXe676PUsJnCmIq99oq2tjazDn+gDoY6IcwLOZMuMRY0wuy5Mzjd1C5AvXrNknEtZiaazSDcdxg4+1BiYdlSEs7drk2d8xVMqSdASB79QN6g8TUOf/8VsLOWIx3IQeVhn0gFkQTlHNQxfEZwG4rnvF9FA1Ndmc="
            night = False
            tr_key = 'somepick'
        elif market == '국내선옵' or market == '야간선옵':
            key = "PSCLO2WTCrnbFTVJLqZcRGZwYVAll8BHU34I"
            secret = "l/12Smyub2n5MSDGwxiLde3vK6FWsRWq6HcU8RPfKYgw31qnDiQLhyaj1y2cpyOromd9nZOkeIBIug7PWu+RQShovpzMGB5uf59xKFnOAIbkmTGFGdNhr9ULEWR4OiK2SDdUuZ9PST94RZfy5IDpewS2vUi0q6wcO2t1C/pJ1QZFxsPNvvk="
            tr_key = 'somepick'
            if market == '국내선옵':
                night = False
            elif market == '야간선옵':
                night = True
            dict_orders = {}
        mock = False
        # self.dict_info = {"key":key,'secret':secret,"ID":'somepick','호가':hoka,'체결가':contract,'체결':chegyeol}
        self.dict_info = {"key":key,'secret':secret,"ID":tr_key,'market':market,'night':night,'mock':mock}
        self.dict_orders = {}
        self.thread_ws = KISReal(dict_info=self.dict_info,dict_orders=self.dict_orders)
        self.thread_ws.price_updated.connect(self.price_data)
        self.thread_ws.order_filled.connect(self.chegyeol_closed)
        self.send_orders.connect(self.thread_ws.subscribe)
        self.send_orders.emit('H0MFCNI0', ['somepick'])
        self.thread_ws.start()
    @pyqtSlot(dict)
    def price_data(self,data):
        print(data)
    @pyqtSlot(dict)
    def chegyeol_closed(self,data):
        print(f"체결:    {data}")

    def add_order(self,code):
        print(code)
        if not code in list(set(self.dict_orders.values())):
            self.thread_ws.add_symbol(code)
        id = datetime.datetime.now().replace(microsecond=0).strftime("%Y%m%d%H%M%S")
        self.dict_orders[id] = code
        self.QTE.clear()
        formatted_text = json.dumps(self.dict_orders, indent=4, ensure_ascii=False)
        self.QTE.setText(formatted_text)
        print(self.dict_orders)
    def del_order(self,uuid):
        try:
            dict_ord_old = self.dict_orders.copy()
            self.dict_orders.pop(uuid)

            if not list(set(dict_ord_old.values())) == list(set(self.dict_orders.values())):
                code = self.dict_orders[uuid]  # 🔥 핵심
                # 동일 종목이 더 있는지 확인
                if code not in self.dict_orders.values():
                    self.thread_ws.remove_symbol(code)
                # self.send_orders.emit(self.dict_orders)
            self.QTE.clear()
            formatted_text = json.dumps(self.dict_orders, indent=4, ensure_ascii=False)
            self.QTE.setText(formatted_text)
            print(self.dict_orders)
        except:
            print(f"uuid 확인 필요 {uuid}")


if __name__ == "__main__":





    # market = '국내주식'
    # if market == '국내주식':
    #     key = "PSnRbdaAPoj86qrw73q25rCnIzc8zBqBs02J"
    #     secret = "68UdwXxybY6j19I/QW86VLXe676PUsJnCmIq99oq2tjazDn+gDoY6IcwLOZMuMRY0wuy5Mzjd1C5AvXrNknEtZiaazSDcdxg4+1BiYdlSEs7drk2d8xVMqSdASB79QN6g8TUOf/8VsLOWIx3IQeVhn0gFkQTlHNQxfEZwG4rnvF9FA1Ndmc="
    # elif market == '국내선옵':
    #     key = "PSCLO2WTCrnbFTVJLqZcRGZwYVAll8BHU34I"
    #     secret = "l/12Smyub2n5MSDGwxiLde3vK6FWsRWq6HcU8RPfKYgw31qnDiQLhyaj1y2cpyOromd9nZOkeIBIug7PWu+RQShovpzMGB5uf59xKFnOAIbkmTGFGdNhr9ULEWR4OiK2SDdUuZ9PST94RZfy5IDpewS2vUi0q6wcO2t1C/pJ1QZFxsPNvvk="
    # kis = KISReal(
    #     app_key=key,
    #     secret_key=secret,
    #     callback=callback
    # )




    import sys
    def ExceptionHook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = ExceptionHook  # 예외 후크 설정 부분 (에러가 표시되지 않으면서 종료되는증상을 방지하기 위함)
    app = QApplication([])
    main_table = Window()
    main_table.setMinimumSize(600, 400)
    main_table.show()
    app.exec()


    # kis.subscribe('H0EUASP0', ['A05605'])  # 선물 체결가
    # kis.subscribe('H0IFCNT0', ['A01606'])  # 선물 체결
    # kis.subscribe('H0IFCNI0', ['somepick'])  # 선물 통보
    # kis.subscribe('H0MFCNI0', ['somepick'])  # 야간선물 통보
    # kis.subscribe('H0MFCNT0', ['A01606','A05606'])  # 야간선물 체결
    # kis.subscribe('H0IFCNI0', ['somepick'])  # 옵션 통보
    # kis.subscribe('H0STCNI0', ['somepick'])  # 주식 체결통보

    # kis.start()